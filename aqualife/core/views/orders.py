from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from core.models import Order, Customer, Worker, Delivery, Activity

PRICES = {"water_delivery": 2.5, "empty_bottles": 50.0, "refilled_bottles": 150.0}


def list_orders(request):
    status = request.GET.get("status", "")
    order_type = request.GET.get("type", "")
    qs = Order.objects.all()
    if status:
        qs = qs.filter(status=status)
    if order_type:
        qs = qs.filter(type=order_type)

    customers = Customer.objects.filter(status="active")
    drivers = Worker.objects.filter(role="driver", status="active")
    turnboys = Worker.objects.filter(role="turnboy", status="active")

    return render(request, "orders/list.html", {
        "orders": qs,
        "customers": customers,
        "drivers": drivers,
        "turnboys": turnboys,
        "status_filter": status,
        "type_filter": order_type,
        "active_page": "orders",
    })


def create_order(request):
    if request.method == "POST":
        customer_id = request.POST.get("customer_id")
        order_type = request.POST.get("type", "water_delivery")
        litres = request.POST.get("litres") or None
        bottle_count = request.POST.get("bottle_count") or None

        customer = Customer.objects.filter(pk=customer_id).first()
        customer_name = customer.name if customer else request.POST.get("customer_name", "")

        if order_type == "water_delivery" and litres:
            total = float(litres) * PRICES["water_delivery"]
        elif order_type == "empty_bottles" and bottle_count:
            total = float(bottle_count) * PRICES["empty_bottles"]
        elif order_type == "refilled_bottles" and bottle_count:
            total = float(bottle_count) * PRICES["refilled_bottles"]
        else:
            total = 0

        order = Order.objects.create(
            customer_id=customer_id or None,
            customer_name=customer_name,
            type=order_type,
            status="pending",
            litres=int(litres) if litres else None,
            bottle_count=int(bottle_count) if bottle_count else None,
            total_amount=total,
            delivery_location=request.POST.get("delivery_location") or None,
            notes=request.POST.get("notes") or None,
        )
        Activity.objects.create(
            type="order_created",
            description=f"New {order.type} order for {order.customer_name}",
            related_id=order.id,
            actor="Admin",
        )
        messages.success(request, f"Order #{order.id} created — KES {total:,.0f}")
    return redirect("orders")


def edit_order(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == "POST":
        driver_id = request.POST.get("driver_id") or None
        turnboy_id = request.POST.get("turnboy_id") or None
        new_status = request.POST.get("status", order.status)

        driver = Worker.objects.filter(pk=driver_id).first() if driver_id else None
        turnboy = Worker.objects.filter(pk=turnboy_id).first() if turnboy_id else None

        order.status = new_status
        order.delivery_location = request.POST.get("delivery_location") or order.delivery_location
        order.notes = request.POST.get("notes") or order.notes
        if driver:
            order.driver_id = driver.id
            order.driver_name = driver.name
        if turnboy:
            order.turnboy_id = turnboy.id
            order.turnboy_name = turnboy.name

        if new_status == "assigned" and (driver or turnboy):
            # Create delivery record
            Delivery.objects.get_or_create(
                order_id=order.id,
                defaults={
                    "order_type": order.type,
                    "customer_id": order.customer_id,
                    "customer_name": order.customer_name,
                    "driver_id": order.driver_id,
                    "driver_name": order.driver_name,
                    "turnboy_id": order.turnboy_id,
                    "turnboy_name": order.turnboy_name,
                    "status": "pending",
                    "delivery_location": order.delivery_location,
                    "amount": order.total_amount,
                },
            )

        order.save()
        messages.success(request, f"Order #{order.id} updated to '{new_status}'.")
    return redirect("orders")


def delete_order(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == "POST":
        oid = order.id
        order.delete()
        messages.success(request, f"Order #{oid} deleted.")
    return redirect("orders")
