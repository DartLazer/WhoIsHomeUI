from django.urls import path

from . import views

urlpatterns = [
    path('', views.getresults, name='index'),
    path('settings/', views.settings, name='settings'),
    path('settings/device-types/', views.device_type_settings, name='device_type_settings'),
    path('setting/device-types/delete/<int:device_type_id>', views.delete_device_type, name='delete_device_type'),
    path('clear_new_hosts/', views.clear_new_hosts, name='clear_new_hosts'),
    # path('now/', views.getresults, name='now'),
    # path('index', views.index, name='index'),
    path('start_scanner/', views.settings_view.start_scanner, name='start_scanner'),
    path('login/', views.authentication_view.log_in, name='login'),
    path('stop_scanner/', views.stop_scanner, name='stop_scanner'),
    path('view_host/?<host_id>', views.view_host, name='view_host'),
    path('scan/', views.scan_now, name='scan'),
    path('network_timeline/', views.network_timeline, name="network_timeline"),
    path('update/', views.update_page, name="update")
]
