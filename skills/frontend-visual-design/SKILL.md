---
slug: frontend-visual-design
name: Frontend Visual Design Taste
name_zh: 前端视觉设计品味
version: 0.1.0
description: Build interfaces that feel deliberate, premium, and current — restrained composition, image-led hierarchy, cohesive content, tasteful motion. Use for landing pages, marketing sites, demos, prototypes, game UIs where the quality depends on art direction, not component count. Avoids the generic-card / weak-branding / UI-clutter trap.
description_zh: 做出有主张、显品味、跟得上时代的界面 —— 克制构图、图像主导的层级、连贯的内容、走心的动效。用于 landing page、营销站、demo、原型、游戏 UI —— 凡是质量靠艺术指导而不是组件数量的场景。专门避开"通用卡片 / 弱品牌 / 杂乱 UI"三个坑。

category: applications
tags: [frontend, design, ui, landing-page, motion]
platforms: []

inputs:
  - name: artifact_type
    type: enum
    required: true
    values: [landing-page, marketing-site, app-shell, demo, prototype, game-ui, dashboard]
    description: |
      What you're building. Drives which "Beautiful
      Defaults" section applies first.
  - name: thesis
    type: string
    required: true
    description: |
      One sentence describing mood, material, and
      energy (e.g. "soft brutalism with brutal
      sans-serif, matte concrete texture, slow
      fades"). Drives the design decisions.
  - name: audience
    type: string
    required: false
    description: |
      Who this is for. Use the language, scale,
      and imagery that matches.
  - name: motion_budget
    type: enum
    required: false
    values: [none, restrained, expressive]
    default: restrained
    description: |
      How much motion is appropriate. "None" for
      document-like surfaces; "expressive" for
      marketing / hero moments.

output:
  format: markdown
  description: |
    A `## Working Model` block (visual thesis,
    content plan, interaction thesis) followed by
    section-by-section design notes, the
    "Beautiful Defaults" applied, and a final
    "Anti-patterns avoided" checklist.

author: "Letta (downstream pack: badhope)"
license: MIT
created: 2026-06-11
updated: 2026-06-11

source:
  url: https://github.com/letta-ai/skills/tree/main/tools/frontend-skill
  fetched_at: 2026-06-11
  commit: cb8a79f91a048ce8b189f564ebe94d74a6edb83e
  license: MIT
  original_path: tools/frontend-skill/SKILL.md
---

# When to use

The user is building something where the quality
of the result depends on **art direction,
hierarchy, restraint, imagery, and motion** —
not on how many components ship. Typical
triggers: "make the landing page look like a
real product", "this prototype needs visual
weight", "the demo is too plain", "I want the
UI to feel premium", "design taste feedback".

Use this skill for:

- Landing pages and marketing sites
- Product demos and prototypes
- Game UIs
- Hero sections, brand pages, manifesto pages
- Any surface where weak design will sink the
  underlying idea

**Do not** use this for:

- Internal admin tools (use the existing
  component library; restraint reads as
  laziness)
- Data-heavy dashboards (use a different skill —
  information density wins)
- Quick CRUD forms (visual taste is irrelevant)
- Pure backend work (no UI)

# Inputs

- `artifact_type` — landing-page / marketing /
  app-shell / demo / prototype / game-ui /
  dashboard.
- `thesis` — one sentence: mood + material +
  energy. The single most important input.
- `audience` (optional) — who reads it.
- `motion_budget` (optional) — none / restrained
  / expressive.

# Output

A `## Working Model` block first, then section
notes, then a `## Beautiful Defaults` recap, then
an `## Anti-patterns avoided` checklist. The
agent should then build (or revise) the artifact
to match.

# Prompt

```prompt
You are designing a UI where the quality of the
work depends on art direction, hierarchy,
restraint, imagery, and motion — not component
count. Default toward award-level composition:
one big idea, strong imagery, sparse copy,
rigorous spacing, and a small number of
memorable motions.

## 1. Write the working model first

Before building, write three things. The user
should be able to read these and tell if you
understood the brief.

  - **Visual thesis** — one sentence:
    mood + material + energy. Example: "soft
    brutalism with brutal sans-serif, matte
    concrete texture, slow fades". A weak thesis
    is "modern and clean". A strong thesis
    commits.
  - **Content plan** — hero, support, detail,
    final CTA. Each section gets one job, one
    dominant visual idea, and one primary
    takeaway or action.
  - **Interaction thesis** — 2-3 motion ideas
    that change the feel of the page. Examples:
    "text fades in after the image settles",
    "hover on a card swaps it for a full-bleed
    variant", "scroll progress reveals the
    section title with a 0.4s ease-out".

If you can't write these, you don't have a
design — you have a layout. Stop and ask the
user what mood they want.

## 2. Beautiful defaults (apply unless told
otherwise)

  - **Start with composition, not components.**
    Decide the grid, the dominant visual, and
    the breathing room before picking a
    Card.
  - **Prefer a full-bleed hero or full-canvas
    visual anchor.** A page that opens with a
    card stack is a blog post, not a landing
    page.
  - **Make the brand or product name the
    loudest text.** If your headline is louder
    than the brand, you wrote an essay, not a
    hero.
  - **Keep copy short enough to scan in
    seconds.** No 4-line paragraphs above the
    fold. If the user has to read, they won't.
  - **Use whitespace, alignment, scale,
    cropping, and contrast before adding
    chrome.** Decoration is a last resort.
  - **Limit the system: two typefaces max, one
    accent color by default.** Three typefaces
    is a portfolio, not a product.
  - **Default to cardless layouts.** Use
    sections, columns, dividers, lists, and
    media blocks instead. Cards are for
    interchangeable items, not for everything.
  - **Treat the first viewport as a poster,
    not a document.** A poster has one big
    thing, generous space around it, and a
    reason to scroll. A document has a
    sidebar and a heading.

## 3. Landing-page default sequence

  1. **Hero** — brand or product, promise, CTA,
     and one dominant visual
  2. **Support** — one concrete feature, offer,
     or proof point
  3. **Detail** — atmosphere, workflow, product
     depth, or story
  4. **Final CTA** — convert, start, visit, or
     contact

### Hero rules

  - One composition only. Two compositions in
    one hero is a busy billboard.
  - Full-bleed image or dominant visual plane.
  - Canonical full-bleed rule: on branded
    landing pages, the hero itself must run
    edge-to-edge with no inherited page
    gutters, framed container, or shared
    max-width. Constrain only the inner
    text/action column.
  - Brand first, headline second, body third,
    CTA fourth. Reverse the order and the
    brand is the smallest thing on the page.
  - No hero cards, stat strips, logo clouds,
    pill soup, or floating dashboards by
    default. They eat the hero.
  - Headlines: roughly 2-3 lines on desktop,
    readable in one glance on mobile.
  - Keep the text column narrow and anchored
    to a calm area of the image (don't put
    white text on the brightest cloud).

### Section rules

  - Each section earns its scroll. If a
    section could be deleted without changing
    the page's argument, delete it.
  - One dominant visual idea per section. A
    section with two dominant visuals is
    arguing with itself.
  - Use a mix of media and type. Pages that
    are all type feel academic; pages that
    are all media feel like a moodboard.
  - End with a single, decisive CTA. The
    "Schedule a call / Read the docs / Sign
    up" trio is three CTAs, not one.

## 4. Motion

  - **Restrained** (default): one entrance
    per section, easing `cubic-bezier(0.2,
    0.8, 0.2, 1)`, durations 300-500ms,
    no bounces.
  - **Expressive** (marketing, hero): bigger
    eases, parallax only on the hero, scroll-
    linked reveals, occasional 3D tilt on
    cards. Don't chain more than 3
    scroll-linked animations in a row.
  - **None** (document / data surfaces):
    no entrance, no hover, no scroll-linked
    anything. Page behaves like a book.

Motion that exists to show off motion is
worse than no motion.

## 5. Imagery

  - Pick one imagery language per page:
    photography / 3D render / illustration /
    abstract gradient / typographic poster.
    Mixing languages in one page reads as
    "design system by committee".
  - Photography: real, specific, current.
    No stock-photo smiles, no AI-generated
    "diverse team high-fiving" backgrounds.
  - 3D: one material, one lighting setup.
    Two materials reads as a render farm
    demo.
  - Illustration: consistent weight, line
    style, and color palette across the
    whole site.
  - Abstract gradient: the gradient itself
    is the design. Make it specific (color
    stops, grain, noise) — not a generic
    purple-pink smear.

## 6. Anti-patterns to flag and remove

Flag and remove, in order of severity:

  - **Pill soup** — rows of feature pills in
    the hero. Each pill is a tax on attention.
    One promise, not seven.
  - **Card stack hero** — three feature cards
    side-by-side at the top. That's a table of
    contents, not a hero.
  - **Stat strip without proof** — "10,000+
    users" with no source. Either cite it or
    drop it.
  - **Logo cloud** — row of customer logos
    that's actually 2 logos scaled up. Cut
    to one row, smaller.
  - **Floating dashboard mockup** — hero shows
    a tilted screenshot of "the product". The
    product is not the hero; the brand is.
  - **Two-column text-and-image blocks
    repeated 5 times** — that's a brochure,
    not a landing page. Vary the layout.
  - **Generic gradient background with white
    card centered** — the default of every
    AI landing page generator. Replace with
    the project's actual visual language.
  - **CTA trio at the bottom** — "Start free /
    Read the docs / Talk to sales" is three
    things; the user will pick none. Pick
    one.
  - **Modal-on-first-visit** — destroys the
    experience the user came for.
  - **Cookie banner covering 30% of the
    viewport** — sized for a court order, not
    a button.
  - **Animation on every scroll** — feels
    like a slideshow. Use motion to mark
    transitions, not to mark scrolling.
  - **"Trusted by" with a brand that doesn't
    match the audience** — instantly
    suspicious.
```

# When NOT to use

- **Internal admin tools** — restraint reads
  as laziness. Use a different skill.
- **Data-heavy dashboards** — information
  density wins. Visual taste is a tax.
- **Quick CRUD forms** — there is no "design"
  here. Just build it.
- **Pure backend work** — no UI; this skill
  has nothing to say.
- **The user has a specific brand system**
  and wants you to follow it — use their
  system, not this skill's defaults.
- **When the user has not given a visual
  thesis** — ask for mood and energy first;
  do not invent a thesis silently.

# Example

**Input:**

```yaml
artifact_type: landing-page
thesis: "soft brutalism with brutal sans-serif,
  matte concrete texture, slow fades"
audience: "engineers considering a new
  observability tool"
motion_budget: restrained
```

**Output:**

```markdown
## Working model

### Visual thesis
Soft brutalism: heavy grotesque type on
matte-concrete texture, generous negative space,
slow 400ms eases. Confident without being loud.
Engineering credibility over marketing gloss.

### Content plan
- **Hero** — brand + one-line promise + one
  concrete number (not "10,000+ users" — a real
  metric like "p99 query at 12ms across 4B
  spans")
- **Support** — one feature with a real
  screenshot from a real install, not a
  dashboard mockup
- **Detail** — "How it works" 3-step flow with
  one diagram, not three diagrams
- **Final CTA** — single button: "Start a 14-day
  trial"

### Interaction thesis
- Text fades in after the hero image settles
  (300ms delay, 400ms ease)
- Section titles use a 0.4s ease-out reveal
  tied to scroll progress
- Card hover: subtle border-color shift, no
  scale, no shadow

## Beautiful defaults applied
- Full-bleed hero, no card stack
- Brand name loudest text in the hero
- Two typefaces: Inter Display (headings),
  IBM Plex Mono (code/numbers)
- One accent color: a desaturated teal
- No pills in hero
- No logo cloud; one row of three real customer
  logos, grayscale
- Copy: 8-word hero headline, 12-word subhead
- Final CTA is one button

## Anti-patterns avoided
- ✗ pill soup
- ✗ card stack hero
- ✗ floating dashboard mockup
- ✗ stat strip without proof
- ✗ CTA trio
- ✗ modal-on-first-visit
- ✗ animation on every scroll
```

The agent then builds the page to match. If
the user pushes back on a default ("but I want
the card stack hero"), change it — but call out
the trade-off in one sentence.
