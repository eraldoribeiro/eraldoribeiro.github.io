// Current year in footer
const yearEl = document.getElementById('year');
if (yearEl) yearEl.textContent = new Date().getFullYear();

// Mobile nav toggle
const toggle = document.querySelector('.nav-toggle');
const menu = document.getElementById('nav-menu');
if (toggle && menu) {
  toggle.addEventListener('click', () => {
    const open = menu.classList.toggle('open');
    toggle.setAttribute('aria-expanded', String(open));
  });
  // Close menu when a link is tapped
  menu.addEventListener('click', (e) => {
    if (e.target.tagName === 'A') {
      menu.classList.remove('open');
      toggle.setAttribute('aria-expanded', 'false');
    }
  });
}

// Publication year filter
const filters = document.querySelectorAll('.filter');
const pubs = document.querySelectorAll('.pub');
const emptyMsg = document.querySelector('.pub-empty');

if (filters.length && pubs.length) {
  filters.forEach((btn) => {
    btn.addEventListener('click', () => {
      const year = btn.dataset.year;

      filters.forEach((b) => b.classList.toggle('is-active', b === btn));

      // Supports "all", an exact year, or a decade like "2010s"
      const decade = year.endsWith('s') ? parseInt(year, 10) : null;
      let visible = 0;
      pubs.forEach((pub) => {
        const py = parseInt(pub.dataset.year, 10);
        const show =
          year === 'all' ||
          (decade !== null ? py >= decade && py < decade + 10 : pub.dataset.year === year);
        pub.hidden = !show;
        if (show) visible++;
      });

      if (emptyMsg) emptyMsg.hidden = visible !== 0;
    });
  });
}
