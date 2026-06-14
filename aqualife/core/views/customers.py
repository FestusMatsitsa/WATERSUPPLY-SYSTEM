from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from core.models import Customer, Activity


def list_customers(request):
    q = request.GET.get("q", "")
    status = request.GET.get("status", "")
    qs = Customer.objects.all()
    if q:
        qs = qs.filter(name__icontains=q) | Customer.objects.filter(phone__icontains=q)
    if status:
        qs = qs.filter(status=status)
    return render(request, "customers/list.html", {
        "customers": qs,
        "q": q,
        "status_filter": status,
        "active_page": "customers",
    })


def create_customer(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        phone = request.POST.get("phone", "").strip()
        if not name or not phone:
            messages.error(request, "Name and phone are required.")
            return redirect("customers")
        customer = Customer.objects.create(
            name=name,
            phone=phone,
            email=request.POST.get("email") or None,
            location=request.POST.get("location") or None,
            address=request.POST.get("address") or None,
            account_balance=request.POST.get("account_balance") or 0,
            status=request.POST.get("status", "active"),
            notes=request.POST.get("notes") or None,
        )
        Activity.objects.create(
            type="customer_created",
            description=f"New customer {customer.name} registered",
            related_id=customer.id,
            actor="Admin",
        )
        messages.success(request, f"Customer '{customer.name}' created successfully.")
    return redirect("customers")


def edit_customer(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == "POST":
        customer.name = request.POST.get("name", customer.name).strip()
        customer.phone = request.POST.get("phone", customer.phone).strip()
        customer.email = request.POST.get("email") or None
        customer.location = request.POST.get("location") or None
        customer.address = request.POST.get("address") or None
        customer.account_balance = request.POST.get("account_balance") or 0
        customer.status = request.POST.get("status", customer.status)
        customer.notes = request.POST.get("notes") or None
        customer.save()
        messages.success(request, f"Customer '{customer.name}' updated.")
    return redirect("customers")


def delete_customer(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == "POST":
        name = customer.name
        customer.delete()
        messages.success(request, f"Customer '{name}' deleted.")
    return redirect("customers")
