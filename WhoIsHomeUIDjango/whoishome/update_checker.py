import logging

import requests
from django.conf import settings as django_settings
from django.utils import timezone

from whoishome.scanner_functions import logger

last_time_checked = False
update_available = False
github_version = False
logger = logging.getLogger('log_to_file')


def update_check():
    global update_available
    if update_available:
        return True
    now = timezone.now()
    global last_time_checked
    if last_time_checked is False or (now - last_time_checked).seconds >= 3600:
        version_check_url = 'https://raw.githubusercontent.com/DartLazer/WhoIsHomeUI/main/mysite/latest_version.txt'
        try:
            r = requests.get(version_check_url)
            if r.status_code == 200:
                last_time_checked = now
                remote_version = float(r.text)
                global github_version
                github_version = remote_version
                if remote_version > django_settings.CURRENT_VERSION:
                    update_available = True
                    return True
                else:
                    update_available = False
                    return False
        except requests.exceptions.ConnectionError:
            logger.error('Unable to check for updates. Connection failed.')
            pass

    else:
        update_available = False
        return False
