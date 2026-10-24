# JSI v2 — Release checklist

## Confirmed in repository
- [x] Isolated rebuild branch `rebuild/jsi-v2` and `v2/` folder
- [x] Separate Home, Publications, Research Areas, About and Contact routes
- [x] Shared stylesheet and publication metadata
- [x] Ten publication records with dedicated v2 article routes; original WordPress remains online
- [x] Search and topic filtering implementation
- [x] No changes to published article bodies
- [x] `noindex,nofollow` on prototype pages to prevent indexing of unfinished site

## Must be verified before production
- [ ] Configure separate Cloudflare preview/build output `v2`; verify real URLs
- [ ] Visual QA at 360, 390, 768, 1024 and 1440px
- [ ] Browser keyboard accessibility and contrast testing
- [ ] Confirm search and filtered links in deployed environment
- [x] Copy existing original media assets into the generated v2 site
- [ ] Visually verify all migrated images against their WordPress originals
- [ ] Verify article body parity, references, author, date and legal text
- [x] Generate ten v2 article reading pages from legacy HTML without substantive editorial rewriting
- [ ] Independently compare each generated article with its original publication
- [x] Automatically validate generated internal links and local assets
- [ ] Manually verify external links and image responses in deployed preview
- [ ] Define URL mapping and redirects before WordPress retirement
- [ ] Review SEO, sitemap, RSS, metadata and structured data (preview remains intentionally noindex)
- [ ] Approve editorial taxonomy and authorship policy
- [ ] Remove prototype noindex only when launch-ready

## Editorial non-negotiables
- A publication has one canonical URL.
- Do not present thematic categories as completed research programs.
- Preserve original documents and record revisions transparently.
- Do not remove WordPress until redirects and historical URLs are accounted for.
