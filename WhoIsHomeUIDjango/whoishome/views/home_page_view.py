from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render

from whoishome.forms import HomePageSettingsForm
from whoishome.models import Host, HomePageSettingsConfig
from whoishome.authentication_utils import user_logged_in_if_locked
from whoishome.update_checker import update_check


@user_passes_test(user_logged_in_if_locked, login_url='/login/')
def home_page(request):
    home_page_settings, created = HomePageSettingsConfig.objects.get_or_create(pk=1)

    if request.POST:
        if 'host_id' in request.POST:
            host = Host.objects.filter(pk=int(request.POST.get('host_id'))).first()
            if host:
                host.mark_seen()
                messages.success(request, f'{host} marked as seen')
            else:
                messages.error(request, 'Host with that HOST ID not found')
        elif 'home_page_settings' in request.POST:
            form = HomePageSettingsForm(request.POST, instance=home_page_settings)
            if form.is_valid():
                form.save()

    home_page_settings_form = HomePageSettingsForm(instance=home_page_settings)

    home_hosts_list = Host.objects.all() if home_page_settings.show_all_devices else Host.objects.filter(is_home=True)
    targets = Host.objects.filter(target=True)
    new_hosts = Host.objects.filter(new=True)

    context = {
        'targets': targets, 'home_hosts_list': home_hosts_list, 'new_hosts': new_hosts, 'scanner_running': False,
        'all_devices': home_page_settings.show_all_devices, 'update_available': update_check(),
        'home_page_settings_form': home_page_settings_form,
    }
    return render(request, 'pages/index.html', context)


@user_passes_test(user_logged_in_if_locked, login_url='/login/')
def clear_new_hosts(request):
    """
    This view clears the "new" status of all Hosts in the database
    """
    Host.objects.update(new=False)
    messages.success(request, f'All hosts set to seen.')
    return HttpResponseRedirect('/whoishome')
