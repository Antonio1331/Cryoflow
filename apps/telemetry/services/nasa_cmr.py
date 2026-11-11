import requests
from django.conf import settings


class NASACMRClient:
    """Интеграционный сервис работы с NASA Common Metadata Repository API."""

    BASE_URL = "https://cmr.earthdata.nasa.gov/search/granules.json"

    def fetch_snow_cover_data(self, bounding_box: list, start_date: str, end_date: str) -> dict:
        params = {
            "short_name": "MOD10A1",
            "temporal": f"{start_date}T00:00:00Z,{end_date}T23:59:59Z",
            "bounding_box": ",".join(map(str, bounding_box)),
            "page_size": 10
        }
        try:
            response = requests.get(self.BASE_URL, params=params, timeout=15)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            # Fallback на резервное кэшированное значение при сбоях API NASA
            return {"error": str(e), "fallback": True}