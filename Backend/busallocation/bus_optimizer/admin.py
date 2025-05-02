from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import RouteSummary

@admin.register(RouteSummary)
class RouteSummaryAdmin(admin.ModelAdmin):
    list_display = ("bus_number", "bus_capacity", "total_students", "is_overloaded", "generated_at")
