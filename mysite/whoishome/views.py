from django.http import HttpResponse, HttpResponseRedirect, HttpRequest, JsonResponse
from django.shortcuts import render
from .scanner_functions import *
from .backgroundtasks import schedule_scan, scan
from background_task.models import Task
from .forms import HostForm, ChangeHostNameForm


def index(request):
    return HttpResponseRedirect('whoishome')


def settings(request):
    email_settings = EmailConfig.objects.get(pk=1)
    context = {'email': email_settings}
    background_tasks = Task.objects.all()

    for background_task in background_tasks:
        context['scanner_running'] = True
        break
    return render(request, 'whoishome/settings.html', context)


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
                                                            'logdata_query': logdata_query})

    print('host not found')
    return HttpResponseRedirect('/whoishome/')


def getresults(request):
    if request.POST:
        if request.POST.get('host_id'):  # is host_id is in the request the host will be marked seen.
            host_id = int(request.POST.get('host_id'))
            host = Host.objects.get(pk=host_id)
            host.mark_seen()
        if request.POST.get('scanner'):  # for testing
            print(request.POST)

    context = {'targets': [], 'home_hosts_list': [], 'new_hosts': [], 'scanner_running': False}  # dictionary to be send to the html page
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

    context = {'logdata_query': logdata_query, 'sorted_log_dict': sorted_log_dict}

    return render(request, 'whoishome/network_timeline.html', context)


def enable_emailer(request):
    email_settings = EmailConfig.objects.get(pk=1)
    email_settings.enable_emailer()
    return HttpResponseRedirect('/whoishome/settings')


def disable_emailer(request):
    email_settings = EmailConfig.objects.get(pk=1)
    email_settings.disable_emailer()
    return HttpResponseRedirect('/whoishome/settings')


def start_scanner(request):
    schedule_scan(repeat=60)
    print('Scan Scheduled')
    return HttpResponseRedirect('/')


def stop_scanner(request):
    background_tasks = Task.objects.filter(task_name='whoishome.backgroundtasks.background_network_scan')
    for background_task in background_tasks:
        background_task.delete()
    print('Scan canceled.')
    return HttpResponseRedirect('/')


def scan_now(request):
    scan()
    return HttpResponseRedirect('/whoishome/')
