import time

import requests
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest, JsonResponse
from django.shortcuts import render, redirect
from django.conf import settings as django_settings
from django.contrib import messages
from django.urls import reverse
from .models import Host, DiscordNotificationsConfig, HomePageSettingsConfig
from .timeline_functions import generate_timeline_data
from .scanner_functions import *
from .forms import HostForm, ChangeHostNameForm, ScannerSettingsForm, EmailSettingsForm, DiscordNotificationsForm, \
    HomePageSettingsForm
import logging

last_time_checked = False
update_available = False
github_version = False

logger = logging.getLogger('log_to_file')


def index(request):
    return HttpResponseRedirect('whoishome')


def clear_new_hosts(request):
    hosts = Host.objects.filter()
    for host in hosts:
        host.new = False
        host.save()

    return HttpResponseRedirect('/whoishome')


def settings(request):
    email_settings, created_bool = EmailConfig.objects.get_or_create(pk=1)

    discord_config = DiscordNotificationsConfig.objects.get(pk=1)

    scanner_config, created_bool = ScannerConfig.objects.get_or_create(pk=1)

    scanner_running = True if scanner_config.scanner_enabled else False

    if 'update_scanner_settings' in request.POST:
        scanner_settings_form = ScannerSettingsForm(request.POST, request=request)
        if scanner_settings_form.is_valid():
            if scanner_settings_form.has_changed():

                if 'email' in scanner_settings_form.changed_data:
                    user = request.user
                    setattr(user, 'email', scanner_settings_form.cleaned_data['email'])
                    user.save()
                    scanner_settings_form.changed_data.remove('email')
                for changed_data in scanner_settings_form.changed_data:
                    setattr(scanner_config, changed_data, scanner_settings_form.cleaned_data[changed_data])

                    messages.add_message(request, messages.INFO,
                                         'Scanner settings saved!',
                                         extra_tags='Saved!')

                scanner_config.save()
            logger.warning('Scanner settings updated.')
            return redirect('settings')

    elif 'update_email_settings' in request.POST:
        email_settings_form = EmailSettingsForm(request.POST, request=request)
        if email_settings_form.is_valid():
            if email_settings_form.has_changed():
                email_config = EmailConfig.objects.get(pk=1)
                if 'email' in email_settings_form.changed_data:
                    user = request.user
                    setattr(user, 'email', email_settings_form.cleaned_data['email'])
                    user.save()
                    email_settings_form.changed_data.remove('email')
                for changed_data in email_settings_form.changed_data:
                    setattr(email_config, changed_data, email_settings_form.cleaned_data[changed_data])

                    messages.add_message(request, messages.INFO,
                                         'Email settings saved!',
                                         extra_tags='Saved!')

                email_config.save()
            logger.warning('Email settings updated.')
            return redirect('settings')

    elif 'update_discord_settings' in request.POST:
        discord_form = DiscordNotificationsForm(request.POST, request=request)
        if discord_form.is_valid():
            if discord_form.has_changed():
                for changed_data in discord_form.changed_data:
                    setattr(discord_config, changed_data, discord_form.cleaned_data[changed_data])
                discord_config.save()
                messages.add_message(request, messages.INFO,
                                     'Discord settings saved!',
                                     extra_tags='Saved!')
            logger.warning('Discord settings updated.')
        return redirect('settings')

    with open('logfile.log') as file:
        logfile = file.readlines()
        if len(logfile) > 30:
            logfile = logfile[-30:]

    scanner_settings_form = ScannerSettingsForm(request=request)
    email_settings_form = EmailSettingsForm(request=request)
    discord_form = DiscordNotificationsForm(request=request)

    return render(request, 'whoishome/settings.html',
                  {'email': email_settings, 'scanner_settings_form': scanner_settings_form,
                   'email_settings_form': email_settings_form,
                   'discord_form': discord_form,
                   "logfile": logfile, 'update_available': update_check(), 'scanner_running': scanner_running,
                   "timezone": django_settings.TIME_ZONE})


def view_host(request, host_id):
    form_saved = False

    if not Host.objects.filter(id=host_id).exists():
        logger.error(f'host: \'{host_id}\' not found')
        return HttpResponseRedirect('/whoishome/')

    host = Host.objects.get(id=host_id)

    if host.new is True:
        host.new = False
        host.save()

    if 'chart_time_range' in request.POST:
        chart_range = request.POST['chart_time_range']
        timeline_dict = generate_timeline_data(host, chart_range)
    else:
        timeline_dict = generate_timeline_data(host, '7')

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
        logdata_query = LogData.objects.filter(host=host).order_by('-id')[:50]
        # contains_logdata = True

    return render(request, 'whoishome/view_host.html', {'host': host, 'host_form': host_form,
                                                        'host_name_form': host_name_form, 'form_saved': form_saved,
                                                        'logdata_query': logdata_query,
                                                        'update_available': update_check(), 'timeline': timeline_dict})


def getresults(request):
    home_page_settings_form = HomePageSettingsForm(request=request)

    if request.POST:
        if request.POST.get('host_id'):  # is host_id is in the request the host will be marked seen.
            host_id = int(request.POST.get('host_id'))
            host = Host.objects.get(pk=host_id)
            host.mark_seen()
        elif 'home_page_settings' in request.POST:
            form = HomePageSettingsForm(request.POST, request=request)
            if form.is_valid():
                home_page_settings = HomePageSettingsConfig.objects.get(pk=1)
                for changed_field in form.changed_data:
                    setattr(home_page_settings, changed_field, form.cleaned_data[changed_field])
                home_page_settings.save()
                home_page_settings_form = HomePageSettingsForm(request=request)

    context = {'targets': [], 'home_hosts_list': [], 'new_hosts': [], 'scanner_running': False,
               'update_available': update_check(),
               'home_page_settings_form': home_page_settings_form, 'all_devices': False}  # dictionary to be send to the html page

    home_page_settings = HomePageSettingsConfig.objects.get(pk=1)

    for host in Host.objects.all():
        if home_page_settings.show_all_devices:
            context['home_hosts_list'].append(host)
            context['all_devices'] = True
        else:
            if host.is_home and not host.target:
                context['home_hosts_list'].append(host)  # adds host to home_host to be added to front page

        if host.target is True:
            context['targets'].append(host)  # adds host to be sent to page.


    for host in Host.objects.all():
        if host.new:
            context['new_hosts'].append(host)

    return render(request, 'whoishome/index.html', context)


def network_timeline(request):
    log_data_query = LogData.objects.filter().order_by('-time_saved')
    if len(log_data_query) > 50:
        log_data_query = log_data_query[:50]
    log_dict = {}
    sort_log = {}
    x = 0
    for log in log_data_query:
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

    context = {'logdata_query': log_data_query, 'sorted_log_dict': sorted_log_dict, 'update_available': update_check()}

    return render(request, 'whoishome/network_timeline.html', context)


def update_page(request):
    changelog_url = 'https://raw.githubusercontent.com/DartLazer/WhoIsHomeUI/main/CHANGELOG.md'
    r = requests.get(changelog_url)
    if r.status_code == 200:
        changelog = r.text
        changelog = changelog.split('\n')
    else:
        changelog = 'Unable to retrieve changelog.'

    context = {'current_version': django_settings.CURRENT_VERSION, 'github_version': github_version,
               'update_available': update_check(), 'changelog': changelog}

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
    scanner_config, created_bool = ScannerConfig.objects.get_or_create(pk=1)
    scanner_config.scanner_enabled = True
    scanner_config.save()
    logger.warning("Scanner started. Scanning every minute.")
    return HttpResponseRedirect('/')


def stop_scanner(request):
    scanner_config, created_bool = ScannerConfig.objects.get_or_create(pk=1)
    scanner_config.scanner_enabled = False
    scanner_config.save()
    logger.warning("Scanner Stopped.")
    return HttpResponseRedirect('/')


def scan_now(request):
    scanner_config, created_bool = ScannerConfig.objects.get_or_create(pk=1)
    if scanner_config.scanner_enabled:
        print('Scanning')
        online_hosts = scan_network()
        scan_processor(online_hosts)
        is_home_check()
    return HttpResponseRedirect('')


def update_check():
    global update_available
    if update_available:
        return True
    now = timezone.now()
    global last_time_checked
    if last_time_checked is False or (now - last_time_checked).seconds >= 3600:
        version_check_url = 'https://raw.githubusercontent.com/DartLazer/WhoIsHomeUI/main/mysite/latest_version.txt'
        try:
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
        except requests.exceptions.ConnectionError:
            logger.error('Unable to check for updates. Connection failed.')
            pass

    else:
        update_available = False
        return False
