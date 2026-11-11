from django.contrib.gis.db import models

class GlacierBasin(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название бассейна")
    code = models.SlugField(unique=True)
    polygon = models.PolygonField(srid=4326, verbose_name="Геопространственные границы")
    total_area_km2 = models.FloatField(verbose_name="Общая площадь (км²)")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class MODISSatelliteSnapshot(models.Model):
    basin = models.ForeignKey(GlacierBasin, on_delete=models.CASCADE, related_name="snapshots")
    observation_date = models.DateField(db_index=True)
    snow_covered_area_km2 = models.FloatField()
    snow_cover_percentage = models.FloatField()
    granule_id = models.CharField(max_length=255, unique=True)
    raw_metadata = models.JSONField(default=dict)

    class Meta:
        ordering = ['-observation_date']