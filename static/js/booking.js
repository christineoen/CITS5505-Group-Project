(() => {
  "use strict";

  const startTimeInput = document.getElementById("start_time");
  const durationInput = document.getElementById("duration_hours");
  const startTimeError = document.getElementById("start-time-error");
  const durationError = document.getElementById("duration-error");
  const form = document.getElementById("booking-form");

  function validateStartTime() {
    if (!startTimeInput.value) return true; // let server handle required
    const [hours, minutes] = startTimeInput.value.split(":").map(Number);
    const totalMinutes = hours * 60 + (minutes || 0);
    const valid = totalMinutes >= 6 * 60 && totalMinutes <= 22 * 60;
    startTimeError.classList.toggle("d-none", valid);
    startTimeInput.classList.toggle("is-invalid", !valid);
    return valid;
  }

  function validateDuration() {
    const val = parseInt(durationInput.value, 10);
    const valid = !isNaN(val) && val >= 1 && val <= 12;
    durationError.classList.toggle("d-none", valid || durationInput.value === "");
    durationInput.classList.toggle("is-invalid", !valid && durationInput.value !== "");
    return valid || durationInput.value === "";
  }

  startTimeInput.addEventListener("change", validateStartTime);
  startTimeInput.addEventListener("input", validateStartTime);
  durationInput.addEventListener("input", validateDuration);
  durationInput.addEventListener("change", validateDuration);

  form.addEventListener("submit", (e) => {
    const timeOk = validateStartTime();
    const durOk = validateDuration();
    if (!timeOk || !durOk) {
      e.preventDefault();
    }
  });
})();
