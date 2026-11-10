/* Mercedes Repair Abu Dhabi | small, dependency-free enhancements */
(() => {
  const WA_NUMBER = '971586095249';

  // Close the mobile drawer after a link is chosen
  const drawer = document.getElementById('drawer');
  if (drawer) {
    drawer.querySelectorAll('a').forEach(a => a.addEventListener('click', () => {
      try { drawer.hidePopover(); } catch (e) { /* popover unsupported */ }
    }));
  }

  // Scroll reveal fallback for browsers without scroll-driven animations
  if (!CSS.supports('animation-timeline: view()') && 'IntersectionObserver' in window) {
    const io = new IntersectionObserver(entries => {
      entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add('is-in'); io.unobserve(e.target); } });
    }, { rootMargin: '0px 0px -8% 0px' });
    document.querySelectorAll('.reveal').forEach(el => io.observe(el));
  }

  // Count-up numbers
  const counters = document.querySelectorAll('[data-count]');
  if (counters.length && 'IntersectionObserver' in window && !matchMedia('(prefers-reduced-motion: reduce)').matches) {
    const run = el => {
      const end = parseFloat(el.dataset.count);
      const dec = (el.dataset.count.split('.')[1] || '').length;
      const t0 = performance.now(), dur = 1400;
      const tick = now => {
        const p = Math.min((now - t0) / dur, 1);
        const v = end * (1 - Math.pow(1 - p, 3));
        el.textContent = v.toLocaleString('en-US', { minimumFractionDigits: dec, maximumFractionDigits: dec });
        if (p < 1) requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
    };
    const co = new IntersectionObserver(entries => {
      entries.forEach(e => { if (e.isIntersecting) { run(e.target); co.unobserve(e.target); } });
    }, { threshold: .6 });
    counters.forEach(el => co.observe(el));
  }

  // Cursor-following glow on service cards
  document.querySelectorAll('.svc').forEach(card => {
    card.addEventListener('pointermove', e => {
      const r = card.getBoundingClientRect();
      card.style.setProperty('--mx', `${e.clientX - r.left}px`);
      card.style.setProperty('--my', `${e.clientY - r.top}px`);
    });
  });

  // Estimate form: no server needed, it opens WhatsApp with the details filled in
  document.querySelectorAll('form[data-wa]').forEach(form => {
    form.addEventListener('submit', e => {
      e.preventDefault();
      if (form.querySelector('[name="website"]')?.value) return; // honeypot
      const d = new FormData(form);
      const lines = [
        'Hello Exotic Auto Services, I would like an estimate for my Mercedes.',
        `Name: ${d.get('name') || ''}`,
        `Mobile: ${d.get('mobile') || ''}`,
        d.get('model') ? `Model / year: ${d.get('model')}` : '',
        `Service: ${d.get('service') || ''}`,
        d.get('message') ? `Details: ${d.get('message')}` : ''
      ].filter(Boolean);
      window.open(`https://wa.me/${WA_NUMBER}?text=${encodeURIComponent(lines.join('\n'))}`, '_blank', 'noopener');
      const ok = form.querySelector('.form__ok');
      if (ok) ok.hidden = false;
    });
  });

  // Footer year
  document.querySelectorAll('[data-year]').forEach(el => { el.textContent = new Date().getFullYear(); });
})();
