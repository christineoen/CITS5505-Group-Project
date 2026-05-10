const radiusSelect = document.getElementById('filter-radius');
const dayPills = document.querySelectorAll('.day-filter-pill');
const cardCols = document.querySelectorAll('.card-col');
const resultsCount = document.getElementById('results-count');
const noResults = document.getElementById('no-results');
const grid = document.getElementById('cards-grid');

function haversineMiles(lat1, lng1, lat2, lng2) {
    const R = 3959;
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLng = (lng2 - lng1) * Math.PI / 180;
    const a = Math.sin(dLat / 2) ** 2 +
        Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
        Math.sin(dLng / 2) ** 2;
    return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}

function applyFilters() {
    const radius = radiusSelect ? parseFloat(radiusSelect.value) : NaN;
    const activeDays = [...dayPills].filter(p => p.classList.contains('active')).map(p => p.dataset.day);
    const userLat = window._userLat;
    const userLng = window._userLng;
    let visible = 0;

    cardCols.forEach(col => {
        const colLat = parseFloat(col.dataset.lat);
        const colLng = parseFloat(col.dataset.lng);
        const colDays = col.dataset.days ? col.dataset.days.split(',') : [];

        const dayMatch = activeDays.length === 0 || activeDays.some(d => colDays.includes(d));

        let radiusMatch = true;
        if (radius && userLat != null && userLng != null && !isNaN(colLat) && !isNaN(colLng)) {
            radiusMatch = haversineMiles(userLat, userLng, colLat, colLng) <= radius;
        }

        const show = dayMatch && radiusMatch;
        col.style.display = show ? '' : 'none';
        if (show) visible++;
    });

    if (resultsCount) resultsCount.textContent = visible;
    if (noResults && grid && !window._sitbuddyMapMode) {
        noResults.classList.toggle('d-none', visible > 0);
        grid.classList.toggle('d-none', visible === 0);
    }
    applyMapFilters();
}

function clearFilters() {
    if (radiusSelect) radiusSelect.value = '20';
    dayPills.forEach(p => p.classList.remove('active'));
    applyFilters();
}

if (radiusSelect) radiusSelect.addEventListener('change', applyFilters);
dayPills.forEach(pill => pill.addEventListener('click', () => {
    pill.classList.toggle('active');
    applyFilters();
}));

const clearBtnEmpty = document.getElementById('clear-filters-empty');
if (clearBtnEmpty) clearBtnEmpty.addEventListener('click', clearFilters);

// Browse map toggle
window._sitbuddyMapMode = false;
const profiles = window._sitbuddyProfiles || [];
const mode     = window._sitbuddyMode || '';
const mapView  = document.getElementById('map-view');
const btnList  = document.getElementById('btn-list');
const btnMap   = document.getElementById('btn-map');

let browseMap = null;
let mapMarkers = [];

function applyMapFilters() {
    if (!browseMap) return;
    const radius = radiusSelect ? parseFloat(radiusSelect.value) : NaN;
    const activeDays = [...dayPills].filter(p => p.classList.contains('active')).map(p => p.dataset.day);
    const userLat = window._userLat;
    const userLng = window._userLng;

    mapMarkers.forEach(({ marker, profile: p }) => {
        const dayMatch = activeDays.length === 0 || activeDays.some(d => p.days.includes(d));
        let radiusMatch = true;
        if (radius && userLat != null && userLng != null && p.lat != null && p.lng != null) {
            radiusMatch = haversineMiles(userLat, userLng, p.lat, p.lng) <= radius;
        }
        if (dayMatch && radiusMatch) {
            marker.addTo(browseMap);
        } else {
            marker.remove();
        }
    });
}

function initBrowseMap() {
    if (browseMap) { browseMap.invalidateSize(); applyMapFilters(); return; }
    browseMap = L.map('map-view').setView([-31.95, 115.86], 12);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(browseMap);
    profiles.forEach(p => {
        if (p.lat == null || p.lng == null) return;
        const label = mode === 'babysitters'
            ? `<strong>${p.name}</strong><br>${p.suburb || p.location}<br>$${p.hourly_rate}/hr<br><a href="/babysitter/${p.id}">View Profile</a>`
            : `<strong>${p.name}</strong><br>${p.suburb || p.location}<br><a href="/parent/${p.id}">View Profile</a>`;
        const marker = L.marker([p.lat, p.lng]).addTo(browseMap).bindPopup(label);
        mapMarkers.push({ marker, profile: p });
    });
    applyMapFilters();
}

if (btnMap) btnMap.addEventListener('click', function () {
    window._sitbuddyMapMode = true;
    mapView.classList.remove('d-none');
    grid.classList.add('d-none');
    if (noResults) noResults.classList.add('d-none');
    btnMap.classList.add('active');
    btnList.classList.remove('active');
    initBrowseMap();
});

if (btnList) btnList.addEventListener('click', function () {
    window._sitbuddyMapMode = false;
    mapView.classList.add('d-none');
    grid.classList.remove('d-none');
    btnList.classList.add('active');
    btnMap.classList.remove('active');
});
