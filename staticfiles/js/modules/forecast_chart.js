export function renderForecastChart(containerId, timelineData, regionName) {
    const xDates = timelineData.map(item => item.date);
    const yValues = timelineData.map(item => item.predicted_snow_km2);

    const trace = {
        x: xDates,
        y: yValues,
        type: 'scatter',
        mode: 'lines+markers',
        name: 'ML Прогноз (км²)',
        line: { color: '#38BDF8', width: 3 },
        marker: { size: 8, color: '#0284C7' }
    };

    const layout = {
        title: {
            text: `ИИ Прогноз площади снега: ${regionName || 'Ферганская долина'}`,
            font: { family: 'Space Grotesk', color: '#F8FAFC', size: 15 }
        },
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        xaxis: {
            title: 'Дата',
            color: '#94A3B8',
            gridcolor: 'rgba(56, 189, 248, 0.1)'
        },
        yaxis: {
            title: 'Площадь (км²)',
            color: '#94A3B8',
            gridcolor: 'rgba(56, 189, 248, 0.1)'
        },
        margin: { l: 40, r: 20, t: 40, b: 40 },
        height: 320
    };

    Plotly.newPlot(containerId, [trace], layout, { responsive: true, displayModeBar: false });
}