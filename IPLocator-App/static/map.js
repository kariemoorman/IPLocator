

document.addEventListener('DOMContentLoaded', function () {
    // Check if coordinates are present & render local-specific map
    if (dc_latitude !== undefined && dc_longitude !== undefined) {
        var map = L.map('map').setView([dc_latitude, dc_longitude], 6);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(map);
    } else {
        // Create a generic map without specific coordinates
        var map = L.map('map').setView([0, 0], 2); // Set a default view
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(map);
    }
    // Check if coordinates are present & render marker
    if (company_latitude !== undefined && company_longitude !== undefined) {
        var marker1 = L.marker([company_latitude, company_longitude], {
            icon: L.icon({
                iconUrl: 'https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png',
                shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
                iconSize: [20, 31],
                iconAnchor: [12, 41],
                popupAnchor: [1, -34],
                shadowSize: [31, 31]
            })
        }).addTo(map);
        marker1.bindTooltip("company", { permanent: false, direction: 'top', offset: [0, -30] }).openTooltip();
    }
    // Check if coordinates are present & render marker
    if (az_latitude !== undefined && az_longitude !== undefined) {
        var marker2 = L.marker([az_latitude, az_longitude], {
            icon: L.icon({
                iconUrl: 'https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-orange.png',
                shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
                iconSize: [20, 31],
                iconAnchor: [12, 41],
                popupAnchor: [1, -34],
                shadowSize: [31, 31]
            })
        }).addTo(map);
        marker2.bindTooltip("availability zone", { permanent: false, direction: 'top', offset: [0, -30] }).openTooltip();
    }
    // Check if coordinates are present & render marker
    if (dc_latitude !== undefined && dc_longitude !== undefined) {
        var marker3 = L.marker([dc_latitude, dc_longitude], {
            icon: L.icon({
                iconUrl: 'https://cdn.rawgit.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
                shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
                iconSize: [20, 31],
                iconAnchor: [12, 41],
                popupAnchor: [1, -34],
                shadowSize: [31, 31]
            })
        }).addTo(map);
        marker3.bindTooltip("datacenter", { permanent: false, direction: 'top', offset: [0, -30] }).openTooltip();


        var panorama = L.panorama().addTo(map);
        panorama.setPosition([dc_latitude, dc_longitude]);
        map.on('click', function(e) {
            panorama.setPosition(e.latlng);
        });
    }
});
