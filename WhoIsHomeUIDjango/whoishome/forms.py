from calendar import month_name
from django import forms
from django.forms import Textarea

from .models import Host, device_types_form_list, ScannerConfig, EmailConfig, DiscordNotificationsConfig, \
    HomePageSettingsConfig, AppSettings, TelegramNotificationsConfig, DeviceType


class HostForm(forms.ModelForm):
    class Meta:
        model = Host
        fields = ('target', 'kid_curfew_mode', 'device_type')

    target = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'onchange': 'form.submit()'}), label='Target',
        required=False)
    kid_curfew_mode = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'onchange': 'form.submit()'}, ),
        label='Curfew Mode', required=False
    )
    device_type = forms.ModelChoiceField(
        queryset=DeviceType.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control', 'onchange': 'form.submit()'}), label='Device Type'
    )


class ChangeHostNameForm(forms.ModelForm):
    class Meta:
        model = Host
        fields = ('name',)

    name = forms.CharField(widget=forms.TextInput({'class': 'form-control'}), label='Host Name')


class HomePageSettingsForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(HomePageSettingsForm, self).__init__(*args, **kwargs)

        home_page_config, created_bool = HomePageSettingsConfig.objects.get_or_create(pk=1)

        self.fields['show_all_devices'] = forms.BooleanField(label='Show all devices',
                                                             initial=home_page_config.show_all_devices, required=False)
        self.fields['show_all_devices'].widget.attrs.update(style='max-width: 12em', onchange='form.submit()')


class ScannerSettingsForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(ScannerSettingsForm, self).__init__(*args, **kwargs)

        scanner_config, created_bool = ScannerConfig.objects.get_or_create(pk=1)
        self.fields['scanner_enabled'] = forms.BooleanField(label='Scanner enabled',
                                                            initial=scanner_config.scanner_enabled, required=False)
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

        email_config, created_bool = EmailConfig.objects.get_or_create(pk=1)

        self.fields['email_switch'] = forms.BooleanField(label="Emails enabled", initial=email_config.email_switch,
                                                         required=False)
        self.fields['new_connection_notification_switch'] = forms.BooleanField(label="New device detected notifications"
                                                                                     " enabled",
                                                                               initial=email_config.new_connection_notification_switch,
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
        self.fields['curfew_subject'] = forms.CharField(initial=email_config.curfew_subject, required=False)
        self.fields['curfew_message'] = forms.CharField(initial=email_config.curfew_message, required=False,
                                                        widget=forms.Textarea)


class DiscordNotificationsForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(DiscordNotificationsForm, self).__init__(*args, **kwargs)
        discord_config = DiscordNotificationsConfig.objects.get(pk=1)
        self.fields['enabled_switch'] = forms.BooleanField(label="Discord Notifications Enabled",
                                                           initial=discord_config.enabled_switch, required=False)
        self.fields['new_connection_notification_switch'] = forms.BooleanField(
            label="New device detected notifications",
            initial=discord_config.new_connection_notification_switch, required=False)
        self.fields['webhook_url'] = forms.CharField(initial=discord_config.webhook_url, required=False)
        self.fields['departure_message'] = forms.CharField(initial=discord_config.departure_message, required=False,
                                                           widget=forms.Textarea)
        self.fields['arrival_message'] = forms.CharField(initial=discord_config.arrival_message, required=False,
                                                         widget=forms.Textarea)
        self.fields['new_connection_message'] = forms.CharField(initial=discord_config.new_connection_message,
                                                                required=False, widget=forms.Textarea)
        self.fields['curfew_message'] = forms.CharField(initial=discord_config.curfew_message, required=False,
                                                        widget=forms.Textarea)


class LockAppForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(LockAppForm, self).__init__(*args, **kwargs)
        app_config = AppSettings.objects.get(pk=1)
        self.fields['login_required'] = forms.BooleanField(label="Lock WhoIsHome with a password",
                                                           initial=app_config.login_required, required=False)
        self.fields['password'] = forms.CharField(label='Password', required=True, widget=forms.PasswordInput)


class CurfewTimesForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(CurfewTimesForm, self).__init__(*args, **kwargs)
        app_config = AppSettings.objects.get(pk=1)
        self.fields['curfew_enabled'] = forms.BooleanField(label="Enable curfew notifications for selected devices.",
                                                           initial=app_config.curfew_enabled, required=False)
        self.fields['curfew_start_time'] = forms.TimeField(label="Beginning of Curfew time", required=True,
                                                           widget=forms.TimeInput(attrs={'type': 'time'}),
                                                           initial=app_config.curfew_start_time)
        self.fields['curfew_end_time'] = forms.TimeField(label="End of Curfew time", required=True,
                                                         widget=forms.TimeInput(attrs={'type': 'time'}),
                                                         initial=app_config.curfew_end_time)


class EnterPasswordForm(forms.Form):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)


class AutoDeleteAfterXDaysForm(forms.ModelForm):
    class Meta:
        model = AppSettings
        fields = ['auto_delete_after_x_days']


class TelegramNotificationsConfigForm(forms.ModelForm):
    class Meta:
        model = TelegramNotificationsConfig
        fields = [
            'enabled_switch',
            'new_device_detected_notifications',
            'bot_token',
            'chat_id',
            'arrival_message',
            'departure_message',
            'curfew_message',
            'new_connection_message'
        ]

        widgets = {
            'arrival_message': Textarea(attrs={'rows': 4, 'cols': 40}),
            'departure_message': Textarea(attrs={'rows': 4, 'cols': 40}),
            'curfew_message': Textarea(attrs={'rows': 4, 'cols': 40}),
            'new_connection_message': Textarea(attrs={'rows': 4, 'cols': 40}),
        }

        labels = {
            'enabled_switch': 'Enable Notifications',
            'new_device_detected_notifications': 'Allow notifications for new devices',
            'bot_token': 'Bot Token',
            'chat_id': 'Chat ID',
            'arrival_message': 'Arrival Message',
            'departure_message': 'Departure Message',
            'curfew_message': 'Curfew Violation Message',
            'new_connection_message': 'New Connection Message',
        }


class AddDeviceTypeForm(forms.ModelForm):
    class Meta:
        model = DeviceType
        fields = ('name', 'icon')

    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), label='Device type *')
    icon = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), label='Icon code *')

    def clean_icon(self):
        """
        Lowercase the icon to work with bootstrap icons
        """
        return self.cleaned_data.get('icon').lower()
