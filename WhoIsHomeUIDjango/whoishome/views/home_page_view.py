from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render

from whoishome.forms import HomePageSettingsForm
from whoishome.models import Host, HomePageSettingsConfig
from whoishome.authentication_utils import user_logged_in_if_locked
from whoishome.update_checker import update_check


@user_passes_test(user_logged_in_if_locked, login_url='/login/')
def getresults(request):
    home_page_settings_form = HomePageSettingsForm(request=request)

    if request.POST:
        if request.POST.get('host_id'):  # is host_id is in the request the host will be marked seen.
            host_id = int(request.POST.get('host_id'))
            host = Host.objects.get(pk=host_id)
            host.mark_seen()
            messages.success(request, f'{host} marked as seen')
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
               'home_page_settings_form': home_page_settings_form,
               'all_devices': False}  # dictionary to be send to the html page

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

    return render(request, 'pages/index.html', context)


@user_passes_test(user_logged_in_if_locked, login_url='/login/')
def clear_new_hosts(request):
    Host.objects.update(new=False)
    messages.success(request, f'All hosts set to seen.')
    return HttpResponseRedirect('/whoishome')


def index(request):
    return HttpResponseRedirect('whoishome')
