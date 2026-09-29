# Implementation plan: `strain-splice-host`

**Map:** [strain-splice-host-map.md](../docs/architecture/strain-splice-host-map.md) · **Specs:**
[host-gate](../docs/architecture/strain-splice-host/spec-host-gate.md) ·
[combination-regen](../docs/architecture/strain-splice-host/spec-combination-regen.md) ·
[recipe-import](../docs/architecture/strain-splice-host/spec-recipe-import.md) ·
[combo-bind](../docs/architecture/strain-splice-host/spec-combo-bind.md) ·
[circuit-topology](../docs/architecture/strain-splice-host/spec-circuit-topology.md) ·
[combo-budget](../docs/architecture/strain-splice-host/spec-combo-budget.md) ·
[tier-ladder](../docs/architecture/strain-splice-host/spec-tier-ladder.md) ·
[socket-pricing](../docs/architecture/strain-splice-host/spec-socket-pricing.md) · **Tasks:**
[strain-splice-host-todo.md](strain-splice-host-todo.md) · **Parent:**
[summoner-convergence-plan.md](summoner-convergence-plan.md) lane C, after species-gear-chain (task prefix
`SSH`).

**Owner approval 2026-09-23:** the spec phase may start — the 55 open rows are released to lanes under this plan's order and hard edges.

## Overview

Make a Strain or Splice (a four-gem word in a cheap item) real from end to end. Today the corpus never
loads (F2), a firing word never reaches the actor (F1), the preview has its own copy of the matcher (F4)
and builds a fake host (F5, F6), and every word grants one flat tier. The program folds the matcher into
one, wires the 76+ generated words into the game and into ActorHub, applies the decided eight-socket
topology (helm to 4 sockets, R11), replaces the retired per-actor cap with checked pricing (R12, R20), and
moves the tier ladder into tuning. Work follows ruling 5's order: regenerate → eight-socket revision →
measure → ladder and pricing.

## Architecture decisions (from the map, not re-litigated)

- **Host-gate goes first.** It is the SOLID fix for the forked matcher (F4). CLAUDE.md does not allow
  extending a forked seam until its fix is sequenced first, and `tier-ladder` changes the matcher. Map §2,
  §9 A1.
- **Ruling 5 order: 2 → 5 → 6 → 7/8.** Regenerate the corpus, then the eight-socket revision, then the
  measurement, then the ladder and the pricing (in parallel). `recipe-import` (3) and `combo-bind` (4)
  come in where they are needed: they are wiring gaps. Map §2 "How this honours ruling 5".
- **R11 — helm 4 sockets in `sockets.v2.json`.** The helm becomes a word host through the tuning ceiling
  and a regeneration. No code, schema or generator case names the helm. The helm re-run is a step
  **inside module 2's exit**. It runs after module 5 has published v2 **and** after the owner has run
  `resocket --write` (map §9.2 S9).
- **R12 — no count cap; scarcity is priced.** `SocketCombinationCap`, `SocketTuning.MaxCombosPerActor`
  and the Python `max_combos_per_actor` are **deleted in module 4**. Module 6 measures power against
  price, and module 8 publishes prices. No task counts, caps or suppresses active combinations.
- **R13 — blocked cells are reported by id.** Nothing is withdrawn automatically. Module 2's exit is
  *"every cell is `entry` or listed by id in the still-blocked report"*.
- **R20 — the `forge-gem` souls leg is a pricing lever.** The combo-budget report derives the leg's
  coefficient for cells whose cheapest route has no bore or imbue step. Socket-pricing publishes it in the
  same `materials` revision as any bore or imbue coefficient.
- **One compose, one projection.** A combination binds through `EquipProjector.Project`. It contributes
  through the equip atom reader under `combo:{role}:{hostItemRef}:{comboId}#c{circuit}`: the grammar
  reserved in actor-hub-ssot §8.1, plus a circuit suffix (C14). No private fold, no second `Bind()`.
  `combo-bind` owns "arm 2" (C15).
- **Generated data is never hand-edited.** The combination corpus changes through `generate
  --retry-blocked` (calls the model, so the owner runs it), `combogen-migrate --write`, and
  `combogen-reemit` (deterministic, no model call). Base types change through `resocket` (deterministic,
  but its `--write` is ask-first, so the owner runs it). Imbue rows come from a deterministic emitter.
- **Tuning is published with the tool** (`gk-core/tools/tuning/publish.py`, `v{n+1}`, never an in-place edit).
  Each revision's reader switch lands in the same commit as its publish (parent H7). Readers use one
  current-revision constant per domain; provenance records **filename** revisions only (map §4, C16).
- **Enforced when content is published, never during play.** The pricing bound is enforced at three
  points: the report's exit code, a BalanceGuard CI test, and `ComboPricingProvenance.Check` at boot.
  No player action is refused on price-per-power grounds (combo-budget §5).

## Dependency graph (modules)

```text
host-gate (1) ─┬──────────────────────────────────────► combo-bind (4) ──┐
               │                                            ▲             │
combination-regen (2) ──► recipe-import (3) ────────────────┘             ▼
   │  (2a: grants, report, rename, retire)                        combo-budget (6) ──┬──► tier-ladder (7)
   │                                                                  ▲   ▲          └──► socket-pricing (8)
   └──► circuit-topology (5) ──► resocket --write ──► combination-regen R11 step (2b)
             ▲ (owner)                 ┘
   combo-bind's Python cap deletion (SSH4.2) ── H3 ──► circuit-topology flip (SSH5.10)
```

The price loop inside wave 6/8: `SSH6.4` report → if red, `SSH8.5` materials publish (after
species-gear-chain `T32`, `T34`) → `SSH6.8` sockets v3 provenance → `SSH7.7` ladder + re-measure.

## Suggested order and parallel lanes (suggested, not enforced)

The only orders a builder **must** honour are the parent hard edges below, the ruling-5 sequence (an owner
ruling this program was specced under), and the same-commit couplings that stop a published file going
unread. Everything else is advice.

| Edge | Kind | Why |
|---|---|---|
| `SSH4.2` → `SSH5.10` | **parent H3** | the combogen reader on v2 hits `_require(..., "maxCombosPerActor")` and stops every generator run |
| `SSH5.10`, `SSH6.8`, `SSH7.7`, `SSH8.5` — publish and reader switch in one commit | **parent H7** | a published revision nothing reads is dark; two hosts on two revisions is a split brain |
| module 1 before `SSH7.2` (the ladder changes the matcher) | ruling 5 + SOLID gate | no extending a forked seam |
| `SSH2.5` (widened re-run) and `SSH5.12` → `SSH5.13` (R11 re-run) before `SSH6.8` (the published measurement) | ruling 5 | the measurement must see the corpus that ships. `SSH6.4` can be built and run earlier; a later corpus move changes the digest and forces a re-measure anyway |
| `SSH6.8` before `SSH7.7` and `SSH8.5`'s final re-measure | ruling 5 / code-enforced (`ComboPricingProvenance`) | the ladder and the prices cannot bind before they are measured |
| `SSH7.7` = ladder publish **and** its re-measure, one commit | code-enforced | boot refuses a ladder the provenance did not measure |
| `SSH8.5` after species-gear-chain `T32`, `T34` | parent §5 `materials` row | tie-break order for the shared file |

**Suggested lanes (separate sessions can run these in parallel):**

| Lane | Tasks | Notes |
|---|---|---|
| α — Core/host (C#) | `SSH1.1`–`SSH1.6` → `SSH3.1`–`SSH3.3` → `SSH4.3`–`SSH4.9` | starts at once; `SSH1.2`/`SSH1.3` fix live defects F5/F6 |
| β — generator (Python) | `SSH2.1`–`SSH2.4`, `SSH2.6`, `SSH2.7` | starts at once; `SSH2.5` is owner-run as soon as `SSH2.1`/`SSH2.2` land |
| γ — prep (no behaviour change) | `SSH4.1`, `SSH4.2` (cap deletion), `SSH5.1`–`SSH5.7` (pins, reader constants, `--remove-key`), `SSH6.5` | independent of α/β; do these early so the flip `SSH5.10` is a small commit |
| δ — measure and price | `SSH6.1`–`SSH6.8`, `SSH8.1`–`SSH8.6` | after the flip and the R11 re-run |
| ε — ladder | `SSH7.1`–`SSH7.8` | `SSH7.1`–`SSH7.6` can run beside δ; `SSH7.7` waits for `SSH6.8` |

**Owner-run steps (not gates):** `SSH2.5` (widened `--retry-blocked`, calls the model), `SSH5.12`
(`resocket --write`, an ask-first corpus rewrite), `SSH5.13` (R11 helm re-run, calls the model), `SSH7.8`
(the ask-first DDL drop), and `SSH8.2` only if the imbue emitter cannot run without the model. Each one is
a task whose acceptance is the owner's run output. Nothing unrelated waits for them.

## Phases

| Wave | Module(s) | Tasks | Sizes | Parallel-safe |
|---|---|---|---|---|
| 1 | `host-gate` | SSH1.1–1.6 | M, S, S, S, S, XS | 1.1 ∥ 1.2 ∥ 1.6; 1.4/1.5 after 1.1 |
| 2 | `combination-regen` (first exit) | SSH2.1–2.7 | S, S, S, S, owner, XS, S | 2.1 ∥ 2.2 ∥ 2.3 ∥ 2.7; 2.5 after 2.1+2.2 |
| 3 | `recipe-import` | SSH3.1–3.3 | S, XS, M | 3.1 ∥ 3.2 |
| 4 | `combo-bind` | SSH4.1–4.9 | S, S, S, S, S, M, S, S, S | 4.1 ∥ 4.2 ∥ 4.3 ∥ 4.5 |
| 5 | `circuit-topology` + `combination-regen` R11 step | SSH5.1–5.13 | S, S, S, S, XS, S, XS, M, S, M, S, owner, owner | 5.1–5.7 all parallel prep |
| 6 | `combo-budget` | SSH6.1–6.8 | S, M, S, M, XS, S, S, M | 6.1 ∥ 6.5 ∥ 6.6 |
| 7 | `tier-ladder` | SSH7.1–7.8 | S, M, S, S, S, S, M, owner | 7.1 ∥ 7.3 ∥ 7.4 |
| 8 | `socket-pricing` | SSH8.1–8.6 | S, S/owner, S, S, M, XS | beside wave 7 |

**Total: 60 tasks**: 4 are owner-run, and `SSH8.2` is owner-run only if the emitter needs the model.

## Checkpoints (review points, not gates)

| # | After | Evidence |
|---|---|---|
| CP1 | wave 1 | one matcher (duplicates removed, found by reflection); the endpoint previews the real role/frame/set flag; an unbored chassis reads *reachable*; rulings 1–3 each have a failing-if-broken test |
| CP2 | wave 2 | `socket-word` is gone from both kind tables; the legacy partition is retired by the verb with a ledger record; the still-blocked report lists every non-`entry` cell by id; the gating metric still gates |
| CP3 | waves 3–4 | boot seeds the real corpus with zero refusals; a firing word binds, contributes under `combo:…#c0`, and withdraws in both orders; the live probe through the real endpoints shows it on the real sheet; `guard-actor-hub.ps1` and `guard-single-writer.ps1` are green |
| CP4 | wave 5 = **module 2 exit + module 5 exit** | `sockets.v2.json` is the only current revision; the evaluator runs per circuit; the corpus was re-stamped by the verb; the R11 re-run's `Coverage/HostRoleDiversity` is printed; every cell is `entry` or reported by id (R13); full suite run once (crosses Core/Data/Server/tool/seedsmith) |
| CP5 | wave 6 | the report exits 0 on the shipped files; the BalanceGuard test is green in CI; `sockets.v3.json` provenance names filename revisions and the corpus digest |
| CP6 | waves 7–8 = program exit (parent CC6) | the ladder's rung 1 equals today; the ladder was re-measured in the same commit it was published; imbue can be paid for every frame × concrete element; a chaff chassis can be bored → imbued → filled → bound end to end; full suite once (crosses boundaries) |

## Cross-program edges

| Edge | With | Rule |
|---|---|---|
| Arm 2 (combination grants) | species-gear-chain `socket-combat-wiring` (`T21`, `T22`) | **`SSH4.6` owns arm 2** (map C15; parent §3). species-gear-chain builds arm 1 (inserts) only. The insert arm is already in code (`EquipProjector.cs:98`–`:111`, `EquipAtomSource.cs:145`), so `SSH4.6` extends that seam. If `T21`/`T22` are still open when `SSH4.6` starts, coordinate on `EquipProjector.cs` and `RpgStore.Items.cs` (shared files) instead of forking |
| `forge-gem` leg shape | species-gear-chain `gem-tier` (`T8`, `T9`) | `gem-tier` owns the leg's shape. `SSH8.5` reprices only the souls coefficient, at the report's derived value (R20) |
| `materials` revision order | species-gear-chain `T32`, `T34` | parent §5: `T32` → `T34` → `SSH8.5`. Whoever publishes later rebases on `v{n}` and takes `v{n+1}`. species-gear-chain's in-place `version` bumps are theirs to correct (map C16) |
| Provenance invalidation | any program that later publishes `sockets`, `strain-splice` or `materials` | after `SSH6.8`, boot refuses a revision the last measurement did not see. A later publisher re-runs `python -m seedsmith items combo-budget --report` and republishes `comboPricing.measuredAgainst` in the same commit |
| `actor-hub-ssot.md` §8.1 | ActorHub SSOT doc | `SSH4.5` amends the reserved `combo:` row with `#c{circuit}` in the same change as the code |
| Sealed item docs | item module 16/21 | never edited; contradictions are recorded in map §6 only |

## Tuning publishes owned (parent §5 rows)

| File | Revision | Task | Parent §5 row |
|---|---|---|---|
| `sockets` | v2: eight-socket ceilings, `head-guard` 4, `rarityGrant` doubled, `maxCombosPerActor` removed | `SSH5.10` | `sockets` (1st) |
| `sockets` | v3: `comboPricing` + `measuredAgainst` | `SSH6.8` | `sockets` (2nd) |
| `sockets` | next: re-measured provenance for the ladder | `SSH7.7` | `sockets` (same row, re-publish; map §4) |
| `strain-splice` | v2: `tierLadder` replaces `minTierPlan` | `SSH7.7` | `strain-splice` |
| `materials` | next: derived bore / imbue / `forge-gem` souls coefficients (R12, R20), **only if the report is red** | `SSH8.5` | `materials` (after species-gear-chain `T32`, `T34`) |

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| The flip (`SSH5.10`) touches many readers at once | readers move to one constant **still naming v1** first (`SSH5.2`–`SSH5.6`), so the flip changes one constant per language |
| The corpus host-set contract goes red between the v2 flip and the owner's re-stamp | ship the **subset** form (corpus hosts ⊆ tuning hosts, no row above its ceiling) in `SSH5.1`; tighten to equality in `SSH5.12` once the re-stamp lands |
| A later publish by another program leaves the server refusing to boot | the cross-program edge above; the refusal names the stale field |
| species-gear-chain edits `materials.v1.json` in place (C16) after `SSH8.5` publishes v2 | the edit is dead history that nothing reads; `SSH8.4`'s literal guard makes it visible |
| Concurrent edits to `EquipProjector.cs` / `RpgStore.Items.cs` by species-gear-chain | one session per problem; check `tasks/sessions/*.json` before `SSH4.6` |
| The report's `power(c,k)` needs `ActorPowerCache.Compose` (C#), but the readable report is Python | `SSH6.4` takes power from the one C# computation, never a Python re-implementation; see Defaults |
| Blocked cells stay blocked after both re-runs | by design (R13): the report is the deliverable; each per-id ruling is applied by the generator later and moves the corpus digest, so it triggers a re-measure |

## Defaults shipped behind (no gates)

| Unknown | Default |
|---|---|
| Owner rulings on still-blocked cells (R13) | cells stay `blocked` in the ledger and are listed by id; modules 3–8 proceed |
| Owner declines `resocket --write` | v2 ships anyway; the R11 re-run (`SSH5.13`) does not run; the subset host-set contract stays; `HostRoleDiversity` shows no helm |
| `socket_combo_ingredient.min_tier` DDL drop (ask-first) | the column stays, is written as `0`, and the matcher never reads it, until `SSH7.8` is approved |
| Materials reprice | none unless `SSH6.4` is red; then the derived value (never lower) |
| `comboPricing.maxRatioToRarityRouteMilli` | 1000 (D23 written as arithmetic); moving it is ask-first |
| Ladder rungs 2–4 | the spec's working values; a balance pass republishes them |
| Where the Python report gets `power(c,k)` | a JSON dump written by the C# `ComboPricing` computation, read by the report. The builder of `SSH6.4` picks the entry point, which must not be a second implementation |
| Imbue rows if the recipe CLI cannot run the emitter without the model | the emitter runs by itself (the forge-gem precedent); otherwise the owner runs the write (`SSH8.2`) |
