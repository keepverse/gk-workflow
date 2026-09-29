# HTML Design Implementation Skill

## Purpose

Implement an approved HTML/CSS draft into production code with **high visual fidelity and structural fidelity**.

The approved draft is the visual specification. Production architecture may differ, but the rendered result must preserve the draft's visual hierarchy, information density, spatial relationships, interaction model, and intended complexity.

This skill exists because AI coding agents frequently make a dangerous substitution:

> "I implemented the same feature."

when the actual requirement is:

> "I implemented this exact UI."

A functionally equivalent UI is not an acceptable substitute for an approved design.

---

# 1. Prime Directive

## The draft is the source of truth

When an approved draft HTML exists:

- DO NOT redesign it.
- DO NOT simplify it.
- DO NOT "modernize" it.
- DO NOT convert it into a generic dashboard.
- DO NOT replace custom visual structures with generic cards.
- DO NOT remove decorative elements because they are difficult.
- DO NOT reduce information density.
- DO NOT invent a different information hierarchy.
- DO NOT substitute a different component merely because it is easier to implement.
- DO NOT assume that "functionally equivalent" means "visually equivalent."

You may change:

- framework
- component boundaries
- state management
- data loading
- CSS organization
- file structure
- internal implementation
- reusable abstractions

You may NOT change the intended visual result without explicit approval.

## Complexity is intentional

A sophisticated game UI may intentionally contain:

- dense information
- multiple visual layers
- charts
- graphs
- source breakdowns
- filters
- grouping
- badges
- VFX
- gradients
- glow
- technical overlays
- decorative geometry
- contextual information
- expandable details

Do not normalize such a UI into a SaaS-style collection of cards.

If the draft looks complex, preserve the complexity.

---

# 2. Required Workflow

Never jump directly from:

    draft.html → production code

Use:

    draft.html
        ↓
    Structural Analysis
        ↓
    Design Specification
        ↓
    Component Contract
        ↓
    Implementation Plan
        ↓
    Production Implementation
        ↓
    Browser Render
        ↓
    Visual Verification
        ↓
    Gap Report
        ↓
    Surgical Fixes
        ↓
    Final Verification
        ↓
    DONE

Every stage is mandatory unless the user explicitly disables it.

---

# 3. Phase 0 — Establish the Baseline

Before modifying production UI:

1. Locate the approved draft.
2. Read the complete draft.
3. Determine its viewport and responsive assumptions.
4. Run/open the draft if possible.
5. Capture a baseline screenshot at the target viewport.
6. Record the draft location.
7. Treat the draft as read-only.

Do not begin implementation while only looking at a cropped screenshot if the HTML itself is available.

The HTML/CSS contains information that a screenshot does not:

- DOM hierarchy
- sizing
- spacing
- grid definitions
- flex relationships
- hidden states
- responsive rules
- typography
- interaction structure
- component repetition
- semantic grouping

---

# 4. Phase 1 — Structural Decomposition

Before writing production code, reconstruct the draft as a hierarchy.

Example:

    Page
    ├── Header
    │   ├── Title
    │   ├── Context
    │   └── Actions
    │
    ├── FilterBar
    │   ├── Search
    │   ├── GroupSelector
    │   ├── SourceFilter
    │   └── ViewMode
    │
    ├── Overview
    │   ├── PrimaryStats
    │   └── DerivedStats
    │
    ├── MainContent
    │   ├── ChartPanel
    │   ├── SourceBreakdown
    │   └── DetailPanel
    │
    └── Footer / Status

Do not skip intermediate containers.

The hierarchy matters because layout relationships are often encoded in the containers rather than the visible children.

---

# 5. Phase 2 — Design Specification

Create a design specification before implementation.

The specification must describe:

## 5.1 Page geometry

Record:

- target viewport
- page width
- page height
- major regions
- columns
- rows
- fixed areas
- scroll areas
- maximum widths
- minimum widths
- alignment anchors

Example:

    viewport: 1440 × 900
    header: 72px
    sidebar: 280px
    main: remaining width
    content: 2-column
    primary panel: 65%
    secondary panel: 35%

Exact values should be extracted from the draft where practical.

## 5.2 Layout model

For every major region identify:

- flex
- grid
- absolute positioning
- overlay
- stacking
- fixed
- sticky
- scroll
- clipping
- alignment

Do not replace a meaningful layout relationship with arbitrary margins.

## 5.3 Spacing system

Identify:

- outer padding
- section gaps
- panel padding
- row gaps
- column gaps
- icon-to-text spacing
- label-to-value spacing
- chart spacing

Preserve relationships, not merely approximate individual numbers.

## 5.4 Visual hierarchy

Identify:

- primary information
- secondary information
- tertiary information
- emphasis
- selected state
- warning state
- positive/negative state
- disabled state
- decorative information

## 5.5 Typography

Record:

- font family
- font size
- weight
- line height
- letter spacing
- capitalization
- numeric styling
- hierarchy

Do not replace a distinctive typography system with the project's default typography merely because it is convenient.

## 5.6 Surface treatment

Record:

- backgrounds
- gradients
- borders
- corner radius
- shadows
- glow
- opacity
- overlays
- textures
- separators

## 5.7 Graphics

Record:

- icons
- images
- charts
- graphs
- progress indicators
- decorative geometry
- SVG/canvas content
- VFX

Graphics are part of the design, not optional decoration.

---

# 6. Phase 3 — Component Contract

Create a component contract.

Every meaningful visual region must have a traceable production component.

Example:

    Draft Region              Production Component
    ------------------------------------------------
    Header                    DerivedStatsHeader
    Filter row                StatsFilterBar
    Main chart                DerivedStatsChart
    Source list               StatSourceBreakdown
    Detail panel              StatDetailPanel
    Modifier row              ModifierEntry

For each component record:

- purpose
- parent
- children
- inputs
- state
- layout responsibility
- visual responsibility
- responsive behavior

## Traceability rule

Every major draft region must map to production code.

Every major production visual region must be explainable as coming from the draft.

If a region exists only because the developer invented it, flag it for review.

If a draft region has disappeared, flag it as a defect.

---

# 7. Phase 4 — Existing Codebase Analysis

Before creating components, inspect the project.

Search for:

- existing components
- design tokens
- CSS variables
- typography
- spacing tokens
- icon systems
- chart libraries
- theme systems
- layout primitives
- responsive utilities
- shared controls

Reuse existing infrastructure when it is visually compatible.

However:

> Reuse does not override fidelity.

If an existing Card component cannot reproduce the draft's visual structure, do not force the design into that Card component.

Prefer:

    existing compatible component → reuse

over:

    existing vaguely similar component → distort design to fit it

---

# 8. Phase 5 — Implementation Plan

Before editing production files, produce a short implementation plan.

The plan must answer:

1. Which files will change?
2. Which components will be created?
3. Which existing components will be reused?
4. Which assets are required?
5. Which states must be implemented?
6. Which responsive behaviors must be preserved?
7. How will the result be visually verified?

Do not perform a large refactor before establishing this plan.

---

# 9. Phase 6 — Implement in Layers

Implement in this order:

## Layer 1 — Skeleton

Implement:

- page dimensions
- major regions
- columns
- rows
- scrolling
- stacking
- primary containers

At this stage, ignore minor decoration.

Verify the silhouette.

## Layer 2 — Information Architecture

Implement:

- headings
- labels
- values
- lists
- filters
- controls
- charts
- data relationships

Verify that information density matches the draft.

## Layer 3 — Visual System

Implement:

- typography
- spacing
- colors
- borders
- radius
- shadows
- gradients
- backgrounds

## Layer 4 — Graphics

Implement:

- icons
- charts
- graphs
- images
- decorative elements
- VFX
- overlays

## Layer 5 — Interaction

Implement:

- hover
- selected
- active
- expanded
- collapsed
- filtering
- grouping
- sorting
- tooltips
- navigation
- keyboard behavior

Do not remove interactions merely because the first implementation is static.

---

# 10. Assets and Icons

If the draft contains an asset:

1. Identify the real asset.
2. Reuse it if available.
3. Use the project's asset pipeline where appropriate.
4. Preserve its intended dimensions and aspect ratio.

Do not replace a distinctive icon with:

- emoji
- arbitrary Unicode symbols
- unrelated icon-library glyphs
- hand-created approximate SVG

unless the user explicitly permits substitution.

If an exact asset cannot be obtained, flag the discrepancy instead of silently pretending it matches.

---

# 11. Charts and Data Visualization

Charts are structural components, not decoration.

Preserve:

- chart dimensions
- axes
- labels
- series
- legend
- grid
- gradients
- line thickness
- point markers
- interaction
- visual emphasis

Do not replace a sophisticated chart with:

    "Chart goes here"

or a generic bar chart.

If the draft uses visualization to communicate relationships between stats, the implementation must preserve that communication.

---

# 12. Information Density Rule

This rule is critical for RPG/game interfaces.

Do not judge quality by whitespace alone.

A dense interface may be intentionally designed for expert users.

Preserve:

- visible secondary values
- source information
- modifiers
- percentages
- deltas
- relationships
- metadata
- filtering controls
- grouping controls

Do not hide information simply to make the interface look "cleaner."

---

# 13. Anti-Generic-UI Rules

The following are implementation failures when they replace intentional design:

- turning every section into a card
- excessive rounded rectangles
- giant empty spacing
- generic dashboard layouts
- default Tailwind styling
- default component-library appearance
- replacing custom panels with standard cards
- replacing charts with simple bars
- removing visual layers
- removing VFX
- removing background treatment
- removing technical/game-like details
- flattening hierarchy
- reducing the number of visible controls
- turning a dense RPG HUD into a business dashboard

If the result could plausibly be mistaken for:

- an admin dashboard
- a SaaS analytics page
- a generic Bootstrap page
- a default component-library demo

then stop and compare against the draft again.

---

# 14. Browser Verification Is Mandatory

After implementation, render the actual production page in a real browser.

Do not rely only on:

- source inspection
- TypeScript compilation
- unit tests
- lint
- "looks correct" reasoning

The browser-rendered result is the final visual truth.

This is especially important because CSS/layout problems are often invisible from source code alone.

---

# 15. Visual Verification Checklist

Compare the draft and implementation in this order.

## A. Silhouette

Ask:

- Does the page have the same overall shape?
- Are the major regions in the same locations?
- Are the proportions similar?
- Is the density similar?

If not, stop here and fix structure before continuing.

## B. Layout

Check:

- widths
- heights
- grid columns
- flex relationships
- alignment
- spacing
- padding
- overflow
- scrolling
- fixed/sticky regions

## C. Typography

Check:

- font
- size
- weight
- line height
- letter spacing
- numeric prominence

## D. Visual surfaces

Check:

- colors
- backgrounds
- gradients
- borders
- radius
- shadows
- glow
- opacity

## E. Graphics

Check:

- icons
- images
- charts
- graphs
- decorative elements
- VFX

## F. Interaction

Check:

- hover
- active
- selected
- expanded
- collapsed
- filtering
- grouping
- sorting
- tooltips

---

# 16. Quantify Differences

When possible, use screenshots and visual comparison rather than vague judgment.

Useful evidence includes:

- side-by-side screenshots
- overlay
- image diff
- bounding-box measurements
- DOM dimensions
- computed styles
- viewport-specific screenshots

A visual regression workflow can render the live implementation and compare it against a baseline, producing structured differences for repair loops. This approach is preferable to relying solely on an agent saying "looks good."

If visual-diff tooling exists in the project, use it.

If it does not, use browser screenshots and inspect the rendered result.

---

# 17. Gap Report

After comparison, create a gap report.

Example:

    # Visual Gap Report

    ## Critical

    1. Main chart is 180px too short.
    2. Filter bar is missing source grouping control.
    3. Right panel begins 32px too low.

    ## Major

    4. Header typography is too small.
    5. Stat cards have insufficient information density.
    6. Background glow is missing.

    ## Minor

    7. Border radius differs by 2px.
    8. Icon is 3px too large.

Prioritize:

    structure > geometry > density > typography > surfaces > decoration

Do not spend time fixing tiny colors while the page structure is wrong.

---

# 18. Surgical Repair Rule

When fixing visual differences:

> Fix the smallest amount of code necessary to correct the identified discrepancy.

Do not respond to:

    "chart is too low"

with:

    "rewrite the entire dashboard layout."

Do not refactor unrelated components during visual correction.

Every repair should have:

- identified discrepancy
- suspected cause
- targeted change
- verification

This prevents the common AI failure mode:

    fix A
    accidentally break B
    rewrite C
    break D
    repeat

---

# 19. No Premature Refactoring

Do not refactor production architecture during the first fidelity pass.

First:

    reproduce the design

Then:

    verify the design

Then:

    improve architecture if necessary

Refactoring before visual fidelity is established creates too many moving parts and makes it difficult to determine whether a mismatch came from the design implementation or the refactor.

---

# 20. Preserve the Draft During Implementation

The draft must remain available for comparison.

Do not overwrite it.

Do not modify it to make the implementation "match."

The correct direction is:

    implementation → moves toward draft

NOT:

    draft → moves toward implementation

If the implementation cannot reproduce something in the draft, the implementation is the thing that must be investigated.

---

# 21. Responsive Behavior

Do not assume that matching one desktop screenshot is sufficient.

If the draft defines responsive behavior, preserve:

- breakpoints
- stacking
- resizing
- hiding/showing
- scrolling
- reordering
- minimum dimensions

Verify at every explicitly supported viewport.

If responsive behavior is not specified, do not invent dramatic redesigns.

Use the desktop structure as the primary source of truth and make only the minimum changes required for usability at smaller widths.

---

# 22. Interaction-State Verification

Visual fidelity applies to states, not only the default page.

Where applicable, verify:

- default
- hover
- focus
- active
- selected
- disabled
- expanded
- collapsed
- loading
- empty
- error
- filtered
- grouped
- sorted

A component is not considered implemented if only its default state resembles the draft.

---

# 23. Completion Gate

The agent MUST NOT report:

> "Implementation complete"

until all applicable gates pass.

## Gate 1 — Structural

- [ ] Major draft regions mapped
- [ ] Component hierarchy documented
- [ ] No unexplained missing sections
- [ ] No unexplained invented sections

## Gate 2 — Functional

- [ ] Required interactions implemented
- [ ] Required data displayed
- [ ] Filters work
- [ ] Grouping works
- [ ] Sorting works
- [ ] Expansion works
- [ ] Navigation works

Only check applicable items.

## Gate 3 — Visual

- [ ] Overall silhouette matches
- [ ] Major geometry matches
- [ ] Information density matches
- [ ] Typography hierarchy matches
- [ ] Surfaces match
- [ ] Icons/assets match
- [ ] Charts match
- [ ] Decorative/VFX elements preserved

## Gate 4 — Browser

- [ ] Actual page rendered
- [ ] Target viewport checked
- [ ] Console errors checked
- [ ] Overflow checked
- [ ] Interactive states checked

## Gate 5 — Traceability

Every major draft region has:

    draft → component → rendered result

If any major region cannot be traced, the task is not complete.

---

# 24. Failure Protocol

If the implementation is visually wrong:

DO NOT:

- defend the implementation
- claim it is "close enough"
- redesign the draft
- perform an unrelated refactor
- add more abstractions
- ask the user to approve an obviously degraded result

Instead:

1. Identify the largest mismatch.
2. Determine whether it is structural or cosmetic.
3. Fix the structural cause.
4. Render again.
5. Compare again.
6. Repeat.

Continue until the remaining differences are either:
- negligible, or
- explicitly documented as blocked by missing assets/tooling/requirements.

---

# 25. Agent Self-Review Questions

Before declaring completion, ask:

### Structure

- Did I preserve the original hierarchy?
- Did I accidentally remove a section?
- Did I merge two sections that were intentionally separate?
- Did I invent a section?

### Layout

- Does the page have the same silhouette?
- Are major widths and heights comparable?
- Are the panels positioned correctly?
- Is the information density comparable?

### Visual design

- Did I accidentally make it look like a generic dashboard?
- Did I remove gradients, glow, borders, or decorative layers?
- Did I replace custom UI with generic cards?
- Did I simplify the charts?
- Did I replace distinctive icons?

### Interaction

- Did I preserve filtering?
- Did I preserve grouping?
- Did I preserve sorting?
- Did I preserve expansion?
- Did I preserve selected/hover states?

### Verification

- Did I actually render the page?
- Did I compare it to the draft?
- What are the three largest remaining differences?
- Did I fix them?

If the agent cannot answer these questions with evidence, it is not finished.

---

# 26. Recommended Artifact Files

For non-trivial implementations, maintain:

    design/
        approved/
            screen.html

        analysis/
            screen-structure.md
            screen-spec.md
            screen-component-map.md

        verification/
            screen-gap-report.md
            screenshots/
                draft.png
                implementation.png
                diff.png

This turns visual implementation into a traceable engineering process rather than an agent's subjective interpretation.

---

# 27. Minimal Operating Procedure

If time/context is limited, the minimum mandatory procedure is:

    1. Read the complete draft HTML.
    2. Decompose its hierarchy.
    3. Write a component map.
    4. Implement the major geometry first.
    5. Implement information density.
    6. Implement visual styling.
    7. Render in browser.
    8. Compare against draft.
    9. Fix the largest differences.
    10. Render again.
    11. Repeat until acceptable.
    12. Report remaining known deviations.

Never skip browser verification merely because the source code "looks correct."

---

# 28. Core Principle

The agent's job is NOT:

> "Create a UI inspired by this HTML."

The agent's job is:

> "Reconstruct this approved visual system in production code while preserving its structure, information hierarchy, density, interaction model, and visual identity."

Architecture is flexible.

Visual intent is not.

**Approved draft → specification → implementation → browser evidence → correction → acceptance.**

That is the workflow.
