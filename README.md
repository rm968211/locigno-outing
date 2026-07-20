# Locigno Outing

The Cross Creek Locigno Outing site — pairings, groups, and tee times, styled after the
printed pairings sheet. Hosted on GitHub Pages; installable to a phone's home screen as a PWA.

## Updating for a new pairing

1. Save the spreadsheet and the formatted PDF from the Commissioners Toolkit.
2. Drop them into `assets/` with these exact names (they're also the download links):
   - `assets/locigno-outing.xlsx`
   - `assets/locigno-outing.pdf`
3. Commit and push. A GitHub Action decodes the save data the Toolkit embeds in the
   spreadsheet's hidden `_meta` sheet, regenerates `index.html` from it, and commits
   the result — Pages redeploys automatically. No hand-editing needed.

The Action also reruns when `tools/` changes, and can be fired manually from the
Actions tab (workflow_dispatch). If the spreadsheet has no save data (not a Toolkit
export), the run fails loudly instead of publishing a stale page.

To tweak the page's look, edit `tools/template.html` (the `@@...@@` tokens are filled
by `tools/build.py`) — or regenerate locally with `python3 tools/build.py` (stdlib only).

## Layout

- `index.html` — the generated page (don't edit by hand; it gets overwritten)
- `tools/build.py`, `tools/template.html` — the generator and its page template
- `.github/workflows/build.yml` — the drop-a-spreadsheet automation
- `manifest.webmanifest`, `sw.js`, `icons/` — the PWA bits (install + offline)
- `assets/` — logo plus the downloadable PDF and spreadsheet
