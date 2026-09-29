# Implementation plan: `solid-enforcement`

**Map:** [docs/architecture/solid-enforcement-map.md](../docs/architecture/solid-enforcement-map.md) ·
**Specs:** [docs/architecture/solid-enforcement/](../docs/architecture/solid-enforcement/) ·
**Tasks:** [solid-enforcement-todo.md](solid-enforcement-todo.md) ·
**Parent:** [summoner-convergence-plan.md](summoner-convergence-plan.md) (lane B foundation: this
program's `commander-identity` and `save-identity` are what lane B's tables are keyed by)

## Overview

Phase 3 of the SOLID program. Phases 1 and 2 fixed violations. This phase makes **each class of
violation impossible to merge.** Every SOLID invariant gets a registry row, a guard wired through one
runner, a cleared backlog, and then a failing gate. It also lands the three structural instances the
owner ruled on: retire `atk`, split `CommanderId`, and bring every file under its responsibility
budget. **Amended 2026-09-18 (rulings R3 + R17):** a sixteenth module, `save-identity`, builds
directly after `commander-identity`: a save owns its empires, keyed `(SaveId, EmpireId)`, and Zomboss
stops being a player row.

Sixteen modules in six waves: the original 48 tasks plus 33 `save-identity` tasks (SE4.11–SE4.43,
numbered after SE4.10 so no existing id moved). Nine checkpoints (0–4, plus 4a/4b/4c inside wave 4,
plus 5). **No hard pre-work gate anywhere.** Every
owner question has a default the plan ships behind (see "Owner questions").

## Architecture decisions (from the map; not re-litigated here)

1. **One guard catalog, one runner.** `gk-core/scripts/enforcement-registry.v1.json` owns guard identity,
   tier and status. `scripts/run-guards.ps1` is the only way CI, `deploy-play` and `verify-change` run
   guards. It replaces three hand-kept lists and one duplicate id→script map.
2. **Green-first, then gate** (owner ruling). `status: backlog` exists only *during* the module that
   owns the backlog. The end state has zero backlog rows.
3. **Extend, don't fork.** Two existing guards are extended (`single-writer` W2/W3; `test-substrate`
   swallowed `File.Delete`) rather than duplicated, and one existing register (`stub-register.md`)
   becomes the debt ledger rather than gaining a sibling.
4. **Markers over heuristics** where a scan cannot tell legitimate from violating:
   `citations-historical`, `pin: closed-vocabulary|immutable`, `srp-budget-exempt`.
5. **`retired` is a registry state.** `progression.bonus.atk` is dropped by the aptitude loader, so
   immutable tuning history stays loadable (`AptitudeResolver.cs:39` would otherwise throw on every
   old version).
6. **`CommanderId` is split before it is opened:** `EmpireId` (the faction) and `CommanderRef` (the
   unit), both open, behind one `ICommanderDirectory`. Saves are byte-compatible. The player's first
   commander displays the player's name; an empty save seeds "Crazy Dave" (rift-gate decision 7, Q5).
7. **The `players` row is the save** (R17): `SaveId` = today's player id, no id rewrite; empires are
   data in `rpg_save_empires(save_id, empire_id, controller)`; code asks `HumanEmpireOf(save)`, never
   assumes `"dave"`. Two empire tiers: **A** re-keyed now (`rpg_actor_progression`, `rpg_xp_ledger`,
   specimens' `empire_id`), **B** empire-typed API that throws for a non-human empire. A table created
   after this module is born `(save_id, empire_id, …)`. Rows S1–S4 in `decisions.md` (landed).

## Dependency graph

```
enforcement-registry ──► guard-runner ──┬──► wire-green-guards
        │                               ├──► commit-policy-green
        └──► debt-ledger                ├──► retire-atk ───────► pvz-write-surface
                  │                     ├──► tuning-immutability
                  │                     ├──► repo-boundary
                  │                     ├──► vocabulary-mirror
                  │                     ├──► population-pin
                  │                     ├──► doc-citation-gate
                  │                     └──► srp-file-budget (last: moves the most code)
                  └──► commander-identity ──► save-identity ──► srp-file-budget splits
                                                   (a) first slice ─► (b) migration unit ─► (c) surfaces
```

## Phases

| Wave | Modules | Tasks | Size | Can run in parallel |
|---|---|---|---|---|
| **0 — spine** | `enforcement-registry`, `guard-runner`, `debt-ledger` | SE0.1–SE0.8 | 2 S, 5 M, 1 XS | SE0.8 alongside SE0.4–0.7 |
| **1 — green what exists** | `wire-green-guards`, `commit-policy-green`, `retire-atk` | SE1.1–SE1.7 | 2 S, 5 M | three lanes: {1.1}, {1.2}, {1.3→1.7} |
| **2 — new guards, small backlogs** | `tuning-immutability`, `repo-boundary`, `pvz-write-surface`, `vocabulary-mirror` | SE2.1–SE2.7 | 3 S, 4 M | four lanes (`pvz-write-surface` needs Checkpoint 1) |
| **3 — backlog-heavy guards** | `population-pin`, `doc-citation-gate` | SE3.1–SE3.13 | 13 M | backlog batches fully parallel by folder |
| **4 — structural instances** | `commander-identity`, `save-identity`, `srp-file-budget` | SE4.1–SE4.4, SE4.11–SE4.43, SE4.5–SE4.10 | commander 4 M; save 20 M, 13 S; srp 4 M, 1 S, 1 XS | `commander-identity` → `save-identity` → `srp-file-budget` splits (SE4.5, the guard, any time after SE0.5) |
| **5 — action base stats** | `action-base-stats` | SE5.1, then tasks from its spec | — | after wave 1 (`retire-atk`); independent of waves 2–4 |

### Parallel lanes (multi-agent execution)

The plan is written so a manager session can assign lanes to separate agents. Rules for that:

- **One session record per lane** (`tasks/sessions/<lane>.json`) with non-overlapping `paths`, checked
  by `scripts/session-boundary-check.py` before the first edit (AGENTS.md session-boundary rule).
- **Registry edits serialise.** Every module ends by flipping its own row in
  `enforcement-registry.v1.json`. Lanes rebase that one file, and never edit another lane's row.
- **Wave 3 backlog batches are per-folder** and share nothing. They are the most parallel work in the
  program, and a batch agent needs only its folder list from `--targets`.
- **Wave 4 is deliberately serial.** All three modules edit many of the same files. Two exceptions,
  both suggested: `save-identity`'s first slice (SE4.11–SE4.14) needs only SE4.1's `EmpireId`, so it may
  run beside SE4.2–SE4.4 (rebase `RpgStore.cs`: SE4.4 owns the seed *name*, SE4.12 the seed's
  *empires*); and inside stage (c), Tier B batches 2–4 are parallel-safe.

## Checkpoints

| # | After | Must be true | Who |
|---|---|---|---|
| **0** | Wave 0 | CI green with `run-guards.ps1 -Tier ci` as the only guard entry; the registry meta-test green with falsifiers; **the owner has seen the map**. The review is non-blocking: work continues, and a redrawn boundary edits specs | owner (review), script (the rest) |
| **1** | Wave 1 | every guard that existed at program start is `gating` or `local`; `retire-atk` done; **full suite green once** (cross-boundary point: Core+Data+Server+Injector+tuning+generated) | script |
| **2** | Wave 2 | four new invariants gating; the pollution files gone and not recreated | script |
| **3** | Wave 3 | `population-pin` and `doc-citations` gating; 0 findings | script |
| **4a** | SE4.11–SE4.14 | first slice on the shared branch; the seams other programs build against exist with tests | script |
| **4b** | SE4.15–SE4.30 | migration unit merged once; rehearsed on a copy of a real save (report, `.bak`, no-op re-run, rollback drill); = parent **CC2** | script, then owner (sees the report) |
| **4c** | SE4.31–SE4.43 | `save-identity` closed: every spec success criterion ticked, I1–I4 gating, full suite green | script |
| **4 = close** | Wave 4 | registry has **zero `backlog` rows**; full suite green; SR-19..SR-23 and the save-identity row struck; owner items surfaced (below) | script, then owner |

## `save-identity` inside lane B (amendment 2026-09-18)

### Suggested order (suggested, not enforced)

```
SE4.1 ─► SE4.11 ─┬─► SE4.12 ─┬─► SE4.14 ─────────────────┐        (a) first slice — Checkpoint 4a
                 └─► SE4.13  └─► SE4.29 (any time)        │
SE4.4 ───────────────────────────────────────────────────┤
                                                          ▼
        SE4.15 ─► 4.16 ─► 4.17 ─► 4.18 ─► 4.19 ─► SE4.20 [H2] ─► 4.21 ─► 4.22 ─┬─► 4.23
        (dormant steps, test-called)          (activate)                        ├─► 4.26
        SE4.27 (pure Core, any time after SE4.11) ─────────────────────────────►├─► 4.28
                                                   SE4.20 ─► 4.24 ─► 4.25       │
                                                          ▼                      ▼
                                   SE4.30 full suite + real-save-copy rehearsal ─► merge   (b) — Checkpoint 4b / CC2
                                                          ▼
        4.31 ─► 4.32, 4.33 · 4.34 ─► 4.35 ─► 4.36 · 4.37 ─► {4.38, 4.39, 4.40} · 4.41 · 4.42 ─► 4.43   (c) — Checkpoint 4c
                                                          ▼
                                              SE4.6, SE4.7, SE4.9 (srp splits of the same files)
```

- **Only one edge here is a parent hard edge: H2.** SE4.20 is "the migration lands". No task in another
  program may **write** a `(save_id, empire_id)` row of `rpg_actor_progression` or `rpg_xp_ledger`
  before it: in practice `SP zomboss-commander-clock`, `EP ai-empire-species` and `EP empire-level`
  (the `empire` progression kind).
- **One in-plan ordering protects the irreversible step:** SE4.20 must not reach the owner's data
  directory without SE4.21–SE4.29 in the same build. **Owner ruling R27 (2026-09-18): built directly on the
  branch, with SE4.20 landing LAST** — SE4.15–SE4.19 and SE4.21–SE4.29 land first (no boot behaviour until
  SE4.20), then SE4.20 turns the migration on, then SE4.30 proves it on a real save copy. That is an ordering, not a pre-work gate: nothing waits on a decision.
- Everything else is advice. SE4.27 and SE4.29 are callable early; stage (c) tasks are independent of
  one another except where a dep is listed.

### Cross-program edges

| Edge | Direction | Kind |
|---|---|---|
| SE4.11–SE4.14 (first slice) → `SP species-mod-ledger` (fusion-pick fix; table born `(save_id, empire_id, …)`), `SP empire-species-container`, `EP commander-roster`, `EP respec-free-counter`, `EP empire-level`, `NS notify-store` (`save_id`) | they build on these seams | soft (parent §3 "Save identity keys") |
| SE4.12 `IsLiveSave` + SE4.29 → `NS player-routing` (`JoinPlayer` refuses archived rows; boot catch-up walks `ListPlayers`) | they consume | soft |
| **SE4.20 → any writer of re-keyed Tier A rows** (`SP zomboss-commander-clock`, `EP ai-empire-species`, `EP empire-level`) | must precede | **hard, parent H2** |
| SE4.21 (`CommanderLevelOf`, `SaveOfRunUnlocked`, `EmpireRef` XP writes) → `SP zomboss-commander-clock`; `SpeciesLevelOf` typing → `EP ai-empire-species` (its separate `rpg_empire_species_progression` table is superseded) | they consume | soft |
| SE4.34/SE4.35 ↔ `SP layer-source-selector` (same world-turn provider, `RpgStore.WorldTurns.cs:559-591`) | whichever lands second rebases; this program owns only the key encoder and `HumanEmpireOf` | soft |
| SE4.14 `OwnsSpecimenUnlocked` + SE4.31 `UniqueActorDto.empireId` → `EP specimen-respec-price` (keying-sweep mismatch 1: payer is the specimen's `EmpireRef`) | they consume; fix is theirs | soft |
| Keying-sweep mismatch 2 (`BP preset-store` born Tier B) and mismatch 3 (`species-progression-ideal.md:441`) | fixed by their owners; SE4.43 only reports what remains | none |
| SE0.8 (ledger `solid` kind) → SE4.11 row; SE0.4/SE0.2 (registry) → SE4.42's I3/I4 on the existing `open-identity` row | inside this program | — |
| Save switch reaching the injector | `SP6.6` | save-identity carries ownership on each spawn command (`SE4.28`) and emits **no** save-switch notice; `SP6.6` builds the one server→injector notice, and nothing here adds a second (parent §3) |

### Tuning publishes owned

**None.** `save-identity` changes identity and keys only; it owns no row of the parent's §5 ledger. Its
one data file, `gk-data/packs/fusion/data/seed/saves/_registry/new-save-empires.v1.json`, is an authored registry (hand-kept
by rule), not tuning and not generated.

### Defaults shipped behind (no gates)

| Unknown | Default this plan ships | Changes if overturned |
|---|---|---|
| How existing saves get empires before the migration | SE4.12 seeds the **current** save at `Init` and on `SetCurrentPlayer`, plus every save created through `CreatePlayer`; `EnsureZombossPlayer`'s row is created unseeded. Consistent with step 2's evidence (being current is save evidence), so step 3 stays idempotent. This lets `SP species-mod-ledger`'s fusion-pick fix deploy before the migration. *Plan-level choice, not in the spec text: flagged for the spec owner* | SE4.12 only; step 3 seeds the rest either way |
| An API call names a save with no empires yet | `HumanEmpireOf` throws `SaveEmpiresNotSeeded`; never guesses `"dave"` | — |
| Worktree or direct mode for the migration unit | **ruled R27: direct, SE4.20 last** | — |
| `?empire=` on routes | only where a consumer exists (the unique-actor list); others when their consumer lands | — |

### Other parent hard edges this program carries

- **H5:** SE0.7 bumps `verification-boundaries.v1.json` to schema 2 (removing `guards`) before
  `TVB registry-contract` takes schema 3. Both rewrite the same file; versions stay monotonic.

## Owner questions — each with the default the plan ships behind

None blocks a task. Each default is reversible, and a later ruling changes a later task, never a
finished one.

| # | Question | Default shipped | Where it lands if overturned |
|---|---|---|---|
| Q1 | ~~Is the creature's base attack also "atk"?~~ | **Ruled 2026-09-18:** damage moves to **action base stats**. Ideal written; becomes wave 5 | — |
| Q2 | ~~The 16 atk-only passive-tree nodes?~~ | **Ruled 2026-09-18:** a deterministic successor function (`progression.bonus.atk → combat.power`, keeping each cell's element) in the tree quota stage, with regeneration as the fallback | — |
| Q3 | ~~GitHub web-merge commits?~~ | **Ruled 2026-09-18: yes** (merges only, as specified) | — |
| Q4 | Promote `magic-numbers` **M3** (a `const` in a balance-surface file with no comment saying why it isn't tunable; 28 today, e.g. `LawnBasicAttackCostGate.cs:47` `MaxTrackedSwings = 2048`) and `overflow` **A3** (an integer overflow risk, not stack overflow: a magnitude stored in 32-bit `int`, which passes its range at Θ 103,557; 46 today) to gating? | **Default reversed to yes, pending the owner's confirmation.** "No" contradicted ruling 2, and "informational" misdescribed A3, which its audit labels HIGH. Cleared in SE3.14/SE3.15 | revert those two tasks |
| Q5 | ~~First commander's name?~~ | **Ruled 2026-09-18: the player's name** (rift-gate decision 7, orphaned, absorbed by `commander-identity`); the empty-save seed becomes "Crazy Dave" per the owner's onboarding idea | — |

**Owner-only items this program surfaces but cannot tick** (they are recorded in the ledger's
Hand-off section): phase 1's program close, and phase 2's T4.4 S7 (deferred into
`species-progression`).

## Verification discipline

- Every task: `.\scripts\verify-change.ps1 -Paths <every touched path> -Session <lane session>`.
- **Full suite exactly at:** Checkpoint 1 (`retire-atk`), SE4.4 (`commander-identity`), SE4.30
  (end of the migration unit, immediately before its real-save rehearsal), SE4.43 (`save-identity`
  close), and Checkpoint 4. Those are AGENTS.md's three sanctioned points (cross-boundary, and finishing the
  program). Never "to be safe" elsewhere.
- **Every new guard** ships with falsifiers proving it can fail. Every flip to `gating` records one
  scratch-branch falsifier run in its commit body.
- **Quote the output, not the intent.** After any edit that a guard or audit measures, re-run the
  scoped check and paste its result into the commit body. (The lesson from `99a288d1`, which reported
  10 → 0 when the tree held 5.)

## Risks and mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| A guard green locally is red on the Windows CI runner (paths, encoding, missing Python) | Med | SE1.1 re-runs each on a clean checkout before flipping; a runner step installs Python if needed; UTF-8 author names get an explicit test (SE1.2) |
| `retire-atk` moves goldens beyond the expected sim-only change | Med | BalanceGuard plus sim goldens before and after; any move with another explanation **stops the module** |
| `commander-identity` meaning-split done by find-and-replace | High | per-site meaning recorded in each commit; the third-commander Open/Closed test; a moved golden stops the module |
| Wave 3 backlog (≈ 274 pins, ≈ 530 citations) stalls | Med | per-folder batches, parallel lanes, and `--targets` lists so each batch is self-contained |
| Injector splits can't be verified in CI | Med | last in SE4.x, alone, with `guard-injector-compile` plus a live boot (`live-lawn-quick-start`) |
| Another session edits a file mid-split | Med | `srp-file-budget` runs last; session records are checked before each split |
| The `save-identity` migration runs on real data from a half-landed build | High | (R27) build directly on the branch with SE4.20 landing last, then the SE4.30 rehearsal on a real save copy; steps are dormant (test-called) until SE4.20; `.bak` taken first and never auto-deleted |
| The legacy Zomboss row is really a player's save named "Zomboss" | Med | step 2 evidence allowlist, ties go to "save" (SE4.16), both collision directions tested |
| A Zomboss specimen passes an ownership check after it shares the save's id | High | SE4.24/SE4.25 wire the one predicate in the same unit as the migration; guard I4 (SE4.42) |
| Filtering specimen reads by the human empire strips Zomboss's atoms | Med | reads classified by purpose (SE4.26) with a roster test and a runtime test |
| Old injector against a migrated server calls Zomboss an ally | Med | server and injector ship in one deploy (`deploy-play.ps1`, release zip); a payload without the new fields registers as unknown, never `Ally` (SE4.28) |
| `ConvertTo-Json` key order unstable, so T1 false positives | Low | SE2.1 verifies the round-trip; fallback to recursive key sort |

## Out of scope (named so nobody widens it)

What a commander *does* (`empire-progression`) · re-deriving `threatBand` with `creature-threat.v2`
(`creature-seed` R-CS5 follow-through) · moving `CreatureSpeciesGen` off `aptitudes.v2`
(`lawn-tuning-profile`) · closed-vocabulary counts stated in prose (reasoned out in
`spec-doc-citation-gate.md`) · a cohesion metric beyond line count.
