from django import forms
from .models import CustomUser


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Min 8 chars, 1 uppercase, 1 number'}),
        min_length=8
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Repeat password'})
    )

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone', 'role']
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'First name'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Last name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email address'}),
            'phone': forms.TextInput(attrs={'placeholder': '98XXXXXXXX'}),
        }

    def clean_password(self):
        password = self.cleaned_data.get('password', '')
        if not any(c.isupper() for c in password):
            raise forms.ValidationError('Password must contain at least 1 uppercase letter.')
        if not any(c.isdigit() for c in password):
            raise forms.ValidationError('Password must contain at least 1 number.')
        return password

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('password') != cleaned.get('confirm_password'):
            raise forms.ValidationError('Passwords do not match.')
        return cleaned

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '')
        digits = phone.replace(' ', '').replace('-', '')
        if not digits.isdigit():
            raise forms.ValidationError('Phone number must contain only digits.')
        if len(digits) != 10:
            raise forms.ValidationError('Nepal phone number must be 10 digits (e.g. 9800000000).')
        if not digits.startswith(('98', '97')):
            raise forms.ValidationError('Enter a valid Nepal phone number starting with 98 or 97.')
        return digits


class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'Email address'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'})
    )


class OTPForm(forms.Form):
    code = forms.CharField(
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'placeholder': '6-digit code',
            'autocomplete': 'one-time-code',
            'inputmode': 'numeric',
            'style': 'letter-spacing: 8px; font-size: 1.5rem; text-align: center;'
        })
    )