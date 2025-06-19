// booking.js

document.addEventListener('DOMContentLoaded', () => {
    const dateInputs  = document.querySelectorAll('input[name="date"]');
    const timeInputs  = document.querySelectorAll('input[name="showtime"]');
    const seatInputs  = document.querySelectorAll('input[name="seats"]');
    const proceedBtn  = document.getElementById('proceedBtn');
    const form        = document.getElementById('bookingForm');

    // Highlight any pre-selected inputs on page load
    function initLabels() {
        dateInputs.forEach(input => {
            if (input.checked) {
                document.querySelector(`label[for="${input.id}"]`)?.classList.add('active');
            }
        });
        timeInputs.forEach(input => {
            if (input.checked) {
                document.querySelector(`label[for="${input.id}"]`)?.classList.add('active');
            }
        });
        seatInputs.forEach(input => {
            if (input.checked) {
                document.querySelector(`label[for="${input.id}"]`)?.classList.add('selected');
            }
        });
    }

    function updateFlow() {
        const dateChosen = Array.from(dateInputs).some(i => i.checked);
        timeInputs.forEach(i => i.disabled = !dateChosen);
        if (!dateChosen) {
            timeInputs.forEach(i => i.checked = false);
            seatInputs.forEach(i => i.checked = false);
        }

        const timeChosen = dateChosen && Array.from(timeInputs).some(i => i.checked);
        seatInputs.forEach(i => {
            const label = document.querySelector(`label[for="${i.id}"]`);
            i.disabled = !timeChosen || (label && label.classList.contains('booked'));
        });

        const seatChosen = Array.from(seatInputs).some(i => i.checked);
        proceedBtn.disabled = !seatChosen;
        proceedBtn.classList.toggle('enabled', seatChosen);
    }

    dateInputs.forEach(radio => {
        radio.addEventListener('change', () => {
            document.querySelectorAll('.picker-dates label').forEach(l => l.classList.remove('active'));
            const lbl = document.querySelector(`label[for="${radio.id}"]`);
            if (lbl) lbl.classList.add('active');

            const date = radio.value;
            const time = document.querySelector('input[name="showtime"]:checked')?.value;
            if (date && time) {
                const url = new URL(window.location.href);
                url.searchParams.set('date', date);
                url.searchParams.set('time', time);
                window.location.href = url.toString();
            }

            updateFlow();
        });
    });

    timeInputs.forEach(radio => {
        radio.addEventListener('change', () => {
            document.querySelectorAll('.picker-times label').forEach(l => l.classList.remove('active'));
            const lbl = document.querySelector(`label[for="${radio.id}"]`);
            if (lbl) lbl.classList.add('active');

            const time = radio.value;
            const date = document.querySelector('input[name="date"]:checked')?.value;
            if (date && time) {
                const url = new URL(window.location.href);
                url.searchParams.set('date', date);
                url.searchParams.set('time', time);
                window.location.href = url.toString();
            }

            updateFlow();
        });
    });

    seatInputs.forEach(cb => {
        cb.addEventListener('change', () => {
            const lbl = document.querySelector(`label[for="${cb.id}"]`);
            lbl?.classList.toggle('selected', cb.checked);
            updateFlow();
        });
    });

    // Prevent submit if anything is missing
    form.addEventListener('submit', e => {
        const hasDate = Array.from(dateInputs).some(i => i.checked);
        const hasTime = Array.from(timeInputs).some(i => i.checked);
        const hasSeat = Array.from(seatInputs).some(i => i.checked);
        if (!hasDate || !hasTime || !hasSeat) {
            e.preventDefault();
            alert('Please select a date, showtime, and at least one seat.');
        }
    });

    // Initialize on page load
    initLabels();
    updateFlow();
});
