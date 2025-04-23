
const trailerUrl = "{{ movie['embed_url'] }}";

function openModal() {
    const modal = document.getElementById('trailerModal');
    const iframe = document.getElementById('trailerFrame');
    const spinner = document.getElementById('spinner');
    const main = document.getElementById('mainContent');
 
    const button = document.querySelector('[data-trailer]');
    const trailerUrl = button.getAttribute('data-trailer');
 
    iframe.src = trailerUrl + '?autoplay=1';
    spinner.classList.remove('hidden');
    modal.style.display = 'block';
    main.classList.add('blurred');
 }
 

function closeModal() {
   const modal = document.getElementById('trailerModal');
   const iframe = document.getElementById('trailerFrame');
   const main = document.getElementById('mainContent');

   iframe.src = "";
   modal.style.display = 'none';
   main.classList.remove('blurred');
}

function hideSpinner() {
   document.getElementById('spinner').classList.add('hidden');
}

window.onclick = function (event) {
   const modal = document.getElementById('trailerModal');
   if (event.target === modal) {
       closeModal();
   }
}



document.addEventListener("DOMContentLoaded", () => {
const seats = document.querySelectorAll(".seat");
const confirmBtn = document.getElementById("confirm-selection");

seats.forEach(seat => {
seat.addEventListener("click", () => {
   if (!seat.classList.contains("occupied")) {
       seat.classList.toggle("selected");
   }
});
});

confirmBtn.addEventListener("click", () => {
const selectedSeats = [];
document.querySelectorAll(".seat.selected").forEach(seat => {
   selectedSeats.push(seat.dataset.seat);
});

alert("You selected: " + selectedSeats.join(", "));
// TODO: Send selectedSeats and movie_id to backend with fetch()
toggleModal();
});
});
