/* Home page scenes: 3D hero (Three.js), GSAP ScrollTrigger animations, data graphics */
(() => {
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const desktop = matchMedia('(min-width: 961px)');
  const hasGsap = !!(window.gsap && window.ScrollTrigger);
  if (hasGsap) gsap.registerPlugin(ScrollTrigger);

  /* ---------------- Preloader ---------------- */
  const loader = document.querySelector('.loader');
  const showLoader = loader && !document.documentElement.classList.contains('no-loader') && hasGsap;
  const introDelay = showLoader ? 1.5 : 0.1;
  if (showLoader) {
    const count = loader.querySelector('.loader__count');
    const bar = loader.querySelector('.loader__bar i');
    const o = { v: 0 };
    gsap.timeline()
      .to(o, { v: 100, duration: 1.1, ease: 'power2.inOut', onUpdate: () => { count.textContent = Math.round(o.v); bar.style.width = o.v + '%'; } })
      .to(loader.querySelector('.loader__inner'), { y: -30, opacity: 0, duration: .35, ease: 'power2.in' })
      .to(loader, { yPercent: -100, duration: .7, ease: 'expo.inOut' }, '-=.1')
      .set(loader, { display: 'none' });
    try { sessionStorage.setItem('seenLoader', '1'); } catch (e) { /* storage blocked */ }
  } else if (loader) {
    loader.style.display = 'none';
  }

  /* ---------------- Three.js hero scene ---------------- */
  const canvas = document.querySelector('.xhero__canvas');
  const scene3d = { speed: 1, camY: 0 };
  if (canvas && window.THREE && !reduce) {
    try {
      const T = window.THREE;
      const renderer = new T.WebGLRenderer({ canvas, antialias: true, alpha: true });
      renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
      renderer.setClearColor(0x08090b, 0);
      const scene = new T.Scene();
      scene.fog = new T.Fog(0x08090b, 12, 70);
      const camera = new T.PerspectiveCamera(55, 1, 0.1, 200);
      camera.position.set(0, 2.4, 9);

      // Floor grid that scrolls toward the camera
      const grid = new T.GridHelper(240, 120, 0x2a313b, 0x15181e);
      grid.position.y = 0;
      scene.add(grid);

      // Light streaks on the floor
      const streaks = [];
      const mobile = innerWidth < 700;
      const N = mobile ? 16 : 34;
      const colors = [0x0078d6, 0x49b2ff, 0x8fcfff];
      for (let i = 0; i < N; i++) {
        const len = 2 + Math.random() * 8;
        const geo = new T.PlaneGeometry(0.05 + Math.random() * 0.05, len);
        const mat = new T.MeshBasicMaterial({ color: colors[i % colors.length], transparent: true, opacity: 0.25 + Math.random() * 0.35 });
        const m = new T.Mesh(geo, mat);
        m.rotation.x = -Math.PI / 2;
        m.position.set(4 + Math.random() * 40, 0.02, -Math.random() * 90);
        m.userData.v = 0.15 + Math.random() * 0.35;
        scene.add(m); streaks.push(m);
      }

      // Floating dust particles
      const pc = mobile ? 300 : 700;
      const pos = new Float32Array(pc * 3);
      for (let i = 0; i < pc; i++) { pos[i * 3] = Math.random() * 50 - 5; pos[i * 3 + 1] = Math.random() * 18; pos[i * 3 + 2] = -Math.random() * 80; }
      const pg = new T.BufferGeometry(); pg.setAttribute('position', new T.BufferAttribute(pos, 3));
      const points = new T.Points(pg, new T.PointsMaterial({ color: 0x0078d6, size: 0.06, transparent: true, opacity: .55 }));
      scene.add(points);

      // Wireframe rings (abstract wheel / turbine) floating in the distance
      const ring = new T.Mesh(new T.TorusGeometry(6, 0.04, 8, 120), new T.MeshBasicMaterial({ color: 0x0078d6, transparent: true, opacity: .35 }));
      ring.position.set(9, 6, -26); scene.add(ring);
      const ring2 = new T.Mesh(new T.TorusGeometry(4.2, 0.03, 8, 100), new T.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: .12 }));
      ring2.position.set(9, 6, -26); scene.add(ring2);

      let mx = 0, my = 0, visible = true;
      addEventListener('pointermove', e => { mx = e.clientX / innerWidth - .5; my = e.clientY / innerHeight - .5; }, { passive: true });
      const resize = () => {
        const w = canvas.clientWidth, h = canvas.clientHeight;
        renderer.setSize(w, h, false); camera.aspect = w / h; camera.updateProjectionMatrix();
      };
      resize(); addEventListener('resize', resize);
      new IntersectionObserver(([e]) => { visible = e.isIntersecting; }).observe(canvas);

      const clock = new T.Clock();
      const loop = () => {
        requestAnimationFrame(loop);
        if (!visible) return;
        const dt = Math.min(clock.getDelta(), 0.05) * 60;
        const sp = scene3d.speed;
        grid.position.z = (grid.position.z + 0.06 * sp * dt) % 2;
        streaks.forEach(s => { s.position.z += s.userData.v * sp * dt; if (s.position.z > 12) { s.position.z = -90; s.position.x = 4 + Math.random() * 40; } });
        points.rotation.y += 0.0006 * dt;
        ring.rotation.x += 0.004 * dt; ring.rotation.y += 0.006 * dt;
        ring2.rotation.x -= 0.005 * dt; ring2.rotation.y += 0.003 * dt;
        camera.position.x += (mx * 2.4 - camera.position.x) * 0.04;
        camera.position.y += (2.4 - my * 1.2 + scene3d.camY - camera.position.y) * 0.04;
        camera.lookAt(0, 1.2, -12);
        renderer.render(scene, camera);
      };
      loop();
    } catch (err) { canvas.remove(); }
  }

  /* ---------------- Hero: car 3D tilt on pointer ---------------- */
  const car3d = document.querySelector('.xhero__car3d');
  if (car3d && !reduce && matchMedia('(pointer: fine)').matches) {
    let tx = 0, ty = 0, cx = 0, cy = 0;
    addEventListener('pointermove', e => { tx = (e.clientX / innerWidth - .5); ty = (e.clientY / innerHeight - .5); }, { passive: true });
    const word = document.querySelector('.xhero__word');
    const chips = document.querySelectorAll('.xhero .chip');
    const tick = () => {
      cx += (tx - cx) * .06; cy += (ty - cy) * .06;
      car3d.style.transform = `rotateY(${cx * -14}deg) rotateX(${cy * 6}deg) translate3d(${cx * -20}px, ${cy * -8}px, 0)`;
      if (word) word.style.translate = `${cx * 60}px ${cy * 20}px`;
      chips.forEach((c, i) => { c.style.translate = `${cx * (30 + i * 18)}px ${cy * (20 + i * 10)}px`; });
      requestAnimationFrame(tick);
    };
    tick();
  }

  if (!hasGsap || reduce) return;

  /* ---------------- Hero intro + scroll scene ---------------- */
  const intro = gsap.timeline({ delay: introDelay, defaults: { ease: 'expo.out' } });
  intro
    .from('.xhero .hero__badge', { y: 30, opacity: 0, duration: 1, clearProps: 'transform,opacity' })
    .from('.xhero__title .line > span', { yPercent: 110, duration: 1.3, stagger: .09 }, '<.1')
    .from('.xhero__lead', { y: 30, opacity: 0, duration: 1, clearProps: 'transform,opacity' }, '<.4')
    .from('.xhero__ctas .btn', { y: 30, opacity: 0, duration: .9, stagger: .08, clearProps: 'transform,opacity' }, '<.1')
    .from('.xhero__word', { scale: .7, opacity: 0, duration: 1.6 }, 0.1)
    .from('.xhero__car3d', { x: 420, opacity: 0, duration: 1.8, ease: 'power4.out' }, 0.25)
    .from('.xhero .chip', { scale: .6, opacity: 0, duration: .9, stagger: .12, ease: 'back.out(1.8)' }, '<.8')
    .from('.xstats .stat', { y: 40, opacity: 0, duration: 1, stagger: .08 }, '<.1');

  gsap.to(scene3d, { speed: 3.2, camY: -.8, ease: 'none', scrollTrigger: { trigger: '.xhero', start: 'top top', end: 'bottom top', scrub: true } });

  ScrollTrigger.matchMedia({
    '(min-width: 961px)': () => {
      const tl = gsap.timeline({ scrollTrigger: { trigger: '.xhero', start: 'top top', end: '+=90%', scrub: 1, pin: true, anticipatePin: 1 } });
      tl.to('.xhero__stage', { xPercent: -38, yPercent: 6, scale: 1.18, ease: 'none' }, 0)
        .to('.xhero__word', { scale: 1.6, opacity: 0, ease: 'none' }, 0)
        .to('.xhero__copy', { y: -120, opacity: 0, ease: 'none' }, 0)
        .to('.xhero .chip', { opacity: 0, y: -40, stagger: .05, ease: 'none' }, 0)
        .to('.xhero__scroll', { opacity: 0, ease: 'none' }, 0);
    }
  });

  /* ---------------- Manifesto: word-by-word fill ---------------- */
  document.querySelectorAll('[data-words]').forEach(p => {
    const words = p.textContent.trim().split(/\s+/);
    p.innerHTML = words.map(w => `<span class="mw">${w}</span>`).join(' ');
    gsap.to(p.querySelectorAll('.mw'), {
      opacity: 1, stagger: .5, ease: 'none',
      scrollTrigger: { trigger: p, start: 'top 80%', end: 'bottom 45%', scrub: true }
    });
  });

  /* ---------------- Clip reveal + parallax images ---------------- */
  gsap.utils.toArray('[data-clip]').forEach(el => {
    gsap.fromTo(el, { clipPath: 'inset(18% 18% 18% 18% round 28px)' }, {
      clipPath: 'inset(0% 0% 0% 0% round 28px)', ease: 'none',
      scrollTrigger: { trigger: el, start: 'top 90%', end: 'top 35%', scrub: true }
    });
  });
  gsap.utils.toArray('[data-parallax]').forEach(img => {
    gsap.fromTo(img, { yPercent: -8 }, { yPercent: 8, ease: 'none', scrollTrigger: { trigger: img.parentElement, start: 'top bottom', end: 'bottom top', scrub: true } });
  });

  /* ---------------- Big marquee speeds with scroll ---------------- */
  gsap.utils.toArray('.bigmarquee__row').forEach((row, i) => {
    gsap.fromTo(row, { x: i ? '-10%' : '0%' }, { x: i ? '0%' : '-10%', ease: 'none', scrollTrigger: { trigger: '.bigmarquee', start: 'top bottom', end: 'bottom top', scrub: true } });
  });

  /* ---------------- Services: sticky showcase ---------------- */
  const sv = document.querySelector('.sv');
  if (sv) {
    const items = sv.querySelectorAll('.sv__item');
    const imgs = sv.querySelectorAll('.sv__img');
    const count = sv.querySelector('.sv__count b');
    const label = sv.querySelector('.sv__label');
    const bar = sv.querySelector('.sv__bar i');
    let active = 0;
    const setActive = i => {
      if (i === active) return;
      active = i;
      items.forEach((el, k) => el.classList.toggle('is-active', k === i));
      imgs.forEach((el, k) => el.classList.toggle('is-active', k === i));
      count.textContent = String(i + 1).padStart(2, '0');
      label.textContent = items[i].querySelector('h3').textContent.trim();
      bar.style.transform = `scaleX(${(i + 1) / items.length})`;
      gsap.fromTo(label, { y: 16, opacity: 0 }, { y: 0, opacity: 1, duration: .5, ease: 'power3.out' });
    };
    ScrollTrigger.matchMedia({
      '(min-width: 961px)': () => {
        items.forEach((el, i) => {
          ScrollTrigger.create({ trigger: el, start: 'top 55%', end: 'bottom 55%', onToggle: self => { if (self.isActive) setActive(i); } });
          el.addEventListener('pointerenter', () => setActive(i));
        });
      }
    });
    gsap.from('.sv__frame', { clipPath: 'inset(12% 12% 12% 12% round 28px)', duration: 1.4, ease: 'expo.out', scrollTrigger: { trigger: sv, start: 'top 70%' } });
  }

  /* ---------------- Heat dashboard ---------------- */
  const heat = document.querySelector('#heat');
  if (heat) {
    const tl = gsap.timeline({ scrollTrigger: { trigger: heat.querySelector('.heat2'), start: 'top 75%' } });
    tl.from('.thermo__merc', { scaleY: 0, transformOrigin: '50% 100%', duration: 1.6, ease: 'power3.out' })
      .from('#heat .chartcard', { y: 50, opacity: 0, duration: .9, stagger: .1, ease: 'power3.out' }, 0)
      .from('#heat [data-grow]', { scaleX: 0, duration: 1.4, stagger: .15, ease: 'power3.out' }, .3)
      .from('.donut__arc', { strokeDashoffset: 364.4, duration: 1.6, ease: 'power3.out' }, .3)
      .from('.months i', { scaleY: 0, duration: .8, stagger: .05, ease: 'back.out(1.6)' }, .4)
      .from('#heat .compcard', { x: 30, opacity: 0, duration: .8, stagger: .1 }, .6);
  }

  /* ---------------- Odometer road ---------------- */
  const road = document.querySelector('.road');
  if (road) {
    const carEl = road.querySelector('.road__car');
    const marks = road.querySelectorAll('.mk');
    const done = road.querySelector('.road__done');
    const st = { p: 0 };
    gsap.to(st, {
      p: 1, ease: 'none',
      scrollTrigger: { trigger: road, start: 'top 85%', end: 'bottom 30%', scrub: 1 },
      onUpdate: () => {
        const x = 40 + st.p * 920;
        carEl.setAttribute('transform', `translate(${x} 92)`);
        done.setAttribute('width', x);
        marks.forEach(m => m.classList.toggle('on', st.p >= parseFloat(m.dataset.at) - .001));
      }
    });
    gsap.from('.ab__card', { y: 60, opacity: 0, duration: 1, stagger: .15, ease: 'power3.out', scrollTrigger: { trigger: '.ab', start: 'top 85%' } });
  }

  /* ---------------- Showroom tabs ---------------- */
  const show = document.querySelector('.showroom');
  if (show) {
    const data = [
      { name: 'S-Class', tag: 'Sedans &amp; Maybach', title: 'A-Class, C-Class, E-Class, S-Class', text: 'Timing chain wear, gearbox valve body faults, AIRMATIC leaks. Maybach: comfort electronics, suspension, climate systems.' },
      { name: 'G-Class', tag: 'G-Class &amp; SUVs', title: 'G 500, G 63, GLA, GLB, GLC, GLE, GLS', text: 'Air suspension, transfer case and oil leaks on SUVs. Steering wear, axle and transfer case service and cooling on the G-Class.' },
      { name: 'AMG GT', tag: 'AMG &amp; Coupes', title: 'C 63, E 63, GT, CLA, CLE, CLS', text: 'Performance brakes, cooling, turbo and exhaust flap faults on AMG. Electrical module faults, brake wear and AC issues on coupes.' },
      { name: 'EQ', tag: 'EQ (electric)', title: 'EQA, EQB, EQE, EQS', text: 'High-voltage system checks, thermal management and software faults. Abu Dhabi recorded more than 15,000 EV registrations in Q1 2025, up 60%.' }
    ];
    const tabs = show.querySelectorAll('.showroom__tab');
    const cars = show.querySelectorAll('.showroom__car');
    const nameEl = show.querySelector('.showroom__name');
    const info = show.querySelector('.showroom__info');
    let cur = 0, busy = false;
    const go = i => {
      if (i === cur || busy) return;
      busy = true;
      const out = cars[cur], inn = cars[i];
      tabs.forEach((t, k) => t.setAttribute('aria-selected', k === i));
      gsap.timeline({ onComplete: () => { busy = false; } })
        .to(out, { xPercent: -80, opacity: 0, filter: 'blur(8px)', duration: .55, ease: 'power3.in' })
        .to([nameEl, info], { opacity: 0, y: 14, duration: .3 }, 0)
        .add(() => {
          out.hidden = true; inn.hidden = false;
          nameEl.textContent = data[i].name;
          info.querySelector('.model__tag').innerHTML = data[i].tag;
          info.querySelector('h3').textContent = data[i].title;
          info.querySelector('p').textContent = data[i].text;
        })
        .fromTo(inn, { xPercent: 60, opacity: 0, filter: 'blur(8px)' }, { xPercent: 0, opacity: 1, filter: 'blur(0px)', duration: .9, ease: 'expo.out' })
        .to([nameEl, info], { opacity: 1, y: 0, duration: .6 }, '<.1')
        .from(inn.querySelectorAll ? inn.querySelectorAll('.ev__bar') : [], { scaleY: 0, transformOrigin: '50% 100%', duration: .9, stagger: .15, ease: 'power3.out' }, '<');
      cur = i;
    };
    tabs.forEach((t, k) => t.addEventListener('click', () => go(k)));
    gsap.from(cars[0], { xPercent: 40, opacity: 0, duration: 1.4, ease: 'expo.out', scrollTrigger: { trigger: show, start: 'top 70%' } });
  }

  /* ---------------- Stacked process cards ---------------- */
  ScrollTrigger.matchMedia({
    '(min-width: 761px)': () => {
      const cards = gsap.utils.toArray('.stack__card');
      cards.forEach((c, i) => {
        const next = cards[i + 1];
        if (!next) return;
        gsap.to(c, { scale: .92 + i * .015, ease: 'none', scrollTrigger: { trigger: next, start: 'top bottom', end: 'top 25%', scrub: true } });
      });
    }
  });

  /* ---------------- Compare bars ---------------- */
  gsap.from('.compare [data-grow]', { scaleX: 0, duration: 1.4, stagger: .2, ease: 'power3.out', scrollTrigger: { trigger: '.compare__chart', start: 'top 75%' } });
  gsap.from('.compare__list li', { x: -40, opacity: 0, duration: .8, stagger: .08, ease: 'power3.out', scrollTrigger: { trigger: '.compare__list', start: 'top 80%' } });

  /* ---------------- Dashboard lights + gauges ---------------- */
  const dash = document.querySelector('.dash');
  if (dash) {
    const tl = gsap.timeline({ scrollTrigger: { trigger: dash, start: 'top 70%' } });
    tl.from('.dash', { y: 80, opacity: 0, duration: 1, ease: 'power3.out' })
      .from('.gauge__arc', { strokeDashoffset: 251, duration: 1.6, ease: 'power2.out' }, .2)
      .fromTo('.gauge--l .gauge__needle', { attr: { transform: 'rotate(-90 100 100)' } }, { attr: { transform: 'rotate(40 100 100)' }, duration: 1.6, ease: 'elastic.out(1, .5)' }, .2)
      .fromTo('.gauge--r .gauge__needle', { attr: { transform: 'rotate(-90 100 100)' } }, { attr: { transform: 'rotate(62 100 100)' }, duration: 1.6, ease: 'elastic.out(1, .5)' }, .3)
      .from('.light', { opacity: .15, duration: .25, stagger: .12 }, .5)
      .from('.light svg', { scale: .4, duration: .5, stagger: .12, ease: 'back.out(2.5)' }, .5);
  }

  /* ---------------- Generic section entrances ---------------- */
  gsap.utils.toArray('.section .head').forEach(h => {
    gsap.from(h.children, { y: 40, opacity: 0, duration: 1, stagger: .08, ease: 'power3.out', scrollTrigger: { trigger: h, start: 'top 85%' } });
  });
  gsap.utils.toArray('.why2 .card, .areas .area').forEach((c, i) => {
    gsap.from(c, { y: 60, opacity: 0, rotateX: -12, transformPerspective: 900, duration: 1, delay: (i % 3) * .08, ease: 'power3.out', clearProps: 'transform', scrollTrigger: { trigger: c, start: 'top 90%' } });
  });
  gsap.utils.toArray('.faq details, .visit > *').forEach((c, i) => {
    gsap.from(c, { y: 30, opacity: 0, duration: .8, delay: (i % 4) * .05, ease: 'power3.out', scrollTrigger: { trigger: c, start: 'top 92%' } });
  });

  /* ---------------- CTA: car drives in ---------------- */
  gsap.fromTo('.cta__car', { xPercent: 70, opacity: 0 }, { xPercent: 0, opacity: 1, ease: 'none', scrollTrigger: { trigger: '.cta--drive', start: 'top 95%', end: 'center 60%', scrub: 1 } });

  addEventListener('load', () => ScrollTrigger.refresh());
})();
