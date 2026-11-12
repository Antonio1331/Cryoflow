export class MapEngine {
    constructor(elementId, initialCoords) {
        this.map = L.map(elementId, {
            center: initialCoords,
            zoom: 7,
            zoomControl: true
        });

        L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
            maxZoom: 18,
            attribution: 'NASA / Esri Orbital Imagery'
        }).addTo(this.map);

        this.overlayLayer = L.layerGroup().addTo(this.map);
    }

    renderBasinTelemetry(basinData) {
        this.overlayLayer.clearLayers();
        if (!basinData || !basinData.coords) return;

        // Контур водосборного бассейна
        const polygon = L.polygon(basinData.coords, {
            color: '#38BDF8',
            fillColor: '#0EA5E9',
            fillOpacity: 0.22,
            weight: 2
        }).addTo(this.overlayLayer);

        // Траектория движения талой воды (Путь капли)
        if (basinData.flow_path) {
            L.polyline(basinData.flow_path, {
                color: '#FC3D21',
                weight: 3,
                dashArray: '6, 6'
            }).addTo(this.overlayLayer);
        }

        // Маркер ледника с векторной SVG-иконкой
        if (basinData.glacier) {
            const glacierIcon = L.divIcon({
                className: 'nasa-glacier-pin',
                html: `<svg width="24" height="24" viewBox="0 0 24 24" fill="#0B3D91" stroke="#38BDF8" stroke-width="2">
                        <polygon points="12 2 22 20 2 20"/>
                       </svg>`,
                iconSize: [24, 24],
                iconAnchor: [12, 12]
            });

            L.marker([basinData.glacier.lat, basinData.glacier.lon], { icon: glacierIcon })
                .bindPopup(`<b>${basinData.glacier.name}</b><br>Источник питания: ${basinData.name}`)
                .addTo(this.overlayLayer);
        }

        this.map.fitBounds(polygon.getBounds(), { padding: [25, 25] });
    }
}