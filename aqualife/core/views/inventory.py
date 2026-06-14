from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from core.models import InventoryItem, Activity


def list_inventory(request):
    category = request.GET.get("category", "")
    qs = InventoryItem.objects.all()
    if category:
        qs = qs.filter(category=category)

    return render(request, "inventory/list.html", {
        "items": qs,
        "category_filter": category,
        "active_page": "inventory",
    })


def create_item(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        quantity = int(request.POST.get("quantity", 0))
        min_level = int(request.POST.get("min_stock_level", 0))
        item = InventoryItem.objects.create(
            name=name,
            category=request.POST.get("category", "empty_bottles"),
            quantity=quantity,
            unit=request.POST.get("unit", "units"),
            min_stock_level=min_level,
            price_per_unit=request.POST.get("price_per_unit") or 0,
            is_low_stock=(quantity <= min_level),
        )
        Activity.objects.create(
            type="inventory_created",
            description=f"New inventory item '{item.name}' added with {quantity} {item.unit}",
            related_id=item.id,
            actor="Admin",
        )
        messages.success(request, f"'{item.name}' added to inventory.")
    return redirect("inventory")


def edit_item(request, pk):
    item = get_object_or_404(InventoryItem, pk=pk)
    if request.method == "POST":
        old_qty = item.quantity
        item.name = request.POST.get("name", item.name).strip()
        item.category = request.POST.get("category", item.category)
        item.quantity = int(request.POST.get("quantity", item.quantity))
        item.unit = request.POST.get("unit", item.unit)
        item.min_stock_level = int(request.POST.get("min_stock_level", item.min_stock_level))
        item.price_per_unit = request.POST.get("price_per_unit") or item.price_per_unit
        item.is_low_stock = item.quantity <= item.min_stock_level
        item.save()
        diff = item.quantity - old_qty
        sign = "+" if diff >= 0 else ""
        Activity.objects.create(
            type="inventory_adjusted",
            description=f"{item.name} stock adjusted by {sign}{diff}: Manual update",
            related_id=item.id,
            actor="Admin",
        )
        messages.success(request, f"'{item.name}' updated.")
    return redirect("inventory")


def delete_item(request, pk):
    item = get_object_or_404(InventoryItem, pk=pk)
    if request.method == "POST":
        name = item.name
        item.delete()
        messages.success(request, f"'{name}' removed from inventory.")
    return redirect("inventory")
