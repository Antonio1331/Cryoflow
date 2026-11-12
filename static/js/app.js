import { MapEngine } from './modules/map_engine.js';
import { renderForecastChart, renderHistoryChart } from './modules/forecast_chart.js';
import { TRANSLATIONS, getCurrentLang, setCurrentLang, t } from './modules/i18n.js';

const FALLBACK_GEOMETRY = {
    naryn: {
        name: "Бассейн р. Нарын",
        coords: [[41.0, 73.5], [41.8, 76.0], [42.1, 78.2], [41.2, 77.5], [40.8, 75.0]],
        glacier: { name: "Ледник Петрова (4,300 м)", lat: 41.91, lon: 78.18 },
        flow_path: [[41.91, 78.18], [41.43, 75.99], [41.75, 72.85], [40.99, 71.67]]
    },
    syrdarya: {
        name: "Верховья Сырдарьи",
        coords: [[40.5, 70.8], [41.5, 72.5], [41.2, 74.0], [40.2, 72.0]],
        glacier: { name: "Ледник Абрамова (4,150 м)", lat: 39.63, lon: 71.56 },
        flow_path: [[39.63, 71.56], [40.38, 71.78], [40.85, 71.10], [40.52, 70.94]]
    },
    andijan: {
        name: "Андижанский речной бассейн",
        coords: [[40.4, 72.1], [41.1, 73.2], [40.9, 74.1], [40.3, 73.0]],
        glacier: { name: "Алайский хребет (3,980 м)", lat: 40.35, lon: 73.85 },
        flow_path: [[40.35, 73.85], [40.76, 73.05], [40.78, 72.34]]
    }
};

let lastApiData = null;

function setText(id, value) {
    const el = document.getElementById(id);
    if (el) el.textContent = value;
}

document.addEventListener('DOMContentLoaded', () => {
    const map = new MapEngine('leaflet-map', [41.2, 74.5]);

    // Сразу отрисовываем стартовый бассейн Нарын при загрузке страницы
    drawBasinOnMap(map, 'naryn', null);

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
        setText('utc-clock', `UTC ${now.toISOString().substring(11, 19)}`);
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

            if (targetId === 'pane-time-machine' && lastApiData?.historical) {
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

    // Смена бассейна сразу обновляет зону на карте и запускает анализ
    const regionSelect = document.getElementById('region-select');
    if (regionSelect) {
        regionSelect.addEventListener('change', () => {
            drawBasinOnMap(map, regionSelect.value, null);
            runSatelliteAnalysis(map);
        });
    }

    // Смена агрокультуры
    const farmingSelect = document.getElementById('farming-select');
    if (farmingSelect) {
        farmingSelect.addEventListener('change', () => updateFarmingFact(getCurrentLang()));
    }

    // Симулятор "Что, если?"
    const tempSim = document.getElementById('temp-sim');
    const precipSim = document.getElementById('precip-sim');
    const updateSimulator = () => {
        if (!tempSim || !precipSim) return;
        const tVal = parseFloat(tempSim.value);
        const pVal = parseInt(precipSim.value, 10);
        setText('temp-val', `+${tVal.toFixed(1)} °C`);
        setText('precip-val', `${pVal > 0 ? '+' : ''}${pVal}%`);

        const deficit = Math.min(0, Math.round((-tVal * 11.5 + pVal * 0.65) * 10) / 10);
        setText('sim-deficit', `${deficit}%`);
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

    // Экспорт телеметрии в CSV
    const exportBtn = document.getElementById('btn-export-csv');
    if (exportBtn) {
        exportBtn.addEventListener('click', () => {
            if (!lastApiData) return;
            const basinTitle = lastApiData.basin?.name || getLocalizedBasinName();
            const rows = [
                ['Basin', 'Forecast_Date', 'Predicted_Snow_km2', 'Melt_Rate_Percent', 'Risk_Level'],
                ...(lastApiData.timeline || []).map(pt => [
                    basinTitle,
                    pt.date,
                    pt.predicted_snow_km2,
                    lastApiData.metrics?.predicted_melt_rate_percent ?? '',
                    lastApiData.metrics?.risk_level ?? ''
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

    runSatelliteAnalysis(map);
});

function drawBasinOnMap(mapEngine, regionCode, apiBasin) {
    const basinData = (apiBasin && Array.isArray(apiBasin.coords))
        ? apiBasin
        : (FALLBACK_GEOMETRY[regionCode] || FALLBACK_GEOMETRY.naryn);

    if (basinData.glacier) {
        setText('journey-glacier', basinData.glacier.name);
    }

    if (typeof mapEngine.renderBasinTelemetry === 'function') {
        mapEngine.renderBasinTelemetry(basinData);
    } else if (typeof mapEngine.renderRegion === 'function') {
        mapEngine.renderRegion(basinData.coords);
    }
}

function getLocalizedBasinName() {
    const regionSelect = document.getElementById('region-select');
    if (!regionSelect) return 'Naryn';
    return regionSelect.options[regionSelect.selectedIndex].textContent;
}

function updateHorizonBadge(lang) {
    const slider = document.getElementById('forecast-slider');
    if (slider) {
        setText('horizon-val', `${slider.value} ${t('days_unit', lang)}`);
    }
}

function updateFarmingFact(lang) {
    const farmingSelect = document.getElementById('farming-select');
    if (farmingSelect) {
        const dict = TRANSLATIONS[lang] || TRANSLATIONS.ru;
        setText('farming-fact', dict.facts[farmingSelect.value] || dict.facts.cotton);
    }
}

function updateDynamicTexts(lang) {
    updateHorizonBadge(lang);
    updateFarmingFact(lang);

    if (!lastApiData) return;

    const dict = TRANSLATIONS[lang] || TRANSLATIONS.ru;
    const basinName = getLocalizedBasinName();

    setText('map-basin-badge', `${t('basin_prefix', lang)}: ${basinName.toUpperCase()}`);
    setText('journey-river', basinName);

    if (lastApiData.metrics) {
        const rawTrend = lastApiData.metrics.trend_label;
        setText('val-trend', dict.trends[rawTrend] || rawTrend);
        setText('val-rate', `${lastApiData.metrics.predicted_melt_rate_percent}${t('rate_unit', lang)}`);
    }

    if (lastApiData.timeline) {
        renderForecastChart('plotly-forecast-chart', lastApiData.timeline, basinName);
    }
    if (lastApiData.historical) {
        renderHistoryChart('plotly-history-chart', lastApiData.historical, basinName);
    }
}

async function runSatelliteAnalysis(mapEngine) {
    const regionSelect = document.getElementById('region-select');
    const horizonSlider = document.getElementById('forecast-slider');
    const dateStartEl = document.getElementById('date_start');
    const dateEndEl = document.getElementById('date_end');
    const lang = getCurrentLang();
    const regionCode = regionSelect ? regionSelect.value : 'naryn';

    const payload = {
        region: regionCode,
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

            // 1. Отрисовка зон на карте
            drawBasinOnMap(mapEngine, regionCode, data.basin);

            // 2. Счетчик гранул NASA CMR
            if (data.nasa_telemetry) {
                const count = data.nasa_telemetry.total_found ?? 0;
                const latest = data.nasa_telemetry.granules?.[0];
                setText('val-granules', latest ? `${count} ГРАНУЛ (${latest.date})` : data.nasa_telemetry.source);
            }

            // 3. Основные метрики
            if (data.metrics) {
                setText('val-snow', `${data.metrics.current_snow_km2} км²`);
                setText('val-cover', `${data.metrics.cover_percentage}%`);

                const riskBadge = document.getElementById('risk-badge');
                if (riskBadge) {
                    riskBadge.textContent = data.metrics.risk_level;
                    riskBadge.classList.toggle('high', data.metrics.risk_level === 'HIGH RISK');
                }
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