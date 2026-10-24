# JSI V2 — WordPress content parity audit (24 October 2026)

Source: `jalasamudrainstitute.WordPress.2026-10-23.xml` (WordPress export, 10 posts). Comparison target: `articles/<slug>/index.html` on `rebuild/jsi-v2`. This report distinguishes evidence from outstanding work.

## Findings

- All 10 WordPress post titles and article slugs were identified and mapped to the 10 migrated source article pages.
- The full original WordPress title of **Anarki Internasional, Persaingan Antar Negara, dan Limitasi Hukum Internasional:  Mengapa Negara Produsen (Kaya) tetap Kaya, dan Negara Konsumen (Miskin) tetap Miskin** was restored in the V2 catalog (commit `5afc08d`).
- Comparing visible text extracted from WordPress `content:encoded` with the legacy article `<article>` body, nine 2024 articles matched by normalized character count, except *Bunuh Diri Kognitif Industri Maritim Indonesia*, which differed by two characters under the two independent extraction methods (HTML entity decoding). Equal length is a screening check, **not proof of full text identity**.
- The 2026 *Di Balik Layar Bursa* article differs in normalized length (WordPress 48,530 characters; legacy article extraction 48,137 characters). Its legacy article starts with the substantive introductory paragraph, whereas the WordPress export contains additional header/layout material. It also includes adapted download blocks. A paragraph-by-paragraph comparison is still required.
- Browser QA passed in GitHub Actions run `40094663166`: Chromium at 360, 390, 768, 1024 and 1440px; archive search, reset, topic filtering and empty state. 25 screenshots uploaded.
- Production remains unchanged; preview is intentionally `noindex`.

## Remaining release blockers

1. Paragraph-by-paragraph content comparison for all ten posts, particularly the October 2026 study; confirm no meaningful text, tables, footnotes, figures, or downloads are missing.
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
