from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, List
from pydantic import BaseModel, Field

from app.services.nasa_client import NASADataClient, RasterProcessor
from app.services.analytics import GlacierAnalytics

router = APIRouter(prefix="/cryo", tags=["Glacier & Water Analytics"])

# Инициализируем клиентов (в реальном приложении можно вынести в зависимости FastAPI)
nasa_client = NASADataClient()


class PolygonRequest(BaseModel):
    polygon: Dict[str, Any] = Field(
        ...,
        description="GeoJSON Polygon геометрия исследуемой зоны (бассейн реки / ледник)"
    )
    date_start: str = Field(..., example="2026-05-01", description="Начальная дата (YYYY-MM-DD)")
    date_end: str = Field(..., example="2026-06-01", description="Конечная дата (YYYY-MM-DD)")


class AnalysisResponse(BaseModel):
    status: str
    bounding_box: List[float]
    metrics: Dict[str, Any]
    trend_analysis: Dict[str, Any] | None = None


@router.post("/analyze-glacier", response_model=AnalysisResponse)
async def analyze_glacier_area(payload: PolygonRequest):
    """
    Эндпоинт для запуска анализа снежного покрова и ледников по заданному полигону.
    """
    try:
        # Проверяем, передан ли полигон и есть ли у него структура
        if not payload.polygon:
            raise HTTPException(status_code=400, detail="Поле 'polygon' отсутствует или пустое.")

        # Безопасно извлекаем координаты
        polygon_type = payload.polygon.get("type", "Polygon")
        coordinates = payload.polygon.get("coordinates")

        if not coordinates:
            raise HTTPException(status_code=400, detail="В GeoJSON полигоне отсутствуют координаты ('coordinates').")

        coords = coordinates[0]
        if not coords:
            raise HTTPException(status_code=400, detail="Неверный формат GeoJSON полигона (пустой массив координат).")

        lons = [p[0] for p in coords]
        lats = [p[1] for p in coords]
        bounding_box = (min(lons), min(lats), max(lons), max(lats))

        # 1. Поиск данных в NASA CMR
        granules = nasa_client.search_snow_cover(
            bounding_box=bounding_box,
            date_range=(payload.date_start, payload.date_end)
        )

        if not granules:
            return {
                "status": "no_data_found",
                "bounding_box": list(bounding_box),
                "metrics": {"message": "За указанный период и регион спутниковые данные не найдены."},
                "trend_analysis": None
            }

        # 2. Скачивание первого доступного растра
        downloaded_files = nasa_client.download_granules(granules[:1])

        if not downloaded_files:
            raise HTTPException(status_code=500, detail="Не удалось скачать растровые файлы с сервера NASA.")

        raster_path = downloaded_files[0]

        # 3. Расчет аналитических метрик по полигону
        metrics = GlacierAnalytics.calculate_snow_cover_metrics(
            raster_path=raster_path,
            polygon_geojson=payload.polygon
        )

        # Демо-имитация временного ряда для оценки тренда
        historical_mock = [
            {"timestamp": "2026-05-01T00:00:00",
             "snow_covered_area_km2": metrics.get("snow_covered_area_km2", 0) * 1.15},
            {"timestamp": "2026-06-01T00:00:00", "snow_covered_area_km2": metrics.get("snow_covered_area_km2", 0)}
        ]
        trend = GlacierAnalytics.compare_time_series(historical_mock)

        return {
            "status": "success",
            "bounding_box": list(bounding_box),
            "metrics": metrics,
            "trend_analysis": trend
        }


    except HTTPException as he:

        raise he

    except Exception as e:

        # ДОБАВЬТЕ ЭТУ СТРОКУ ДЛЯ ДЕБАГА:

        import traceback

        traceback.print_exc()

        raise HTTPException(status_code=500, detail=f"Ошибка обработки космических данных: {str(e)}")