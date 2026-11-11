from django.db import models
from apps.telemetry.models import GlacierBasin

class ForecastLog(models.Model):
    basin = models.ForeignKey(GlacierBasin, on_delete=models.CASCADE)
    generated_at = models.DateTimeField(auto_now_add=True)
    forecast_days = models.IntegerField(default=90)
    predicted_melt_rate = models.FloatField()
    risk_level = models.CharField(max_length=50)
    forecast_data = models.JSONField(help_text="Временной ряд прогноза")