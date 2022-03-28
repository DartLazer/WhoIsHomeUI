import requests
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest, JsonResponse
from django.shortcuts import render, redirect
from django.conf import settings as django_settings
from django.urls import reverse
from django.utils import timezone
from .scanner_functions import *
from .backgroundtasks import schedule_scan, scan
from background_task.models import Task
from .forms import HostForm, ChangeHostNameForm, ScannerSettingsForm, EmailSettingsForm
from urllib.parse import urlencode
import logging

last_time_checked = False
update_available = False
github_version = False

logger = logging.getLogger('log_to_file')


def index(request):
    return HttpResponseRedirect('whoishome')


def settings(request):
    email_settings = EmailConfig.objects.get(pk=1)

    context = {'email': email_settings}
    background_tasks = Task.objects.all()
    saved_indicator = 0
    saved_flag = request.GET.get('saved')
    scanner_running = False
    if len(background_tasks) > 0:
        scanner_running = True

    if 'update_scanner_settings' in request.POST:
        scanner_settings_form = ScannerSettingsForm(request.POST, request=request)
        if scanner_settings_form.is_valid():
            base_url = reverse('settings')
            if scanner_settings_form.has_changed():
                scanner_config = ScannerConfig.objects.get(pk=1)
                saved_indicator = 1  # forms has changed, toggling saved flag
                if 'email' in scanner_settings_form.changed_data:
                    user = request.user
                    setattr(user, 'email', scanner_settings_form.cleaned_data['email'])
                    user.save()
                    scanner_settings_form.changed_data.remove('email')
                for changed_data in scanner_settings_form.changed_data:
                    setattr(scanner_config, changed_data, scanner_settings_form.cleaned_data[changed_data])
                scanner_config.save()
            query_string = urlencode({'saved': saved_indicator})  # for saved modal
            url = '{}?{}'.format(base_url, query_string)
            logger.warning('Scanner settings updated.')
            return redirect(url)

    elif 'update_email_settings' in request.POST:
        email_settings_form = EmailSettingsForm(request.POST, request=request)
        if email_settings_form.is_valid():
            base_url = reverse('settings')
            if email_settings_form.has_changed():
                email_config = EmailConfig.objects.get(pk=1)
                saved_indicator = 1  # forms has changed, toggling saved flag
                if 'email' in email_settings_form.changed_data:
                    user = request.user
                    setattr(user, 'email', email_settings_form.cleaned_data['email'])
                    user.save()
                    email_settings_form.changed_data.remove('email')
                for changed_data in email_settings_form.changed_data:
                    setattr(email_config, changed_data, email_settings_form.cleaned_data[changed_data])
                email_config.save()
            query_string = urlencode({'saved': saved_indicator})  # for saved modal
            url = '{}?{}'.format(base_url, query_string)
            logger.warning('Email settings updated.')
            return redirect(url)

    with open('logfile.log') as file:
        logfile = file.readlines()
        if len(logfile) > 30:
            logfile = logfile[-30:]

    scanner_settings_form = ScannerSettingsForm(request=request)
    email_settings_form = EmailSettingsForm(request=request)

    return render(request, 'whoishome/settings.html',
                  {'email': email_settings, 'scanner_settings_form': scanner_settings_form, 'email_settings_form': email_settings_form,
                   'saved_flag': saved_flag,
                   "logfile": logfile, 'update_available': update_check(), 'scanner_running': scanner_running})


def view_host(request, host_id):
    form_saved = False
    if Host.objects.filter(id=host_id).exists():
        host = Host.objects.get(id=host_id)
        if host.new is True:
            host.new = False
            host.save()
        host_form = HostForm(request=request, host=host)
        host_name_form = ChangeHostNameForm(request=request, host=host)

        if 'device_type' in request.POST:
            form = HostForm(request.POST, request=request, host=host)
            if form.is_valid():
                if form.has_changed():
                    for changed_field in form.changed_data:
                        setattr(host, changed_field, form.cleaned_data[changed_field])
                    host.save()
                    form_saved = True
                    host_form = HostForm(request=request, host=host)
        elif 'ChangeHostNameForm' in request.POST:
            form = ChangeHostNameForm(request.POST, request=request, host=host)
            if form.is_valid():
                if form.has_changed():
                    for changed_field in form.changed_data:
                        setattr(host, changed_field, form.cleaned_data[changed_field])
                    host.save()
                    form_saved = True
                    host_name_form = ChangeHostNameForm(request=request, host=host)

        logdata_query = None
        if LogData.objects.filter(host=host).exists():
            logdata_query = LogData.objects.filter(host=host).order_by('-id')[:10]
            # contains_logdata = True

        return render(request, 'whoishome/view_host.html', {'host': host, 'host_form': host_form, 'host_name_form': host_name_form, 'form_saved': form_saved,
                                                            'logdata_query': logdata_query, 'update_available': update_check()})

    logger.error(f'host: \'{host_id}\' not found')
    return HttpResponseRedirect('/whoishome/')


def getresults(request):
    if request.POST:
        if request.POST.get('host_id'):  # is host_id is in the request the host will be marked seen.
            host_id = int(request.POST.get('host_id'))
            host = Host.objects.get(pk=host_id)
            host.mark_seen()

    context = {'targets': [], 'home_hosts_list': [], 'new_hosts': [], 'scanner_running': False,
               'update_available': update_check()}  # dictionary to be send to the html page
    try:
        for host in Host.objects.all():
            try:
                if host.is_home and not host.target:
                    context['home_hosts_list'].append(host)  # adds host to home_host to be added to front page
                if host.target is True:
                    context['targets'].append(host)  # adds host to be sent to page.
            except ObjectDoesNotExist:  # target has not been scanned yet.
                if host.is_home:
                    context['home_hosts_list'].append(host)

        for host in Host.objects.all():
            if host.new:
                context['new_hosts'].append(host)

    except:
        pass

    return render(request, 'whoishome/index.html', context)


def network_timeline(request):
    logdata_query = LogData.objects.filter().order_by('-time_saved')[:10]
    log_dict = {}
    sort_log = {}
    x = 0
    for log in logdata_query:
        if log.check_out:
            log_dict[x] = {"time": log.check_out, 'arrival': False, 'host': log.host, 'logdata': log}
            sort_log[x] = log.check_out
            x += 1
        log_dict[x] = {"time": log.check_in, 'arrival': True, 'host': log.host, 'logdata': log}
        sort_log[x] = log.check_in
        x += 1

    sorted_log_list = sorted(sort_log, key=sort_log.get, reverse=True)
    sorted_log_dict = {}
    x = 0

    for sorted_index in sorted_log_list:
        sorted_log_dict[x] = log_dict[sorted_index]
        x += 1

    context = {'logdata_query': logdata_query, 'sorted_log_dict': sorted_log_dict, 'update_available': update_check()}

    return render(request, 'whoishome/network_timeline.html', context)


def update_page(request):
    changelog_url = 'https://raw.githubusercontent.com/DartLazer/WhoIsHomeUI/main/CHANGELOG.md'
    r = requests.get(changelog_url)
    if r.status_code == 200:
        changelog = r.text
        changelog = changelog.split('\n')
        print(changelog)
    else:
        changelog = 'Unable to retrieve changelog.'

    context = {'current_version': django_settings.CURRENT_VERSION, 'github_version': github_version, 'update_available': update_check(), 'changelog': changelog}

    return render(request, 'whoishome/update.html', context)


def enable_emailer(request):
    email_settings = EmailConfig.objects.get(pk=1)
    email_settings.enable_emailer()
    logger.warning("Emailer Enabled.")
    return HttpResponseRedirect('/whoishome/settings')


def disable_emailer(request):
    email_settings = EmailConfig.objects.get(pk=1)
    email_settings.disable_emailer()
    logger.warning("Emailer Disabled.")
    return HttpResponseRedirect('/whoishome/settings')


def start_scanner(request):
    schedule_scan(repeat=60)
    logger.warning("Scanner started. Scanning in 1 minute.")
    return HttpResponseRedirect('/')


def stop_scanner(request):
    background_tasks = Task.objects.filter(task_name='whoishome.backgroundtasks.background_network_scan')
    for background_task in background_tasks:
        background_task.delete()
    logger.warning("Scanner stopped.")
    return HttpResponseRedirect('/')


def scan_now(request):
    scan()
    return HttpResponseRedirect('/whoishome/')


def update_check():
    global update_available
    if update_available:
        return True
    now = timezone.now()
    global last_time_checked
    if last_time_checked is False or (now - last_time_checked).seconds >= 3600:
        version_check_url = 'https://raw.githubusercontent.com/DartLazer/WhoIsHomeUI/main/mysite/latest_version.txt'
        r = requests.get(version_check_url)
        if r.status_code == 200:
            last_time_checked = now
            remote_version = float(r.text)
            global github_version
            github_version = remote_version
            if remote_version > django_settings.CURRENT_VERSION:
                update_available = True
                return True
            else:
                update_available = False
                return False
    else:
        update_available = False
        return False
