from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .forms import RegistrationForm, LoginForm, OTPForm
from .models import CustomUser, OTP
from .forms import ProfileUpdateForm, PasswordChangeForm
from apps.listings.models import Listing
from django.shortcuts import get_object_or_404


def register_view(request):
    form = RegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])

        # ------------------------------------------------------------
        # OTP EMAIL VERIFICATION — DISABLED
        # ------------------------------------------------------------
        # Users are now activated immediately on registration instead
        # of being required to confirm a 6-digit email code. The OTP
        # generation/sending logic below is commented out (not
        # deleted) so it can be re-enabled later if needed.
        # ------------------------------------------------------------
        user.email_verified = True
        user.save()

        # otp = OTP.generate(user)
        #
        # # Try real email, fallback to terminal print
        # try:
        #     send_mail(
        #         'Your RoomFinder OTP',
        #         f'Your verification code is: {otp.code}\n\nExpires in 5 minutes.',
        #         settings.DEFAULT_FROM_EMAIL,
        #         [user.email],
        #     )
        # except Exception:
        #     print(f'\n{"="*50}')
        #     print(f'  OTP for {user.email}: {otp.code}')
        #     print(f'{"="*50}\n')
        #
        # request.session['otp_user_id'] = user.id
        # messages.success(
        #     request, 'Account created! Enter the OTP sent to your email. (Development: check terminal)')
        # return redirect('accounts:verify_otp')

        login(request, user)
        messages.success(request, f'Welcome to RoomFinder, {user.first_name}!')

        if user.is_staff or user.role == 'admin':
            return redirect('admin_panel:dashboard')
        return redirect('listings:homepage')

    return render(request, 'accounts/register.html', {'form': form})


def verify_otp_view(request):
    # ------------------------------------------------------------
    # OTP EMAIL VERIFICATION — DISABLED
    # ------------------------------------------------------------
    # This view is no longer part of the registration/login flow.
    # Accounts are activated immediately, so nothing should redirect
    # here anymore. Kept in place (harmless redirect) instead of
    # deleting, in case the URL is bookmarked or still referenced
    # somewhere. The original logic is commented out below.
    # ------------------------------------------------------------
    return redirect('accounts:login')

    # user_id = request.session.get('otp_user_id')
    # if not user_id:
    #     return redirect('accounts:register')
    #
    # form = OTPForm(request.POST or None)
    # if request.method == 'POST' and form.is_valid():
    #     try:
    #         otp = OTP.objects.filter(
    #             user_id=user_id,
    #             code=form.cleaned_data['code']
    #         ).latest('created_at')
    #
    #         if otp.is_valid():
    #             otp.user.email_verified = True
    #             otp.user.save()
    #             otp.delete()
    #             del request.session['otp_user_id']
    #             messages.success(
    #                 request, 'Email verified! You can now log in.')
    #             return redirect('accounts:login')
    #         else:
    #             form.add_error(
    #                 'code', 'OTP has expired. Please register again.')
    #
    #     except OTP.DoesNotExist:
    #         form.add_error('code', 'Invalid OTP. Please try again.')
    #
    # return render(request, 'accounts/verify_otp.html', {'form': form})


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

        # ------------------------------------------------------------
        # OTP EMAIL VERIFICATION — DISABLED
        # ------------------------------------------------------------
        # The "not verified -> resend OTP -> redirect to verify_otp"
        # branch has been removed. All authenticated users now log
        # in directly. Original logic kept below for reference.
        # ------------------------------------------------------------
        # elif not user.email_verified:
        #     # Regenerate OTP and send again
        #     otp = OTP.generate(user)
        #     try:
        #         send_mail(
        #             'Your RoomFinder OTP',
        #             f'Your verification code is: {otp.code}\n\nExpires in 5 minutes.',
        #             settings.DEFAULT_FROM_EMAIL,
        #             [user.email],
        #         )
        #     except Exception:
        #         print(f'\n{"="*50}')
        #         print(f'  OTP for {user.email}: {otp.code}')
        #         print(f'{"="*50}\n')
        #
        #     request.session['otp_user_id'] = user.id
        #     messages.warning(
        #         request, 'Email not verified. Check your terminal for OTP.')
        #     return redirect('accounts:verify_otp')

        else:
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name}!')
            if user.is_staff or user.role == 'admin':
                return redirect('admin_panel:dashboard')
            return redirect('listings:homepage')

    return render(request, 'accounts/login.html', {'form': form})


@login_required
def profile_view(request, user_id=None):
    """View any user's public profile."""
    if user_id:
        profile_user = get_object_or_404(CustomUser, pk=user_id)
    else:
        profile_user = request.user

    listings = None
    if profile_user.role == 'landlord':
        listings = Listing.objects.filter(
            owner=profile_user, status='approved'
        ).prefetch_related('images')[:6]

    return render(request, 'accounts/profile.html', {
        'profile_user': profile_user,
        'listings': listings,
        'is_own_profile': profile_user == request.user,
    })


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(
            request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = ProfileUpdateForm(instance=request.user)

    return render(request, 'accounts/edit_profile.html', {'form': form})


@login_required
def change_password(request):
    form = PasswordChangeForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = request.user
        if not user.check_password(form.cleaned_data['current_password']):
            form.add_error('current_password',
                           'Current password is incorrect.')
        else:
            user.set_password(form.cleaned_data['new_password'])
            user.save()
            # Keep user logged in after password change
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, user)
            messages.success(request, 'Password changed successfully!')
            return redirect('accounts:profile')

    return render(request, 'accounts/change_password.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('accounts:login')