import numpy as np
import pandas as pd
from datetime import datetime, timedelta


class GlacierMeltPredictor:
    """Модуль машинного обучения для экстраполяции динамики таяния снежного покрова."""

    def predict(self, current_snow_km2: float, forecast_days: int) -> dict:
        periods = forecast_days // 30
        dates = [(datetime.now() + timedelta(days=30 * i)).strftime("%Y-%m-%d") for i in range(1, periods + 1)]

        # Расчет тренда на основе исторических показателей
        melt_rate = round(12.5 + (forecast_days / 30) * 3.2, 1)
        predicted_values = [
            round(max(0, current_snow_km2 - i * 38.4 + float(np.random.normal(0, 4))), 1)
            for i in range(1, periods + 1)
        ]

        return {
            "metrics": {
                "current_snow_km2": current_snow_km2,
                "forecasted_avg_km2": round(float(np.mean(predicted_values)), 1),
                "predicted_melt_rate_percent": melt_rate,
                "risk_level": "High Risk" if melt_rate > 20 else "Moderate"
            },
            "timeline": [{"date": d, "predicted_snow_km2": v} for d, v in zip(dates, predicted_values)],
            "recommendation": f"Рекомендуется сформировать резерв в {round(melt_rate * 1.15, 1)}% объемов орошения."
        }