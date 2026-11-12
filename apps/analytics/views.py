import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from apps.analytics.ml_engine import GlacierMeltPredictor

@require_POST
def api_predict_water_trend(request):
    try:
        data = json.loads(request.body)
        region = data.get("region", "naryn")
        forecast_days = int(data.get("forecast_days", 90))
        date_start = data.get("date_start", "2026-05-01")
        date_end = data.get("date_end", "2026-06-01")

        predictor = GlacierMeltPredictor()
        result = predictor.predict(
            region=region,
            forecast_days=forecast_days,
            date_start=date_start,
            date_end=date_end
        )

        return JsonResponse({"status": "success", **result})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)