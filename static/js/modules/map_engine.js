export class MapEngine {
    constructor(elementId, initialCoords) {
        this.map = L.map(elementId, {
            center: initialCoords,
            zoom: 8,
            zoomControl: true
        });

        // Бесплатная спутниковая карта Esri (не требует API-ключа)
        L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
            maxZoom: 19,
            attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
        }).addTo(this.map);

        this.polygonLayer = L.layerGroup().addTo(this.map);
    }

    renderRegion(coordinates) {
        this.polygonLayer.clearLayers();
        const polygon = L.polygon(coordinates, {
            color: '#38BDF8',
            fillColor: '#0EA5E9',
            fillOpacity: 0.3,
            weight: 25
        });
        polygon.addTo(this.polygonLayer);
        this.map.fitBounds(polygon.getBounds());
    }
}