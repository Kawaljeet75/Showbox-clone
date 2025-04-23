document.addEventListener("DOMContentLoaded", function () {
    const seats = document.querySelectorAll(".seat input[type='checkbox']");
    const maxSeats = 5;
    let selectedCount = 0;

    seats.forEach(seat => {
        seat.addEventListener("change", function () {
            if (this.checked) {
                if (selectedCount >= maxSeats) {
                    alert(`You can only select up to ${maxSeats} seats.`);
                    this.checked = false;
                } else {
                    selectedCount++;
                    this.parentElement.classList.add("selected");
                }
            } else {
                selectedCount--;
                this.parentElement.classList.remove("selected");
            }
        });
    });

    // On submit, collect selected seats
    const form = document.querySelector("form");
    form.addEventListener("submit", function (e) {
        const selectedSeats = [];
        document.querySelectorAll(".seat input[type='checkbox']:checked").forEach(seat => {
            selectedSeats.push(seat.value);
        });

        // Add selected seats to hidden input
        const hiddenInput = document.createElement("input");
        hiddenInput.type = "hidden";
        hiddenInput.name = "selected_seats";
        hiddenInput.value = selectedSeats.join(",");
        form.appendChild(hiddenInput);
    });
});
