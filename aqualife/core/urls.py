from django.urls import path
from core.views import (
    dashboard,
    customers,
    orders,
    deliveries,
    inventory,
    workers,
    payroll,
    finance,
    analytics,
    field,
    supervisor,
    auth as auth_views,
)

urlpatterns = [
    path("login/", auth_views.login_view, name="login"),
    path("logout/", auth_views.logout_view, name="logout"),
    path("", dashboard.index, name="dashboard"),

    path("customers/", customers.list_customers, name="customers"),
    path("customers/create/", customers.create_customer, name="customer_create"),
    path("customers/<int:pk>/edit/", customers.edit_customer, name="customer_edit"),
    path("customers/<int:pk>/delete/", customers.delete_customer, name="customer_delete"),

    path("orders/", orders.list_orders, name="orders"),
    path("orders/create/", orders.create_order, name="order_create"),
    path("orders/<int:pk>/edit/", orders.edit_order, name="order_edit"),
    path("orders/<int:pk>/delete/", orders.delete_order, name="order_delete"),

    path("deliveries/", deliveries.list_deliveries, name="deliveries"),
    path("deliveries/<int:pk>/driver-confirm/", deliveries.driver_confirm, name="delivery_driver_confirm"),
    path("deliveries/<int:pk>/turnboy-confirm/", deliveries.turnboy_confirm, name="delivery_turnboy_confirm"),

    path("inventory/", inventory.list_inventory, name="inventory"),
    path("inventory/create/", inventory.create_item, name="inventory_create"),
    path("inventory/<int:pk>/edit/", inventory.edit_item, name="inventory_edit"),
    path("inventory/<int:pk>/delete/", inventory.delete_item, name="inventory_delete"),

    path("workers/", workers.list_workers, name="workers"),
    path("workers/create/", workers.create_worker, name="worker_create"),
    path("workers/<int:pk>/edit/", workers.edit_worker, name="worker_edit"),
    path("workers/<int:pk>/delete/", workers.delete_worker, name="worker_delete"),

    path("payroll/", payroll.list_payroll, name="payroll"),
    path("payroll/generate/", payroll.generate_payroll, name="payroll_generate"),
    path("payroll/<int:pk>/approve/", payroll.approve_payroll, name="payroll_approve"),
    path("payroll/<int:pk>/hold/", payroll.hold_payroll, name="payroll_hold"),
    path("payroll/<int:pk>/adjust/", payroll.adjust_payroll, name="payroll_adjust"),

    path("finance/", finance.finance_index, name="finance"),
    path("finance/create/", finance.create_transaction, name="transaction_create"),
    path("finance/<int:pk>/delete/", finance.delete_transaction, name="transaction_delete"),

    path("analytics/", analytics.analytics_index, name="analytics"),

    path("field/", field.index, name="field_dashboard"),
    path("field/deliveries/", field.list_deliveries, name="field_deliveries"),
    path("field/deliveries/<int:pk>/confirm/", field.confirm_delivery, name="field_delivery_confirm"),

    path("supervisor/", supervisor.index, name="supervisor_dashboard"),
    path("supervisor/deliveries/", supervisor.list_deliveries, name="supervisor_deliveries"),
]
