from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import IntegrityError
from core.models import Worker, Activity


def require_admin(request):
    if not request.user.is_superuser:
        messages.error(request, "Only admin may access worker account management.")
        return False
    return True


def list_workers(request):
    if not require_admin(request):
        return redirect("dashboard")

    role = request.GET.get("role", "")
    status = request.GET.get("status", "")
    qs = Worker.objects.all()
    if role:
        qs = qs.filter(role=role)
    if status:
        qs = qs.filter(status=status)

    users = User.objects.filter(is_active=True).order_by("username")

    return render(request, "workers/list.html", {
        "workers": qs,
        "users": users,
        "role_filter": role,
        "status_filter": status,
        "active_page": "workers",
    })


def create_worker(request):
    if not require_admin(request):
        return redirect("dashboard")

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        phone = request.POST.get("phone", "").strip()
        if not name or not phone:
            messages.error(request, "Name and phone are required.")
            return redirect("workers")

        user = None
        username = request.POST.get("new_username", "").strip()
        password = request.POST.get("new_password", "")
        password_confirm = request.POST.get("new_password_confirm", "")

        if username:
            if not password:
                messages.error(request, "Password is required when creating a new user account.")
                return redirect("workers")
            if password != password_confirm:
                messages.error(request, "Password and confirm password must match.")
                return redirect("workers")
            if User.objects.filter(username__iexact=username).exists():
                messages.error(request, "That username is already taken.")
                return redirect("workers")
            try:
                user = User.objects.create_user(username=username, password=password, is_active=True)
            except IntegrityError:
                messages.error(request, "Unable to create the user account. Choose a different username.")
                return redirect("workers")
        elif request.POST.get("user_id"):
            user = User.objects.filter(pk=request.POST.get("user_id")).first()

        worker = Worker.objects.create(
            user=user,
            name=name,
            phone=phone,
            email=request.POST.get("email") or None,
            role=request.POST.get("role", "driver"),
            status=request.POST.get("status", "active"),
            daily_rate=request.POST.get("daily_rate") or 0,
            license_number=request.POST.get("license_number") or None,
            vehicle_assigned=request.POST.get("vehicle_assigned") or None,
        )
        Activity.objects.create(
            type="worker_created",
            description=f"New {worker.role} {worker.name} added",
            related_id=worker.id,
            actor=request.user.username,
        )
        messages.success(request, f"Worker '{worker.name}' added.")
    return redirect("workers")


def edit_worker(request, pk):
    if not require_admin(request):
        return redirect("dashboard")

    worker = get_object_or_404(Worker, pk=pk)
    if request.method == "POST":
        worker.name = request.POST.get("name", worker.name).strip()
        worker.phone = request.POST.get("phone", worker.phone).strip()
        worker.email = request.POST.get("email") or None
        worker.role = request.POST.get("role", worker.role)
        worker.status = request.POST.get("status", worker.status)
        worker.daily_rate = request.POST.get("daily_rate") or worker.daily_rate
        worker.license_number = request.POST.get("license_number") or None
        worker.vehicle_assigned = request.POST.get("vehicle_assigned") or None

        selected_user = User.objects.filter(pk=request.POST.get("user_id")).first() if request.POST.get("user_id") else None

        if request.POST.get("new_username"):
            new_username = request.POST.get("new_username", "").strip()
            if worker.user and worker.user.username.lower() != new_username.lower() and User.objects.filter(username__iexact=new_username).exists():
                messages.error(request, "That username is already taken.")
                return redirect("workers")
            if worker.user:
                worker.user.username = new_username
                worker.user.save()
            else:
                password = request.POST.get("new_password", "")
                password_confirm = request.POST.get("new_password_confirm", "")
                if not password:
                    messages.error(request, "Password is required when creating a new user account.")
                    return redirect("workers")
                if password != password_confirm:
                    messages.error(request, "Password and confirm password must match.")
                    return redirect("workers")
                worker.user = User.objects.create_user(username=new_username, password=password, is_active=True)
        elif selected_user is not None:
            worker.user = selected_user
        else:
            worker.user = None

        if request.POST.get("new_password") and worker.user:
            password = request.POST.get("new_password")
            password_confirm = request.POST.get("new_password_confirm")
            if password != password_confirm:
                messages.error(request, "Password and confirm password must match.")
                return redirect("workers")
            worker.user.set_password(password)
            worker.user.save()

        worker.save()
        messages.success(request, f"Worker '{worker.name}' updated.")
    return redirect("workers")


def delete_worker(request, pk):
    worker = get_object_or_404(Worker, pk=pk)
    if request.method == "POST":
        name = worker.name
        worker.delete()
        messages.success(request, f"Worker '{name}' removed.")
    return redirect("workers")
