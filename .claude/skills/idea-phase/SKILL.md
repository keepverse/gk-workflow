---
name: idea-phase
description: Run the enrichment/idea phase for a new feature — load the game vision first, then architecture principles, separate wiring gaps from real gaps, research genre prior art, and capture the result as docs/architecture/<program>-ideal.md. Use before /spec, whenever a feature is still a shape rather than a requirement ("I want to add X", "let's think about X", "enrichment phase", "pre-balance").
---

# Idea phase

The phase before `/spec`. The output is an **ideal doc** — what the feature *is*, what already exists,
and which questions are genuinely open — not a specification and not code.

**Player menus / ActorSheet tabs / badges / gauges / FE CSS-graph audits:** stop and use the
`idea-ui` skill (`/idea-ui`) instead — SSOT `docs/architecture/idea-ui-phase.md`. This skill is for
RPG **systems**; menu work needs module-first Lego inventory or it repeats the Condition glance
failure (live data, mute chips, stub titles, god-page CSS).

`/spec` answers *"what exactly are we building."* This answers *"what is this feature, and what is
already true?"* Running `/spec` first produces a confident spec against a system you misread.

## ⛔ Step 0 — load the principles into context, out loud

**Do this first, every time, before reading any subsystem doc.** These get lost in the middle of long
sessions, which is the exact failure this skill exists to prevent.

State these back in your own words before proposing anything:

0. **Read the game vision first.** Open `docs/guide/the-game.md` and `docs/guide/the-loops.md` in
   this session. State the genre (RPG + empire building) and **name which loop(s)** this idea
   extends. If none fit, **stop** — that is an owner decision to grow `the-loops.md`, not permission
   to invent a parallel pitch. Product vision wins on *what the player is playing*; architecture
   wins on Funnel, the resource registry gate (a new quantity passes P4 and P6 and lands its row in
   `empire-resource-ssot.md` — there is no fixed stock count), no player class, one power ladder, and
   gameless-first (`decisions.md` Product vision, Empire resource registry and Standalone-first rows).
1. **Every RPG feature lives in the RPG layer. It is never built by changing what PvZ is.**
   The full statement is in `CLAUDE.md` ("Every RPG feature lives in the RPG layer"). Read it in this
   session — it is a rule, not a pointer.
2. **The PvZ write surface constrains only persistent vanilla stat changes.** It says nothing about
   what an RPG feature may do. RPG mechanics resolve through the RPG's own stack
   (`DamagePacket` → dispatcher → shield/combat math → Funnel → FA10), all of which run during a
   lawn match.
3. **Two async systems, deltas not absolutes, record-then-drain.** Delay is the designed degradation
   mode, not a problem to engineer around.
4. **One power ladder.** Contests read `Θ` (linear, difference-based); magnitudes read `P(Θ)`.
   `ssot-power-scale.md` §10 is a closed inventory — a power-shaped number not in it has no
   permission to exist. Reading the *existing* ladder is free; inventing a new `f(level)` is the
   defect.
5. **The balance surface is data.** Any number a balance pass would touch belongs in
   `gk-core/data/tuning/<domain>.v{n}.json`, not a `const`.
6. **No hard progression ceilings.** Caps on magnitudes are soft/configurable; absolute bounds throw.
7. **Gameless-first is capability, not the pitch.** Every RPG feature must stay playable with Fusion
   closed after it unlocks. The injector may enrich, never permanently gate. Do not collapse this
   into "Fusion is optional flavor" or into "this only works in Fusion forever."

Then satisfy the `docs/DESIGN-GATE.md` §1 reading gate for every subsystem the feature touches —
including the **Product vision** row. A feature in the idea phase usually touches four or five rows —
read them all before forming a view.

## Step 1 — inventory what exists, in three buckets

The single most valuable output of this phase. Most "new" features are 70% built already.
**Sort every finding into exactly one bucket, and use these words:**

| Bucket | Means | How to report it |
|---|---|---|
| **Built** | Works end to end today | file:line, and say what proves it |
| **Wiring gap** | The machinery exists and is inert — a default-off toggle, a null delegate, a debug-only entry point, a missing argument at every call site | file:line of the *specific* line that is inert. **This is not a wall.** |
| **Real gap** | No mechanism exists anywhere | say what would have to be built |

**Never report a wiring gap as an architectural limit.** That is the mistake this skill was written
after: an aura design read the injector's Unity write surface, found four inert paths, and concluded
the feature could only cover 5 of 12 stats. Every one was a wiring gap; the real count was 11 of 12.

Prefer parallel subagents for the survey — the inventory is wide and mostly independent. Give each
one a narrow brief and require file:line citations and verbatim quotes.

## Step 2 — research prior art outside the repo

Genre conventions are cheap to read and expensive to rediscover. Web-search how shipped games solved
the same problem, and bring back **concrete numbers, formulas, and the documented failure modes** —
not vibes. A mechanic's known failure mode ("this becomes always-on wallpaper", "this reducer has a
singularity at 100%") is worth more than its description.

Cite sources. Flag anything unverified as unverified rather than repeating a plausible number.

## Step 3 — find the real question

Feasibility is usually not the question. By this point the honest question is normally one of:

- **What should it do** — the content/identity question
- **How is it tuned** — which numbers are authored, in what file, in what unit
- **Which shape** — of two or three viable structures, which fits the existing patterns

Say which one it is, and put the owner's actual decisions in one short list. Do not manufacture
open questions to fill a template; a recommendation nobody disputes is a decision, and an answerable
question is a task.

## Step 4 — write the ideal doc

**Path: `docs/architecture/<program>-ideal.md`.** Always. This is the repo's own convention
(`buff-debuff-scope-ideal.md`, `world-graph-ideal.md`, `effect-atom` ideal, `item-ideal.md`,
`resource-hub-ideal.md`). Never `SPEC.md`, never `tasks/plan.md`.

Structure that has worked here:

```markdown
# <Feature> — the ideal

**Status:** idea phase, <date>. Not a spec. No build authorized.

## Which loop this extends — one or more names from docs/guide/the-loops.md (required)
## What this is            — the feature in a paragraph, in the player's language
## What already exists     — the three buckets, with file:line
## Prior art               — genre research, with numbers and sources
## The shape               — the structure being proposed, and the alternatives rejected
## Tunables                — every number this introduces, and which gk-core/data/tuning file owns it
## What this deliberately does not decide
## Open questions          — owner decisions only, each one answerable
```

**Restate the load-bearing principles inline in the doc**, briefly, where they constrain a choice —
do not link to them. A downstream session reads this doc, not its links. That is the whole lesson.

Mark superseded ideals as superseded rather than deleting them; the reasoning trail is worth keeping.

## Step 5 — hand off

State the path you wrote and what the next step is (`/spec` for a capability map + module specs, once
the open questions are answered). **Do not** slide into writing specs, plans, or code — the ideal doc
is the deliverable, and the owner decides when it graduates.

**In a creative run** (`/creative`, `docs/contributing/creative-mode.md`) the owner is absent by design:
Step 3's owner decisions become the run's decision log (policy §7), and this hand-off is replaced by an
independent `creative-gate` review (policy §6). Everything else in this skill applies unchanged.

## Red flags

- Proposing before reading the game vision (`the-game.md` / `the-loops.md`)
- Inventing a parallel pitch, or making the lawn the whole game
- Collapsing gameless-first ("this only works in Fusion, forever") or "fixing" standalone-first by deleting it
- Adding a currency or material that fails the bottleneck test or skips its registry row, a player
  class, a stamina gate, or replacing expeditions with delves
- Proposing before reading — the sequence is **read → verify against code → propose**
- The word "impossible" about anything that is actually an inert line of code
- Reasoning about what PvZ can represent when the feature lives in the RPG layer
- A new `f(level)` curve instead of reading `Θ` / `P(Θ)`
- A balance number written as a `const`
- Writing to `SPEC.md`, `tasks/plan.md`, or `tasks/todo.md`
- Manufacturing open questions, or presenting a settled recommendation as a question
- An ideal doc that links to a principle instead of stating it
- An ideal doc with no **Which loop this extends** section
