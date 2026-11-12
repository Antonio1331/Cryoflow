import { MapEngine } from './modules/map_engine.js';
import { renderForecastChart, renderHistoryChart } from './modules/forecast_chart.js';
import { TRANSLATIONS, getCurrentLang, setCurrentLang, t } from './modules/i18n.js';

let lastApiData = null;

document.addEventListener('DOMContentLoaded', () => {
    const map = new MapEngine('leaflet-map', [41.2, 74.5]);

    // Инициализация сохранённого языка
    const langSelect = document.getElementById('lang-select');
    const savedLang = getCurrentLang();
    if (langSelect) {
        langSelect.value = savedLang;
        langSelect.addEventListener('change', (e) => {
            const newLang = setCurrentLang(e.target.value);
            updateDynamicTexts(newLang);
        });
    }
    setCurrentLang(savedLang);

    // UTC часы
    setInterval(() => {
        const now = new Date();
        const clockEl = document.getElementById('utc-clock');
        if (clockEl) clockEl.textContent = `UTC ${now.toISOString().substring(11, 19)}`;
    }, 1000);

    // Переключение вкладок
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            tabBtns.forEach(b => b.classList.remove('active'));
            tabPanes.forEach(p => p.classList.remove('active'));

            btn.classList.add('active');
            const targetId = btn.getAttribute('data-target');
            const targetPane = document.getElementById(targetId);
            if (targetPane) targetPane.classList.add('active');

            if (targetId === 'pane-time-machine' && lastApiData) {
                renderHistoryChart('plotly-history-chart', lastApiData.historical, getLocalizedBasinName());
            }
        });
    });

    // Слайдер ML-прогноза
    const forecastSlider = document.getElementById('forecast-slider');
    if (forecastSlider) {
        forecastSlider.addEventListener('input', () => {
            updateHorizonBadge(getCurrentLang());
        });
        forecastSlider.addEventListener('change', () => runSatelliteAnalysis(map));
    }

    // Смена агрокультуры
    const farmingSelect = document.getElementById('farming-select');
    if (farmingSelect) {
        farmingSelect.addEventListener('change', () => updateFarmingFact(getCurrentLang()));
    }

    // Симулятор
    const tempSim = document.getElementById('temp-sim');
    const precipSim = document.getElementById('precip-sim');
    const updateSimulator = () => {
        if (!tempSim || !precipSim) return;
        const tVal = parseFloat(tempSim.value);
        const pVal = parseInt(precipSim.value, 10);
        document.getElementById('temp-val').textContent = `+${tVal.toFixed(1)} °C`;
        document.getElementById('precip-val').textContent = `${pVal > 0 ? '+' : ''}${pVal}%`;

        const deficit = Math.min(0, Math.round((-tVal * 11.5 + pVal * 0.65) * 10) / 10);
        document.getElementById('sim-deficit').textContent = `${deficit}%`;
    };
    if (tempSim && precipSim) {
        tempSim.addEventListener('input', updateSimulator);
        precipSim.addEventListener('input', updateSimulator);
    }

    // Отправка формы
    const form = document.getElementById('analytics-form');
    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            await runSatelliteAnalysis(map);
        });
    }

    // ---> ВСТАВЛЯТЬ СЮДА (Экспорт телеметрии в CSV) <---
    const exportBtn = document.getElementById('btn-export-csv');
    if (exportBtn) {
        exportBtn.addEventListener('click', () => {
            if (!lastApiData) return;
            const rows = [
                ['Basin', 'Forecast_Date', 'Predicted_Snow_km2', 'Melt_Rate_Percent', 'Risk_Level'],
                ...lastApiData.timeline.map(pt => [
                    lastApiData.basin.name,
                    pt.date,
                    pt.predicted_snow_km2,
                    lastApiData.metrics.predicted_melt_rate_percent,
                    lastApiData.metrics.risk_level
                ])
            ];
            const csvContent = '\uFEFF' + rows.map(r => r.join(';')).join('\n');
            const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = `cryoflow_telemetry_${new Date().toISOString().slice(0, 10)}.csv`;
            link.click();
            URL.revokeObjectURL(url);
        });
    }
    // ---> КОНЕЦ ВСТАВКИ <---

    runSatelliteAnalysis(map);
});
function getLocalizedBasinName() {
    const regionSelect = document.getElementById('region-select');
    if (!regionSelect) return 'Naryn';
    return regionSelect.options[regionSelect.selectedIndex].textContent;
}

function updateHorizonBadge(lang) {
    const slider = document.getElementById('forecast-slider');
    const badge = document.getElementById('horizon-val');
    if (slider && badge) {
        badge.textContent = `${slider.value} ${t('days_unit', lang)}`;
    }
}

function updateFarmingFact(lang) {
    const farmingSelect = document.getElementById('farming-select');
    const factEl = document.getElementById('farming-fact');
    if (farmingSelect && factEl) {
        const dict = TRANSLATIONS[lang] || TRANSLATIONS.ru;
        factEl.textContent = dict.facts[farmingSelect.value] || dict.facts.cotton;
    }
}

function updateDynamicTexts(lang) {
    updateHorizonBadge(lang);
    updateFarmingFact(lang);

    if (!lastApiData) return;

    const dict = TRANSLATIONS[lang] || TRANSLATIONS.ru;
    const basinName = getLocalizedBasinName();

    document.getElementById('map-basin-badge').textContent = `${t('basin_prefix', lang)}: ${basinName.toUpperCase()}`;
    document.getElementById('journey-river').textContent = basinName;

    const rawTrend = lastApiData.metrics.trend_label;
    document.getElementById('val-trend').textContent = dict.trends[rawTrend] || rawTrend;
    document.getElementById('val-rate').textContent = `${lastApiData.metrics.predicted_melt_rate_percent}${t('rate_unit', lang)}`;

    renderForecastChart('plotly-forecast-chart', lastApiData.timeline, basinName);
    renderHistoryChart('plotly-history-chart', lastApiData.historical, basinName);
}

async function runSatelliteAnalysis(mapEngine) {
    const regionSelect = document.getElementById('region-select');
    const horizonSlider = document.getElementById('forecast-slider');
    const dateStartEl = document.getElementById('date_start');
    const dateEndEl = document.getElementById('date_end');
    const lang = getCurrentLang();

    const payload = {
        region: regionSelect ? regionSelect.value : 'naryn',
        forecast_days: horizonSlider ? parseInt(horizonSlider.value, 10) : 90,
        date_start: dateStartEl ? dateStartEl.value : '2026-05-01',
        date_end: dateEndEl ? dateEndEl.value : '2026-06-01'
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
            lastApiData = data;

            // 1. Обновление счетчика гранул NASA CMR
            const granulesEl = document.getElementById('val-granules');
            if (granulesEl && data.nasa_telemetry) {
                const count = data.nasa_telemetry.total_found ?? 0;
                const latest = data.nasa_telemetry.granules?.[0];
                granulesEl.textContent = latest
                    ? `${count} ГРАНУЛ (${latest.date})`
                    : `${data.nasa_telemetry.source}`;
            }

            // 2. Обновление основных метрик
            document.getElementById('val-snow').textContent = `${data.metrics.current_snow_km2} км²`;
            document.getElementById('val-cover').textContent = `${data.metrics.cover_percentage}%`;

            const riskBadge = document.getElementById('risk-badge');
            if (riskBadge) {
                riskBadge.textContent = data.metrics.risk_level;
                riskBadge.classList.toggle('high', data.metrics.risk_level === 'HIGH RISK');
            }

            // 3. Обновление карты и маршрута ледника
            if (data.basin) {
                document.getElementById('journey-glacier').textContent = data.basin.glacier.name;
                mapEngine.renderBasinTelemetry(data.basin);
            }

            // 4. Перерисовка графиков и переводов
            updateDynamicTexts(lang);
        }
    } catch (err) {
        console.error('Ошибка телеметрии:', err);
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