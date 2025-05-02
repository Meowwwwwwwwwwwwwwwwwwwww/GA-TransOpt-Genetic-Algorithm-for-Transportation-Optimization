from django.db import models

# Create your models here.
from django.db import models

class RouteSummary(models.Model):
    bus_number = models.CharField(max_length=20)
    bus_capacity = models.PositiveIntegerField()
    total_students = models.PositiveIntegerField()
    total_stops = models.PositiveIntegerField()
    total_distance_km = models.FloatField()
    is_overloaded = models.BooleanField(default=False)
    generated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"RouteSummary for Bus {self.bus_number} on {self.generated_at.date()}"
