from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from core.models import Delivery, Order, Activity
from core.utils import get_worker_for_user


def list_deliveries(request):
    status = request.GET.get("status", "")
    qs = Delivery.objects.all()
    if status:
        qs = qs.filter(status=status)

    return render(request, "deliveries/list.html", {
        "deliveries": qs,
        "status_filter": status,
        "active_page": "deliveries",
    })


def driver_confirm(request, pk):
    delivery = get_object_or_404(Delivery, pk=pk)
    worker = get_worker_for_user(request.user)
    if request.method == "POST":
        if not worker or worker.role != "driver" or delivery.driver_id != worker.id:
            messages.error(request, "You are not authorized to confirm this delivery.")
            return redirect("field_deliveries")
        if delivery.status == "pending":
            delivery.status = "driver_confirmed"
            delivery.driver_confirmed_at = timezone.now()
            delivery.save()
            Order.objects.filter(pk=delivery.order_id).update(status="in_progress")
            Activity.objects.create(
                type="driver_confirmed",
                description=f"Driver confirmed delivery #{delivery.id} to {delivery.customer_name}",
                related_id=delivery.id,
                actor=delivery.driver_name or worker.name,
            )
            messages.success(request, "Driver confirmation recorded.")
        else:
            messages.warning(request, "Delivery is not in pending state.")
    return redirect("field_deliveries" if worker and worker.is_field_staff() else "deliveries")


def turnboy_confirm(request, pk):
    delivery = get_object_or_404(Delivery, pk=pk)
    worker = get_worker_for_user(request.user)
    if request.method == "POST":
        if not worker or worker.role != "turnboy" or delivery.turnboy_id != worker.id:
            messages.error(request, "You are not authorized to confirm this delivery.")
            return redirect("field_deliveries")
        if delivery.status == "driver_confirmed":
            delivery.status = "completed"
            delivery.turnboy_confirmed_at = timezone.now()
            delivery.completed_at = timezone.now()
            delivery.save()
            Order.objects.filter(pk=delivery.order_id).update(status="delivered")
            Activity.objects.create(
                type="delivery_completed",
                description=f"Delivery #{delivery.id} to {delivery.customer_name} fully confirmed",
                related_id=delivery.id,
                actor=delivery.turnboy_name or worker.name,
            )
            messages.success(request, "Delivery completed and confirmed by turnboy.")
        else:
            messages.warning(request, "Driver must confirm first before turnboy confirmation.")
    return redirect("field_deliveries" if worker and worker.is_field_staff() else "deliveries")
