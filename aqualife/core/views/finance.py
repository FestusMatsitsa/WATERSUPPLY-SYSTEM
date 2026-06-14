from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum, Q
from django.utils import timezone
from core.models import Transaction, Activity


CATEGORIES = {
    "income": ["water_delivery", "bottle_sales", "other_income"],
    "expense": ["fuel", "payroll", "maintenance", "supplies", "utilities", "other_expense"],
}


def finance_index(request):
    tx_type = request.GET.get("type", "")
    category = request.GET.get("category", "")
    qs = Transaction.objects.all()
    if tx_type:
        qs = qs.filter(type=tx_type)
    if category:
        qs = qs.filter(category=category)

    today = timezone.localdate()
    month_start = today.replace(day=1)

    total_income = Transaction.objects.filter(type="income", date__gte=month_start).aggregate(t=Sum("amount"))["t"] or 0
    total_expense = Transaction.objects.filter(type="expense", date__gte=month_start).aggregate(t=Sum("amount"))["t"] or 0
    net = float(total_income) - float(total_expense)

    return render(request, "finance/index.html", {
        "transactions": qs[:100],
        "type_filter": tx_type,
        "category_filter": category,
        "total_income": total_income,
        "total_expense": total_expense,
        "net": net,
        "income_categories": CATEGORIES["income"],
        "expense_categories": CATEGORIES["expense"],
        "active_page": "finance",
    })


def create_transaction(request):
    if request.method == "POST":
        tx_type = request.POST.get("type", "income")
        amount = float(request.POST.get("amount", 0))
        tx = Transaction.objects.create(
            type=tx_type,
            amount=amount,
            category=request.POST.get("category") or None,
            description=request.POST.get("description") or None,
            reference=request.POST.get("reference") or None,
            date=request.POST.get("date") or str(timezone.localdate()),
        )
        messages.success(request, f"Transaction recorded: KES {amount:,.0f} {tx_type}.")
    return redirect("finance")


def delete_transaction(request, pk):
    tx = get_object_or_404(Transaction, pk=pk)
    if request.method == "POST":
        tx.delete()
        messages.success(request, "Transaction deleted.")
    return redirect("finance")
