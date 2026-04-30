const locationSelect = document.getElementById('filter-location');
const dayCheckboxes = document.querySelectorAll('.day-filter');
const cardCols = document.querySelectorAll('.card-col');
const resultsCount = document.getElementById('results-count');
const noResults = document.getElementById('no-results');
const grid = document.getElementById('cards-grid');

function applyFilters() {
    const location = locationSelect ? locationSelect.value : '';
    const checkedDays = [...dayCheckboxes].filter(cb => cb.checked).map(cb => cb.value);
    let visible = 0;

    cardCols.forEach(col => {
        const colLocation = col.dataset.location || '';
        const colDays = col.dataset.days ? col.dataset.days.split(',') : [];

        const locationMatch = !location || colLocation === location;
        const dayMatch = checkedDays.length === 0 || checkedDays.some(d => colDays.includes(d));

        const show = locationMatch && dayMatch;
        col.style.display = show ? '' : 'none';
        if (show) visible++;
    });

    if (resultsCount) resultsCount.textContent = visible;
    if (noResults && grid && !window._sitbuddyMapMode) {
        noResults.classList.toggle('d-none', visible > 0);
        grid.classList.toggle('d-none', visible === 0);
    }
}

function clearFilters() {
    if (locationSelect) locationSelect.value = '';
    dayCheckboxes.forEach(cb => cb.checked = false);
    applyFilters();
}

if (locationSelect) locationSelect.addEventListener('change', applyFilters);
dayCheckboxes.forEach(cb => cb.addEventListener('change', applyFilters));

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

function initBrowseMap() {
    if (browseMap) { browseMap.invalidateSize(); return; }
    browseMap = L.map('map-view').setView([-31.95, 115.86], 12);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(browseMap);
    profiles.forEach(p => {
        if (p.lat == null || p.lng == null) return;
        const label = mode === 'babysitters'
            ? `<strong>${p.name}</strong><br>${p.suburb || p.location}<br>$${p.hourly_rate}/hr<br><a href="/babysitter/${p.id}">View Profile</a>`
            : `<strong>${p.name}</strong><br>${p.suburb || p.location}<br><a href="/parent/${p.id}">View Profile</a>`;
        L.marker([p.lat, p.lng]).addTo(browseMap).bindPopup(label);
    });
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
