from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Polygon
from apps.telemetry.models import GlacierBasin

class Command(BaseCommand):
    help = "Заполнение PostGIS начальными геозонами бассейнов рек"

    def handle(self, *args, **options):
        basins = [
            {
                "name": "Бассейн р. Нарын (Ферганская долина)",
                "code": "naryn",
                "total_area_km2": 59100.0,
                # Координаты контурного полигона (WGS84)
                "polygon": Polygon((
                    (73.5, 41.0),
                    (76.0, 41.8),
                    (78.2, 42.1),
                    (77.5, 41.2),
                    (75.0, 40.8),
                    (73.5, 41.0)
                ))
            },
            {
                "name": "Верховья Сырдарьи (Наманган)",
                "code": "syrdarya",
                "total_area_km2": 219000.0,
                "polygon": Polygon((
                    (70.8, 40.5),
                    (72.5, 41.5),
                    (74.0, 41.2),
                    (72.0, 40.2),
                    (70.8, 40.5)
                ))
            }
        ]

        for b in basins:
            obj, created = GlacierBasin.objects.update_or_create(
                code=b["code"],
                defaults={
                    "name": b["name"],
                    "total_area_km2": b["total_area_km2"],
                    "polygon": b["polygon"]
                }
            )
            action = "Создан" if created else "Обновлен"
            self.stdout.write(self.style.SUCCESS(f"{action} бассейн: {obj.name}"))