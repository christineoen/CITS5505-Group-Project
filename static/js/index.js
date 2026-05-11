const distanceSelect = document.getElementById('filter-distance');
const dayBtns = document.querySelectorAll('.day-filter-btn');
const cardCols = document.querySelectorAll('.card-col');
const resultsCount = document.getElementById('results-count');
const noResults = document.getElementById('no-results');
const grid = document.getElementById('cards-grid');

const userLat = window._userLat || null;
const userLng = window._userLng || null;

function haversineKm(lat1, lng1, lat2, lng2) {
    const R = 6371;
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLng = (lng2 - lng1) * Math.PI / 180;
    const a = Math.sin(dLat / 2) ** 2 +
        Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * Math.sin(dLng / 2) ** 2;
    return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}

const KM_PER_MILE = 1.609;

function applyFilters() {
    const activeDays = [...dayBtns].filter(btn => btn.classList.contains('active')).map(btn => btn.dataset.day);
    const distanceMiles = distanceSelect ? parseFloat(distanceSelect.value) || 0 : 0;
    let visible = 0;

    cardCols.forEach(col => {
        const colDays = col.dataset.days ? col.dataset.days.split(',') : [];
        const colLat = parseFloat(col.dataset.lat);
        const colLng = parseFloat(col.dataset.lng);

        const dayMatch = activeDays.length === 0 || activeDays.some(d => colDays.includes(d));

        let distanceMatch = true;
        if (distanceMiles && userLat && userLng && !isNaN(colLat) && !isNaN(colLng)) {
            const distKm = haversineKm(userLat, userLng, colLat, colLng);
            distanceMatch = distKm <= distanceMiles * KM_PER_MILE;
        }

        const show = dayMatch && distanceMatch;
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
    if (distanceSelect) distanceSelect.value = '';
    dayBtns.forEach(btn => btn.classList.remove('active'));
    applyFilters();
}

dayBtns.forEach(btn => btn.addEventListener('click', function () {
    this.classList.toggle('active');
    applyFilters();
}));
if (distanceSelect) distanceSelect.addEventListener('change', applyFilters);

const clearBtn = document.getElementById('clear-filters');
const clearBtnEmpty = document.getElementById('clear-filters-empty');
if (clearBtn) clearBtn.addEventListener('click', clearFilters);
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
    const activeDays = [...dayBtns].filter(btn => btn.classList.contains('active')).map(btn => btn.dataset.day);
    const distanceMiles = distanceSelect ? parseFloat(distanceSelect.value) || 0 : 0;

    mapMarkers.forEach(({ marker, profile: p }) => {
        const dayMatch = activeDays.length === 0 || activeDays.some(d => p.days.includes(d));

        let distanceMatch = true;
        if (distanceMiles && userLat && userLng && p.lat != null && p.lng != null) {
            const distKm = haversineKm(userLat, userLng, p.lat, p.lng);
            distanceMatch = distKm <= distanceMiles * KM_PER_MILE;
        }

        if (dayMatch && distanceMatch) {
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
    btnMap.classList.replace('btn-outline-secondary', 'btn-primary');
    btnList.classList.replace('btn-primary', 'btn-outline-secondary');
    initBrowseMap();
});

if (btnList) btnList.addEventListener('click', function () {
    window._sitbuddyMapMode = false;
    mapView.classList.add('d-none');
    grid.classList.remove('d-none');
    btnList.classList.replace('btn-outline-secondary', 'btn-primary');
    btnMap.classList.replace('btn-primary', 'btn-outline-secondary');
});
