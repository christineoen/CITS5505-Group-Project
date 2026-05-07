(() => {
  "use strict";

  const dateInput = document.getElementById("booking-date");
  const startTimeInput = document.getElementById("start_time");
  const durationInput = document.getElementById("duration_hours");
  const startTimeError = document.getElementById("start-time-error");
  const durationError = document.getElementById("duration-error");
  const form = document.getElementById("booking-form");

  // Map day names to JavaScript day numbers (0=Sunday, 1=Monday, etc.)
  // Supports both full names ("Monday") and abbreviations ("Mon")
  const dayNameToNumber = {
    "Sun": 0, "Sunday": 0,
    "Mon": 1, "Monday": 1,
    "Tue": 2, "Tuesday": 2,
    "Wed": 3, "Wednesday": 3,
    "Thu": 4, "Thursday": 4,
    "Fri": 5, "Friday": 5,
    "Sat": 6, "Saturday": 6
  };

  // Debug: Log available days
  console.log("Available days from backend:", window.availableDays);
  
  // Convert available days to numbers
  const availableDayNumbers = (window.availableDays || []).map(day => dayNameToNumber[day]);
  
  console.log("Available day numbers (JS getDay format):", availableDayNumbers);

  // Initialize Flatpickr date picker
  if (dateInput && typeof flatpickr !== 'undefined') {
    flatpickr(dateInput, {
      minDate: window.todayDate || "today",
      dateFormat: "Y-m-d",
      disable: [
        function(date) {
          // Disable dates that are not in the available days
          if (!availableDayNumbers || availableDayNumbers.length === 0) {
            console.log("No availability specified, allowing all dates");
            return false; // Don't disable any dates if no availability specified
          }
          
          const dayOfWeek = date.getDay(); // 0=Sunday, 1=Monday, ..., 6=Saturday
          const shouldDisable = !availableDayNumbers.includes(dayOfWeek);
          
          return shouldDisable;
        }
      ],
      locale: {
        firstDayOfWeek: 1 // Start week on Monday
      },
      onReady: function(selectedDates, dateStr, instance) {
        // Add custom styling
        instance.calendarContainer.style.boxShadow = "0 0.5rem 1rem rgba(0, 0, 0, 0.15)";
        console.log("Flatpickr initialized successfully");
        console.log("Will enable days:", availableDayNumbers, "which are:", (window.availableDays || []).join(", "));
      }
    });
  } else {
    console.error("Flatpickr not initialized:", {
      dateInput: !!dateInput,
      flatpickrLoaded: typeof flatpickr !== 'undefined'
    });
  }

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
    const dateOk = dateInput.value !== "";
    
    if (!dateOk || !timeOk || !durOk) {
      e.preventDefault();
      if (!dateOk) {
        dateInput.classList.add("is-invalid");
      }
    }
  });
})();
