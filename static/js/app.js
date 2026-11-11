import { MapEngine } from './modules/map_engine.js';
import { renderForecastChart } from './modules/forecast_chart.js';

document.addEventListener('DOMContentLoaded', () => {
    const map = new MapEngine('leaflet-map', [41.4, 74.0]);

    // Переключение вкладок в интерфейсе
    const tabBtns = document.querySelectorAll('.tab-btn');
    tabBtns.forEach((btn, idx) => {
        btn.addEventListener('click', () => {
            tabBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            handleTabSwitch(idx);
        });
    });

    // Обработка формы запуска анализа
    const form = document.getElementById('analytics-form');
    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            await runSatelliteAnalysis(map);
        });
    }

    // Первоначальная загрузка базового прогноза
    runSatelliteAnalysis(map);
});

async function runSatelliteAnalysis(mapEngine) {
    const regionSelect = document.getElementById('region-select');
    const horizonSlider = document.getElementById('forecast-slider');

    const payload = {
        region: regionSelect ? regionSelect.value : 'naryn',
        forecast_days: horizonSlider ? parseInt(horizonSlider.value) : 90
    };

    try {
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
            document.getElementById('val-snow').textContent = `${data.metrics.current_snow_km2} км²`;
            document.getElementById('val-cover').textContent = `${data.metrics.predicted_melt_rate_percent}%`;

            renderForecastChart('plotly-forecast-chart', data.timeline, payload.region);
        }
    } catch (err) {
        console.error('Ошибка получения аналитики:', err);
    }
}

function handleTabSwitch(tabIndex) {
    const tabPane = document.getElementById('tab-ai-forecast');
    if (!tabPane) return;

    if (tabIndex === 1) {
        // Вкладка "Путь Капли"
        tabPane.innerHTML = `
            <div class="drop-journey-box">
                <h5>Гидрологический путь талой воды Тянь-Шаня</h5>
                <p>📍 <b>Ледник Петрова (4,300 м)</b> ➔ р. Нарын ➔ Токтогульское ГЭС ➔ Наманганские каналы ➔ Хлопковые поля (Фергана)</p>
                <div class="flow-step">Время добегания воды до оросительных каналов: <b>38 часов</b></div>
            </div>
        `;
    } else if (tabIndex === 3) {
        // Вкладка "Симулятор 'Что, если?'"
        tabPane.innerHTML = `
            <div class="simulator-box">
                <h5>Симулятор климатического отклонения</h5>
                <label>Аномалия температуры (°C):</label>
                <input type="range" id="temp-sim" min="+0.5" max="+4.0" step="0.5" value="+1.5">
                <span id="temp-val">+1.5 °C</span>
                <p class="mt-2">Прогнозируемый дефицит воды к августу: <span style="color:#EF4444; font-weight:bold;">-28.4%</span></p>
            </div>
        `;
        document.getElementById('temp-sim').addEventListener('input', (e) => {
            document.getElementById('temp-val').textContent = `${e.target.value} °C`;
        });
    }
}

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