# JSI v2 — Release checklist

## Confirmed in repository
- [x] Isolated rebuild branch `rebuild/jsi-v2` and `v2/` folder
- [x] Separate Home, Publications, Research Areas, About routes
- [x] Shared stylesheet and publication metadata
- [x] Ten publication records with canonical links to existing site
- [x] Search and topic filtering implementation
- [x] No changes to published article bodies
- [x] `noindex,nofollow` on prototype pages to prevent indexing of unfinished site

## Must be verified before production
- [ ] Configure separate Cloudflare preview/build output `v2`; verify real URLs
- [ ] Visual QA at 360, 390, 768, 1024 and 1440px
- [ ] Browser keyboard accessibility and contrast testing
- [ ] Confirm search and filtered links in deployed environment
- [ ] Validate complete media inventory and download originals to repository
- [ ] Verify article body parity, references, author, date and legal text
- [ ] Build v2 article reading template and import content without substantive edits
- [ ] Check every internal/external link and image response
- [ ] Define URL mapping and redirects before WordPress retirement
- [ ] Review SEO, sitemap, RSS, metadata and structured data
- [ ] Approve editorial taxonomy and authorship policy
- [ ] Remove prototype noindex only when launch-ready

## Editorial non-negotiables
- A publication has one canonical URL.
- Do not present thematic categories as completed research programs.
- Preserve original documents and record revisions transparently.
- Do not remove WordPress until redirects and historical URLs are accounted for.
