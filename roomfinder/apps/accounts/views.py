from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .forms import RegistrationForm, LoginForm, OTPForm
from .models import CustomUser, OTP


def register_view(request):
    form = RegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.email_verified = False
        user.save()

        otp = OTP.generate(user)

        # Try real email, fallback to terminal print
        try:
            send_mail(
                'Your RoomFinder OTP',
                f'Your verification code is: {otp.code}\n\nExpires in 5 minutes.',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
            )
        except Exception:
            print(f'\n{"="*50}')
            print(f'  OTP for {user.email}: {otp.code}')
            print(f'{"="*50}\n')

        request.session['otp_user_id'] = user.id
        messages.success(request, 'Account created! Enter the OTP sent to your email. (Development: check terminal)')
        return redirect('accounts:verify_otp')

    return render(request, 'accounts/register.html', {'form': form})


def verify_otp_view(request):
    user_id = request.session.get('otp_user_id')
    if not user_id:
        return redirect('accounts:register')

    form = OTPForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        try:
            otp = OTP.objects.filter(
                user_id=user_id,
                code=form.cleaned_data['code']
            ).latest('created_at')

            if otp.is_valid():
                otp.user.email_verified = True
                otp.user.save()
                otp.delete()
                del request.session['otp_user_id']
                messages.success(request, 'Email verified! You can now log in.')
                return redirect('accounts:login')
            else:
                form.add_error('code', 'OTP has expired. Please register again.')

        except OTP.DoesNotExist:
            form.add_error('code', 'Invalid OTP. Please try again.')

    return render(request, 'accounts/verify_otp.html', {'form': form})


def login_view(request):
    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = authenticate(
            request,
            username=form.cleaned_data['email'],
            password=form.cleaned_data['password']
        )

        if user is None:
            form.add_error(None, 'Invalid email or password.')

        elif not user.email_verified:
            # Regenerate OTP and send again
            otp = OTP.generate(user)
            try:
                send_mail(
                    'Your RoomFinder OTP',
                    f'Your verification code is: {otp.code}\n\nExpires in 5 minutes.',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                )
            except Exception:
                print(f'\n{"="*50}')
                print(f'  OTP for {user.email}: {otp.code}')
                print(f'{"="*50}\n')

            request.session['otp_user_id'] = user.id
            messages.warning(request, 'Email not verified. Check your terminal for OTP.')
            return redirect('accounts:verify_otp')

        else:
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name}!')
            if user.is_staff or user.role == 'admin':
                return redirect('admin_panel:dashboard')
            return redirect('listings:homepage')

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('accounts:login')