from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User
from core.models import LoginAttempt
from core.utils import get_worker_for_user
from datetime import timedelta


def send_admin_notification(username, reason="Account locked due to failed login attempts"):
    """Send email notification to admin user"""
    try:
        admin = User.objects.filter(is_superuser=True).first()
        if admin and admin.email:
            subject = f"Aqualife Ops - {reason}"
            message = f"Account '{username}' has been locked.\n\n{reason}\n\nPlease check the admin panel."
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [admin.email])
    except Exception as e:
        print(f"Failed to send admin notification: {e}")


def send_password_reset_email(user):
    """Send password reset email to user"""
    try:
        token = default_token_generator.make_token(user)
        reset_link = f"http://your-domain.com/auth/reset-password/{user.pk}/{token}/"
        subject = "Aqualife Ops - Password Reset"
        message = f"Your account has been locked. Click the link below to reset your password:\n\n{reset_link}"
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
    except Exception as e:
        print(f"Failed to send password reset email: {e}")


def login_view(request):
    next_url = request.POST.get("next") or request.GET.get("next", "/")
    if request.method == "POST":
        raw_username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        matched_user = User.objects.filter(username__iexact=raw_username).first()
        username = matched_user.username if matched_user else raw_username
        
        # Check if account is locked
        login_attempt, created = LoginAttempt.objects.get_or_create(username=raw_username)
        
        if login_attempt.locked_at:
            lock_duration = timedelta(minutes=15)
            if timezone.now() < login_attempt.locked_at + lock_duration:
                remaining_time = int(((login_attempt.locked_at + lock_duration) - timezone.now()).total_seconds() / 60)
                messages.error(request, f"Account locked. Try again in {remaining_time} minutes.")
                return render(request, "login.html", {"next": next_url})
            else:
                # Unlock after 15 minutes
                login_attempt.locked_at = None
                login_attempt.failed_attempts = 0
                login_attempt.save()
        
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_active:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}.")
            # Reset login attempts on successful login
            login_attempt.failed_attempts = 0
            login_attempt.locked_at = None
            login_attempt.save()

            worker = get_worker_for_user(user)
            if user.is_superuser:
                if url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                    return redirect(next_url)
                return redirect("dashboard")

            if worker:
                if worker.is_field_staff():
                    return redirect("field_dashboard")
                if worker.is_supervisor():
                    return redirect("supervisor_dashboard")

            messages.error(request, "Your account is not linked to a worker profile.")
            return redirect("login")
        
        # Failed login attempt
        login_attempt.failed_attempts += 1
        if login_attempt.failed_attempts >= settings.MAX_LOGIN_ATTEMPTS:
            login_attempt.locked_at = timezone.now()
            login_attempt.save()
            send_admin_notification(username)
            messages.error(request, "Account locked due to too many failed attempts. Admin has been notified.")
            return render(request, "login.html", {"next": next_url})
        
        login_attempt.save()
        remaining = settings.MAX_LOGIN_ATTEMPTS - login_attempt.failed_attempts
        messages.error(request, f"Invalid username or password. {remaining} attempts remaining.")

    return render(request, "login.html", {"next": next_url})


def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("login")


