from django.urls import path
from .views import api_predict_water_trend

urlpatterns = [
    path('predict/', api_predict_water_trend, name='api_predict_water_trend'),
]