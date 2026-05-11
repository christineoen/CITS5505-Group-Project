const rateModal = document.getElementById('rateModal');
if (rateModal) {
    rateModal.addEventListener('show.bs.modal', function(event) {
        const btn = event.relatedTarget;
        const bookingId = btn.getAttribute('data-booking-id');
        const rateeName = btn.getAttribute('data-ratee-name');
        document.getElementById('rating-form').action = `/bookings/${bookingId}/rate`;
        document.getElementById('ratee-name-display').textContent = rateeName;
        document.querySelectorAll('input[name="score"]').forEach(r => r.checked = false);
        document.getElementById('rating-comment').value = '';
        document.getElementById('char-count').textContent = '0';
        document.getElementById('star-label-text').textContent = 'Select a rating';
        updateStars(0);
    });
}

const starLabels = ['', 'Poor', 'Fair', 'Good', 'Very Good', 'Excellent'];

function updateStars(score) {
    document.querySelectorAll('.star-label').forEach((label, idx) => {
        label.style.color = idx < score ? '#f59e0b' : '#d1d5db';
    });
}

document.querySelectorAll('input[name="score"]').forEach(radio => {
    radio.addEventListener('change', function() {
        const score = parseInt(this.value);
        updateStars(score);
        document.getElementById('star-label-text').textContent = starLabels[score];
    });
});

document.querySelectorAll('.star-label').forEach((label, idx) => {
    label.addEventListener('mouseenter', () => updateStars(idx + 1));
    label.addEventListener('mouseleave', () => {
        const checked = document.querySelector('input[name="score"]:checked');
        updateStars(checked ? parseInt(checked.value) : 0);
    });
});

const commentArea = document.getElementById('rating-comment');
if (commentArea) {
    commentArea.addEventListener('input', function() {
        document.getElementById('char-count').textContent = this.value.length;
    });
}
