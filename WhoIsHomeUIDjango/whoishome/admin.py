from django.contrib import admin
from .models import Host, ScannerConfig, EmailConfig, LogData, DiscordNotificationsConfig, HomePageSettingsConfig


# Register your models here.

class HostAdmin(admin.ModelAdmin):
    list_display = ('name', 'ip', 'is_home', 'last_seen')
    fields = ['name', 'mac', 'last_seen', 'arrival_time', 'departure_time', 'scans_missed_counter', 'is_home', 'new', 'target', 'device_type']


class TargetAdmin(admin.ModelAdmin):
    list_display = ('name', 'mac')


class LogDataAdmin(admin.ModelAdmin):
    list_display = ('id', 'host', 'check_in', 'check_out')


class ScannerConfigAdmin(admin.ModelAdmin):
    fields =['scanner_enabled', 'not_home_treshold', 'internet_interface', 'ip_subnet', 'ip_range_start', 'ip_range_end']


admin.site.register(Host, HostAdmin)
admin.site.register(ScannerConfig, ScannerConfigAdmin)
admin.site.register(EmailConfig)
admin.site.register(HomePageSettingsConfig)
admin.site.register(DiscordNotificationsConfig)
admin.site.register(LogData, LogDataAdmin)
