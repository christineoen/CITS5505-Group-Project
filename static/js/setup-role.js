const cards       = document.querySelectorAll('.role-card');
const roleInput   = document.getElementById('selected-role');
const continueBtn = document.getElementById('continue-btn');

function selectCard(role) {
    cards.forEach(c => c.classList.toggle('selected', c.dataset.role === role));
    roleInput.value = role;
    continueBtn.disabled = false;
}

cards.forEach(card => card.addEventListener('click', () => selectCard(card.dataset.role)));

// Restore previously selected card (e.g. browser back from step 2)
if (roleInput.value) selectCard(roleInput.value);
