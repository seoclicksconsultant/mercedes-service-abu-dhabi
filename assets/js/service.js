/* Mercedes service pages: hero motion, on-page nav, charts, filters, tabs, timeline */
document.addEventListener('DOMContentLoaded', () => {
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const fine = matchMedia('(pointer: fine)').matches;
  const hasGsap = !!(window.gsap && window.ScrollTrigger) && !reduce;
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];

  // ---------- Charts and meters start when they scroll into view ----------
  const live = $$('.viz, .symf, .esc, .cap, .layers, .istats');
  if ('IntersectionObserver' in window && !reduce) {
    const io = new IntersectionObserver(es => es.forEach(e => {
      if (e.isIntersecting) { e.target.classList.add('is-live'); io.unobserve(e.target); }
    }), { threshold: .35 });
    live.forEach(el => io.observe(el));
  } else live.forEach(el => el.classList.add('is-live'));

  // ---------- Symptom filter ----------
  $$('.ssym').forEach(sec => {
    const btns = $$('.symf__b', sec), cards = $$('.sym', sec);
    btns.forEach(b => b.addEventListener('click', () => {
      const f = b.dataset.f;
      btns.forEach(x => { const on = x === b; x.classList.toggle('is-on', on); x.setAttribute('aria-pressed', String(on)); });
      cards.forEach(c => c.classList.toggle('is-dim', f !== 'all' && c.dataset.lvl !== f));
    }));
  });

  // ---------- Decision explorer tabs ----------
  $$('[data-tabs]').forEach(box => {
    const tabs = $$('[role="tab"]', box);
    const show = t => {
      tabs.forEach(x => {
        const on = x === t;
        x.setAttribute('aria-selected', String(on));
        x.tabIndex = on ? 0 : -1;
        document.getElementById(x.getAttribute('aria-controls')).hidden = !on;
      });
    };
    tabs.forEach((t, i) => {
      t.tabIndex = i ? -1 : 0;
      t.addEventListener('click', () => show(t));
      t.addEventListener('keydown', e => {
        const d = { ArrowDown: 1, ArrowRight: 1, ArrowUp: -1, ArrowLeft: -1 }[e.key];
        if (!d) return;
        e.preventDefault();
        const n = tabs[(i + d + tabs.length) % tabs.length];
        n.focus(); show(n);
      });
    });
  });

  // ---------- On-page nav: active link + reading progress ----------
  const sub = $('.subnav');
  if (sub) {
    const links = $$('.subnav__links a', sub);
    const box = $('.subnav__links', sub);
    const map = new Map(links.map(a => [a.getAttribute('href').slice(1), a]));
    const secs = [...map.keys()].map(id => document.getElementById(id)).filter(Boolean);
    let current = null;
    const setActive = id => {
      if (id === current) return;
      current = id;
      links.forEach(a => a.classList.toggle('is-active', a === map.get(id)));
      const a = map.get(id);
      if (a) box.scrollTo({ left: a.offsetLeft - box.clientWidth / 2 + a.clientWidth / 2, behavior: 'smooth' });
    };
    const main = $('.svcpage');
    const onScroll = () => {
      const y = window.scrollY;
      const top = sub.offsetTop, end = main.offsetTop + main.offsetHeight - innerHeight;
      sub.style.setProperty('--pp', Math.min(1, Math.max(0, (y - top) / (end - top || 1))).toFixed(4));
      let id = null;
      for (const s of secs) if (s.getBoundingClientRect().top < innerHeight * .35) id = s.id;
      setActive(id);
    };
    addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  // ---------- Process timeline fill + step highlight ----------
  const ptl = $('.ptl');
  if (ptl) {
    const steps = $$('.pstep', ptl);
    const upd = () => {
      const r = ptl.getBoundingClientRect();
      const p = Math.min(1, Math.max(0, (innerHeight * .6 - r.top) / r.height));
      ptl.style.setProperty('--pp', p.toFixed(4));
      steps.forEach(s => {
        const d = $('.pstep__dot', s).getBoundingClientRect();
        s.classList.toggle('is-on', d.top < innerHeight * .6);
      });
    };
    addEventListener('scroll', upd, { passive: true });
    upd();
  }

  // ---------- Hero sparks (canvas) ----------
  const fxc = $('.shero2__fx');
  if (fxc && !reduce) {
    const ctx = fxc.getContext('2d');
    const tone = getComputedStyle($('.shero2')).getPropertyValue('--tone').trim() || '#1a8cff';
    let W = 0, H = 0, run = true;
    const size = () => { const r = fxc.getBoundingClientRect(); W = fxc.width = r.width * devicePixelRatio; H = fxc.height = r.height * devicePixelRatio; };
    const spawn = () => ({ x: W * (.45 + Math.random() * .55), y: H * (.35 + Math.random() * .6), vx: (Math.random() - .5) * .35, vy: -(.25 + Math.random() * .7), r: (.6 + Math.random() * 1.8) * devicePixelRatio, a: 0, life: 0, max: 220 + Math.random() * 260 });
    size(); addEventListener('resize', size);
    const parts = Array.from({ length: innerWidth < 760 ? 26 : 60 }, spawn);
    const tick = () => {
      if (!run) return;
      ctx.clearRect(0, 0, W, H);
      ctx.fillStyle = tone; ctx.shadowColor = tone; ctx.shadowBlur = 12 * devicePixelRatio;
      for (const p of parts) {
        p.life++; p.x += p.vx; p.y += p.vy;
        p.a = Math.sin(Math.min(1, p.life / p.max) * Math.PI);
        ctx.globalAlpha = p.a * .8;
        ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, 7); ctx.fill();
        if (p.life > p.max) Object.assign(p, spawn());
      }
      ctx.globalAlpha = 1;
      requestAnimationFrame(tick);
    };
    new IntersectionObserver(es => { const was = run; run = es[0].isIntersecting; if (run && !was) requestAnimationFrame(tick); }).observe(fxc);
    requestAnimationFrame(tick);
  }

  // ---------- Services: 3D coverflow ----------
  const cfl = $('[data-cflow]');
  if (cfl) {
    const sec = cfl.closest('section'), track = $('.cflow__track', cfl), cards = $$('.cf', track);
    const fx = () => {
      const mid = innerWidth / 2; let best = null, bd = 1e9;
      cards.forEach(c => {
        const r = c.getBoundingClientRect();
        const d = (r.left + r.width / 2 - mid) / (innerWidth / 2);
        const k = Math.max(-1.5, Math.min(1.5, d)), a = Math.abs(k);
        c.style.transform = `perspective(1300px) rotateY(${(-k * 26).toFixed(2)}deg) translateZ(${(-a * 110).toFixed(1)}px) scale(${(1 - a * .05).toFixed(3)})`;
        c.style.opacity = (1 - Math.min(a, 1.5) * .3).toFixed(3);
        if (Math.abs(d) < bd) { bd = Math.abs(d); best = c; }
      });
      cards.forEach(c => c.classList.toggle('is-front', c === best));
    };
    let st = null;
    if (hasGsap && matchMedia('(min-width: 1024px)').matches) {
      const dist = () => Math.max(0, track.scrollWidth - innerWidth);
      const tw = gsap.to(track, {
        x: () => -dist(), ease: 'none', onUpdate: fx,
        scrollTrigger: {
          trigger: sec, start: () => 'top ' + (($('.header') ? $('.header').offsetHeight : 0) + ($('.subnav') ? $('.subnav').offsetHeight : 0)) + 'px', end: () => '+=' + dist(), pin: true, scrub: .7, invalidateOnRefresh: true,
          onUpdate: s => { sec.style.setProperty('--cp', Math.max(.06, s.progress).toFixed(3)); fx(); }, onRefresh: fx
        }
      });
      st = tw.scrollTrigger;
    } else {
      track.addEventListener('scroll', () => {
        requestAnimationFrame(fx);
        sec.style.setProperty('--cp', Math.max(.06, track.scrollLeft / Math.max(1, track.scrollWidth - track.clientWidth)).toFixed(3));
      }, { passive: true });
    }
    $$('[data-cf]', sec).forEach(b => b.addEventListener('click', () => {
      const step = (cards[1] ? cards[1].offsetWidth : 360) + 22, dir = +b.dataset.cf;
      if (st) { const y = st.scroll() + dir * step; if (window.__lenis) window.__lenis.scrollTo(y); else scrollTo({ top: y, behavior: 'smooth' }); }
      else track.scrollBy({ left: dir * step, behavior: 'smooth' });
    }));
    fx(); addEventListener('resize', fx);
  }

  // ---------- Reference cards: 3D ring ----------
  $$('[data-ring]').forEach(ring => {
    const track = $('.ring__track', ring), cards = $$('.spec', track), n = cards.length, count = $('.ring__count b', ring);
    if (n < 3) return;
    let idx = 0, r = 400, hover = false, seen = false;
    const step = 360 / n;
    const go = i => {
      idx = (i % n + n) % n;
      track.style.transform = `translateZ(${-r}px) rotateY(${-idx * step}deg)`;
      cards.forEach((c, k) => c.classList.toggle('is-front', k === idx));
      if (count) count.textContent = String(idx + 1).padStart(2, '0');
    };
    const layout = () => {
      ring.classList.add('is-3d');
      const cw = Math.min(330, ring.clientWidth * .82);
      r = Math.round(cw / 2 / Math.tan(Math.PI / n)) + 40;
      ring.style.setProperty('--cw', cw + 'px'); ring.style.setProperty('--r', r + 'px'); ring.style.setProperty('--step', step + 'deg');
      cards.forEach((c, k) => { c.style.setProperty('--i', k); c.style.minHeight = '0'; });
      const ch = Math.max(...cards.map(c => c.offsetHeight));
      cards.forEach(c => { c.style.minHeight = ''; });
      ring.style.setProperty('--ch', ch + 'px');
      track.style.transition = 'none'; go(idx); void track.offsetWidth; track.style.transition = '';
    };
    layout(); addEventListener('resize', layout);
    $$('[data-ring-go]', ring).forEach(b => b.addEventListener('click', () => go(idx + +b.dataset.ringGo)));
    cards.forEach((c, k) => c.addEventListener('click', () => go(k)));
    let x0 = null;
    ring.addEventListener('pointerdown', e => { x0 = e.clientX; });
    ring.addEventListener('pointerup', e => { if (x0 !== null && Math.abs(e.clientX - x0) > 40) go(idx + (e.clientX < x0 ? 1 : -1)); x0 = null; });
    ring.addEventListener('pointerenter', () => { hover = true; });
    ring.addEventListener('pointerleave', () => { hover = false; });
    if (!reduce) {
      new IntersectionObserver(es => { seen = es[0].isIntersecting; }, { threshold: .4 }).observe(ring);
      setInterval(() => { if (seen && !hover && !document.hidden) go(idx + 1); }, 3800);
    }
  });

  if (!hasGsap) return;

  // ---------- Hero intro ----------
  const tl = gsap.timeline({ defaults: { ease: 'power4.out' } });
  tl.from('.shero2 h1 .w > span', { yPercent: 115, rotateX: -70, opacity: 0, duration: 1.1, stagger: .045 })
    .from('.shero2 .crumbs, .shero2__badge', { y: 16, opacity: 0, duration: .7, stagger: .08 }, 0)
    .from('.shero2__lead, .shero2__ctas, .shero2 .trust, .shero2 .rate', { y: 26, opacity: 0, duration: .9, stagger: .08, clearProps: 'transform,opacity' }, .35)
    .from('.turn', { opacity: 0, scale: .5, duration: 1.6 }, .1)
    .from('.shero2__car', { x: -320, opacity: 0, skewX: -8, duration: 1.6, ease: 'expo.out' }, .45)
    .from('.schip', { y: 30, opacity: 0, duration: .9, stagger: .15, clearProps: 'opacity' }, 1)
    .from('.shero2 .hstat', { y: 30, opacity: 0, duration: .8, stagger: .08, clearProps: 'transform,opacity' }, .7);

  const hero = $('.shero2');
  if (hero) {
    const sc = { trigger: hero, start: 'top top', end: 'bottom top', scrub: true };
    gsap.to('.shero2__emblem', { rotate: 90, ease: 'none', scrollTrigger: sc });
    gsap.to('.shero2__car', { xPercent: 18, scale: 1.08, ease: 'none', scrollTrigger: sc });
    gsap.to('.shero2__bg img', { yPercent: 12, ease: 'none', scrollTrigger: sc });
    gsap.to('.shero2__word', { xPercent: -20, ease: 'none', scrollTrigger: sc });
  }

  // pointer depth: each [data-depth] layer moves by its own amount and the stage tilts
  const stage = $('[data-stage]');
  if (stage && fine && hero) {
    const layers = $$('[data-depth]', stage).map(el => ({ d: +el.dataset.depth, qx: gsap.quickTo(el, 'x', { duration: 1, ease: 'power3' }), qy: gsap.quickTo(el, 'y', { duration: 1, ease: 'power3' }) }));
    const rx = gsap.quickTo(stage, 'rotationY', { duration: 1.2, ease: 'power3' }), ry = gsap.quickTo(stage, 'rotationX', { duration: 1.2, ease: 'power3' });
    gsap.set(stage, { transformPerspective: 1400 });
    hero.addEventListener('pointermove', e => {
      const x = e.clientX / innerWidth - .5, y = e.clientY / innerHeight - .5;
      layers.forEach(l => { l.qx(x * l.d); l.qy(y * l.d * .6); });
      rx(x * 8); ry(-y * 5);
    });
    hero.addEventListener('pointerleave', () => { layers.forEach(l => { l.qx(0); l.qy(0); }); rx(0); ry(0); });
  }

  // ---------- Cards rise in a stagger ----------
  $$('.specs:not(.ring__track), .swatches, .wcards, .rels, .letters, .wls').forEach(grid => {
    gsap.from(grid.children, {
      y: 40, opacity: 0, duration: .9, ease: 'power3.out', stagger: .06, clearProps: 'transform,opacity',
      scrollTrigger: { trigger: grid, start: 'top 85%', once: true }
    });
  });

  // ---------- Booking: car drives in ----------
  const bcar = $('.sbook__car');
  if (bcar) gsap.from(bcar, { x: -260, opacity: 0, duration: 1.6, ease: 'expo.out', scrollTrigger: { trigger: bcar, start: 'top 92%', once: true } });

  // layout settles after images and fonts load: re-measure every trigger (keeps the pinned coverflow in place)
  const refresh = () => ScrollTrigger.refresh();
  addEventListener('load', refresh);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(refresh);
  $$('img').forEach(img => {
    if (!img.complete) img.addEventListener('load', () => { clearTimeout(window.__stR); window.__stR = setTimeout(refresh, 150); }, { once: true });
  });

  $$('.sheat__glow').forEach(g => gsap.to(g, { xPercent: 30, yPercent: 20, ease: 'none', scrollTrigger: { trigger: g.parentElement, start: 'top bottom', end: 'bottom top', scrub: true } }));
});
