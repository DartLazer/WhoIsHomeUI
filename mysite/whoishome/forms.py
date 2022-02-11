from django import forms
from .models import Host, device_types_form_list


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
