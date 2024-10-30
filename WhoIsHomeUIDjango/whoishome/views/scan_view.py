from datetime import timedelta

from django.http import HttpResponseRedirect
from django.utils import timezone

from whoishome.models import ScannerConfig, AppSettings, LogData
from whoishome.scanner_functions import scan_network, scan_processor, is_home_check


def scan_now(request):
    scanner_config, created_bool = ScannerConfig.objects.get_or_create(pk=1)

    app_settings = AppSettings.objects.get(pk=1)
    if app_settings.auto_delete_after_x_days > 0:
        # Calculate the datetime for the cutoff
        cutoff_date = timezone.now() - timedelta(days=app_settings.auto_delete_after_x_days)

        # Query the database to get all LogData instances older than the cutoff_date
        logs_to_delete = LogData.objects.filter(time_saved__lt=cutoff_date)

        # Delete all of them
        logs_to_delete.delete()

    if scanner_config.scanner_enabled:
        print('Scanning')
        online_hosts = scan_network()
        scan_processor(online_hosts)
        is_home_check()
    return HttpResponseRedirect('')
