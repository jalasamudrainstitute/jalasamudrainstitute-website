# JSI V2 — WordPress content parity audit (24 October 2026)

Source: `jalasamudrainstitute.WordPress.2026-10-23.xml` (WordPress export, 10 posts). Comparison target: `articles/<slug>/index.html` on `rebuild/jsi-v2`. This report distinguishes evidence from outstanding work.

## Findings

- All 10 WordPress post titles and article slugs were identified and mapped to the 10 migrated source article pages.
- The full original WordPress title of **Anarki Internasional, Persaingan Antar Negara, dan Limitasi Hukum Internasional:  Mengapa Negara Produsen (Kaya) tetap Kaya, dan Negara Konsumen (Miskin) tetap Miskin** was restored in the V2 catalog (commit `5afc08d`).
- A direct normalized **full-string equality comparison** of the WordPress export's `content:encoded` against the legacy article `<article>` body confirms **all nine 2024 articles match exactly**, including *Bunuh Diri Kognitif Industri Maritim Indonesia*. The earlier two-character discrepancy was caused by inconsistent HTML entity normalization, not changed editorial content. Comparison used the archived 33-file site-build artifact `github-actions-artifact-12553506817.zip` and the original WordPress XML.
- The 2026 *Di Balik Layar Bursa* article differs in normalized length (WordPress 48,530 characters; legacy article 48,137 characters). The WordPress original has 185 characters of introductory category/title text before the substantive article; the remainder is 48,345 characters. A character-level diff of the remainder indicates the residual differences are concentrated in the final downloadable PDF/Word attachment blocks (link labels and filenames). **Editorial paragraphs appear preserved**, but the attachment URLs, file availability and figure/table fidelity still require independent verification.
- Browser QA passed in GitHub Actions run `40094663166`: Chromium at 360, 390, 768, 1024 and 1440px; archive search, reset, topic filtering and empty state. 25 screenshots uploaded.
- Production remains unchanged; preview is intentionally `noindex`.

## Remaining release blockers

1. Independently confirm attachment URLs, figures/tables and downloadable files in the October 2026 study. Full normalized text equality is confirmed for the other nine posts.
2. Verify image/media availability and fidelity against original WordPress pages.
3. Review publication authorship, date metadata and provisional taxonomy.
4. Verify links and interactive behavior on deployed preview (as distinct from local Chromium build).
5. Approve production domain, canonical URLs, sitemap/feed, redirects and indexability before merging or deploying production.

Do not treat this report as production launch approval.

## Additional paragraph-fingerprint comparison (24 October 2026)

Compared all WordPress WXR post-body paragraph sequences with GitHub legacy article-body paragraph sequences, stripping markup and collapsing whitespace. **Eight of ten** matched exactly in paragraph count and 32-bit rolling text fingerprint: D4, Buddha/Vedas, Gradasi, Komeng, Diktator Dunia Maya, AUKUS, Anarki Internasional, and Balance of Power. This is stronger than the character-count screening above, but a rolling fingerprint is not a cryptographic identity proof.

- **Bunuh Diri Kognitif:** 12 paragraphs on both sides, but different fingerprint and a two-character raw-body length difference; requires focused inspection.
- **Di Balik Layar Bursa:** WordPress 185 paragraphs, legacy HTML 183. Original WordPress contains full PDF/DOCX attachment blocks; the legacy article substitutes concise download panels. Verify that the 183 prose paragraphs are unchanged, and that both files remain accessible.
- **Embedded media:** none of the ten WXR post bodies contains an inline `<img>` tag. Nine contain YouTube links; the tenth has document attachments. Remote video embeds, thumbnails and document downloads require separate live checks.

The release remains preview-only until the two discrepancies and live asset checks are resolved.

## Media inventory and browser QA closure — 24 October 2026

The WordPress XML contains **zero inline `<img>` elements in all ten posts**. Nine 2024 posts contain one WordPress YouTube embed figure each; the 2026 capital-market article has no inline figure/image. The video references remain in the migrated HTML, but **rendering of those embeds as playable video has not been confirmed**; the original WordPress markup contains plain YouTube URLs within embed wrappers.

The 2026 article references four unique PDF/DOCX URLs: two external MSCI PDFs, one JSI-authored PDF, and one JSI-authored DOCX. The migrated HTML retains both MSCI PDF links and the DOCX link. The JSI-authored PDF was intentionally localized to `/assets/original/di-balik-layar-bursa-perdagangan-terkoordinasi-jejak-rekening-dan-ancaman-standalone-market-msci-terhadap-bursa-efek-indonesia_16_oktober_2026-1.pdf`; this file **exists in the repository**. HTTP download availability on deployed preview has not been independently verified.

Latest complete CI result for commit `02bb1bd`: quality checks **success** (run `40095760111`), Chromium browser QA **success** (run `40095760157`). Browser QA now visits every migrated article at five widths and checks headings, nonempty article bodies, overflow, broken loaded images and relative internal links. This is automated testing, **not manual review of screenshots**.

**Release position:** V2 is a functional, tested **private preview**, not a production launch. Remaining work requiring explicit approval is selecting the final production hostname, redirect/canonical strategy and switching indexability; external media/download availability and visual review should also be checked before launch. No production merge or domain cutover has occurred.
