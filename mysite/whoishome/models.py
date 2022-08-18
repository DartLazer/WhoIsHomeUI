from django.db import models
from django.utils import timezone

device_types = ['unknown', 'pc', 'phone', 'server', 'laptop', 'tv', "speaker", "Smart Home Device", "tablet"]
device_types_form_list = [("unknown", "unknown"), ("pc", "pc"), ("phone", "phone"), ("server", "server"), ("laptop", "laptop"), ("tv", "tv"),
                          ("speaker", "speaker"),
                          ("Smart Home Device", "Smart Home Device"), ("tablet", "tablet")]
device_types_icons = {"unknown": "question-circle", "pc": "pc-display-horizontal", "phone": "phone", "server": "server", "laptop": "laptop", "tv": "tv",
                      "speaker": "speaker",
                      "Smart Home Device": "house", "tablet": "tablet"}


def strfdelta(tdelta, fmt):
    d = {"days": tdelta.days}
    d["hours"], rem = divmod(tdelta.seconds, 3600)
    d["minutes"], d["seconds"] = divmod(rem, 60)
    return fmt.format(**d)


def build_timedelta_string(time_delta_object):
    if time_delta_object.days > 0:
        return strfdelta(time_delta_object, "{days} days, {hours} hours, and {minutes} minutes.")
    elif time_delta_object.seconds > 3600:
        return strfdelta(time_delta_object, "{hours} hours, and {minutes} minutes.")
    else:
        return strfdelta(time_delta_object, "{minutes} minutes.")


class Host(models.Model):
    name = models.CharField(max_length=50)
    mac = models.CharField(max_length=17)
    ip = models.CharField(max_length=50, default=0)
    first_seen = models.DateTimeField('Time last seen', default=timezone.now)
    last_seen = models.DateTimeField('Time last seen', default=timezone.now)
    arrival_time = models.DateTimeField('Last recorded arrival time', default=timezone.now)
    departure_time = models.DateTimeField('Last recorded departure time', default=timezone.now)
    scans_missed_counter = models.IntegerField(default=0)
    is_home = models.BooleanField(default=False)
    new = models.BooleanField(default=True)
    target = models.BooleanField(default=False)
    device_type = models.CharField(max_length=50, default="unknown")

    def __str__(self):
        return self.name

    def mark_seen(self):
        self.new = False
        self.save()

    def show_icon(self):
        try:
            return device_types_icons[self.device_type]
        except KeyError:
            return device_types_icons['unknown']


class Target(models.Model):
    name = models.CharField(max_length=50)
    mac = models.CharField(max_length=17)

    def __str__(self):
        return self.name


class LogData(models.Model):
    host = models.ForeignKey(Host, on_delete=models.CASCADE)
    check_in = models.DateTimeField('Check-in Time', default=timezone.now)
    check_out = models.DateTimeField('Check-out Time', null=True, blank=True)
    previous_check_out = models.DateTimeField('Previous Check-Out- Time', null=True, blank=True)
    ip = models.CharField(max_length=50, default="unknown")
    time_saved = models.DateTimeField('DateTime Last edited', default=timezone.now)

    def time_home(self):
        time_home = (self.check_out - self.check_in)
        return build_timedelta_string(time_home)

    def time_away(self):
        if self.previous_check_out is not None:
            time_away = self.check_in - self.previous_check_out
            return build_timedelta_string(time_away)
        return None


class ScannerConfig(models.Model):
    not_home_treshold = models.IntegerField(default= 21)
    internet_interface = models.CharField(max_length=15, default='eth0')
    arp_string = models.CharField(max_length=100, default='arp-scan --interface=')
    ip_subnet = models.CharField(max_length=100, default='192.168.2.')
    ip_range_start = models.CharField(max_length=100, default='1')
    ip_range_end = models.CharField(max_length=100, default='198')


class DiscordNotificationsConfig(models.Model):
    enabled_switch = models.BooleanField(default=False)
    new_connection_notification_switch = models.BooleanField(default=False)
    webhook_url = models.CharField(max_length=256)
    arrival_message = models.CharField(max_length=500)
    departure_message = models.CharField(max_length=500)
    new_connection_message = models.CharField(max_length=500, default='At time {arrival_time} a new device connected '
                                                                      'to the network\n'
                                                                      'MAC: {mac}\n'
                                                                      'IP: {ip}\n'
                                                                      'Name: {name}')

class EmailConfig(models.Model):
    email_switch = models.BooleanField(default=False)
    new_connection_notification_switch = models.BooleanField(default=False)
    sender_address = models.CharField(max_length=100, default='test@test.com')
    your_password = models.CharField(max_length=100, default='secretpassword')
    to_address = models.CharField(max_length=100, default='to@test.com')
    smtp_domain = models.CharField(max_length=100, default='smtp@test.com')
    smtp_port = models.CharField(max_length=100, default='465')
    departure_mail_subject = models.CharField(max_length=100, default='{target} has left home.')
    departure_mail_body = models.CharField(max_length=500, default='{target} has left home at time {departure_time}.')
    arrival_mail_suject = models.CharField(max_length=100, default='{target} has arrived home.')
    arrival_mail_body = models.CharField(max_length=500, default='{target} has arrived home at time {arrival_time}')
    new_connection_mail_subject = models.CharField(max_length=500, default='New device detected.')
    new_connection_mail_body = models.CharField(max_length=500,
                                              default='At time {arrival_time} a device connected to the '
                                                      'network\n'
                                                      'MAC: {host.mac}\n'
                                                      'IP: {host.ip}\n'
                                                      'Name: {host.name}')

    def enable_emailer(self):
        self.email_switch = True
        self.save()
        print('emailer gaat aan!')

    def disable_emailer(self):
        self.email_switch = False
        self.save()
        print('emailer gaat uit!')
