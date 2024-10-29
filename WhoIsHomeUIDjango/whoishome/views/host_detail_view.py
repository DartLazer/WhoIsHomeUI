from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponseRedirect
from django.shortcuts import render

from whoishome.forms import HostForm, ChangeHostNameForm
from whoishome.models import Host, LogData
from whoishome.timeline_functions import generate_timeline_data
from whoishome.authentication_utils import user_logged_in_if_locked
from whoishome.update_checker import logger, update_check


@user_passes_test(user_logged_in_if_locked, login_url='/login/')
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
        chart_range = 3
        timeline_dict = generate_timeline_data(host, '3')

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
                                                        'update_available': update_check(), 'timeline': timeline_dict,
                                                        'timeline_chart_range:': chart_range})
