import { t, getCurrentLang } from './i18n.js';

export function renderForecastChart(containerId, timelineData, regionTitle) {
    const el = document.getElementById(containerId);
    if (!el || !timelineData) return;

    const lang = getCurrentLang();
    const xDates = timelineData.map(item => item.date);
    const yValues = timelineData.map(item => item.predicted_snow_km2);

    const trace = {
        x: xDates,
        y: yValues,
        type: 'scatter',
        mode: 'lines+markers',
        fill: 'tozeroy',
        fillcolor: 'rgba(56, 189, 248, 0.12)',
        line: { color: '#38BDF8', width: 3 },
        marker: { size: 7, color: '#FC3D21', line: { color: '#FFF', width: 1 } }
    };

    const layout = {
        title: {
            text: `${t('chart_forecast_title', lang)} // ${regionTitle.toUpperCase()}`,
            font: { family: 'JetBrains Mono', color: '#E2E8F0', size: 13 }
        },
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(6, 11, 24, 0.5)',
        xaxis: { color: '#94A3B8', gridcolor: 'rgba(56, 189, 248, 0.08)' },
        yaxis: { title: t('chart_y_area', lang), color: '#94A3B8', gridcolor: 'rgba(56, 189, 248, 0.08)' },
        margin: { l: 55, r: 20, t: 42, b: 36 },
        height: 280
    };

    Plotly.newPlot(containerId, [trace], layout, { responsive: true, displayModeBar: false });
}

export function renderHistoryChart(containerId, historicalData, regionTitle) {
    const el = document.getElementById(containerId);
    if (!el || !historicalData) return;

    const lang = getCurrentLang();
    const trace = {
        x: historicalData.years,
        y: historicalData.snow_km2,
        type: 'bar',
        marker: {
            color: ['#0B3D91', '#0284C7', '#0EA5E9', '#38BDF8', '#F59E0B', '#FC3D21']
        }
    };

    const layout = {
        title: {
            text: `${t('chart_history_title', lang)} (${regionTitle.toUpperCase()})`,
            font: { family: 'JetBrains Mono', color: '#E2E8F0', size: 13 }
        },
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(6, 11, 24, 0.5)',
        xaxis: { color: '#94A3B8' },
        yaxis: { title: t('chart_y_peak', lang), color: '#94A3B8', gridcolor: 'rgba(56, 189, 248, 0.08)' },
        margin: { l: 55, r: 20, t: 42, b: 36 },
        height: 280
    };

    Plotly.newPlot(containerId, [trace], layout, { responsive: true, displayModeBar: false });
}