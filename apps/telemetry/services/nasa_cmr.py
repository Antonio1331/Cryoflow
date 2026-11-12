import requests
from django.core.cache import cache

class NASACMRClient:
    BASE_URL = "https://cmr.earthdata.nasa.gov/search/granules.json"

    def fetch_snow_cover_granules(self, region_code: str, bbox: list, start_date: str, end_date: str) -> dict:
        cache_key = f"nasa_cmr_{region_code}_{start_date}_{end_date}"
        try:
            cached = cache.get(cache_key)
            if cached:
                return cached
        except Exception:
            pass

        params = {
            "short_name": "MOD10A1",
            "temporal": f"{start_date}T00:00:00Z,{end_date}T23:59:59Z",
            "bounding_box": ",".join(map(str, bbox)),
            "page_size": 15,
            "sort_key": "-start_date"
        }

        try:
            response = requests.get(self.BASE_URL, params=params, timeout=8)
            response.raise_for_status()
            entries = response.json().get("feed", {}).get("entry", [])

            granules = [
                {
                    "id": item.get("producer_granule_id") or item.get("title", "MOD10A1.A2026"),
                    "date": item.get("time_start", "")[:10],
                    "satellite": "TERRA" if "MOD" in item.get("title", "MOD") else "AQUA",
                    "cloud_cover": item.get("cloud_cover", "N/A")
                }
                for item in entries[:5]
            ]

            result = {"source": "NASA CMR LIVE", "total_found": len(entries), "granules": granules}
            try:
                cache.set(cache_key, result, timeout=3600)
            except Exception:
                pass
            return result
        except Exception:
            return {"source": "NASA CMR FALLBACK", "total_found": 0, "granules": []}