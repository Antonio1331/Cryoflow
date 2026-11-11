import { MapEngine } from './modules/map_engine.js';

document.addEventListener('DOMContentLoaded', () => {
    const map = new MapEngine('leaflet-map', [41.4, 74.0]);

    // Обработка отправки формы
    const form = document.getElementById('analytics-form');
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const payload = {
            region: document.getElementById('region-select').value,
            forecast_days: parseInt(document.getElementById('forecast-slider').value)
        };

        const response = await fetch('/api/v1/analytics/predict/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();
        if (data.status === 'success') {
            updateMetricsUI(data.metrics);
            renderForecastChart(data.timeline);
        }
    });
});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}