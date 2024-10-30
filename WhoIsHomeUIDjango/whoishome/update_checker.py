import logging

import requests
from django.conf import settings as django_settings
from django.utils import timezone

from whoishome.scanner_functions import logger

LAST_TIME_CHECKED = False
UPDATE_AVAILABLE = False
GITHUB_VERSION = False
logger = logging.getLogger('log_to_file')


def get_github_version():
    return GITHUB_VERSION


def update_check():
    global UPDATE_AVAILABLE
    global GITHUB_VERSION
    global LAST_TIME_CHECKED
    if UPDATE_AVAILABLE:
        return True
    now = timezone.now()

    if LAST_TIME_CHECKED is False or (now - LAST_TIME_CHECKED).seconds >= 3600:
        version_check_url = 'https://raw.githubusercontent.com/DartLazer/WhoIsHomeUI/main/WhoIsHomeUIDjango/latest_version.txt'
        try:
            r = requests.get(version_check_url)
            if r.status_code == 200:
                LAST_TIME_CHECKED = now
                remote_version = float(r.text)
                GITHUB_VERSION = remote_version
                if remote_version > django_settings.CURRENT_VERSION:
                    UPDATE_AVAILABLE = True
                    return True
                else:
                    UPDATE_AVAILABLE = False
                    return False
        except requests.exceptions.ConnectionError:
            logger.error('Unable to check for updates. Connection failed.')
            pass

    else:
        UPDATE_AVAILABLE = False
        return False
