# Mercedes Repair Abu Dhabi | Exotic Auto Services

Static website (no framework) for the Mercedes-Benz service pages of Exotic Auto Services LLC, M-21 Mussafah, Abu Dhabi.

## Pages

| URL | Source |
| --- | --- |
| `/` | `_src/pages/index.html` |
| `/about-us/` | `_src/pages/about.html` |
| `/contact/` | `_src/pages/contact.html` |
| `/privacy-policy/` | `_src/pages/privacy-policy.html` |
| `/terms-conditions/` | `_src/pages/terms-conditions.html` |
| `/mercedes-brake-repair/` and 8 more service pages | `_src/services/*.md` |

### Service pages

The nine service pages (brake, transmission, engine, painting, body shop, diagnostics, oil change, electrical, AC) are generated from the client's copy in `_src/services/<slug>.md` by `_src/services_build.py`. Per-page settings (accent colour, hero car and photos, chips, stats and chart data) live in `_src/services_config.py`. Every number in a stat or chart comes from that page's copy.

Each service page has a cinematic hero (darkened HD workshop photo with slow zoom, glowing sparks canvas, HD car on a rotating 3D turntable with a light sweep, mouse-depth parallax), a pinned 3D coverflow for the services list, a 3D rotating ring for the first reference table and a stat rail for "why act early". Hero photos are `hero-<service>.webp` (Pexels, ids in the table below).

To change wording, edit the `.md` file and run `python3 build.py`. Tables are turned into designed components automatically: symptom tables become a filterable urgency grid, "Situation / Best option" tables become a decision explorer, Yes/No tables a comparison matrix, paint codes become colour swatches, warning lights a dashboard, and other reference tables become spec cards.

The shared `<head>`, header and footer live in `_src/partials/`. Edit those once and rebuild.

## Build and preview

```bash
python3 build.py                 # writes index.html, about-us/, contact/, privacy-policy/, terms-conditions/
python3 -m http.server 8765      # then open http://127.0.0.1:8765/
```

Pages use clean URLs (`about-us/`), so preview through a local server rather than opening the files directly.

## Design

- Font: Poppins (Google Fonts), body and paragraph text 16px.
- Theme: dark luxury (obsidian stage, graphite surfaces, chrome headings, studio spotlights, mirror-floor reflections under the cars). The theme layer is `assets/css/luxe.css`, generated on every build by `_src/luxe_gen.py` from the light stylesheets plus the hand-written rules in `_src/luxe_manual.css`. Edit `luxe_manual.css`, not `luxe.css`.
- Palette from current Mercedes-AMG paint: Obsidian Black `#0b0d11`, Selenite Grey `#7c838e`, Alpine Grey `#e8ebef`, Polar White, with Mercedes digital blue `#0078d6` for actions. Tokens are at the top of `assets/css/style.css`.
- Modern CSS without a build step: View Transitions between pages, scroll-driven reveal animations (with an IntersectionObserver fallback), Popover API mobile menu, animated native `<details>` FAQ, container queries and `color-mix()`.
- The estimate form needs no server. It opens WhatsApp (+971 58 609 5249) with the customer's details filled in.
- JSON-LD: `AutoRepair` business schema on every page and `FAQPage` on the home page.

## Images

All images are WebP in `assets/img/`. Photos from Unsplash (Unsplash License, free for commercial use):

| File | Unsplash photo |
| --- | --- |
| s-class-street.webp | https://unsplash.com/photos/black-mercedes-benz-sedan-on-cobblestone-street-y3neNkE6efI |
| g-class-coast.webp | https://unsplash.com/photos/silver-mercedes-benz-g-class-near-table-mountain-PtJDCD4fTI4 |
| workshop-e-class.webp | https://unsplash.com/photos/mechanic-working-on-a-car-engine-in-a-workshop-XP8o9_Arwqg |
| mechanic-engine.webp | https://unsplash.com/photos/mechanic-working-on-car-engine-UZUzvJEvKnI |
| under-car-suspension.webp | https://unsplash.com/photos/a-man-working-on-a-car-under-a-vehicle-K5624F8cipE |
| engine-bay.webp | https://unsplash.com/photos/close-up-of-a-car-engine-with-many-wires-VZcQi2ZS2TU |
| interior-amg.webp | https://unsplash.com/photos/black-mercedes-benz-car-interior-5DremXTTKE0 |
| steering-wheel.webp | https://unsplash.com/photos/black-mercedes-benz-steering-wheel-jbaWsWgimJw |
| g-class-tunnel.webp | https://unsplash.com/photos/black-mercedes-benz-g-class-in-tunnel-qfniR1cYiOI |
| e-class-night.webp | https://unsplash.com/photos/silver-mercedes-coupe-on-road-during-night-time-GfA_3_hLUNA |
| mercedes-star.webp | https://unsplash.com/photos/mercedes-benz-emblem-gs3duh5iqkw |
| amg-gt-monaco.webp | https://unsplash.com/photos/matte-black-mercedes-amg-gt-in-monaco-MaraDXSaTho |

HD car cutouts (Pexels License, free for commercial use; cut out at 5000px+ and exported at 2200px). Photo page: `https://www.pexels.com/photo/<id>/`

| File | Pexels photo id |
| --- | --- |
| s-class-w223-hd.webp | 18369291 |
| s-class-blue.webp | 26691371 |
| g63-black-hd.webp | 15610277 |
| g-class-green.webp | 18403260 |
| amg-gt-r-blue.webp | 16511358 |
| amg-gt63-white.webp | 7662147 |
| eqe-53-amg-black.webp | 29830328 |
| hero-brake / transmission / engine | 34277926 / 4756887 / 12658302 |
| hero-painting / body / diagnostics | 17992463 / 33814734 / 4116193 |
| hero-oil / electrical / ac | 8478259 / 11968597 / 12066296 |

Service-page images (Unsplash License; Unsplash photo id in brackets, open as `https://unsplash.com/photos/<id>`):

| File | Source photo id |
| --- | --- |
| brake-caliper-red / amg-wheel-caliper | 1611760425078-0db242ad4b74 / 1748172215389-cc4691924dbd |
| gearbox-cutaway / gear-shifter | 1711199694531-e982a79ea381 / 1606128031531-52ae98c9707a |
| amg-v8-engine / amg-engine-cover | 1653491888797-763405227051 / 1764872139995-92da69a2eb4e |
| paint-detailing / paint-booth | 1652987086612-d948b775d358 / 1676035291793-645c307e5a4e |
| body-technician / body-sanding | 1727893359929-9980a2171105 / 1786489785858-b64715400a37 |
| diagnostic-scan / diagnostic-laptop | 1771340012378-3c86cb649193 / 1727893372771-b4ccae9b9f0b |
| oil-pour-mercedes / oil-golden | 1771340742493-52fbd5476ccb / 1768689033119-c3ac1e437d20 |
| ev-engine-bay / car-battery | 1767990495521-95cceb571125 / 1765211003026-f7666ea3a948 |
| ac-vents / s-class-door-vent | 1565534355217-85fcfb04ce71 / 1780296269515-0c8c068d0767 |

`favicon.svg` and `apple-touch-icon.webp` are the site's own mark (not the Exotic logo).

## Still to confirm with the client

- Warranty length: the copy still reads `[X]-month` in two places on the home page (buyer's checklist table and "Warranty on Our Work") and on the engine repair page (why choose us + FAQ). The painting page reads `[X]-year`. Exotic's site does not state a warranty period.
- Painting page: `[paint brand]` (the refinish paint system used) still needs the real brand name.
- Diagnostics page: the copy had an editor note to add the diagnostic fee (or say it is credited against the repair). The note is hidden; the page says "We confirm the diagnostic fee before we start." Add the fee to `_src/services/mercedes-diagnostics.md` if wanted.
- Final domain: add `<link rel="canonical">` and absolute `og:image` URLs once the live domain is known.
