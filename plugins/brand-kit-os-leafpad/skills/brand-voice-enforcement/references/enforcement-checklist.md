# Brand Voice Enforcement Checklist

Use this checklist before delivering any brand-aligned content.

## Pre-flight checks

- [ ] **Brand kit loaded** — Is the correct brand kit's expression and governance data in context?
- [ ] **Audience identified** — Is the content targeting a specific persona or general audience?
- [ ] **Platform known** — Is the content for a specific channel (email, social, blog, ad)?

## Voice & tone

- [ ] Tone dimensions match brand settings (formal/casual, serious/playful, etc.)
- [ ] Voice archetype is consistent throughout
- [ ] Preferred terminology is used (check `preferred_terminology`)
- [ ] Avoided words/phrases are not present (check `negative_directory`)

## Governance

- [ ] No blacklisted claims or promises
- [ ] Compliance notes observed (regulatory, legal)
- [ ] Disclosure policy followed (AI disclosure, disclaimers)
- [ ] Behavioral constraints respected

## Quality

- [ ] Content serves the stated purpose
- [ ] Call-to-action is clear (if applicable)
- [ ] Length is appropriate for the platform
- [ ] Formatting follows brand visual style guidelines

## Blog SEO & structure (blog posts only)

These are measured checks. **Body length and title are hard, blocking gates.** Image, external sources, and internal links are strong recommendations (warnings), not publish blockers.

- [ ] **Body length ≥ 800 words** (HARD) — target 900+. Count the body prose (headings + paragraphs + list items), excluding the title and the disclosure footer. Under 800 is a hard fail.
- [ ] **Title is 8–12 words** (HARD) — count whitespace-separated words in the title. Outside 8–12 is a hard fail (`This Title Has Exactly Eight Words Here` = 7, fail). Revise the title, do not publish.
- [ ] **At least one image** embedded in the body (WARNING, not blocking) — try `leafpad_generate_image` (on-brand palette); if it fails server-side, fall back to Gamma/Higgsfield, else flag a manual-image task. A missing image does **not** block publish.
- [ ] **External sources cited** — where the article makes a factual, statistical, or trend claim, at least 2 credible external sources are linked (from the research step).
- [ ] **Internal links** — 2–4 links to existing Leafpad posts.
