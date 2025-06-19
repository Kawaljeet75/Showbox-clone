document.addEventListener("DOMContentLoaded", () => {
  const filterButtons = document.querySelectorAll(".filter-btn");

  filterButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      filterButtons.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      // Dynamic filtering effect can be added here
      console.log(`Filtering: ${btn.innerText}`);
    });
  });

  const heroText = document.querySelector(".hero-content h1");
  if (heroText) {
    heroText.classList.add("text-glow");
  }

  window.addEventListener("scroll", () => {
    const nav = document.querySelector(".navbar");
    if (window.scrollY > 50) {
      nav.classList.add("scrolled");
    } else {
      nav.classList.remove("scrolled");
    }
  });
});


//  just checking for filters 
// Optional: Enhance dropdowns with smooth show/hide logic
document.querySelectorAll('.dropdown').forEach(dropdown => {
  const menu = dropdown.querySelector('.dropdown-content');

  dropdown.addEventListener('mouseenter', () => {
    menu.style.display = 'block';
    setTimeout(() => {
      menu.style.opacity = '1';
      menu.style.transform = 'translateY(0)';
    }, 10);
  });

  dropdown.addEventListener('mouseleave', () => {
    menu.style.opacity = '0';
    menu.style.transform = 'translateY(10px)';
    setTimeout(() => {
      menu.style.display = 'none';
    }, 300);
  });
});


// dropdown toggle just for mobile/touch devices 
const toggleBtn = document.getElementById('formatDropdownBtn');
  const dropdown = document.getElementById('dropdownMenu');

  toggleBtn.addEventListener('click', (e) => {
    e.preventDefault();
    dropdown.classList.toggle('show');
  });

  document.addEventListener('click', (e) => {
    if (!toggleBtn.contains(e.target) && !dropdown.contains(e.target)) {
      dropdown.classList.remove('show');
    }
  });

  if ('ontouchstart' in window || navigator.maxTouchPoints) {
    // attach JS toggle only for touch devices
  }








