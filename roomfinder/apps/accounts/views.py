from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.conf import settings
from .forms import RegistrationForm, LoginForm, OTPForm
from .models import CustomUser, OTP

def register_view(request):
    form = RegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.save()
        otp = OTP.generate(user)
        send_mail(
            'Your RoomFinder OTP',
            f'Your verification code is: {otp.code}',
            settings.EMAIL_HOST_USER,
            [user.email],
        )
        request.session['otp_user_id'] = user.id
        return redirect('accounts:verify_otp')
    return render(request, 'accounts/register.html', {'form': form})

def verify_otp_view(request):
    user_id = request.session.get('otp_user_id')
    if not user_id:
        return redirect('accounts:register')
    form = OTPForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        try:
            otp = OTP.objects.get(user_id=user_id, code=form.cleaned_data['code'])
            if otp.is_valid():
                otp.user.email_verified = True
                otp.user.save()
                otp.delete()
                return redirect('accounts:login')
            else:
                form.add_error('code', 'OTP has expired.')
        except OTP.DoesNotExist:
            form.add_error('code', 'Invalid OTP.')
    return render(request, 'accounts/verify_otp.html', {'form': form})

def login_view(request):
    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = authenticate(request, username=form.cleaned_data['email'],
                            password=form.cleaned_data['password'])
        if user and user.email_verified:
            login(request, user)
            return redirect('/')
        form.add_error(None, 'Invalid credentials or email not verified.')
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('accounts:login')