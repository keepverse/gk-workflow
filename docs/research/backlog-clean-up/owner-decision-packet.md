# Owner decision packet — `backlog-clean-up`

**Program:** backlog-clean-up · **Map:** [../../architecture/backlog-clean-up-map.md](../../architecture/backlog-clean-up-map.md) module 2 ·
**Spec:** [../../architecture/backlog-clean-up/spec-owner-decision-batch.md](../../architecture/backlog-clean-up/spec-owner-decision-batch.md) ·
**Status:** D1–D4 answered 2026-09-20, same day as the map approval — see
[rulings-2026-09-20.md](../../architecture/backlog-clean-up/rulings-2026-09-20.md). This document
records those five original questions for the reconciliation trail, then lists the **K3 rows those
rulings did not cover** — product and balance calls that change how the game feels, where no ruling
answers them. Nothing here waits without a default; each row states one.

## Part 1 — the five original questions (answered)

| # | Question | Default if unanswered | Ruling |
|---|---|---|---|
| D1 (K1) | Does R28's no-human-gate autonomy extend beyond the 11 convergence programs? | No change until answered | **Yes, to all programs** (2026-09-20). Every owner-review/owner-run/ask-first gate outside convergence may pass by independent agent review, including K4 live gates run under the live-probe standard. Model-calling corpus runs still need D4. |
| D2 (K3) | `rider-default-on` flipped on the cost gate only. Keep the combat loop on? | Keep on | **Keep on. Stamina gets tuned later** — a new `lawn-combat-ai` caster (RPG AI layer) is the owner's chosen path, captured at [lawn-combat-ai-ideal.md](../../architecture/lawn-combat-ai-ideal.md). |
| D3 (K3) | Close the kill→soul gap (live-probe Task 17 / lawn-combat-wire L-N26)? | Keep open | **Close it** — applied 2026-09-20 (`paperwork-reconcile` BCU1.8). |
| D4 (K2) | Which model-calling runs to schedule? | None scheduled | **All four groups authorized** — action-distribution-gaps B0→B1, item-seedgen full corpus, passive-tree J9/J10/J13, the small re-classifies. Each runs under its own multi-agent charter (BCU2.10–BCU2.13). |
| D5 (K3) | Approve `identity-rename`/`ip-censor` plans? | Out of this program's scope | Not ruled on; still the plans' own owner ask. Listed here only to point at their own plan headers — `tasks/identity-rename-todo.md`, `tasks/ip-censor-todo.md`. |

## Part 2 — remaining K3 rows (product/balance calls no ruling covers)

Numbered `K3.1`…`K3.n` to avoid colliding with the spec-phase rulings' own `D7`/`D8` (a different,
already-closed pair, per `rulings-2026-09-20.md`'s second table — matched by content, never by
number, the same trap `paperwork-reconcile` hit repeatedly this program).

| # | Question | Default if unanswered | Releases | Evidence |
|---|---|---|---|---|
| K3.1 | `lawn-tuning-profile`'s `lawn-scale-live-proof` (the scale half of `rider-default-on`) has never run — M2 (stamina pool dwarfed by aptitude regen) is unfixed. Should the combat loop's default-on status be revisited pending that proof, or does D2's "keep on, tune later" already answer this? | Already answered by D2 — no further gate; the scale gate is scheduled first in the lawn plan (BCU2.4), not blocking the loop staying on | `lawn-plan.md`'s own build order (once written), `lawn-combat-ai-ideal.md` | lane A: `lawn-playable-map.md`'s own "rider-default-on PARTIAL" finding |
| K3.2 | base-defense force-size tunables — what should each side's committed force size be? | Ship current provisional values; flag for a balance pass once siege-stage is playable in-browser | `tasks/base-defense-todo.md:1914` | lane F |
| K3.3 | base-defense `Dugout` obstacle's CONCEAL rule — no numeric mechanic exists (unlike Trench/Rampart/Wire, which ship). Author one, or leave `Dugout` as the one inert cover type by design? | Leave inert, documented as the spec's own precedent for "four shipped, one inert" | `tasks/base-defense-todo.md:1916` | lane F |
| K3.4 | base-defense `SectorTypeFlags.Fortress` — built and tested, no shipped `SectorTypeCatalog` row sets it. Which sector type gets it (candidate: `homeworld`)? | Leave unset; no sector currently claims the Fortress bonus | `tasks/base-defense-todo.md:1919` | lane F |
| K3.5 | empire-development: real values for the relic drop weight/rate table and `EmpireWonderUpkeepRateMilli` (both shipped provisional/low on purpose) | Keep provisional values (relic rate low-default, upkeep `50`) until a real playtest sample exists | `tasks/empire-development-todo.md:89-90` | lane F |
| K3.6 | battle-timeline B20+B21 (interactive turns, decision trace) — Core is built; the server half needs a battle UI that does not exist. Is a battle UI worth building for this? | Stay deferred — `battle-tempo-map.md`'s own 2026-09-04 audited-and-deferred call stands | `tasks/backlog-clear-todo.md` Phase 8 (this program's own P4 correction, BCU1.4) | lane D |
| K3.7 | game-gui Checkpoint I — reframe "every plate has a matching surface" (6 of 7 target pages are live compositions inside existing layers, not superseded wrappers; deleting them breaks the app), or grow the layers' own content to close the literal gap? | Reframe the checkpoint's own wording to match what shipped; do not delete live pages | `tasks/backlog-clear-todo.md` Phase 5 (GG1); `tasks/game-gui-todo.md:1658` | lane G, lane B1 |
| K3.8 | item program's ~15-20 owner-only product asks (Phases 3-5, 7): registry version bump timing, `classes.v1.json` v4 full-run scheduling, unique pity mechanism, PvZ-mode consumables / "rest" / permanent-stat-up confirmation, per-specimen draughts, charm-capacity growth mechanism, a `Restore` admin surface, and the named §9-§11 ask-first rows | Ship current shapes unchanged; each individual ask stays open until batched into one owner sitting | `tasks/item-todo.md` Phases 3-5, 7 (~15-20 lines, each self-flagged "the owner's"/"ask-first") | lane G |
| K3.9 | `war-feedback-plan`'s six mechanics (Climate Echoes, Oath Cards, Zomboss Ledger, Fallow Lure, Chronicle Challenges, Gilding) — which, if any, get promoted to a real `/idea` round? Two (Gilding, Zomboss Ledger) touch territory `species-progression`/`empire-progression` also cover | None promoted; the file stays a clean idea backlog | `tasks/war-feedback-plan.md` | lane E |
| K3.10 | seedsmith `bond` passive tree's own name — a genuine 1-1-1 model vote split, twice, left unresolved by design ("never fabricate a winner"). Re-run the vote, or accept a third tie-break rule? | Leave unresolved; re-run later at no cost beyond one more vote | `tasks/seedsmith-content-standard-todo.md:585-587` | lane B2 |

## Reconciliation against the lane reports' OWNER-ONLY rows

Every OWNER-ONLY / ⛔ row found across lanes A–G resolves to exactly one of:

- **Closed by D1–D4** (kill→soul gap; the four corpus runs; R28's scope question itself).
- **Reclassified K1 → agent-run live gate**, per D1 + the live-probe standard (BP1-4's owner review,
  BP4's owner live proof, WM1's owner playtest, B27-style perf probes, and every other K4 row this
  audit's own "Precedent test" already found passable) — scheduled as ordinary tasks in this program's
  wave 3 or in the plans `orphan-plan-authoring` writes, never left as a silent gate.
- **A K2 model-calling run** named at D4 (BCU2.10–BCU2.13), or a K2 run D4 did **not** name
  (roster-balance's full re-run, passive-tree's H8 timed pilot) — those stay owner-scheduled, listed
  here for completeness: roster-balance's real full generation re-run (`tasks/roster-balance-todo.md:106-113`,
  same model/corpus as the action-distribution-gaps run) and passive-tree's H8 20-tree review pilot
  (`tasks/passive-tree-todo.md:537,3544-3564`, a human timing/eyeball pass explicitly confirmed not a
  code gap) — neither authorized by D4, so neither is scheduled; both wait on the owner naming a
  charter the same way D4's four groups did.
- **A genuine K4 live-visual row** where the precedent test still fails (a truly first-of-its-kind
  judgement, e.g. creature-standalone's live two-specimen fusion `execute`, which is irreversible and
  consumes real specimens) — stays owner-only; not released by D1, because D1 releases K4 rows *that
  pass the precedent test*, and an irreversible real-specimen consumption has none.
- **One of the ten K3 rows above.**

Count check: this reconciliation is a coverage assertion, not a population pin — the closed list is
"every row lanes A-G marked OWNER-ONLY/⛔ resolves to one of the five buckets above," never a specific
number of rows.
