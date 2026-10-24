# Jala Samudra Institute — Isolated v2 rebuild

The public WordPress site and the existing production Pages site remain unchanged. Work on branch `rebuild/jsi-v2` is a **non-production preview**.

## Source and build
- `v2/index.html`: editorial homepage.
- `v2/publications/`, `v2/research/`, `v2/about/`, `v2/contact/`: institutional pages.
- `v2/data/publications.json`: index of ten migrated publications and working research taxonomy.
- `v2/scripts/build.py`: generates ten article reading routes using the legacy article bodies, and copies original media into `v2-dist/`.
- `v2/scripts/check_site.py`: checks generated routes, local links, images, page count and preview indexing safeguards.

Build locally from repository root:

```sh
python3 v2/scripts/build.py
python3 v2/scripts/check_site.py
python3 -m http.server 8000 --directory v2-dist
```

Open `http://localhost:8000/`. A successful CI run also uploads the `jsi-v2-site-preview` artifact. It is a ZIP of the generated static site, **not a live public URL**.

## Deployment isolation
For a separate Cloudflare Pages preview project, use build command `python3 v2/scripts/build.py && python3 v2/scripts/check_site.py`, output directory `v2-dist`, branch `rebuild/jsi-v2`. Do not reconfigure the existing production project to use this branch.

## Editorial integrity
Do not silently rewrite articles, invent author credentials, or describe taxonomy categories as completed research programs. Verify article text, images, references, dates, and historical URL mapping before launch. Preview pages deliberately include `noindex`, and generated `robots.txt` blocks crawling. **Remove these restrictions only as part of an approved production release.**

See `v2/RELEASE-CHECKLIST.md` for remaining gates.
