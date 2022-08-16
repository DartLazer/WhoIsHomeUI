import datetime
import os
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from .models import Host, ScannerConfig, EmailConfig, Target, LogData, DiscordNotificationsConfig
import smtplib
import logging
from discord import Webhook, RequestsWebhookAdapter
import requests

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
        scanned_host_object = Host.objects.get_or_create(mac=mac,
                                                         defaults={'arrival_time': time_found, 'last_seen': time_found,
                                                                   'first_seen': time_found,
                                                                   'ip': scanned_ip,
                                                                   'name': scanned_dictionary[mac].get('Device-Name')})
        if scanned_host_object[1] is False:
            scanned_host_object[0].last_seen = time_found
            scanned_host_object[0].scans_missed_counter = 0
            scanned_host_object[0].ip = scanned_ip
        else:
            LogData.objects.create(host=scanned_host_object[0])
        scanned_host_object[0].save()

    for host in Host.objects.all():
        if host.mac.casefold() not in scanned_dictionary.keys():
            host.scans_missed_counter += 1
            host.save()
    return None


def is_home_check():  # checks and if necessary alters the 'is_home' state of the target
    email = EmailConfig.objects.get(pk=1)
    discord = DiscordNotificationsConfig.objects.get(pk=1)
    settings = ScannerConfig.objects.get(pk=1)
    not_home_threshold = getattr(settings, 'not_home_treshold')
    for host in Host.objects.all():
        if host.scans_missed_counter == 0 and host.is_home is False:  # if the target was away and now checks in again: target got home and send email
            host.arrival_time = host.last_seen
            host.is_home = True
            host.save()
            previous_check_out_time = LogData.objects.filter(host=host).last().check_out
            LogData.objects.create(host=host, previous_check_out=previous_check_out_time, ip=host.ip)

            if host.target:  # Checks if the host is a target (and thus notify)
                if getattr(discord, 'enabled_switch'):
                    discord_notify(host, discord, 'arrival')

                if getattr(email, 'email_switch'):
                    email_sender(host, 'arrival')

            host.save()
        elif host.scans_missed_counter > not_home_threshold and host.is_home is True:  # not home threshold is # scans target can miss to prevent
            # unnecessary emails. However the actual departure time(last scan) time is saved and sent in email. So only the email is delayed
            host.is_home = False
            host.departure_time = host.last_seen
            host.save()

            host_log_data = LogData.objects.filter(host=host).last()
            host_log_data.check_out = timezone.now()
            host_log_data.time_saved = timezone.now()
            host_log_data.save()

            if host.target:  # Checks if the host is a target (and thus notify)
                if getattr(discord, 'enabled_switch'):
                    discord_notify(host, discord, 'departure')

                if getattr(email, 'email_switch'):
                    email_sender(host, 'departure')

    return None


def discord_notify(host: Host, discord_config: DiscordNotificationsConfig, event_type: str):
    webhook = Webhook.from_url(discord_config.webhook_url, adapter=RequestsWebhookAdapter())
    target = getattr(host, 'name')
    arrival_time = getattr(host, 'arrival_time').strftime("%H:%M:%S on %d-%b-%Y ")
    departure_time = getattr(host, 'departure_time').strftime("last seen at: %H:%M:%S on %d-%b-%Y ")

    time_home = getattr(host, 'departure_time') - getattr(host, 'arrival_time')
    time_home = format_time_delta_object(time_home)

    time_away = getattr(host, 'arrival_time') - getattr(host, 'departure_time')
    time_away = format_time_delta_object(time_away)

    if event_type == 'arrival':  # if target is home formats the string according to the arrival email. Else
        body = getattr(discord_config, 'arrival_message').format(target=target, arrival_time=arrival_time,
                                                                 departure_time=departure_time, time_away=time_away,
                                                                 time_home=time_home)
    else:
        body = getattr(discord_config, 'departure_message').format(target=target, departure_time=departure_time,
                                                                   arrival_time=arrival_time, time_away=time_away,
                                                                   time_home=time_home)

    webhook.send(body)


def email_sender(host, email_type):  # sends arrival/departure emails
    print('Sending email')
    email = EmailConfig.objects.get(pk=1)
    target = getattr(host, 'name')
    arrival_time = getattr(host, 'arrival_time').strftime("%H:%M:%S on %d-%b-%Y ")
    departure_time = getattr(host, 'departure_time').strftime("last seen at: %H:%M:%S on %d-%b-%Y ")

    time_home = getattr(host, 'departure_time') - getattr(host, 'arrival_time')
    time_home = format_time_delta_object(time_home)

    time_away = getattr(host, 'arrival_time') - getattr(host, 'departure_time')
    time_away = format_time_delta_object(time_away)

    sender_address = getattr(email, 'sender_address')
    receiver_address = getattr(email, 'to_address')
    account_password = getattr(email, 'your_password')
    smtp_domain = getattr(email, 'smtp_domain')
    smtp_port = getattr(email, 'smtp_port')

    if email_type == 'arrival':  # if target is home formats the string according to the arrival email. Else departure email
        subject = getattr(email, 'arrival_mail_suject').format(target=target, arrival_time=arrival_time,
                                                               depature_time=departure_time, time_away=time_away,
                                                               time_home=time_home)
        body = getattr(email, 'arrival_mail_body').format(target=target, arrival_time=arrival_time,
                                                          departure_time=departure_time, time_away=time_away,
                                                          time_home=time_home)
    else:
        subject = getattr(email, 'departure_mail_subject').format(target=target, departure_time=departure_time,
                                                                  time_away=time_away,
                                                                  time_home=time_home)
        body = getattr(email, 'departure_mail_body').format(target=target, departure_time=departure_time,
                                                            arrival_time=arrival_time, time_away=time_away,
                                                            time_home=time_home)

    smtp_server = smtplib.SMTP_SSL(smtp_domain, int(smtp_port))
    try:
        smtp_server.login(sender_address, account_password)
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f'Email Error during authentication. Make sure email setup is correct.\n: {e}')
        return

    message = f"Subject: {subject}\n\n{body}"
    try:
        smtp_server.sendmail(sender_address, receiver_address, message)
    except smtplib.SMTPException as e:
        logger.error(f'Unknown email error. Printing out:\n {e}')

    smtp_server.close()


def strfdelta(tdelta: datetime.timedelta, fmt: str):
    d = {"days": tdelta.days}
    d["hours"], rem = divmod(tdelta.seconds, 3600)
    d["minutes"], d["seconds"] = divmod(rem, 60)
    return fmt.format(**d)


def format_time_delta_object(time_delta: datetime.timedelta):
    if time_delta.days >= 1:
        time_delta = strfdelta(time_delta, '{days} days {hours}:{minutes}:{seconds}')
    elif time_delta.seconds > 3600:
        time_delta = strfdelta(time_delta, '{hours} hours and {minutes} minutes.')
    else:
        time_delta = strfdelta(time_delta, '{minutes} minutes.')

    return time_delta
