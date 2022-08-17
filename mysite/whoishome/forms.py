from django import forms
from .models import Host, device_types_form_list, ScannerConfig, EmailConfig, DiscordNotificationsConfig


class HostForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        self.host = kwargs.pop("host")
        device_types_list = device_types_form_list
        device_types_list.insert(0, (self.host.device_type, self.host.device_type))
        super(HostForm, self).__init__(*args, **kwargs)
        self.fields["device_type"] = forms.ChoiceField(
            choices=device_types_list, required=False, label=False)
        self.fields['device_type'].widget.attrs.update(style='max-width: 12em', onchange='form.submit()')
        self.fields['target'] = forms.BooleanField(initial=self.host.target, required=False)
        self.fields['target'].widget.attrs.update(style='max-width: 12em', onchange='form.submit()')
        device_types_list.pop(0)


class ChangeHostNameForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        self.host = kwargs.pop("host")
        super(ChangeHostNameForm, self).__init__(*args, **kwargs)
        self.fields['name'] = forms.CharField(initial=self.host.name, max_length=50)


class ScannerSettingsForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(ScannerSettingsForm, self).__init__(*args, **kwargs)
        
        try:
            scanner_config = ScannerConfig.objects.get(pk=1)
        except ObjectDoesNotExist:
            ScannerConfig.objects.create(
                not_home_treshold= 21,
                internet_interface= "eth0",
                arp_string= "arp-scan --interface=",
                ip_subnet= "192.168.2.",
                ip_range_start= "1",
                ip_range_end= "198"
            )
            scanner_config = ScannerConfig.objects.get(pk=1)
            
        self.fields['not_home_treshold'] = forms.IntegerField(label="Not home treshold",
                                                              initial=scanner_config.not_home_treshold, required=False)
        self.fields['internet_interface'] = forms.CharField(label="Internet Interface",
                                                            initial=scanner_config.internet_interface, required=False)
        self.fields['ip_subnet'] = forms.CharField(label="IP Subnet", initial=scanner_config.ip_subnet, required=False)
        self.fields['ip_range_start'] = forms.CharField(label="IP Range start", initial=scanner_config.ip_range_start,
                                                        required=False)
        self.fields['ip_range_end'] = forms.CharField(label="IP Range end", initial=scanner_config.ip_range_end,
                                                      required=False)


class EmailSettingsForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(EmailSettingsForm, self).__init__(*args, **kwargs)
        
        try:
            email_config = EmailConfig.objects.get(pk=1)
        except ObjectDoesNotExist:
            EmailConfig.objects.create(
                email_switch=False, 
                sender_address= "secret@secret.com",
                your_password= "secret",
                to_address= "secret@gmail.com",
                smtp_domain= "smtp.gmail.com",
                smtp_port= "465",
                departure_mail_subject="test",
                departure_mail_body= "test",
                arrival_mail_suject= "test",
                arrival_mail_body= "test"
            )
            email_config = EmailConfig.objects.get(pk=1)
            
        self.fields['email_switch'] = forms.BooleanField(label="Emails enabled", initial=email_config.email_switch,
                                                         required=False)
        self.fields['new_connection_notification_switch'] = forms.BooleanField(label="New device detected notifications"
                                                        " enabled", initial=email_config.new_connection_notification_switch,
                                                         required=False)

        self.fields['sender_address'] = forms.CharField(max_length=100, initial=email_config.sender_address,
                                                        required=False)
        self.fields['your_password'] = forms.CharField(widget=forms.PasswordInput, required=False)
        self.fields['to_address'] = forms.CharField(initial=email_config.to_address, required=False)
        self.fields['smtp_domain'] = forms.CharField(initial=email_config.smtp_domain, required=False)
        self.fields['smtp_port'] = forms.CharField(initial=email_config.smtp_port, required=False)
        self.fields['new_connection_mail_subject'] = forms.CharField(initial=email_config.new_connection_mail_subject,
                                                                required=False)
        self.fields['new_connection_mail_body'] = forms.CharField(initial=email_config.new_connection_mail_body,
                                                                  required=False, widget=forms.Textarea)
        self.fields['departure_mail_subject'] = forms.CharField(initial=email_config.departure_mail_subject,
                                                                required=False)
        self.fields['departure_mail_body'] = forms.CharField(initial=email_config.departure_mail_body, required=False,
                                                             widget=forms.Textarea)
        self.fields['arrival_mail_suject'] = forms.CharField(initial=email_config.arrival_mail_suject, required=False)
        self.fields['arrival_mail_body'] = forms.CharField(initial=email_config.arrival_mail_body, required=False,
                                                           widget=forms.Textarea)


class DiscordNotificationsForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(DiscordNotificationsForm, self).__init__(*args, **kwargs)
        discord_config = DiscordNotificationsConfig.objects.get(pk=1)
        self.fields['enabled_switch'] = forms.BooleanField(label="Discord Notifications Enabled",
                                                           initial=discord_config.enabled_switch, required=False)
        self.fields['new_connection_notification_switch'] = forms.BooleanField(label="New device detected notifications",
                                                           initial=discord_config.new_connection_notification_switch, required=False)
        self.fields['webhook_url'] = forms.CharField(initial=discord_config.webhook_url, required=False)
        self.fields['departure_message'] = forms.CharField(initial=discord_config.departure_message, required=False,
                                                           widget=forms.Textarea)
        self.fields['arrival_message'] = forms.CharField(initial=discord_config.arrival_message, required=False,
                                                         widget=forms.Textarea)
        self.fields['new_connection_message'] = forms.CharField(initial=discord_config.new_connection_message,
                                                                required=False, widget=forms.Textarea)
