from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from core.models import Worker, PayrollRecord, Activity


def list_payroll(request):
    date_filter = request.GET.get("date", "")
    status_filter = request.GET.get("status", "")
    qs = PayrollRecord.objects.all()
    if date_filter:
        qs = qs.filter(period_date=date_filter)
    if status_filter:
        qs = qs.filter(status=status_filter)

    return render(request, "payroll/list.html", {
        "records": qs,
        "date_filter": date_filter,
        "status_filter": status_filter,
        "today": timezone.localdate(),
        "active_page": "payroll",
    })


def generate_payroll(request):
    if request.method == "POST":
        date_str = request.POST.get("date", str(timezone.localdate()))
        active_workers = Worker.objects.filter(status="active")
        created = 0
        for worker in active_workers:
            _, was_created = PayrollRecord.objects.get_or_create(
                worker_id=worker.id,
                period_date=date_str,
                defaults={
                    "worker_name": worker.name,
                    "worker_role": worker.role,
                    "base_pay": worker.daily_rate,
                    "bonuses": 0,
                    "deductions": 0,
                    "penalties": 0,
                    "net_pay": worker.daily_rate,
                    "status": "pending",
                    "deliveries_count": 0,
                    "adjustments": [],
                },
            )
            if was_created:
                created += 1
        Activity.objects.create(
            type="payroll_generated",
            description=f"Payroll generated for {date_str} — {created} new records",
            actor="Admin",
        )
        messages.success(request, f"Payroll generated: {created} new records for {date_str}.")
    return redirect("payroll")


def approve_payroll(request, pk):
    record = get_object_or_404(PayrollRecord, pk=pk)
    if request.method == "POST":
        record.status = "approved"
        record.save()
        Activity.objects.create(
            type="payroll_approved",
            description=f"Payment for {record.worker_name} approved",
            related_id=record.id,
            actor="Admin",
        )
        messages.success(request, f"Payroll for '{record.worker_name}' approved.")
    return redirect("payroll")


def hold_payroll(request, pk):
    record = get_object_or_404(PayrollRecord, pk=pk)
    if request.method == "POST":
        record.status = "held"
        reason = request.POST.get("reason", "")
        record.admin_comment = reason
        record.save()
        Activity.objects.create(
            type="payroll_held",
            description=f"Payment for {record.worker_name} put on hold",
            related_id=record.id,
            actor="Admin",
        )
        messages.warning(request, f"Payroll for '{record.worker_name}' put on hold.")
    return redirect("payroll")


def adjust_payroll(request, pk):
    record = get_object_or_404(PayrollRecord, pk=pk)
    if request.method == "POST":
        adj_type = request.POST.get("adj_type", "bonus")
        amount = float(request.POST.get("amount", 0))
        comment = request.POST.get("comment", "")

        adjustments = record.adjustments or []
        adjustments.append({
            "type": adj_type,
            "amount": amount,
            "comment": comment,
            "created_at": str(timezone.now()),
        })
        record.adjustments = adjustments

        if adj_type == "bonus":
            record.bonuses = float(record.bonuses) + amount
        elif adj_type == "deduction":
            record.deductions = float(record.deductions) + amount
        elif adj_type == "penalty":
            record.penalties = float(record.penalties) + amount

        record.net_pay = float(record.base_pay) + float(record.bonuses) - float(record.deductions) - float(record.penalties)
        record.save()
        messages.success(request, f"Adjustment added to '{record.worker_name}' payroll.")
    return redirect("payroll")
