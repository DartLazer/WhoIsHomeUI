from background_task import background
from .scanner_functions import *
from django.utils import timezone


@background(schedule=60)
def schedule_scan():
    scan()


def scan():
    print('Scanning')
    time = timezone.now()
    print(f'Scanner start om: {time}')
    online_hosts = scan_network()
    scan_processor(online_hosts)
    is_home_check()
