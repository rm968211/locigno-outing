# Locigno Outing

The Cross Creek Locigno Outing site — pairings, groups, and tee times, styled after the
printed pairings sheet. Hosted on GitHub Pages; installable to a phone's home screen as a PWA.

## Updating for a new pairing

1. **The page** — edit `index.html`. Everything is static; look for `<!-- EDIT -->` comments.
   Each event is one `.event` card: the header holds the name, `(x holes)`, and the tee time;
   the table rows hold the groups; the `.gam` footer holds the buy-in and details.
   Seniors get ` <span class="sr">SR</span>` after their rank tag.
   The page can also be regenerated from a Toolkit spreadsheet's embedded save data —
   the current content came from `JeffsPairings.xlsx` (Cross creek 2026, iCloud Drive).
2. **The downloads** — replace the two files in `assets/`:
   - `assets/locigno-outing.pdf` — the formatted PDF from the Commissioners Toolkit
   - `assets/locigno-outing.xlsx` — the spreadsheet from the Commissioners Toolkit
   (Both currently contain placeholders.)
3. Commit and push — Pages redeploys automatically, and the service worker picks up
   fresh content on the next visit (network-first, cache only as offline fallback).

## Layout

- `index.html` — the whole page, self-contained styles and scripts
- `manifest.webmanifest`, `sw.js`, `icons/` — the PWA bits (install + offline)
- `assets/` — logo plus the downloadable PDF and spreadsheet
