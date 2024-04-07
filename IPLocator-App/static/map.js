

document.addEventListener('DOMContentLoaded', function () {

    var map = L.map('map').setView([latitude, longitude], 6);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    //'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png'
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    var marker = L.marker([latitude, longitude], {
        icon: L.icon({
            iconUrl: 'https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
            shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
            iconSize: [20, 31],
            iconAnchor: [12, 41],
            popupAnchor: [1, -34],
            shadowSize: [31, 31]
        })
    }).addTo(map);

    var marker2 = L.marker([lat, long], {
        icon: L.icon({
            iconUrl: 'https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
            shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
            iconSize: [20, 31],
            iconAnchor: [12, 41],
            popupAnchor: [1, -34],
            shadowSize: [31, 31]
        })
    }).addTo(map);

    var panorama = L.panorama().addTo(map);
    panorama.setPosition([latitude, longitude]);
    map.on('click', function(e) {
        panorama.setPosition(e.latlng);
    });
});
