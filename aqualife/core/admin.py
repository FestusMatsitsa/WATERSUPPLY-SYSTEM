from django.contrib import admin
from .models import Customer, Worker, Order, Delivery, InventoryItem, PayrollRecord, Transaction, Activity

admin.site.register(Customer)
admin.site.register(Worker)
admin.site.register(Order)
admin.site.register(Delivery)
admin.site.register(InventoryItem)
admin.site.register(PayrollRecord)
admin.site.register(Transaction)
admin.site.register(Activity)
