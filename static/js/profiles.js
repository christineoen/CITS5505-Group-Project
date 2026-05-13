// Postcode / suburb autocomplete
const searchInput    = document.getElementById('location-search');
const dropdown       = document.getElementById('location-dropdown');
const suburbHidden   = document.getElementById('suburb');
const postcodeHidden = document.getElementById('postcode');
const latHidden      = document.getElementById('lat');
const lonHidden      = document.getElementById('lon');
const locationFeedback = document.getElementById('location-feedback');

let debounceTimer = null;
let activeIndex   = -1;

function showDropdown(results) {
    dropdown.innerHTML = '';
    if (!results.length) { dropdown.style.display = 'none'; return; }
    results.forEach(r => {
        const li = document.createElement('li');
        li.className = 'list-group-item list-group-item-action py-2';
        li.textContent = `${r.suburb} (${r.postcode})`;
        li.addEventListener('mousedown', e => { e.preventDefault(); selectResult(r); });
        dropdown.appendChild(li);
    });
    dropdown.style.display = 'block';
    activeIndex = -1;
}

function selectResult(r) {
    searchInput.value    = `${r.suburb} (${r.postcode})`;
    suburbHidden.value   = r.suburb;
    postcodeHidden.value = r.postcode;
    if (latHidden) latHidden.value = r.lat || '';
    if (lonHidden) lonHidden.value = r.lon || '';
    dropdown.style.display = 'none';
    showLocationFeedback(r);
}

function clearSelection() {
    suburbHidden.value   = '';
    postcodeHidden.value = '';
    if (latHidden) latHidden.value = '';
    if (lonHidden) lonHidden.value = '';
    if (locationFeedback) locationFeedback.innerHTML = '';
}

function showLocationFeedback(r) {
    if (!locationFeedback) return;
    const isWA = r.state === 'Western Australia';
    let html = `<span class="text-success">&#10003; ${r.suburb}, ${r.state || 'Australia'}</span>`;
    if (!isWA) {
        html += `<br><span class="text-warning">&#9888; This service is currently focused on the Perth area. Availability may be limited in your location.</span>`;
    }
    locationFeedback.innerHTML = html;
}

async function searchPostcode(q) {
    if (q.length < 2) { dropdown.style.display = 'none'; return; }
    try {
        const resp = await fetch(`/auth/postcode-search?q=${encodeURIComponent(q)}`);
        showDropdown(await resp.json());
    } catch (_) { dropdown.style.display = 'none'; }
}

if (searchInput) {
    searchInput.addEventListener('input', function () {
        clearSelection();
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => searchPostcode(this.value.trim()), 300);
    });

    searchInput.addEventListener('keydown', function (e) {
        const items = dropdown.querySelectorAll('.list-group-item');
        if (!items.length) return;
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            activeIndex = Math.min(activeIndex + 1, items.length - 1);
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            activeIndex = Math.max(activeIndex - 1, 0);
        } else if (e.key === 'Enter' && activeIndex >= 0) {
            e.preventDefault();
            items[activeIndex].dispatchEvent(new MouseEvent('mousedown'));
            return;
        } else if (e.key === 'Escape') {
            dropdown.style.display = 'none'; return;
        } else { return; }
        items.forEach((el, i) => el.classList.toggle('active', i === activeIndex));
    });

    document.addEventListener('click', e => {
        if (!searchInput.contains(e.target) && !dropdown.contains(e.target)) {
            dropdown.style.display = 'none';
        }
    });
}

// Profile edit/cancel toggle
const editBtn         = document.getElementById('edit-btn');
const cancelBtn       = document.getElementById('cancel-btn');
const viewMode        = document.getElementById('view-mode');
const editForm        = document.getElementById('edit-form');
const headerStatic    = document.getElementById('header-photo-static');
const headerEdit      = document.getElementById('header-photo-edit');
const reviewsSection  = document.getElementById('reviews-section');

if (editBtn) {
    editBtn.addEventListener('click', function () {
        viewMode.classList.add('d-none');
        editForm.classList.remove('d-none');
        if (headerStatic)   headerStatic.classList.add('d-none');
        if (headerEdit)     headerEdit.classList.remove('d-none');
        if (reviewsSection) reviewsSection.classList.add('d-none');
        editBtn.classList.add('d-none');
        if (cancelBtn) cancelBtn.classList.remove('d-none');
    });
}
if (cancelBtn) {
    cancelBtn.addEventListener('click', function () {
        editForm.classList.add('d-none');
        viewMode.classList.remove('d-none');
        if (headerStatic)   headerStatic.classList.remove('d-none');
        if (headerEdit)     headerEdit.classList.add('d-none');
        if (reviewsSection) reviewsSection.classList.remove('d-none');
        cancelBtn.classList.add('d-none');
        if (editBtn) editBtn.classList.remove('d-none');
    });
}

// Children dynamic form — parent setup only; no-ops silently on sitter page
const addBtn      = document.getElementById('add-child');
const childList   = document.getElementById('children-list');
const hiddenField = document.getElementById('children-json');

function serializeChildren() {
    const children = [];
    childList.querySelectorAll('.child-row').forEach(row => {
        const name = row.querySelector('.child-name').value.trim();
        const age  = parseInt(row.querySelector('.child-age').value, 10);
        children.push({ name: name || null, age: isNaN(age) ? null : age });
    });
    hiddenField.value = JSON.stringify(children);
}

function addChildRow(name, age) {
    const row = document.createElement('div');
    row.className = 'child-row d-flex gap-2 align-items-center';
    row.innerHTML = `
        <input type="text"   class="form-control child-name" placeholder="Name (optional)" value="${name || ''}">
        <input type="number" class="form-control child-age"  placeholder="Age" min="0" max="17" style="width:90px;" value="${age !== null && age !== undefined ? age : ''}">
        <button type="button" class="btn btn-outline-danger btn-sm remove-child" aria-label="Remove">✕</button>`;
    row.querySelector('.remove-child').addEventListener('click', () => { row.remove(); serializeChildren(); });
    row.querySelectorAll('input').forEach(el => el.addEventListener('input', serializeChildren));
    childList.appendChild(row);
    serializeChildren();
}

if (addBtn) {
    addBtn.addEventListener('click', () => addChildRow('', null));

    try {
        const seed = (typeof window._parentChildren !== 'undefined')
            ? window._parentChildren
            : JSON.parse(hiddenField.value || '[]');
        seed.forEach(c => addChildRow(c.name || '', c.age));
    } catch (_) {}

    document.querySelector('form').addEventListener('submit', serializeChildren);
}

// Photo upload preview — no-ops silently when widget is absent
const photoInput = document.getElementById('photo-input');
if (photoInput) {
    photoInput.addEventListener('change', function () {
        const file = this.files[0];
        if (!file) return;
        const preview = document.getElementById('photo-preview');
        const placeholder = document.getElementById('photo-placeholder');
        const reader = new FileReader();
        reader.onload = e => {
            preview.src = e.target.result;
            preview.classList.remove('d-none');
            if (placeholder) placeholder.classList.add('d-none');
        };
        reader.readAsDataURL(file);
    });
}
