# Jala Samudra Institute — Clean Rebuild

This is a **new, isolated website**. The existing root website and WordPress remain unchanged.

## Architecture
- `v2/index.html`: editorial homepage preview.
- `v2/assets/site.css`: one shared visual system.
- `v2/assets/site.js`: accessible publication search and topic filtering.
- `v2/data/publications.json`: source-controlled publication index; article bodies are not modified.

## Editorial integrity
Existing publications are preserved at their original URLs. Never alter substantive article text without author approval. Verify original imagery, references, dates, and legacy redirects before launch.

## Deployment
For a Cloudflare Pages preview, configure a separate project with build output `v2` on branch `rebuild/jsi-v2`. Do not point production to `v2` before QA.

## Release gates
Content parity, asset inventory, accessible responsive navigation, all links, SEO, mobile/desktop QA, and rollback readiness.
