/* Mercedes Repair Abu Dhabi | site-wide enhancements */
(() => {
  const WA_NUMBER = '971586095249';
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const fine = matchMedia('(pointer: fine)').matches;

  // ---------- Smooth scroll (Lenis) wired to GSAP ScrollTrigger ----------
  let lenis = null;
  if (!reduce && window.Lenis) {
    lenis = new Lenis({ lerp: 0.09, smoothWheel: true });
    document.documentElement.style.scrollBehavior = 'auto';
    if (window.gsap && window.ScrollTrigger) {
      gsap.registerPlugin(ScrollTrigger);
      lenis.on('scroll', ScrollTrigger.update);
      gsap.ticker.add(t => lenis.raf(t * 1000));
      gsap.ticker.lagSmoothing(0);
    } else {
      const raf = t => { lenis.raf(t); requestAnimationFrame(raf); };
      requestAnimationFrame(raf);
    }
    document.querySelectorAll('a[href^="#"], a[href^="./#"]').forEach(a => {
      a.addEventListener('click', e => {
        const id = a.getAttribute('href').replace('./', '');
        const el = id.length > 1 && document.querySelector(id);
        if (el) { e.preventDefault(); lenis.scrollTo(el, { offset: -90 }); }
      });
    });
  }
  window.__lenis = lenis;

  // ---------- Mobile drawer ----------
  const drawer = document.getElementById('drawer');
  if (drawer) {
    drawer.querySelectorAll('a').forEach(a => a.addEventListener('click', () => {
      try { drawer.hidePopover(); } catch (e) { /* unsupported */ }
    }));
  }

  // ---------- Reveal fallback ----------
  if (!CSS.supports('animation-timeline: view()') && 'IntersectionObserver' in window) {
    const io = new IntersectionObserver(entries => {
      entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add('is-in'); io.unobserve(e.target); } });
    }, { rootMargin: '0px 0px -8% 0px' });
    document.querySelectorAll('.reveal').forEach(el => io.observe(el));
  }

  // ---------- Count-up numbers ----------
  const counters = document.querySelectorAll('[data-count]');
  if (counters.length && 'IntersectionObserver' in window && !reduce) {
    const run = el => {
      const end = parseFloat(el.dataset.count);
      const dec = (el.dataset.count.split('.')[1] || '').length;
      const t0 = performance.now(), dur = 1600;
      const tick = now => {
        const p = Math.min((now - t0) / dur, 1);
        const v = end * (1 - Math.pow(1 - p, 4));
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

  // ---------- Spotlight glow follows pointer ----------
  document.querySelectorAll('.svc, .why2 .card').forEach(card => {
    card.addEventListener('pointermove', e => {
      const r = card.getBoundingClientRect();
      card.style.setProperty('--mx', `${e.clientX - r.left}px`);
      card.style.setProperty('--my', `${e.clientY - r.top}px`);
    });
  });

  if (fine && !reduce) {
    // ---------- 3D tilt ----------
    document.querySelectorAll('.tilt').forEach(el => {
      el.addEventListener('pointermove', e => {
        const r = el.getBoundingClientRect();
        const x = (e.clientX - r.left) / r.width - .5;
        const y = (e.clientY - r.top) / r.height - .5;
        el.style.transform = `perspective(1000px) rotateY(${x * 10}deg) rotateX(${-y * 10}deg) translateZ(0)`;
      });
      el.addEventListener('pointerleave', () => {
        el.style.transition = 'transform .6s cubic-bezier(.2,.7,.2,1)';
        el.style.transform = '';
        setTimeout(() => { el.style.transition = ''; }, 600);
      });
    });

    // ---------- Magnetic buttons ----------
    document.querySelectorAll('.magnetic').forEach(el => {
      el.addEventListener('pointermove', e => {
        const r = el.getBoundingClientRect();
        el.style.translate = `${(e.clientX - r.left - r.width / 2) * .25}px ${(e.clientY - r.top - r.height / 2) * .35}px`;
      });
      el.addEventListener('pointerleave', () => { el.style.translate = ''; });
    });

    // ---------- Cursor ring ----------
    const cur = document.querySelector('.cursor');
    if (cur) {
      let x = innerWidth / 2, y = innerHeight / 2, cx = x, cy = y;
      addEventListener('pointermove', e => { x = e.clientX; y = e.clientY; cur.classList.add('is-on'); }, { passive: true });
      document.addEventListener('pointerleave', () => cur.classList.remove('is-on'));
      const loop = () => {
        cx += (x - cx) * .2; cy += (y - cy) * .2;
        cur.style.transform = `translate(${cx}px, ${cy}px)`;
        requestAnimationFrame(loop);
      };
      loop();
      document.querySelectorAll('a, button, summary, .tilt').forEach(el => {
        el.addEventListener('pointerenter', () => cur.classList.add('is-hover'));
        el.addEventListener('pointerleave', () => cur.classList.remove('is-hover'));
      });
    }
  }

  // ---------- Estimate form opens WhatsApp ----------
  document.querySelectorAll('form[data-wa]').forEach(form => {
    form.addEventListener('submit', e => {
      e.preventDefault();
      if (!form.reportValidity()) return;
      if (form.querySelector('[name="website"]')?.value) return;
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

  // ---------- Inner pages: GSAP reveals ----------
  if (!reduce && window.gsap && window.ScrollTrigger && !document.querySelector('.xhero')) {
    gsap.utils.toArray('.page-hero h1, .page-hero p, .page-hero .btn-row').forEach((el, i) => {
      gsap.from(el, { y: 40, opacity: 0, duration: 1, delay: .1 + i * .1, ease: 'power3.out' });
    });
    const car = document.querySelector('.page-hero__car');
    if (car) gsap.from(car, { x: 200, opacity: 0, duration: 1.4, ease: 'power3.out', delay: .2 });
  }

  document.querySelectorAll('[data-year]').forEach(el => { el.textContent = new Date().getFullYear(); });
})();
