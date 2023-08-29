import datetime
import os
from django.utils import timezone
from .models import Host, ScannerConfig, EmailConfig, LogData, DiscordNotificationsConfig, AppSettings, \
    TelegramNotificationsConfig
import logging

from .notification_functions import discord_notify, email_sender, telegram_notify

logger = logging.getLogger('log_to_file')


def scan_network():  # scans the network using arp-scan module. Performs a scan in the specified ip range
    settings = ScannerConfig.objects.get(pk=1)
    arp_string = getattr(settings, 'arp_string')
    internet_interface = getattr(settings, 'internet_interface')
    ip_subnet = getattr(settings, 'ip_subnet')
    ip_range_start = getattr(settings, 'ip_range_start')
    ip_range_end = getattr(settings, 'ip_range_end')
    online_hosts = {}
    raw_scan_output = os.popen(arp_string + internet_interface + ' --retry 3 ' + ip_subnet + ip_range_start + '-' +
                               ip_subnet + ip_range_end).read()

    if raw_scan_output == "":
        logger.error("Scan output is empty. Did you correctly set the adapter and subnet in settings page?")

    split_output = raw_scan_output.split('\n')[2:-5]  # Split command output by \n, index [2:-5] contains target data.
    for host in split_output:
        stripped_host = host.split(
            '\t')  # split the target data by tabs which will give us device ip, mac and device name.
        online_hosts[stripped_host[1]] = {'IP': stripped_host[0], 'Device-Name': stripped_host[
            2]}  # add the found data to dictionary with MAC as key.
    return online_hosts


def scan_processor(scanned_dictionary):
    time_found = timezone.now()
    for mac in scanned_dictionary.keys():
        scanned_ip = scanned_dictionary[mac].get('IP')
        host, host_created = Host.objects.get_or_create(mac=mac,
                                                        defaults={'arrival_time': time_found, 'last_seen': time_found,
                                                                  'first_seen': time_found,
                                                                  'ip': scanned_ip,
                                                                  'name': scanned_dictionary[mac].get('Device-Name')})
        if host_created:
            LogData.objects.create(host=host)
            notify(host, 'new')

        else:
            host.last_seen = time_found
            host.scans_missed_counter = 0
            host.ip = scanned_ip
            host.save()

    for host in Host.objects.all():
        if host.mac.casefold() not in scanned_dictionary.keys():
            host.scans_missed_counter += 1
            host.save()
    return None


def is_home_check():  # checks and if necessary alters the 'is_home' state of the target
    settings = ScannerConfig.objects.get(pk=1)
    not_home_threshold = getattr(settings, 'not_home_treshold')
    for host in Host.objects.all():
        if host.scans_missed_counter == 0 and host.is_home is False:  # if the target was away and now checks in
            # again: target got home and send email
            host.arrival_time = host.last_seen
            host.is_home = True
            host.save()
            previous_check_out_time = LogData.objects.filter(host=host).last().check_out
            LogData.objects.create(host=host, previous_check_out=previous_check_out_time, ip=host.ip)

            if host.target:  # Checks if the host is a target (and thus notify)
                notify(host, 'arrival')
            elif host.kid_curfew_mode:
                notify(host, 'arrival')

            host.save()
        elif host.scans_missed_counter > not_home_threshold and host.is_home is True:  # not home threshold is
            # scans target can miss to prevent unnecessary emails.
            # However the actual departure time(last scan) time is saved and sent in email.
            # So only the email is delayed

            host.is_home = False
            host.departure_time = host.last_seen
            host.save()

            host_log_data = LogData.objects.filter(host=host).last()
            host_log_data.check_out = timezone.now()
            host_log_data.time_saved = timezone.now()
            host_log_data.save()

            if host.target:  # Checks if the host is a target (and thus notify)
                notify(host, 'departure')

    return None


def notify(host: Host, notification_type: str):
    email_config = EmailConfig.objects.get(pk=1)
    discord_config = DiscordNotificationsConfig.objects.get(pk=1)
    telegram_config = TelegramNotificationsConfig.objects.get(pk=1)
    app_settings = AppSettings.objects.get(pk=1)
    print(app_settings.curfew_enabled)
    if app_settings.curfew_enabled:
        current_time = datetime.datetime.now()
        if app_settings.curfew_start_time < current_time.time() > app_settings.curfew_end_time:
            logger.info(f'CURFEW Intruder: {host.name}')
            if getattr(discord_config, 'enabled_switch'):
                discord_notify(host, discord_config, 'curfew')

            if getattr(email_config, 'email_switch'):
                email_sender(host, 'curfew')
        return

    print('NOTIFY')
    if getattr(discord_config, 'enabled_switch'):
        discord_notify(host, discord_config, notification_type)

    if getattr(email_config, 'email_switch'):
        email_sender(host, notification_type)

    if getattr(telegram_config, 'enabled_switch'):
        telegram_notify(host, telegram_config, notification_type)
