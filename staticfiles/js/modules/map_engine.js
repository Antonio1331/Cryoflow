export class MapEngine {
    constructor(elementId, initialCoords) {
        this.map = L.map(elementId, {
            center: initialCoords,
            zoom: 8,
            zoomControl: false
        });

        // NASA Dark Matter Map Style
        L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
            maxZoom: 19,
            subdomains: 'abcd'
        }).addTo(this.map);

        this.polygonLayer = L.layerGroup().addTo(this.map);
    }

    renderRegion(coordinates) {
        this.polygonLayer.clearLayers();
        const polygon = L.polygon(coordinates, {
            color: '#38BDF8',
            fillColor: '#0EA5E9',
            fillOpacity: 0.25,
            weight: 2
        });
        polygon.addTo(this.polygonLayer);
        this.map.fitBounds(polygon.getBounds());
    }
}