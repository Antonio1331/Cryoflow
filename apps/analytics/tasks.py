from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging

from apps.telemetry.models import GlacierBasin, MODISSatelliteSnapshot
from apps.telemetry.services.nasa_cmr import NASACMRClient

logger = logging.getLogger(__name__)


@shared_task
def sync_nasa_modis_telemetry():
    """Ежедневная фоновая задача выкачивания данных по снежному покрову."""
    client = NASACMRClient()
    today = timezone.now().date()
    yesterday = today - timedelta(days=1)

    basins = GlacierBasin.objects.all()
    updated_count = 0

    for basin in basins:
        bbox = list(basin.polygon.extent)  # [min_lon, min_lat, max_lon, max_lat]
        data = client.fetch_snow_cover_data(
            bounding_box=bbox,
            start_date=yesterday.strftime("%Y-%m-%d"),
            end_date=today.strftime("%Y-%m-%d")
        )

        if "error" not in data and "feed" in data:
            entries = data["feed"].get("entry", [])
            for entry in entries:
                granule_id = entry.get("id", f"MOD10A1_{basin.code}_{today}")

                # Симуляция вычисления NDSI по метаданным гранулы
                snow_area = round(basin.total_area_km2 * 0.12, 2)
                snow_pct = round((snow_area / basin.total_area_km2) * 100, 1)

                MODISSatelliteSnapshot.objects.update_or_create(
                    granule_id=granule_id,
                    defaults={
                        "basin": basin,
                        "observation_date": today,
                        "snow_covered_area_km2": snow_area,
                        "snow_cover_percentage": snow_pct,
                        "raw_metadata": entry
                    }
                )
                updated_count += 1

    logger.info(f"Синхронизация NASA MODIS завершена. Добавлено записей: {updated_count}")
    return updated_count