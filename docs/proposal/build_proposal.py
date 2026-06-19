#!/usr/bin/env python3
"""Build the Brand Kit OS x Leafpad partnership proposal PDF."""
from fpdf import FPDF

FONT_DIR = "/usr/share/fonts/truetype/liberation"
GREEN = (20, 83, 45)        # deep green headings
GREEN2 = (29, 107, 58)      # accent
INK = (31, 42, 36)
MUTED = (92, 107, 98)
SOFT_BG = (234, 244, 238)
SOFT_BORDER = (207, 232, 214)
ROW_ALT = (247, 250, 248)
TH_BG = (234, 244, 238)
BADGE = (29, 107, 58)
BADGE_SOFT = (207, 232, 214)

PAGE_W = 210
ML, MR, MT, MB = 20, 20, 20, 18
CONTENT_W = PAGE_W - ML - MR


class PDF(FPDF):
    def __init__(self):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.set_margins(ML, MT, MR)
        self.set_auto_page_break(True, margin=MB)
        self.add_font("Lib", "", f"{FONT_DIR}/LiberationSans-Regular.ttf")
        self.add_font("Lib", "B", f"{FONT_DIR}/LiberationSans-Bold.ttf")
        self.add_font("Lib", "I", f"{FONT_DIR}/LiberationSans-Italic.ttf")
        self.add_font("Lib", "BI", f"{FONT_DIR}/LiberationSans-BoldItalic.ttf")
        self.set_font("Lib", "", 10.5)
        self._footer_on = False

    def footer(self):
        if not self._footer_on:
            return
        self.set_y(-14)
        self.set_font("Lib", "", 7.5)
        self.set_text_color(150, 160, 152)
        self.cell(0, 5, "Brand Kit OS  ×  Leafpad  —  Partnership Proposal", align="L")
        self.cell(0, 5, f"{self.page_no()}", align="R")


def H2(pdf, text):
    pdf.ln(3)
    if pdf.get_y() > 250:
        pdf.add_page()
    pdf.set_font("Lib", "B", 14)
    pdf.set_text_color(*GREEN)
    pdf.multi_cell(CONTENT_W, 7, text)
    y = pdf.get_y() + 0.5
    pdf.set_draw_color(*SOFT_BORDER)
    pdf.set_line_width(0.5)
    pdf.line(ML, y, ML + CONTENT_W, y)
    pdf.ln(3)


def H3(pdf, text):
    pdf.ln(1.5)
    pdf.set_font("Lib", "B", 11.5)
    pdf.set_text_color(*GREEN2)
    pdf.multi_cell(CONTENT_W, 5.5, text)
    pdf.ln(1)


def para(pdf, segments, lh=5.2, size=10.5, space_after=2.0):
    """segments: list of (text, style) where style in '', 'B', 'I', 'BI'."""
    if isinstance(segments, str):
        segments = [(segments, "")]
    pdf.set_text_color(*INK)
    for text, style in segments:
        pdf.set_font("Lib", style, size)
        pdf.write(lh, text)
    pdf.ln(lh)
    if space_after:
        pdf.ln(space_after)


def bullets(pdf, items, lh=5.2, size=10.5):
    pdf.set_text_color(*INK)
    for item in items:
        if isinstance(item, str):
            item = [(item, "")]
        x = ML + 4
        pdf.set_xy(ML + 1.5, pdf.get_y())
        pdf.set_font("Lib", "B", size)
        pdf.set_text_color(*GREEN2)
        pdf.cell(2.5, lh, "•")
        pdf.set_xy(x, pdf.get_y())
        pdf.set_text_color(*INK)
        # render wrapped text in a reduced width using write within a sub-box
        start_y = pdf.get_y()
        pdf.set_left_margin(x)
        for text, style in item:
            pdf.set_font("Lib", style, size)
            pdf.write(lh, text)
        pdf.ln(lh)
        pdf.set_left_margin(ML)
    pdf.ln(1.5)


def callout(pdf, label, segments):
    pad = 4
    # measure height by rendering into a temp? Simpler: estimate via multi_cell dry-run
    pdf.ln(1)
    x0 = ML
    y0 = pdf.get_y()
    inner_w = CONTENT_W - 2 * pad
    # Pre-compute height using split_only
    pdf.set_font("Lib", "", 10)
    # Build a plain string for measurement
    plain = "".join(s for s, _ in segments)
    lines = pdf.multi_cell(inner_w, 5, plain, dry_run=True, output="LINES")
    body_h = len(lines) * 5
    total_h = body_h + 5 + 2 * pad  # label line + padding
    if y0 + total_h > 270:
        pdf.add_page()
        y0 = pdf.get_y()
    pdf.set_fill_color(*SOFT_BG)
    pdf.set_draw_color(*SOFT_BORDER)
    pdf.set_line_width(0.3)
    pdf.rect(x0, y0, CONTENT_W, total_h, style="DF")
    # label
    pdf.set_xy(x0 + pad, y0 + pad - 0.5)
    pdf.set_font("Lib", "B", 8)
    pdf.set_text_color(*GREEN2)
    pdf.cell(inner_w, 4, label.upper())
    # body with inline styles
    pdf.set_xy(x0 + pad, y0 + pad + 4)
    pdf.set_left_margin(x0 + pad)
    pdf.set_text_color(*INK)
    for text, style in segments:
        pdf.set_font("Lib", style, 10)
        pdf.write(5, text)
    pdf.set_left_margin(ML)
    pdf.set_xy(x0, y0 + total_h)
    pdf.ln(3)


def table(pdf, headers, rows, widths, fs=8.6, header_fs=8.8):
    line_h = 4.4
    pdf.set_draw_color(*SOFT_BORDER)
    pdf.set_line_width(0.2)

    def row_height(cells, font_size):
        maxlines = 1
        for txt, w in zip(cells, widths):
            pdf.set_font("Lib", "", font_size)
            lines = pdf.multi_cell(w - 3, line_h, str(txt), dry_run=True, output="LINES")
            maxlines = max(maxlines, len(lines))
        return maxlines * line_h + 2

    def draw_row(cells, font_size, bold=False, fill=None, text_color=INK):
        h = row_height(cells, font_size)
        if pdf.get_y() + h > 280:
            pdf.add_page()
            # redraw header
            draw_row(headers, header_fs, bold=True, fill=TH_BG, text_color=GREEN)
        x = ML
        y = pdf.get_y()
        for txt, w in zip(cells, widths):
            if fill:
                pdf.set_fill_color(*fill)
                pdf.rect(x, y, w, h, style="F")
            pdf.rect(x, y, w, h, style="D")
            pdf.set_xy(x + 1.5, y + 1)
            pdf.set_font("Lib", "B" if bold else "", font_size)
            pdf.set_text_color(*text_color)
            pdf.multi_cell(w - 3, line_h, str(txt), align="L")
            x += w
        pdf.set_xy(ML, y + h)

    draw_row(headers, header_fs, bold=True, fill=TH_BG, text_color=GREEN)
    for i, r in enumerate(rows):
        draw_row(r, fs, fill=ROW_ALT if i % 2 else (255, 255, 255))
    pdf.ln(3)


pdf = PDF()

# ---------------- COVER ----------------
pdf.add_page()
pdf.ln(34)
pdf.set_font("Lib", "B", 9)
pdf.set_text_color(*GREEN2)
pdf.cell(0, 5, "PARTNERSHIP PROPOSAL   ·   CONFIDENTIAL")
pdf.ln(10)
pdf.set_font("Lib", "B", 30)
pdf.set_text_color(*GREEN)
pdf.cell(0, 13, "Brand Kit OS  ×  Leafpad")
pdf.ln(15)
pdf.set_font("Lib", "", 14)
pdf.set_text_color(59, 74, 65)
pdf.multi_cell(CONTENT_W, 7, "Toward Natively Compatible Products for Automated, On-Brand Blog Publishing")
pdf.ln(8)
pdf.set_font("Lib", "", 10.5)
pdf.set_text_color(*MUTED)
pdf.multi_cell(150, 5.4,
    "A proposal to make Brand Kit OS and Leafpad work together natively — pairing Leafpad's "
    "publishing engine with Brand Kit OS's editorial intelligence so users can generate "
    "consistently on-brand blog content end to end, with minimal manual effort.")
pdf.ln(14)
# meta box
mb_y = pdf.get_y()
pdf.set_draw_color(*GREEN2)
pdf.set_line_width(0.9)
pdf.line(ML, mb_y, ML, mb_y + 26)
pdf.set_line_width(0.2)
meta = [
    ("Prepared for:", " The Leafpad Team"),
    ("Prepared by:", " Brand Kit OS"),
    ("Date:", " June 19, 2026"),
    ("Re:", " Native MCP compatibility & shared field-mapping standard"),
]
pdf.set_xy(ML + 4, mb_y + 1)
for k, v in meta:
    pdf.set_x(ML + 4)
    pdf.set_font("Lib", "B", 10)
    pdf.set_text_color(*INK)
    pdf.write(6, k)
    pdf.set_font("Lib", "", 10)
    pdf.set_text_color(59, 74, 65)
    pdf.write(6, v)
    pdf.ln(6)

pdf._footer_on = True

# ---------------- 1. PURPOSE ----------------
pdf.add_page()
H2(pdf, "1. Purpose & Framing")
para(pdf, [
    ("This is first and foremost a ", ""), ("partnership proposal", "B"),
    (", not a feature-request list. Our goal is to build a plugin that lets users leverage the "
     "distinct strengths of ", ""), ("both", "B"),
    (" products — Leafpad's publishing and generation engine, and Brand Kit OS's brand "
     "intelligence — to produce automated, on-brand blog posts for their websites.", ""),
])
para(pdf, [
    ("We have already built a working integration through the Model Context Protocol (MCP), and it "
     "works well today. This document explains ", ""), ("how", "I"),
    (" the two products complement each other, proposes a ", ""),
    ("shared field-mapping standard", "B"),
    (" so an AI agent can treat our data models as interoperable, and outlines a small set of ", ""),
    ("MCP exposures", "B"),
    (" that would take the combined experience from “works” to “native.”", ""),
])
callout(pdf, "The ask in one line", [
    ("Let's make Brand Kit OS and Leafpad ", ""), ("natively compatible", "B"),
    (", so a user with both can go from brand strategy to published, on-brand blog post with a "
     "single automated pipeline.", ""),
])

# ---------------- 2. WHY THE TWO FIT ----------------
H2(pdf, "2. Why the Two Products Fit Together")
para(pdf, [
    ("Leafpad's native understanding of a brand comes from its knowledge base, which retrieves over "
     "the organization's ", ""), ("existing published site content", "I"),
    (". That makes Leafpad's generation ", ""), ("reactive", "B"),
    (" — it mirrors what a brand has already said. Powerful, but it has three structural limits:", ""),
])
bullets(pdf, [
    [("Cold start: ", "B"), ("new or thin sites have little content to imitate, so output drifts generic.", "")],
    [("Drift compounding: ", "B"), ("if existing content is inconsistent, generation learns and amplifies it.", "")],
    [("No intended state: ", "B"), ("retrieval captures what a brand has said — never what it should "
      "sound like, who it is for, or what it must never do.", "")],
])
para(pdf, [
    ("Brand Kit OS supplies that missing layer: a structured source of truth for what a brand ", ""),
    ("intends to be", "B"),
    (" — voice, personality, governance, audience, products, and terminology. Together, the model "
     "becomes ", ""), ("prescriptive", "B"), (" instead of reactive.", ""),
])

H3(pdf, "What each product brings")
table(pdf,
    ["Leafpad — the publishing body", "Brand Kit OS — the editorial brain"],
    [
        ["Generation engine & scheduled topic generation", "Prescriptive voice, tone & verbal style"],
        ["Publishing surface, drafts, SEO fields, tags", "Governance: forbidden terms, disclosures, formatting"],
        ["Brand-styled AI image generation (palette auto-applied)", "Audience & persona targeting"],
        ["Knowledge base over existing site content (retrieval)", "Product positioning, differentiators, competitive angle"],
        ["Google Analytics integration & native analytics view", "Preferred terminology & deliberate SEO lexicon"],
    ],
    [CONTENT_W / 2, CONTENT_W / 2])

H3(pdf, "The complement, field by field")
table(pdf,
    ["Leafpad gap (native)", "Brand Kit OS fills it with"],
    [
        ["No explicit voice model — only imitation via retrieval", "Voice archetypes, tone, verbal style, preferred terminology"],
        ["No personality consistency across posts", "Traits, values, principles, moods"],
        ["No compliance / governance guardrails", "Negative directory, disclosure policy, formatting constraints"],
        ["No audience targeting", "Audience personas & persona-aware framing"],
        ["No accurate product positioning or CTAs", "Products, differentiators, callouts"],
        ["Freeform SEO keywords", "Branded, deliberate keyword set & preferred terminology"],
    ],
    [CONTENT_W * 0.42, CONTENT_W * 0.58])

# ---------------- 3. HOW IT WORKS TODAY ----------------
pdf.add_page()
H2(pdf, "3. How the Integration Works Today")
para(pdf, [
    ("Because Leafpad's generation runs server-side, Brand Kit OS adds value at the two points where "
     "the MCP exposes a seam. Both work now.", ""),
])
H3(pdf, "Leverage point 1 — Pre-generation brand brief")
para(pdf, [
    ("Leafpad's scheduled-post tool accepts an optional ", ""), ("prompt", "B"),
    (". Brand Kit OS compiles a full brand brief — voice, governance rules, audience, preferred and "
     "forbidden terms — into that prompt, so even Leafpad's autonomous scheduled drafts come out "
     "on-brand instead of generic. This is the single highest-leverage integration: it upgrades the "
     "hands-off path, not just the manual one.", ""),
])
H3(pdf, "Leverage point 2 — Pre-publish QA on the draft")
para(pdf, [
    ("Every generated post lands as a ", ""), ("draft", "B"),
    (". The agent reads the draft back, audits it against governance (forbidden terms, disclosures, "
     "formatting) and voice, and adjusts it before publish. Because this happens entirely in draft "
     "state, it is iteration — not remediation — with ", ""), ("no business-value loss", "B"),
    (". The draft buffer is a safe staging area, and the user controls the publish gate.", ""),
])
callout(pdf, "Net effect", [
    ("Brand Kit OS becomes the standard a Leafpad blog is measured against — at generation time and "
     "again at publish time — giving users consistency at scale, across every post and every future "
     "scheduled post.", ""),
])
H3(pdf, "Strategic benefits this unlocks for Leafpad users")
bullets(pdf, [
    [("Cold-start solved: ", "B"), ("brands with no site content still get on-brand output on day one.", "")],
    [("Consistency over time: ", "B"), ("one source of truth anchors every post against drift.", "")],
    [("Multi-brand / agency leverage: ", "B"), ("each brand kit is a distinct, swappable voice.", "")],
    [("Compliance-grade content: ", "B"), ("disclosures and forbidden-term enforcement make autonomous "
      "publishing safe for regulated brands.", "")],
    [("Brand-aware imagery: ", "B"), ("Leafpad applies palette and visual style automatically; Brand Kit "
      "OS supplies the on-brand subject and motif as the prompt.", "")],
])

# ---------------- 4. COMPATIBILITY PROTOCOL ----------------
pdf.add_page()
H2(pdf, "4. Proposal: A Shared Field-Compatibility Protocol")
para(pdf, [
    ("The most valuable near-term step requires ", ""), ("no engineering on either side", "B"),
    (": a shared reference that tells an AI agent ", ""),
    ("when a Brand Kit OS field and a Leafpad field are the same thing", "I"),
    (", and what transform makes them interoperable. Today an agent knows what to send, but not the ", ""),
    ("compatibility semantics", "B"), (" behind each pairing. This protocol encodes that.", ""),
])
para(pdf, [("Each pairing carries one of five ", ""), ("match types", "B"),
           (", so the agent knows how to treat it:", "")], space_after=1)
bullets(pdf, [
    [("Exact", "B"), (" — same field, send as-is.", "")],
    [("Transform", "B"), (" — same meaning, needs a deterministic conversion.", "")],
    [("Partial", "B"), (" — related but not identical; map with a rule + caveat.", "")],
    [("No-equivalent", "B"), (" — exists in one product only; drop or hold.", "")],
    [("Auto-handled", "B"), (" — set server-side by Leafpad; the agent must not send it.", "")],
])
w = [CONTENT_W * 0.25, CONTENT_W * 0.17, CONTENT_W * 0.16, CONTENT_W * 0.42]
table(pdf,
    ["Brand Kit OS field", "Leafpad field", "Match type", "Protocol for the agent"],
    [
        ["Drafted title", "name", "Exact", "Send directly"],
        ["Kebab-case slug", "slug", "Exact", "Optional; Leafpad auto-derives if omitted"],
        ["body_markdown", "html_content", "Transform", "Convert MD→HTML; escape literal & in body"],
        ["seo.title", "seo_title", "Exact (≤60)", "Send directly; enforce 60-char cap"],
        ["seo.description", "seo_description", "Exact (140–160)", "Send raw text; do not HTML-escape"],
        ["seo.keywords[] + preferred terms", "seo_keywords", "Transform", "Join array → comma string"],
        ["Content pillars / categories", "tags", "Partial", "Map pillar→tag name; reuse existing; immutable after create"],
        ["governance.disclosure", "(in html_content)", "Transform", "Render disclosure into body HTML — no dedicated field"],
        ["Persona / author", "author", "Auto-handled", "Do not send; Leafpad sets byline. Persona informs voice"],
        ["Visual style / palette", "image styling", "Auto-handled", "Do not send; image tool applies brand style. Prompt = subject"],
        ["excerpt", "—", "No-equivalent", "Drop for Leafpad; retain for other channels"],
        ["reading_time, canonical_url, visibility", "—", "No-equivalent", "Drop on publish"],
        ["Image alt / caption", "— (requested)", "No-equiv → pending", "Embed in <img> HTML today; see §5"],
    ],
    w, fs=8.2)
callout(pdf, "Why this matters for the partnership", [
    ("When the two teams agree that a pair of fields ", ""), ("should", "I"),
    (" be treated as equivalent, we add a row and the agent immediately understands the compatibility "
     "— because the protocol column is an instruction, not just documentation. If Leafpad ships a "
     "schema change, one row updates and behavior follows. This is the foundation of “natively "
     "compatible.”", ""),
])

# ---------------- 5. REQUESTS ----------------
pdf.add_page()
H2(pdf, "5. Where Native Support from Leafpad Would Help")
para(pdf, [
    ("These are the points where a small MCP exposure on Leafpad's side would remove friction and "
     "unlock a materially better joint experience. They are ordered by impact on the shared product.", ""),
])
w5 = [8, CONTENT_W * 0.34 - 4, CONTENT_W * 0.66 - 4]
table(pdf,
    ["#", "Request", "Why it helps the joint product"],
    [
        ["1", "Schedule a finished post for future auto-publish (real published_at)",
         "Today's scheduler generates a topic into a draft on a date; it cannot publish a pre-written post live on a schedule. A true publish date enables genuine editorial calendars."],
        ["2", "Draft / status visibility — a status filter on the post-list tool and scheduled-queue read access",
         "The agent can fetch a known draft by slug, but cannot enumerate drafts or see the scheduled queue. A status filter closes the QA and planning loop."],
        ["3", "Image alt & caption as first-class write fields",
         "We can generate brand-appropriate alt/caption text today, but it can only live in raw HTML. Write fields make accessibility and captions native and durable."],
        ["4", "Mutable tags on update, and independently updatable SEO fields",
         "Tags are immutable after creation (requires recreating the post), and SEO fields are all-or-nothing on update. Both force clumsy workarounds."],
        ["5", "canonical_url field",
         "Essential for syndicated / cross-posted content — a real SEO gap today."],
        ["6", "Analytics read access via MCP (per-post views & GA metrics)",
         "Leafpad already has the GA integration and native analytics; exposing it for read lets the brand strategy learn from what performs. Owned and best delivered by Leafpad."],
        ["7", "Knowledge-base freshness / re-index control",
         "The company-data tool is read-only Q&A with no way to trigger a re-index or check index freshness."],
    ],
    w5, fs=8.2)

H3(pdf, "What we are deliberately not asking for")
para(pdf, [
    ("We do ", ""), ("not", "B"),
    (" want a delete or archive endpoint in the MCP. Manual-UI-only deletion is a feature, not a gap: "
     "the friction is intentional, and keeping destructive actions out of the automated path is a "
     "safeguard we want to preserve. We note this to show our requests are scoped and considered, not "
     "a wishlist.", ""),
])

# ---------------- 6. MUTUAL BENEFIT ----------------
H2(pdf, "6. Why This Is Good for Leafpad")
bullets(pdf, [
    [("Stickier output quality: ", "B"), ("brand grounding raises the floor on every generated post, "
      "which reflects directly on Leafpad's perceived quality.", "")],
    [("Expanded addressable use cases: ", "B"), ("agencies and regulated brands become viable customers "
      "once governance and multi-brand voice are in the loop.", "")],
    [("Differentiation: ", "B"), ("“brand-governed, automated publishing” is a stronger story "
      "than generation alone — one neither product tells as well separately.", "")],
    [("Low lift: ", "B"), ("the compatibility protocol needs no engineering; the MCP requests are "
      "incremental field exposures, not new systems.", "")],
])

# ---------------- 7. NEXT STEPS ----------------
H2(pdf, "7. Proposed Next Steps")
steps = [
    "Align on the field-compatibility protocol (§4) as a shared, living reference both teams own.",
    "Review the §5 MCP exposures and agree on a rough priority and sequence.",
    "Define what “natively compatible” means as a milestone — the specific fields and flows that should work end to end without manual HTML or workarounds.",
    "Pilot the combined pipeline on a shared test brand and review the output together.",
]
pdf.set_text_color(*INK)
for i, s in enumerate(steps, 1):
    pdf.set_x(ML + 1.5)
    pdf.set_font("Lib", "B", 10.5)
    pdf.set_text_color(*GREEN2)
    pdf.cell(6, 5.2, f"{i}.")
    pdf.set_left_margin(ML + 7)
    pdf.set_font("Lib", "", 10.5)
    pdf.set_text_color(*INK)
    pdf.set_x(ML + 7)
    pdf.multi_cell(CONTENT_W - 7, 5.2, s)
    pdf.set_left_margin(ML)
    pdf.ln(1)
pdf.ln(1)

callout(pdf, "In short", [
    ("We are not trying to bolt onto Leafpad — we are proposing that our products meet in the middle, "
     "with a shared mapping standard and a handful of native fields, so a user with both can turn "
     "brand strategy into published, on-brand content automatically. We would value your team's "
     "buy-in to make that compatibility native.", ""),
])

pdf.ln(2)
pdf.set_font("Lib", "", 8)
pdf.set_text_color(122, 138, 128)
pdf.multi_cell(CONTENT_W, 4.2,
    "Prepared by Brand Kit OS for discussion with the Leafpad team · June 19, 2026 · "
    "Field behaviors referenced here were calibrated against the live Leafpad MCP and are subject to "
    "re-verification on schema change.")

out = "/home/user/brand-kit-os-plugin-leafpad/docs/proposal/Brand-Kit-OS-x-Leafpad-Partnership-Proposal.pdf"
pdf.output(out)
print("WROTE", out)
