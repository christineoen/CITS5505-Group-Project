const mapEl = document.getElementById('profile-map');

if (mapEl) {
    const lat = parseFloat(mapEl.dataset.lat);
    const lng = parseFloat(mapEl.dataset.lng);

    if (!isNaN(lat) && !isNaN(lng)) {
        const profileMap = L.map('profile-map').setView([lat, lng], 14);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(profileMap);
        L.marker([lat, lng]).addTo(profileMap);
    }
}
