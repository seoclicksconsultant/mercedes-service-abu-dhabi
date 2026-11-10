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

The shared `<head>`, header and footer live in `_src/partials/`. Edit those once and rebuild.

## Build and preview

```bash
python3 build.py                 # writes index.html, about-us/, contact/, privacy-policy/, terms-conditions/
python3 -m http.server 8765      # then open http://127.0.0.1:8765/
```

Pages use clean URLs (`about-us/`), so preview through a local server rather than opening the files directly.

## Design

- Font: Poppins (Google Fonts), body and paragraph text 16px.
- Palette from current Mercedes-AMG paint: Obsidian Black `#0b0d11`, Selenite Grey `#7c838e`, Alpine Grey `#e8ebef`, Polar White, with Mercedes digital blue `#0078d6` for actions. Tokens are at the top of `assets/css/style.css`.
- Modern CSS without a build step: View Transitions between pages, scroll-driven reveal animations (with an IntersectionObserver fallback), Popover API mobile menu, animated native `<details>` FAQ, container queries and `color-mix()`.
- The estimate form needs no server. It opens WhatsApp (+971 58 609 5249) with the customer's details filled in.
- JSON-LD: `AutoRepair` business schema on every page and `FAQPage` on the home page.

## Images

All images are WebP in `assets/img/`. Car cutouts (transparent background) were made with the macOS Vision framework from these Unsplash photos (Unsplash License, free for commercial use):

| File | Unsplash photo |
| --- | --- |
| g63-obsidian-black.webp | https://unsplash.com/photos/black-mercedes-benz-g-class-on-wet-track-bYR-hWhX2so |
| amg-gt-selenite-grey.webp | https://unsplash.com/photos/a-sleek-grey-mercedes-benz-sports-car-parked-outdoors-Vo28HDfaYR4 |
| s-class-w223.webp, s-class-street.webp | https://unsplash.com/photos/black-mercedes-benz-sedan-on-cobblestone-street-y3neNkE6efI |
| g-class-silver.webp, g-class-coast.webp | https://unsplash.com/photos/silver-mercedes-benz-g-class-near-table-mountain-PtJDCD4fTI4 |
| amg-gt-black.webp | https://unsplash.com/photos/a-sleek-black-mercedes-benz-sports-car-parked-outdoors-VH_oOHVhAdI |
| g63-red.webp | https://unsplash.com/photos/red-mercedes-benz-g-class-suv--Pt97OtdYWY |
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

`favicon.webp` is the Exotic Auto Services favicon from exoticautoservices.ae.

## Still to confirm with the client

- Warranty length: the copy still reads `[X]-month` in two places on the home page (buyer's checklist table and "Warranty on Our Work"). Exotic's site does not state a warranty period.
- Final domain: add `<link rel="canonical">` and absolute `og:image` URLs once the live domain is known.
