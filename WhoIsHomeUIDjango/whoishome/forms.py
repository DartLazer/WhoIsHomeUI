from django import forms
from django.forms import Textarea

from .models import Host, ScannerConfig, EmailConfig, DiscordNotificationsConfig, \
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

    name = forms.CharField(widget=forms.TextInput({'class': 'form-control'}), label='Host Name', required=False)


class HomePageSettingsForm(forms.ModelForm):
    class Meta:
        model = HomePageSettingsConfig
        fields = ('show_all_devices',)

    show_all_devices = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'onchange': 'form.submit()'}), required=False
    )


class ScannerSettingsForm(forms.ModelForm):
    class Meta:
        model = ScannerConfig
        fields = ('scanner_enabled', 'not_home_treshold', 'internet_interface', 'ip_subnet',
                  'ip_range_start', 'ip_range_end')


class EmailSettingsForm(forms.ModelForm):
    class Meta:
        model = EmailConfig
        exclude = ('',)

    new_connection_mail_body = forms.CharField(widget=forms.Textarea)
    departure_mail_body = forms.CharField(widget=forms.Textarea)
    arrival_mail_body = forms.CharField(widget=forms.Textarea)
    curfew_message = forms.CharField(widget=forms.Textarea)

    labels = {
        'enabled_switch': 'Enable Notifications',
        'new_device_detected_notifications': 'Allow notifications for new devices',
    }


class DiscordNotificationsForm(forms.ModelForm):
    class Meta:
        model = DiscordNotificationsConfig
        exclude = ('',)

    new_connection_message = forms.CharField(widget=forms.Textarea)
    departure_message = forms.CharField(widget=forms.Textarea)
    arrival_message = forms.CharField(widget=forms.Textarea)
    curfew_message = forms.CharField(widget=forms.Textarea)

    labels = {
        'enabled_switch': 'Enable Notifications',
        'new_device_detected_notifications': 'Allow notifications for new devices',
    }


class EnterPasswordForm(forms.Form):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)


class AppSettingsForm(forms.ModelForm):
    class Meta:
        model = AppSettings
        exclude = ('',)

    login_required = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Login Required',
        required=False
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='Password',
        required=False
    )

    auto_delete_after_x_days = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        label='Auto Delete After X Days',
        required=False
    )
    curfew_enabled = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Curfew Enabled',
        required=False
    )
    curfew_start_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        label='Curfew Start Time',
        required=False
    )
    curfew_end_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        label='Curfew End Time',
        required=False
    )

    def clean(self):
        cleaned_data = super().clean()
        login_required = cleaned_data.get('login_required')
        password = cleaned_data.get('password')

        # Validate that password is provided when login_required is True
        if login_required and not password:
            self.add_error('password', 'Password is required when enabling the login requirement.')
            # Do not raise a form-wide ValidationError here

        return cleaned_data


class TelegramNotificationsConfigForm(forms.ModelForm):
    class Meta:
        model = TelegramNotificationsConfig
        exclude = ('',)

        widgets = {
            'arrival_message': Textarea(attrs={'rows': 4, 'cols': 40}),
            'departure_message': Textarea(attrs={'rows': 4, 'cols': 40}),
            'curfew_message': Textarea(attrs={'rows': 4, 'cols': 40}),
            'new_connection_message': Textarea(attrs={'rows': 4, 'cols': 40}),
        }

        labels = {
            'enabled_switch': 'Enable Notifications',
            'new_device_detected_notifications': 'Allow notifications for new devices',
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
