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

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'last_name', 'phone',
            'bio', 'address', 'date_of_birth',
            'profile_picture', 'facebook_url',
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3,
                                         'placeholder': 'Tell others about yourself...'}),
            'address': forms.TextInput(attrs={'class': 'form-control',
                                              'placeholder': 'Your address'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control',
                                                     'type': 'date'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control',
                                                       'accept': 'image/*'}),
            'facebook_url': forms.URLInput(attrs={'class': 'form-control',
                                                   'placeholder': 'https://facebook.com/yourprofile'}),
        }


class PasswordChangeForm(forms.Form):
    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control',
                                          'placeholder': 'Current password'})
    )
    new_password = forms.CharField(
        min_length=8,
        widget=forms.PasswordInput(attrs={'class': 'form-control',
                                          'placeholder': 'New password'})
    )
    confirm_new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control',
                                          'placeholder': 'Confirm new password'})
    )

    def clean_new_password(self):
        password = self.cleaned_data.get('new_password', '')
        if not any(c.isupper() for c in password):
            raise forms.ValidationError('Password must contain at least 1 uppercase letter.')
        if not any(c.isdigit() for c in password):
            raise forms.ValidationError('Password must contain at least 1 number.')
        return password

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('new_password') != cleaned.get('confirm_new_password'):
            raise forms.ValidationError('New passwords do not match.')
        return cleaned

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