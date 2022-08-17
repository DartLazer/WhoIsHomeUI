from .models import Host, LogData
from datetime import datetime, timedelta
from django.utils.timezone import localtime
from django.utils import timezone


def generate_timeline_data(host: Host, chart_range: str):

    if not LogData.objects.filter(host=host).exists():
        print(f'No logdata found for {host}')

    if chart_range is None:
        days_back_date = timezone.now() - timedelta(days=7)
    else:
        chart_range = int(chart_range)
        if chart_range == 0:
            chart_range = 9999
        days_back_date = timezone.now() - timedelta(days=chart_range)

    log_data = LogData.objects.filter(host=host, check_in__gte=days_back_date)
    timeline = []
    for log in log_data:
        if log.check_out:
            timeline.append([localtime(log.check_in), localtime(log.check_out), 'home'])
        else:
            # timeline.append([log.check_in, datetime.now(), 'home'])
            pass

    label = host.name
    return {'label': label, 'timeline': timeline}
