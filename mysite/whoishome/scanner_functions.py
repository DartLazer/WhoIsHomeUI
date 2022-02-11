import os
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from .models import Host, ScannerConfig, EmailConfig, Target, LogData
import smtplib


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
        scanned_host_object = Host.objects.get_or_create(mac=mac, defaults={'arrival_time': time_found, 'last_seen': time_found, 'first_seen': time_found,
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
    settings = ScannerConfig.objects.get(pk=1)
    not_home_threshold = getattr(settings, 'not_home_treshold')
    for host in Host.objects.all():
        if host.scans_missed_counter == 0 and host.is_home is False:  # if the target was away and now checks in again: target got home and send email
            host.arrival_time = host.last_seen
            host.is_home = True
            host.save()

            previous_check_out_time = LogData.objects.filter(host=host).last().check_out
            LogData.objects.create(host=host, previous_check_out=previous_check_out_time, ip=host.ip)
            if getattr(email, 'email_switch'):
                try:
                    Target.objects.get(name=host.name)
                    email_sender(host, 'arrival')
                except ObjectDoesNotExist:
                    pass
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

            if getattr(email, 'email_switch'):
                try:
                    Target.objects.get(name=host.name)
                    email_sender(host, 'departure')
                except ObjectDoesNotExist:
                    pass
    return None


def email_sender(host, email_type):  # sends arrival/departure emails
    email = EmailConfig.objects.get(pk=1)
    target = getattr(host, 'name')
    arrival_time = getattr(host, 'arrival_time').strftime("%H:%M:%S on %d-%b-%Y ")
    departure_time = getattr(host, 'departure_time').strftime("last seen at: %H:%M:%S on %d-%b-%Y ")
    sender_address = getattr(email, 'sender_address')
    receiver_address = getattr(email, 'to_address')
    account_password = getattr(email, 'your_password')
    smtp_domain = getattr(email, 'smtp_domain')
    smtp_port = getattr(email, 'smtp_port')

    if email_type == 'arrival':  # if target is home formats the string according to the arrival email. Else departure email
        subject = getattr(email, 'arrival_mail_suject').format(target=target, arrival_time=arrival_time)
        body = getattr(email, 'arrival_mail_body').format(target=target, arrival_time=arrival_time)
    else:
        subject = getattr(email, 'departure_mail_subject').format(target=target, departure_time=departure_time)
        body = getattr(email, 'departure_mail_body').format(target=target, departure_time=departure_time, arrival_time=arrival_time)

    smtp_server = smtplib.SMTP_SSL(smtp_domain, int(smtp_port))
    smtp_server.login(sender_address, account_password)
    message = f"Subject: {subject}\n\n{body}"
    smtp_server.sendmail(sender_address, receiver_address, message)
    smtp_server.close()
