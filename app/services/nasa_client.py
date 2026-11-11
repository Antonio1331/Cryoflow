import os
import earthaccess
from typing import List, Dict, Any
import rasterio
from rasterio.mask import mask
from shapely.geometry import box, mapping
import geopandas as gpd

from app.config import settings


class NASADataClient:
    def __init__(self):
        self._authenticate()

    def _authenticate(self):
        """
        Аутентификация в системе NASA Earthdata.
        """
        try:
            if settings.NASA_USERNAME and settings.NASA_PASSWORD:
                # Устанавливаем переменные окружения, которые earthaccess читает автоматически
                os.environ["EARTHDATA_USERNAME"] = settings.NASA_USERNAME
                os.environ["EARTHDATA_PASSWORD"] = settings.NASA_PASSWORD

                # Авторизация через стратегию environment
                auth = earthaccess.login(strategy="environment", persist=True)
            else:
                # Попытка найти существующую сессию / токен или интерактивный вход
                auth = earthaccess.login(strategy="netrc", persist=True)

            if auth:
                print("✅ Успешная авторизация в NASA Earthdata!")
            else:
                print("⚠️ Внимание: Не удалось пройти авторизацию NASA Earthdata.")
        except Exception as e:
            print(f"⚠️ Ошибка аутентификации NASA: {e}")

    def search_snow_cover(
            self,
            bounding_box: tuple[float, float, float, float],
            date_range: tuple[str, str]
    ) -> List[Dict[str, Any]]:
        """
        Поиск продуктов снежного покрова MODIS (например, MOD10A1) по Bounding Box и датам.
        """
        results = earthaccess.search_data(
            short_name="MOD10A1",  # Продукт MODIS Snow Cover Daily
            bounding_box=bounding_box,
            temporal=date_range,
            count=5
        )
        return results

    def download_granules(self, granules: List[Any]) -> List[str]:
        """
        Скачивает найденные гранулы (файлы) в локальный кэш.
        """
        files = earthaccess.download(granules, settings.DATA_CACHE_DIR)
        return files


class RasterProcessor:
    @staticmethod
    def crop_raster_by_polygon(
            raster_path: str,
            polygon_geojson: Dict[str, Any]
    ) -> tuple[Any, dict]:
        gdf = gpd.GeoDataFrame.from_features([polygon_geojson])

        with rasterio.open(raster_path) as src:
            out_image, out_transform = mask(src, gdf.geometry, crop=True)
            out_meta = src.meta.copy()

            out_meta.update({
                "driver": "GTiff",
                "height": out_image.shape[1],
                "width": out_image.shape[2],
                "transform": out_transform
            })

        return out_image, out_meta