document.addEventListener("DOMContentLoaded", async function () {

    const mapEl = document.getElementById("map");
    const lookupEl = document.getElementById("lookup-value");

    if (!mapEl || !lookupEl) return;

    const baseIconOptions = {
        shadowUrl: "/static/images/marker-shadow.png",
        iconSize: [20, 31],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [31, 31]
    };

    const icons = {
        company: L.icon({
            ...baseIconOptions,
            iconUrl: "/static/images/marker-icon-2x-orange.png"
        }),
        az: L.icon({
            ...baseIconOptions,
            iconUrl: "/static/images/marker-icon-2x-blue.png"
        }),
        dc: L.icon({
            ...baseIconOptions,
            iconUrl: "/static/images/marker-icon-2x-red.png"
        })
    };

    try {
        const response = await fetch("/api/ip-info", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                ip_or_url: lookupEl.value
            })
        });

        if (!response.ok) throw new Error("API error");

        const data = await response.json();

        const toNum = v => Number.isFinite(+v) ? +v : null;

        const dcLat = toNum(data.dc_latitude);
        const dcLng = toNum(data.dc_longitude);

        const map = (dcLat && dcLng)
            ? L.map("map").setView([dcLat, dcLng], 6)
            : L.map("map").setView([0, 0], 2);

        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
            attribution: "&copy; OpenStreetMap contributors"
        }).addTo(map);

        if (toNum(data.company_latitude) && toNum(data.company_longitude)) {
            L.marker(
                [data.company_latitude + 0.01, data.company_longitude],
                { icon: icons.company }
            )
                .addTo(map)
                .bindTooltip("company");
        }

        if (toNum(data.az_latitude) && toNum(data.az_longitude)) {
            L.marker(
                [data.az_latitude - 0.01, data.az_longitude - 0.01],
                { icon: icons.az }
            )
                .addTo(map)
                .bindTooltip("availability zone");
        }

        if (dcLat && dcLng) {
            L.marker(
                [dcLat, dcLng],
                { icon: icons.dc }
            )
                .addTo(map)
                .bindTooltip("datacenter");
        }

    } catch (err) {
        console.error("Map error:", err);
    }
});
