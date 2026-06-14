from django.shortcuts import render
from django.db.models import Sum, Count, Q
from django.utils import timezone
from core.models import Customer, Worker, Order, Delivery, InventoryItem, PayrollRecord, Transaction, Activity


def index(request):
    today = timezone.localdate()

    today_revenue = Transaction.objects.filter(
        type="income", date=today
    ).aggregate(total=Sum("amount"))["total"] or 0

    yesterday = today - timezone.timedelta(days=1)
    yesterday_revenue = Transaction.objects.filter(
        type="income", date=yesterday
    ).aggregate(total=Sum("amount"))["total"] or 1

    revenue_change = round(((float(today_revenue) - float(yesterday_revenue)) / float(yesterday_revenue)) * 100, 1)

    today_deliveries = Delivery.objects.filter(created_at__date=today).count()
    completed_today = Delivery.objects.filter(created_at__date=today, status="completed").count()

    active_orders = Order.objects.exclude(status__in=["delivered", "cancelled"]).count()

    low_stock = InventoryItem.objects.filter(is_low_stock=True).count()

    total_customers = Customer.objects.filter(status="active").count()

    workers_on_duty = Worker.objects.filter(status="active").count()

    pending_payroll = PayrollRecord.objects.filter(
        status="pending"
    ).aggregate(total=Sum("net_pay"))["total"] or 0

    recent_activity = Activity.objects.order_by("-created_at")[:4]

    context = {
        "today_revenue": today_revenue,
        "revenue_change": revenue_change,
        "today_deliveries": today_deliveries,
        "completed_today": completed_today,
        "active_orders": active_orders,
        "low_stock": low_stock,
        "total_customers": total_customers,
        "workers_on_duty": workers_on_duty,
        "pending_payroll": pending_payroll,
        "recent_activity": recent_activity,
        "active_page": "dashboard",
    }
    return render(request, "dashboard.html", context)
