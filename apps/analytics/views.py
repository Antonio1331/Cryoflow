import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from apps.analytics.ml_engine import GlacierMeltPredictor


@require_POST
def api_predict_water_trend(request):
    try:
        data = json.loads(request.body)
        forecast_days = int(data.get("forecast_days", 90))
        current_snow = float(data.get("current_snow_km2", 450.5))

        predictor = GlacierMeltPredictor()
        result = predictor.predict(current_snow_km2=current_snow, forecast_days=forecast_days)

        return JsonResponse({"status": "success", **result})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)