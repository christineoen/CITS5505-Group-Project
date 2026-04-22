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
    if (noResults && grid) {
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
