from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, get_object_or_404, redirect

from whoishome.authentication_utils import user_logged_in_if_locked
from whoishome.forms import AddDeviceTypeForm
from whoishome.models import DeviceType


@user_passes_test(user_logged_in_if_locked, login_url='/login/')
def device_type_settings(request):
    if request.method == 'POST':
        form = AddDeviceTypeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'New device type added.')

    device_types = DeviceType.objects.all().order_by('name')
    form = AddDeviceTypeForm()

    return render(request, 'pages/settings/device_type.html',
                  {'form': form, 'device_types': device_types})

@user_passes_test(user_logged_in_if_locked, login_url='/login/')
def delete_device_type(request, device_type_id):
    order = get_object_or_404(DeviceType, id=device_type_id)
    order.delete()
    messages.error(request, 'Device type deleted')
    return redirect('device_type_settings')
