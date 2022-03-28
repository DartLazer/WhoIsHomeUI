from django.urls import path


from . import views

urlpatterns = [
    path('', views.getresults, name='index'),
    path('settings/', views.settings, name='settings'),
    # path('now/', views.getresults, name='now'),
    # path('index', views.index, name='index'),
    path('start_scanner/', views.start_scanner, name='start_scanner'),
    path('stop_scanner/', views.stop_scanner, name='stop_scanner'),
    path('enable_emailer/', views.enable_emailer, name='enable_emailer'),
    path('disable_emailer/', views.disable_emailer, name='disable_emailer'),
    path('view_host/?<host_id>', views.view_host, name='view_host'),
    path('scannow/', views.scan_now, name='scan_now'),
    path('network_timeline/', views.network_timeline, name="network_timeline"),
    path('update/', views.update_page, name="update")
]
