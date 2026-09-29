# Implementation plan: `summoner-convergence` — the parent plan

**What this is.** The one parent over every program specced or amended in the 2026-09-18 spec round.
It owns **cross-program order, parallel lanes, shared-file sequencing and checkpoints**. Each program's
own tasks live in its own plan/todo pair (below). This file never duplicates a sub-plan's task; it
names the edges between them.

**Binding inputs:** [spec-rulings-2026-09-18.md](../docs/architecture/spec-rulings-2026-09-18.md) (R1–R24) ·
the landed `decisions.md` rows (commit `1575db58`) · each program's map. Nothing here re-litigates a
ruling or a map decision.

**Suggested, never enforced.** The owner asked for order and parallelism as *suggestions based on
dependencies*. Every "lane" and "suggested order" below is advice. The only things a sub-plan must
honour are the **hard edges** (§4): places where doing B before A is wrong code or an unattributable
golden move, not just an inconvenient order. Everything else may be reordered, parallelised or split by
whoever builds it.

**Autonomy (owner ruling R28, 2026-09-18).** Full, no human gate — agents are the gates. Every sub-plan step marked
*owner-run*, *owner review*, *owner-approved* or *ask first* is run by the implementation orchestrator and
passes an **independent agent review** instead. R26 (Roslyn approved) and R27 (save-identity migration built
directly on the branch, SE4.20 last) also apply. This paragraph overrides the older wording inside the
sub-plans; it does not change the rulings, the hard edges or the repo's hard rules.

**No pre-work gates.** Per `planning-and-task-breakdown` "Gates vs. checkpoints": nothing here blocks
*starting* on an external decision. All 24 rulings are in; every remaining unknown ships behind a stated
default inside its sub-plan. The one irreversible action in scope — `save-identity`'s schema migration —
is protected by its own spec (timestamped backup, one transaction, idempotent re-run), not by a gate.

---

## 1. Programs and their plan pairs

| Program | Map | Plan / todo | State of the pair | Task id prefix |
|---|---|---|---|---|
| `action` (A26 = `T62`/`T63`, A31 = `T67`, **A33 new = `T74`**) | [action-map.md](../docs/architecture/action-map.md) §17 | [action-plan.md](action-plan.md) / [action-todo.md](action-todo.md) | existing; A33 task appended | `T` (existing numbering) |
| `action-skill-tiers` | [map](../docs/architecture/action-skill-tiers-map.md) | [plan](action-skill-tiers-plan.md) / [todo](action-skill-tiers-todo.md) | new | `ST` |
| `action-enrich` | [map](../docs/architecture/action-enrich-map.md) | [plan](action-enrich-plan.md) / [todo](action-enrich-todo.md) | new | `AE` |
| `solid-enforcement` (+ **`save-identity`**) | [map](../docs/architecture/solid-enforcement-map.md) | [plan](solid-enforcement-plan.md) / [todo](solid-enforcement-todo.md) | existing; save-identity tasks appended | `SE` (existing numbering) |
| `species-progression` | [map](../docs/architecture/species-progression-map.md) | [plan](species-progression-plan.md) / [todo](species-progression-todo.md) | new | `SP` |
| `empire-progression` | [map](../docs/architecture/empire-progression-map.md) | [plan](empire-progression-plan.md) / [todo](empire-progression-todo.md) | new | `EP` |
| `build-preset` | [map](../docs/architecture/build-preset-map.md) | [plan](build-preset-plan.md) / [todo](build-preset-todo.md) | new | `BP` |
| `species-gear-chain` | [map](../docs/architecture/species-gear-chain-map.md) | [plan](species-gear-chain-plan.md) / [todo](species-gear-chain-todo.md) | existing; amended for R9/R10/R20/R22 + strengthen pass | `T` (existing numbering) |
| `strain-splice-host` | [map](../docs/architecture/strain-splice-host-map.md) | [plan](strain-splice-host-plan.md) / [todo](strain-splice-host-todo.md) | new | `SSH` |
| `notification-ssot` | [map](../docs/architecture/notification-ssot-map.md) | [plan](notification-ssot-plan.md) / [todo](notification-ssot-todo.md) | new | `NS` |
| `test-verification-boundary` | [map](../docs/architecture/test-verification-boundary-map.md) | [plan](test-verification-boundary-plan.md) / [todo](test-verification-boundary-todo.md) | new | `TVB` |

A cross-program reference in any todo is written `<prefix><id>` (e.g. `SE4.12`, `SP6.1`), never a bare
number, so it cannot be mistaken for a local task.

## 2. The four suggested lanes

Lanes group programs that share code and must agree on shared numbers. **Different lanes can run fully
in parallel**, in separate sessions; inside a lane, the suggested order follows the dependencies.

```
LANE A — actions                  LANE B — identity & progression          LANE C — items               LANE D — infrastructure
action A26 ─┐                     SE commander-identity                    species-gear-chain           test-verification-boundary
action A31 ─┼─(visibility only)   │                                        (remaining + craft-assurance)   (after SE0.1–0.4, SE0.7)
action A33 ─┘                     ▼                                        │                            notification-ssot
ST2 → ST1 ─┐                      SE save-identity (first slice early,     ▼                            (independent; wave 5 waits
ST3 → ST4 → ST5                   │   then migration)                      strain-splice-host             on its G0 asks)
           ▼                      ▼                                        (1→2→5→6→7/8)
AE action-base ──(golden 3)──► SP species-progression (C1 fix, 6.1)
AE lawn-action-base               │
                                  ▼
                                  EP empire-progression (waves A–D)
                                  │
                                  ▼
                                  BP build-preset (after EP)
```

| Lane | Suggested first task | Why first |
|---|---|---|
| A | `ST2.1` → `ST2.2` (cost scaled once) | a live defect (costMulti²), smallest blast radius, and first in the golden order |
| B | `SE4.1` commander-identity, then `save-identity` first slice **`SE4.11`–`SE4.14`** (types, `rpg_save_empires`, `HumanEmpireOf`, `OwnsSpecimenUnlocked`) | most of lanes B's tables are born keyed by it; the first slice unblocks `SP` mod-ledger (the fusion-pick bug) without waiting on the migration |
| C | `T39` (`craft-assurance` free-ward fix) | a live defect (enhancement protection is free), no dependencies |
| D | `TVB0.1` (`release.yml` exit checks) |
| D (also) | `SE0.1`–`SE0.8`, then `SE` waves 1–3 (guard registry, runner, retire-atk, new guards) | solid-enforcement's own spine: `TVB`'s registry lane waits on `SE0.7` (H5), and `SE1.6` (retire-atk content regeneration) receives `AE1.4`'s list of `atk`-granting content. It is infrastructure, so it sits in lane D; `SE` wave 4 (identity) is lane B | a live defect (release gate masks failures), touches nothing else |

Four live defects found in the spec round each have a "fix first" task in their lane (above) plus
`SP` mod-ledger's fusion-pick fix. None needs another lane.

## 3. Cross-lane couplings (soft — coordinate, don't block)

| Coupling | Between | Rule |
|---|---|---|
| Golden re-bless order | A and B | §4 hard edge H1 |
| Tuning-file revisions | all | §5 ledger; one publish per revision, in the stated order |
| `EffectiveRungOf` resolver | `ST2`, `AE action-base` | ST2 owns the pre-scale line; AE makes the resolver public and reachable; neither re-implements the other |
| Combination binding ("arm 2") | C | owned by `SSH combo-bind`; species-gear-chain never builds it |
| Verification registry schema | D and `SE` | SE0.7 → TVB registry-contract (schema 3) → python-test-lane (4) → seam-coverage (5) |
| Save identity keys | B and `NS`, `BP`, `EP` | every new empire-owned table is born `(save_id, empire_id, …)`; wire names keep "player" (R17) |
| Save-switch notice to the injector | B, `SE`, `NS` | **one** generic server→injector notice on `PUT /api/players/current`, built by `SP6.6`; `SE` and `NS` reuse it and never add a second (save-identity carries ownership on each spawn and no longer emits one) |
| `RpgStore.WorldTurns.cs` (four editors) | B | suggested order: `SP1.2` → `EP1.14` → `EP3.8`/`EP3.11` → `EP4.18`; `SE4.34`/`SE4.35` rebase onto whichever landed first |
| Excluded-species admission | C and `creature-seed` | ask 4 in `creature-seed-map.md`; species-materials waits on it or ships behind its refusal |

## 4. Hard edges — the only orders a sub-plan must honour

| # | Edge | Why it is hard |
|---|---|---|
| H1 | Golden re-bless order (**a re-bless may share a commit with the ONE code change that causes it — preferred, so the shared branch is never red — and never with a second cause**): `ST2.3` → `ST1.3` → `AE1.5` → `SP1.2` C1 fix (a defect correction, not a re-bless) → `SP6.1` → `EP4.18` R23 Zomboss pool layer. **Independent single-cause moves** that may land at any point but never share a commit with another cause: `EP1.14` (specimen default build), `EP2.7`, `EP2.13`+`EP2.14` (regenerated build plan) | `tunables-ssot.md` T7: each golden move must be attributable to exactly one cause. Two causes in one re-bless is unreviewable. Each re-bless is its own commit |
| H2 | `SE save-identity` migration (**`SE4.20`**, which makes `Init` run it; built in one worktree SE4.15–SE4.30) lands before any task that **writes** a `(save_id, empire_id)`-keyed row of a table it re-keys (`rpg_actor_progression`, XP ledger) | the migration is the one irreversible step; writing new-shape rows first would be migrated twice |
| H3 | `SSH` Python cap deletion (module 4) before `SSH circuit-topology`'s switch to `sockets.v2` | otherwise every generator run fails on the missing `maxCombosPerActor` key |
| H4 | `TVB python-test-lane`'s CI pytest step lands only after the stale `test_resource_ownership` pins are dropped | R15: CI never goes red from this program |
| H5 | `SE0.7` (registry schema 2) before `TVB registry-contract` (schema 3) | both rewrite the same file; schema numbers must be monotonic |
| H6 | `AE action-base` replaces the `LiveAtk` read in the same change that introduces the base | never a window where both feed damage |
| H7 | A tuning revision's host reader switch (server `Program.cs` **and** injector `RpgHost.cs` where both load it) lands in the same commit as the publish | a published file nothing reads is dark; two hosts on two versions is a split brain |

Everything not in this table is a suggestion.

## 5. Shared tuning-file revision ledger

The single place that orders publishes to files more than one program touches. Each row's owner map
holds the detail; this table only fixes the order. Publish = `gk-core/tools/tuning/publish.py` → `v{n+1}`,
never an in-place edit (T4).

| File | Next revisions, in order | Owners |
|---|---|---|
| `action-rungs` | v3 scope windows (`ST3.1`, with the planner switch) → v4 R8 `referencePower` retune **published inside `ST5.2`'s commit together with every reader switch** (H7; `ST4.5` only records `recommendedReferencePower`) | action-skill-tiers |
| `action-base` | v1 created (`AE action-base`) | action-enrich |
| `aptitudes` | v9 retire-atk (`SE1.4`) → next: R21 `read.layerWeightMilliByScope` (`SP` 6.1) | solid-enforcement, species-progression |
| `progression` | per `empire-progression-map.md` "Tuning version sequence": lawn-deploy-progression, `SP` zomboss-commander-clock, `EP` empire-level | creature-lawn-deploy, species-progression, empire-progression |
| `species-build` | per `empire-progression-map.md` "Tuning version sequence" (5 publishes, 4 modules) | empire-progression |
| `aptitude-presets` | v2 (`EP1.3`) | empire-progression |
| `sockets` | v2 circuit topology incl. helm 4 (`SSH circuit-topology`) → v3 `comboPricing` (`SSH combo-budget`) | strain-splice-host |
| `materials` | species-gear-chain `T32`, `T34` → `SSH socket-pricing` (incl. R20 `forge-gem`) | species-gear-chain, strain-splice-host |
| `strain-splice` | v2 tier ladder (`SSH tier-ladder`) | strain-splice-host |
| `deployment-hierarchy` | v3 craft wear (`T24` if it changes the table, else with `T49`) | species-gear-chain |
| `enhancement` | v2 only if `T49` moves the bands (conditional) | species-gear-chain |
| repair / upgrade-cost rows (`T23`, `T37`) | as named in `species-gear-chain-plan.md` "Tuning revisions"; conditional | species-gear-chain |
| notify catalog | v1 `NS notify-vocabulary` → v2 `NS world-notify-source` → v3 `NS cache-notify-source` | notification-ssot |
| `species-material-run`, `craft-assurance`, `creature-yield` | v1 created by their modules | species-gear-chain |

If two lanes race for the same file, the later publisher rebases onto the earlier `v{n}` and takes
`v{n+1}`; the order above is the tie-break.

**Pricing provenance (from `SSH6.8` on).** `sockets`, `strain-splice` and `materials` carry a
`measuredAgainst` provenance the server checks at boot. **Any** later publish of one of those three files —
by any program, `species-gear-chain` included — re-runs `combo-budget --report` and republishes the
provenance in the **same commit**, or the server refuses to boot (a named refusal, not a silent pass).

## 6. Checkpoints (review points, not gates)

| # | Checkpoint | Evidence |
|---|---|---|
| CC1 | **Live defects closed** — costs scaled once, fusion picks accepted, enhancement protection paid, release gate exit-checked | each lane's first task green; the four regression tests named in their sub-plans |
| CC2 | **Identity foundation** — `commander-identity` and `save-identity` landed; migration run on a real save copy; backup present | `SE` checkpoint evidence; a re-run of the migration is a no-op |
| CC3 | **Damage from the action** — battle and lawn hits read the action base; `LiveAtk` has no damage reader | `AE` Checkpoints 1–2; golden re-bless commits in H1 order |
| CC4 | **Layers resolve alone** — `SP` 6.1 re-bless landed with its explained table; zombie XP credits Zomboss's empire | `SP` checkpoints |
| CC5 | **Empire progression live** — empire level, earned free respecs, priced unique respec, creature commanders | `EP` CP1–CP6 |
| CC6 | **Items converge** — species materials 2/8/0, combinations bind and are priced, helm hosts words | `T` and `SSH` checkpoints; combo-budget report green |
| CC7 | **Infrastructure** — python lane, sharding, Core split, notifications: waves 1–6 landed except Gate G2 (blocked: no real world-creation route, `WS-live-1`) and the gated centre (`NS6.8` → `NS6.11`/`NS6.12`) | `TVB`, `NS` checkpoints |
| CC8 | **Convergence** — full suite green (`test-fast.ps1 -AllDefault` — the one place the full suite is the right tool: end of a large cross-program feature); a live probe per `live-probe-standard.md` on a real save | the three full-suite conditions in AGENTS.md all hold here |

## 7. Working rules for every sub-plan (restated so a builder reads them here)

1. **Verify each task once** with `.\scripts\verify-change.ps1 -Paths <every touched path> -Session <id>`.
   Full suite only at CC8 or a sub-plan's own final checkpoint.
2. **One logical change per commit** with plain git (`git add <explicit paths>`, then `git commit`); never `-A`/`-a`. (The repo-git gate was retired 2026-09-19.)
3. **One session per problem** (`tasks/sessions/<id>.json`, status `active` → `merged`), never
   touching another session's paths.
4. **Tunables in `gk-core/data/tuning/`** through `publish.py`; §5 order for shared files.
5. **Generated data is never hand-edited** — change the generator and regenerate.
6. **Tests assert contracts and closed vocabularies**, never population counts or generated text.
7. **A golden move is one cause, one commit** (H1). A todo that lists the re-bless as its own task (`ST2.3`, `ST1.3`, `AE1.5`, `SP6.1`, `EP4.18`, `EP1.14`, …) may be committed **together with** its code task — that is still one cause — and should be, so no commit on the shared branch leaves goldens red.
8. **SOLID and the ActorHub one-compose rule** — a task that needs a second composer or a private fold is
   wrong, not a special case.

---

## Appendix — sub-plan template (every new plan/todo pair follows this)

**`tasks/<program>-plan.md`:** header (map, specs, tasks links, one-line relationship to this parent) ·
Overview (one paragraph) · Architecture decisions (from the map, not re-litigated; cite rulings R#) ·
Dependency graph (ASCII, modules) · **Suggested order and parallel lanes** (explicitly "suggested, not
enforced"; mark which edges are this parent's hard edges H#) · Phases table (wave, modules, task ids,
sizes, parallel-safe) · Checkpoints (review points) · Cross-program edges (with `<prefix><id>`) ·
Tuning publishes (rows of §5 it owns) · Risks and mitigations · Defaults shipped behind (no gates).

**`tasks/<program>-todo.md`:** one entry per task, in the house format:

```markdown
- [ ] **<PREFIX><wave>.<n> — <title>** · <XS|S|M|L> · deps: <ids or —> · *(spec: <module-id>)*
  - Acceptance: <specific, testable; ≤3 bullets>
  - Verify: `<real command>` (verify-change -Paths …, dotnet test --filter …, pytest …)
  - Files: <paths likely touched, ≤5; split if more>
```

Checkpoints appear between waves as `### Checkpoint <n>` with `- [ ]` evidence lines. No task is L+ —
split it. No task touches more than ~5 files. Every task traces to a module id in its map.
