from django.db import models
from django.contrib.auth.models import User


class Customer(models.Model):
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=50)
    email = models.CharField(max_length=200, blank=True, null=True)
    location = models.CharField(max_length=200, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    account_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, default="active")
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = "customers"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class Worker(models.Model):
    ROLE_CHOICES = [
        ("driver", "Driver"),
        ("turnboy", "Turnboy"),
        ("supervisor", "Supervisor"),
    ]

    user = models.OneToOneField(User, blank=True, null=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=50)
    email = models.CharField(max_length=200, blank=True, null=True)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)
    status = models.CharField(max_length=20, default="active")
    daily_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    license_number = models.CharField(max_length=100, blank=True, null=True)
    vehicle_assigned = models.CharField(max_length=200, blank=True, null=True)
    total_deliveries = models.IntegerField(default=0)
    total_earnings = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = "workers"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def is_field_staff(self):
        return self.role in {"driver", "turnboy"}

    def is_supervisor(self):
        return self.role == "supervisor"


class Order(models.Model):
    customer_id = models.IntegerField(blank=True, null=True)
    customer_name = models.CharField(max_length=200)
    type = models.CharField(max_length=50)
    status = models.CharField(max_length=50, default="pending")
    litres = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    bottle_count = models.IntegerField(blank=True, null=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    delivery_location = models.CharField(max_length=300, blank=True, null=True)
    driver_id = models.IntegerField(blank=True, null=True)
    driver_name = models.CharField(max_length=200, blank=True, null=True)
    turnboy_id = models.IntegerField(blank=True, null=True)
    turnboy_name = models.CharField(max_length=200, blank=True, null=True)
    delivered_at = models.DateTimeField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = "orders"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.id} — {self.customer_name}"

    def type_display(self):
        return {"water_delivery": "Water Delivery", "empty_bottles": "Empty Bottles", "refilled_bottles": "Refilled Bottles"}.get(self.type, self.type)

    def status_badge(self):
        return {
            "pending": "secondary",
            "approved": "primary",
            "assigned": "info",
            "in_progress": "warning",
            "delivered": "success",
            "cancelled": "danger",
        }.get(self.status, "secondary")


class Delivery(models.Model):
    order_id = models.IntegerField(blank=True, null=True)
    order_type = models.CharField(max_length=50, blank=True, null=True)
    customer_id = models.IntegerField(blank=True, null=True)
    customer_name = models.CharField(max_length=200, blank=True, null=True)
    driver_id = models.IntegerField(blank=True, null=True)
    driver_name = models.CharField(max_length=200, blank=True, null=True)
    turnboy_id = models.IntegerField(blank=True, null=True)
    turnboy_name = models.CharField(max_length=200, blank=True, null=True)
    status = models.CharField(max_length=50, default="pending")
    driver_confirmed_at = models.DateTimeField(blank=True, null=True)
    turnboy_confirmed_at = models.DateTimeField(blank=True, null=True)
    delivery_location = models.CharField(max_length=300, blank=True, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    completed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = "deliveries"
        ordering = ["-created_at"]

    def status_badge(self):
        return {
            "pending": "secondary",
            "driver_confirmed": "warning",
            "completed": "success",
            "failed": "danger",
        }.get(self.status, "secondary")


class InventoryItem(models.Model):
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=50)
    quantity = models.IntegerField(default=0)
    unit = models.CharField(max_length=50, default="units")
    min_stock_level = models.IntegerField(default=0)
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_low_stock = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = "inventory"
        ordering = ["name"]

    def __str__(self):
        return self.name


class PayrollRecord(models.Model):
    worker_id = models.IntegerField(blank=True, null=True)
    worker_name = models.CharField(max_length=200)
    worker_role = models.CharField(max_length=50, blank=True, null=True)
    period_date = models.DateField()
    base_pay = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    bonuses = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    penalties = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_pay = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, default="pending")
    deliveries_count = models.IntegerField(default=0)
    admin_comment = models.TextField(blank=True, null=True)
    adjustments = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = "payroll"
        ordering = ["-period_date", "worker_name"]

    def status_badge(self):
        return {
            "pending": "warning",
            "approved": "primary",
            "held": "danger",
            "paid": "primary",
        }.get(self.status, "secondary")


class Transaction(models.Model):
    type = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    category = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    reference = models.CharField(max_length=200, blank=True, null=True)
    related_order_id = models.IntegerField(blank=True, null=True)
    related_worker_id = models.IntegerField(blank=True, null=True)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = "transactions"
        ordering = ["-date", "-created_at"]

    def type_badge(self):
        return "success" if self.type == "income" else "danger"


class Activity(models.Model):
    type = models.CharField(max_length=100)
    description = models.TextField()
    related_id = models.IntegerField(blank=True, null=True)
    actor = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(db_column="timestamp", auto_now_add=True)

    class Meta:
        managed = True
        db_table = "activity"
        ordering = ["-created_at"]


class LoginAttempt(models.Model):
    username = models.CharField(max_length=200)
    failed_attempts = models.IntegerField(default=0)
    locked_at = models.DateTimeField(blank=True, null=True)
    last_attempt_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = "login_attempts"
        unique_together = ("username",)

    def __str__(self):
        return f"{self.username} — {self.failed_attempts} failed attempts"
