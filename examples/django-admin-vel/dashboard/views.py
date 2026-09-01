from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET

from .models import Product


@staff_member_required(login_url="/admin/login/")
def home(request):
    return render(request, "index.html")


@require_GET
@staff_member_required(login_url="/admin/login/")
def inventory_summary(request):
    products = list(Product.objects.values("id", "name", "sku", "stock"))
    low_stock = [product for product in products if product["stock"] < 5]
    return JsonResponse({
        "total_products": len(products),
        "units_in_stock": sum(product["stock"] for product in products),
        "low_stock": low_stock,
        "products": products,
    })
