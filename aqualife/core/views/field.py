from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from core.models import Delivery
from core.utils import require_worker_role, get_worker_for_user


@require_worker_role({"driver", "turnboy"})
def index(request):
    worker = request.worker
    deliveries = _get_worker_deliveries(worker)
    context = {
        "active_page": "field",
        "worker": worker,
        "deliveries": deliveries,
        "pending_count": deliveries.filter(status="pending").count() if worker.role == "driver" else deliveries.filter(status="driver_confirmed").count(),
        "completed_count": deliveries.filter(status="completed").count(),
    }
    return render(request, "field/dashboard.html", context)


@require_worker_role({"driver", "turnboy"})
def list_deliveries(request):
    worker = request.worker
    status_filter = request.GET.get("status", "")
    deliveries = _get_worker_deliveries(worker)
    if status_filter:
        deliveries = deliveries.filter(status=status_filter)

    return render(request, "field/deliveries.html", {
        "active_page": "field_deliveries",
        "worker": worker,
        "deliveries": deliveries,
        "status_filter": status_filter,
    })


@require_worker_role({"driver", "turnboy"})
def confirm_delivery(request, pk):
    worker = request.worker
    delivery = get_object_or_404(Delivery, pk=pk)
    if request.method != "POST":
        return redirect("field_deliveries")

    if worker.role == "driver":
        if delivery.driver_id != worker.id:
            messages.error(request, "This delivery is not assigned to you.")
            return redirect("field_deliveries")
        if delivery.status != "pending":
            messages.warning(request, "This delivery cannot be confirmed by driver.")
            return redirect("field_deliveries")
        delivery.status = "driver_confirmed"
        delivery.driver_confirmed_at = timezone.now()
        delivery.save()
        messages.success(request, "Driver confirmation recorded.")
    else:
        if delivery.turnboy_id != worker.id:
            messages.error(request, "This delivery is not assigned to you.")
            return redirect("field_deliveries")
        if delivery.status != "driver_confirmed":
            messages.warning(request, "This delivery cannot be confirmed by turnboy yet.")
            return redirect("field_deliveries")
        delivery.status = "completed"
        delivery.turnboy_confirmed_at = timezone.now()
        delivery.completed_at = timezone.now()
        delivery.save()
        messages.success(request, "Turnboy delivery confirmation recorded.")

    return redirect("field_deliveries")


def _get_worker_deliveries(worker):
    if worker.role == "driver":
        return Delivery.objects.filter(driver_id=worker.id)
    return Delivery.objects.filter(turnboy_id=worker.id)
