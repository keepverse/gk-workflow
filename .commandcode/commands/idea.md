---
description: Run the idea/enrichment phase for a feature — load architecture principles, inventory what exists, research prior art, capture docs/architecture/<program>-ideal.md
---

Invoke the `idea-phase` skill and follow it exactly.

**Player menus / FE glance / badges / gauges / CSS-graph audits:** use **`/idea-ui`** instead (skill
`idea-ui`, SSOT `docs/architecture/idea-ui-phase.md`). Generic `/idea` is for RPG systems; menu
composition has a separate failure mode (god TSX / page CSS) that this command does not catch.

**Step 0 is not optional.** Before reading any subsystem doc, state the architecture principles back
in your own words — above all: **every RPG feature lives in the RPG layer and is never built by
changing what PvZ is** (`AGENTS.md`). Skipping this is what sent a previous session down a wrong path
for an hour, concluding a feature was impossible when every blocker was an inert line of code.

Then satisfy the `docs/DESIGN-GATE.md` §1 reading gate for every subsystem the feature touches —
in this session, before forming a view.

Sort every finding into **built / wiring gap / real gap**, using those exact words, with `file:line`
for each. A default-off toggle, a null delegate, a debug-only entry point, or a missing argument at
every call site is a **wiring gap** — never report one as an architectural limit.

Web-search genre prior art and bring back concrete numbers, formulas and documented failure modes,
with sources.

Deliverable: **`docs/architecture/<program>-ideal.md`**. Always that path. Restate load-bearing
principles inline in the doc rather than linking to them — a downstream session reads the doc, not
its links. Do not write specs, plans, or code; the ideal doc is where this phase stops.

ARGUMENTS: $ARGUMENTS (the feature or program to explore — e.g. `aura-skill`. If omitted, ask what
feature we are exploring before doing anything else.)
