const editBtn    = document.getElementById('edit-btn');
const cancelBtn  = document.getElementById('cancel-edit');
const viewMode   = document.getElementById('view-mode');
const editForm   = document.getElementById('edit-form');

if (editBtn) {
    editBtn.addEventListener('click', () => {
        viewMode.classList.add('d-none');
        editForm.classList.remove('d-none');
    });
}

if (cancelBtn) {
    cancelBtn.addEventListener('click', () => {
        editForm.classList.add('d-none');
        viewMode.classList.remove('d-none');
    });
}
