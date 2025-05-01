from django.urls import path
from .views import run_ga

urlpatterns = [
    path('run/', run_ga),  # API available at /api/run/
]
