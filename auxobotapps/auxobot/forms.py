from django import forms
from .models import BotConfig


class BotConfigForm(forms.ModelForm):
    class Meta:
        model = BotConfig
        fields = ['exchange', 'api_key', 'api_secret', 'risk_level']
        widgets = {
            'api_key': forms.PasswordInput(attrs={'placeholder': 'Enter your API Key'}),
            'api_secret': forms.PasswordInput(attrs={'placeholder': 'Enter your Secret Key'}),
            'exchange': forms.Select(attrs={'class': 'form-select'}),
            'risk_level': forms.RadioSelect(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['api_key'].widget.attrs.update({'autocomplete': 'off'})
        self.fields['api_secret'].widget.attrs.update({'autocomplete': 'off'})