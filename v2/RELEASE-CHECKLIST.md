# JSI v2 — Release checklist

## Confirmed in repository
- [x] Isolated rebuild branch `rebuild/jsi-v2` and `v2/` folder
- [x] Separate Home, Publications, Research Areas, About and Contact routes
- [x] Shared stylesheet and publication metadata
- [x] Ten publication records with dedicated v2 article routes; original WordPress remains online
- [x] Search and topic filtering implementation
- [x] No changes to published article bodies
- [x] `noindex` on prototype pages and disallow-all `robots.txt` to prevent indexing of unfinished site

## Must be verified before production
- [x] Configure separate Cloudflare preview with build command `python3 v2/scripts/build.py && python3 v2/scripts/check_site.py` and output `v2-dist`; Cloudflare build and deployment succeeded on 2026-10-24 at https://jsi-v2-review.pages.dev/
- [x] Automated Chromium screenshots and horizontal-overflow checks at 360, 390, 768, 1024 and 1440px (GitHub Actions run 40094663166, success)
- [x] Review 25 captured screenshots across five core pages and five viewport widths for overall layout and horizontal overflow
- [ ] Compare article images visually with their WordPress originals (not covered by core-page screenshots)
- [x] Add keyboard skip navigation and verify in-page anchor targets in automated QA
- [ ] Browser keyboard accessibility and contrast testing
- [x] Browser QA of archive search, reset, topic filtering and empty state against the built site (run 40094663166)
- [ ] Independently verify the same interactions on the deployed public preview
- [x] Copy existing original media assets into the generated v2 site
- [ ] Visually verify all migrated images against their WordPress originals
- [x] Enforce generated HTML article-body parity with the migrated repository source, plus title/date checks at build time
- [ ] Independently verify references, authorship, dates, images and legal text against the original WordPress publications
- [x] Generate ten v2 article reading pages from legacy HTML without substantive editorial rewriting
- [ ] Independently compare all ten generated articles with the original WordPress publication (repository parity alone is insufficient)
- [x] Automatically validate generated internal links and local assets
- [ ] Manually verify external links and image responses in deployed preview
- [x] Generate and validate a one-to-one source URL mapping for the ten original WordPress articles (`data/source-url-map.json` in built preview)
- [ ] Decide and implement historical redirects only when the final production domain and WordPress retirement plan are confirmed
- [x] Add original-body-derived descriptions to migrated article metadata
- [x] Generate and XML-validate preview sitemap and RSS feed; Cloudflare build succeeded
- [ ] Audit production SEO metadata, canonical URLs, structured data, sitemap/RSS hostnames and indexing at launch (preview remains intentionally noindex)
- [ ] Approve editorial taxonomy and authorship policy
- [ ] Remove prototype noindex only when launch-ready

## Editorial non-negotiables
- A publication has one canonical URL.
- Do not present thematic categories as completed research programs.
- Preserve original documents and record revisions transparently.
- Do not remove WordPress until redirects and historical URLs are accounted for.
