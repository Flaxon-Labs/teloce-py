from django.urls import path

from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("api/dashboard/summary/", views.inventory_summary, name="inventory-summary"),
]
