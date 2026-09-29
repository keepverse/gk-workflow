---
description: Load the seedsmith design domain — generation principles, game-design prior art, AI-native contract rules — then run the idea or spec phase for a generation feature
---

Load the `seedsmith-design` skill via the `skill` tool and follow it exactly, then continue into `/idea` or `/spec`
depending on what the work needs.

**Step 0 is not optional, and it is not a formality.** State the six laws back in your own words before
reading any subsystem doc. Two of them have already cost this repo real time when they were skipped:

- **Seed → concrete → per-player.** Seedsmith emits seeds; the *game runtime* rolls the concrete object
  per player and stores it in that player's tables. **The SDK already exists** —
  `Instantiator.TryInstantiate` — and `ActionSeeder` already reuses `Instantiator.Draw` verbatim. Never
  design a second roll. `TryInstantiate` has zero production callers, so most "we need a generator"
  findings are **wiring gaps**.
- **Every RPG feature lives in the RPG layer**, never built by changing what PvZ is. A previous session
  spent an hour concluding a feature was impossible when every blocker was an inert line of code.

Then satisfy the `docs/DESIGN-GATE.md` §1 reading gate **plus** the skill's own Step 1 table, in this
session, before forming a view. `docs/research/ai-native-generation/README.md` and
`docs/research/game-design/` are the two that make this skill different from `/idea` — read them.

Sort every finding into **built / wiring gap / real gap**, those exact words, with `file:line`.

**Answer the game-design questions with numbers, not adjectives.** Grid density in particular: compute
`combinations × axis` against roster size and compare to the measured bands (~3.6 per cell safe, ~12.6
the failure zone). A taxonomy proposed without that number is a guess.

**Before any web search, read `docs/research/game-design/06-unsourced.md`.** Eight passes and several
hundred searches already established what does not exist. Re-running them costs the same budget for the
same nothing.

**Deliverable paths — no condition to evaluate.** Ideal → `docs/architecture/<program>-ideal.md`.
Capability map → `docs/architecture/<program>-map.md`, approved before any module spec. Module specs →
`docs/architecture/<program>/spec-<module-id>.md`. Plan → `tasks/<program>-plan.md` and
`tasks/<program>-todo.md`, **always the prefixed pair**. `SPEC.md`, `tasks/plan.md` and `tasks/todo.md`
are not defaults and not fallbacks — do not read them, do not test whether they are free. State the
paths you wrote.

Restate load-bearing principles **inline** in whatever you write. A downstream session reads the doc,
not its links.

Order the build so the model-free modules come first — a parse, a table, a schema and a dump produce
real value with zero tokens spent, and they make the expensive stage's inputs reviewable.

ARGUMENTS: the generation feature to design (e.g. `species effect containers`, `item loot seeds`,
`action roll`). If omitted, ask what we are designing before doing anything else.
