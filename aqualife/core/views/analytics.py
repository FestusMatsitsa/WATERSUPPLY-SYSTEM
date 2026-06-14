import json
from django.shortcuts import render
from django.db.models import Sum, Count
from django.utils import timezone
from core.models import Transaction, Delivery, Order, Worker, InventoryItem


def analytics_index(request):
    today = timezone.localdate()

    # 30-day revenue trend
    revenue_labels = []
    revenue_data = []
    for i in range(29, -1, -1):
        day = today - timezone.timedelta(days=i)
        label = day.strftime("%b %d")
        income = Transaction.objects.filter(
            type="income", date=day
        ).aggregate(t=Sum("amount"))["t"] or 0
        revenue_labels.append(label)
        revenue_data.append(float(income))

    # Worker performance (deliveries by driver)
    worker_perf = (
        Delivery.objects.filter(status="completed", driver_name__isnull=False)
        .values("driver_name")
        .annotate(count=Count("id"))
        .order_by("-count")[:8]
    )
    worker_labels = [w["driver_name"] for w in worker_perf]
    worker_data = [w["count"] for w in worker_perf]

    # Order type breakdown
    type_breakdown = (
        Order.objects.values("type")
        .annotate(count=Count("id"))
    )
    type_labels = [t["type"].replace("_", " ").title() for t in type_breakdown]
    type_data = [t["count"] for t in type_breakdown]

    # Income vs expense (last 6 months)
    monthly_labels = []
    monthly_income = []
    monthly_expense = []
    for i in range(5, -1, -1):
        month = (today.replace(day=1) - timezone.timedelta(days=i * 30)).replace(day=1)
        label = month.strftime("%b %Y")
        inc = Transaction.objects.filter(
            type="income",
            date__year=month.year,
            date__month=month.month,
        ).aggregate(t=Sum("amount"))["t"] or 0
        exp = Transaction.objects.filter(
            type="expense",
            date__year=month.year,
            date__month=month.month,
        ).aggregate(t=Sum("amount"))["t"] or 0
        monthly_labels.append(label)
        monthly_income.append(float(inc))
        monthly_expense.append(float(exp))

    # Low stock items
    low_stock_items = InventoryItem.objects.filter(is_low_stock=True)

    # Top workers by deliveries
    top_workers = Worker.objects.filter(status="active").order_by("-total_deliveries")[:5]

    context = {
        "revenue_labels": json.dumps(revenue_labels),
        "revenue_data": json.dumps(revenue_data),
        "worker_labels": json.dumps(worker_labels),
        "worker_data": json.dumps(worker_data),
        "type_labels": json.dumps(type_labels),
        "type_data": json.dumps(type_data),
        "monthly_labels": json.dumps(monthly_labels),
        "monthly_income": json.dumps(monthly_income),
        "monthly_expense": json.dumps(monthly_expense),
        "low_stock_items": low_stock_items,
        "top_workers": top_workers,
        "active_page": "analytics",
    }
    return render(request, "analytics/index.html", context)
