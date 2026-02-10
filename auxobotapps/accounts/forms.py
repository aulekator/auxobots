from django import forms
from .models import UserProfile

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['email', 'username', 'password', 'refered_by']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'reffered_by': forms.TextInput(attrs={'class': 'form-control'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control'}),
            }
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def clean(self):
        cleaned_data =  super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        reffered_by = cleaned_data.get("refered_by")

        if password != confirm_password:
            raise forms.ValidationError("Password and Confirm Password do not match")
        
        if reffered_by and not UserProfile.objects.filter(reffered_by=reffered_by).exists():
            self.add_error("reffered_by", "refferal code does match any user in our system")

        return cleaned_data