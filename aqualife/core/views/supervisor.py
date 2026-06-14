from django.shortcuts import render
from django.db.models import Count
from core.models import Delivery, Worker
from core.utils import require_worker_role


@require_worker_role({"supervisor"})
def index(request):
    pending = Delivery.objects.filter(status="pending").count()
    in_progress = Delivery.objects.filter(status="driver_confirmed").count()
    completed = Delivery.objects.filter(status="completed").count()
    active_drivers = Worker.objects.filter(role="driver", status="active").count()
    active_turnboys = Worker.objects.filter(role="turnboy", status="active").count()
    top_drivers = (
        Delivery.objects.filter(status="completed", driver_id__isnull=False)
        .values("driver_name")
        .annotate(count=Count("id"))
        .order_by("-count")[:5]
    )

    return render(request, "supervisor/dashboard.html", {
        "active_page": "supervisor",
        "pending": pending,
        "in_progress": in_progress,
        "completed": completed,
        "active_drivers": active_drivers,
        "active_turnboys": active_turnboys,
        "top_drivers": top_drivers,
    })


@require_worker_role({"supervisor"})
def list_deliveries(request):
    status_filter = request.GET.get("status", "")
    deliveries = Delivery.objects.all()
    if status_filter:
        deliveries = deliveries.filter(status=status_filter)

    return render(request, "supervisor/deliveries.html", {
        "active_page": "supervisor_deliveries",
        "deliveries": deliveries,
        "status_filter": status_filter,
    })
