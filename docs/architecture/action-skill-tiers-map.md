# Capability map: `action-skill-tiers`

**Status:** proposed 2026-09-18 from [action-skill-tiers-ideal.md](action-skill-tiers-ideal.md) (six
owner rulings, 2026-09-18). **Not approved. No build authorized.** Module specs →
`docs/architecture/action-skill-tiers/spec-<module-id>.md`; plan → `tasks/action-skill-tiers-plan.md` +
`tasks/action-skill-tiers-todo.md` (not written yet — written after this map is approved).

**Parent programs, unchanged:** `action` ([action-ideal.md](action-ideal.md), sealed) and `action-corpus`
([action-corpus-map.md](action-corpus-map.md)). This map does not reopen either. It owns only the tier
work those two leave uncovered.

---

## 1. What this program is, in one paragraph

A skill tier is the item program's tier discipline applied to actions: **the atom tier `t1–t5` is how
strong one effect is, and the rung (1–10) decides which tiers an action may carry — rung plays the role
rarity plays for items** (ruling 1). No new column, no new curve, no new vocabulary. The mechanisms all
exist. **This program wires the ones that do not reach production yet**, and makes the scope windows the
owner called "tunable defaults" actually tunable.

## 2. The rulings, and what each one asks of this map

| # | Ruling (ideal, 2026-09-18) | Where it lands here |
|---|---|---|
| 1 | Tier = atom-tier window, rung = rarity. **No `tier` column** | No module adds a column, a field named `tier`, or a vocabulary. `ST1` puts the rung's existing `MinTier`/`MaxTier` onto the existing `ContainerRow.MinTier`/`MaxTier` fields |
| 2 | Rung stays 1–10, `qPower = 1.75^((r-1)/2)` | No module changes a rung value. `ST3` removes a hard-coded `cap == 10` check but ships the same 10 rows |
| 3 | `powerBudgetMilli` ships neutral and **stated untuned** (standing risk) | `ST4` builds the report that tunes it; `ST5` makes it live in production. **R8 (2026-09-18) settles it:** ST4's first report tunes `referencePower`, published before ST5 lands (§10) |
| 4 | Windows are tunable defaults; **A-U1 lands before any window is a structure gate** | A-U1 **is built** (§3). `ST3` makes the windows tunable. `ST2` makes the window's ceiling bound the holder's rung, which is the half of the window that was not wired |
| 5 | Checkpoint 4 smoke batch before any tier-driven full run; S5→S1 top-up first | No module calls a model or schedules a full run. S5→S1 is `action-distribution-gaps`'s and its tooling is done (§3) |
| 6 | Graduates to its own map | This document |

## 3. What already exists — reconcile, do not duplicate

| Thing | State | Evidence | Owner |
|---|---|---|---|
| **A-U1 `rung-semantics`** — authored `Rung` and holder `EffectiveRung` named apart; `heldCap`/`rungCap` split; `minRung` dropped | **built** | `UnlockLadder.cs:56-77` (`EffectiveRung` type, `min(earnCount, rungCap)`); `ActionRow.cs:127` (`record struct EffectiveRung`); `gk-core/data/tuning/action-unlock.v1.json:14-15`; spec [action-corpus/spec-rung-semantics.md](action-corpus/spec-rung-semantics.md) | action-corpus |
| **A-G1 `tier-access-gate`** — `powerBudgetMilli`, rung-keyed budget check with a production caller | **built, inert in production** — see contradiction C-4 | `RungRow.cs:29`; `RpgStore.ActionCatalog.cs:105-110`; `gk-core/src/FusionRpg.Server/Program.cs` loads `action-rungs.v1.json`, which has no `powerBudgetMilli` column; spec [action-corpus/spec-tier-access-gate.md](action-corpus/spec-tier-access-gate.md) | action-corpus (spec); **activation is `ST5` here** |
| **S5→S1 top-up + verdict semantics** | **tooling built**; the two real runs are owner-gated | `tasks/action-distribution-gaps-todo.md` Phase 1 and Phase 2 marked done (commits `bdd91b68`, `d49d2640`); `generate_distribution_planner.py:450-452` (`--round`, `--top-up-from`) | action-distribution-gaps |
| Model-calling stages A-P1/A-P2/A-P3 | built, **owner-gated** for any full run | `action-corpus-map.md` status block | action-corpus — **untouched here** |
| Structure is gated by the scope window's ceiling | **built** — the authored `Rung` *is* the window ceiling, and the guard reads it | `ActionCorpusComposer.cs:57-58` (`Rung = rungBand.Collapse()`), `ActionRow.cs:118` (`Collapse() => Ceiling`), `StructureBudgetGuard.cs:41` | — |
| `qPowerMilli` per rung | built; **read by this program and by `action-enrich`; its meaning does not change** | `action-rungs.v2.json` rows; `action-enrich-ideal.md` "The shape" | action (A12) |

## 4. Modules

Ids are stable kebab-case. `ST` = skill tiers.

| # | Module id | Owns | Generator? | Depends on |
|---|---|---|---|---|
| **ST1** | `composer-tier-window` | The rung's `MinTier`/`MaxTier` reaches the one real action roll (import-time `ActionCorpusComposer`). Today it is read by nothing | No seedsmith change | — |
| **ST2** | `holder-rung-pricing` | The holder's effective rung is bounded by the action's authored window ceiling, and cost is scaled by **one** rung reading, not two | No seedsmith change | — |
| **ST3** | `scope-window-tunables` | The per-scope windows (general / family / signature) move from a Python constant into `gk-core/data/tuning/action-rungs.v3.json`, read by every seedsmith stage that uses them | **Yes** — planner, coverage report, innate picker, three propose prompt tables | — |
| **ST4** | `budget-calibration-report` | A model-free reading of how far real accepted content sits from each rung's budget, expressed as the `referencePower` each action would need; the `publish.py` path to retune the scalar in one edit; and (R8) the first retune itself, published as `action-rungs.v4.json` | No seedsmith change (C# report + `gk-core/tools/tuning/publish.py`) | ST1 (report); ST3 (the v4 publish sits on ST3's v3) |
| **ST5** | `rung-table-activation` | Every reader (server, injector, seedsmith) loads the same, budgeted, R8-tuned rung-table version (v4), so A-G1's check runs in production; a domain-parameterised guard keeps each tuning domain's readers on one version | **Yes** — three seedsmith path constants + one provenance string | ST3, ST4 |

**All five modules are BUILT (2026-09-19), and A-G1 is live.** ST1 `cbfb2217` (with `d1d2d342`, `a4fc08d2`), ST2 `b171513b` (with `03a4dd8f`, `75553de4`, `521fa3c6`, `f7c9d12a`), ST3 `a007029a` (with `298bd81c`, `48cb54ef`, `6754b509`, `5a66d8ff`, `e6324de1`), ST4 `252edca2` (with `fb8bbf12`, `94274afb`, `ce5860e2`, and the R8 reading at `b0e06781`), ST5 `550fb4fe` (with `7a6c4ed8`, `ef67cdea`, `27dd9ebe`, `06bc87f0`, `5c59e295`). The A-G1 row above read "built, inert in production" because both hosts loaded `action-rungs.v1.json`, which carries no `powerBudgetMilli`; that contradiction C-4 is now closed — the hosts load **v4**, and `gk-core/tests/FusionRpg.Data.Tests/Actions/ActionBudgetLiveTests.cs` proves the check refuses a planted over-budget container by name.

**Follow-up owed to the action-corpus program (recorded, not edited from here):** `docs/architecture/action-corpus-map.md`'s A-G1 status and the five specs in `spec-tier-access-gate.md` §7 still describe A-G1 as unactivated; they need the same "live as of ST5" correction as the ideal above.

### 4.1 Seedsmith / generator coverage, per module

| Module | Seedsmith stage that changes | Seed fields | Tuning file | Regenerate | Tests |
|---|---|---|---|---|---|
| ST1 | **None.** The tier window is applied at C# import time; the seed keeps carrying only `rungBand` (an index) and `atomFamilies` (ids) | none new | `action-rungs.v{n}.json` (read) | none — server re-import on boot | Core.Tests only |
| ST2 | **None.** Holder pricing is battle runtime | none | `action-rungs.v{n}.json`, `action-unlock.v1.json` (read) | none | Core.Tests only |
| ST3 | `distribution_planner/derive.py:379-412,770` · `coverage_report/derive.py:45,180,671` · `innate_picker/derive.py:65,103` · `general_propose/prompts.py:172-175` · `family_propose/prompts.py:198-201` · `signature_propose/prompts.py:217-218` | none new — `rungBand` stays a `[floor, ceiling]` index pair | `action-rungs.v3.json` `scopeWindows` (new block) | `generate_distribution_planner --dry-run`, `generate_coverage_report --dry-run`, `generate_innate_picker --dry-run` (byte-identical at the shipped values) | `test_distribution_planner.py`, `test_coverage_report.py`, `test_innate_picker.py`, the three `test_*_propose.py` |
| ST4 | **None.** Pricing is C# (`ActorPowerCache`); the report reads the imported catalog | none | `action-rungs.v{n}.json` (read; publish path extended) | none | Core.Tests, Data.Tests, `gk-core/tools/tuning` pytest |
| ST5 | `characteristic_pool/pool.py:31,85` · `generate_distribution_planner.py:60` · `generate_validate_heal.py:54` (path constants; `pool.py:85` is a provenance string emitted into `gk-data/packs/fusion/data/seed/actions/_generated/characteristic-pool.json`) | none | `action-rungs.v4.json` | the three `--dry-run` runs above: byte-identical except the pool file's one `sourceVocabulary` provenance line | Guard.Tests (version-agreement guard) + the seedsmith suites above |

**No module runs A-P1/A-P2/A-P3.** No module writes `data/seed/actions/committed-round-*.json` — it is
generated output and is never hand-edited.

## 5. Dependency graph and build order

```
  ST1 composer-tier-window ──► ST4 report ──► ST4 R8 retune publish (v4) ──┐
  ST3 scope-window-tunables (publishes v3) ──────────┘                      ├──► ST5 rung-table-activation (readers → v4)
                                                                            │
  ST2 holder-rung-pricing   (independent of the above; ordered before action-enrich `action-base` — §7)
```

**Build order:** `ST1 ∥ ST2 ∥ ST3` → `ST4` → `ST5`.

- **ST4 after ST1** because the report must price the content ST1 produces. Pricing the pre-window
  content would calibrate against atoms the window will remove.
- **ST4's retune publish after ST3's publish** because both write `action-rungs`: ST3 publishes v3
  (`scopeWindows`), the R8 retune publishes v4 on top of it. `publish.py` numbers from the latest file,
  so the other order would silently make the retune v3 and the windows v4, and every spec naming a
  version would be wrong.
- **ST5 last** because it turns a live rejection on. It must not land until ST4's reading and the R8
  retune exist (§6 Checkpoint 4).

### 5.1 Tuning-file version sequence (one publisher per version)

| File | Version | Publisher | Contents added |
|---|---|---|---|
| `action-rungs` | v1 | A12 (shipped) | the 10 rows; **production loads this today** (`gk-core/src/FusionRpg.Server/Program.cs:262`, `RpgHost.cs:225-227`) |
| `action-rungs` | v2 | A-G1 (shipped) | `powerBudgetMilli`, `referencePower = 1000`, untuned |
| `action-rungs` | **v3** | **ST3** | `scopeWindows` |
| `action-rungs` | **v4** | **ST4 (R8)** | `powerBudgetMilli` repriced at the report's `referencePower`, `referencePowerUntuned = false`, `_meta` cites the report file |
| `action-rungs` | — | **ST5** | publishes nothing; moves every reader to v4 |
| `action-base` | v1 | `action-enrich` `action-base` | new domain (authored v1), no overlap |

`action-enrich` reads `qPowerMilli` from whichever version is loaded and publishes no `action-rungs`
version; `qPowerMilli` is identical in v1–v4. A later window retune (ruling 4, free) is v{n+1} after v4.

## 6. Checkpoints

- **Checkpoint 1 — the tier window is real.** After ST1, every imported action's fixed atoms lie inside
  its authored rung's `[MinTier, MaxTier]`, and the composed container carries that window.
- **Checkpoint 2 — one rung reading prices one holder.** After ST2, a held action's cost is scaled once,
  by the holder's effective rung, and that rung never exceeds the action's window ceiling.
- **Checkpoint 3 — the windows are tunable.** After ST3, changing a window is a `publish.py` call and a
  planner re-run. No code edit. The shipped values reproduce byte-identical briefs.
- **Checkpoint 4 — the budget is measured and tuned before it bites.** ST4's report exists for the real
  imported catalog, and (R8) its recommended `referencePower` is published as v4 through
  `--reprice-rung-power-budget … --mark-tuned` before ST5. The report is not a pass/fail on content; the
  publish is not optional (R8: leaving 1000 is the standing risk's trigger 1).
- **Checkpoint 5 — A-G1 is live.** After ST5, the server and the injector load v4 and every seedsmith
  reader names the same version; no committed action is rejected by the live budget (by construction of
  R8's value, ST4 contract 6).

## 7. Cross-program hazards

| Program | Hazard | Rule here |
|---|---|---|
| **action-enrich** | Reads `qPowerMilli` as the action's damage base, at the holder's **`effectiveRung`** (A-U1 §3.1) | **Resolved 2026-09-18.** `action-enrich/spec-action-base.md` makes `BattleRunState.EffectiveRungOf` one instance resolver that `CostLedger` and the hit both call, so ST2's window bound (inside `UnlockLadder.EffectiveRung`) reaches cost and base at once. ST2 **solely** owns the compile-time cost pre-scale (`ActionCompiler.cs:61`); `action-base` does not touch that line. This program does not change `qPowerMilli`'s meaning or values |
| **action-enrich — goldens** | ST1, ST2 and `action-base` can each move battle goldens | **One re-bless commit per cause, in the order ST2 → ST1 → `action-base`** (`action-enrich-map.md` §Golden re-bless order; tunables T7). A module whose change moves no golden says so and re-blesses nothing |
| **action (A23 `cost-scaling-holder-rung`)** | ST2 fixes a double cost scaling A23's build left behind (C-7) | ST2 edits `ActionCompiler`/`BattleRunState` cost plumbing only; it does not change A23's `rungOf` contract |
| **action (A26–A32)** | `BattleEngine.Resolve`'s `unlockStateFor` has **no production caller** (only `ActionCostsCooldownsAdoptionTests.cs:308,313`), so holder rungs are inert in production today | ST2 fixes the function holders will use. It does not wire holders into production battles. **Correction (strengthen pass):** this row used to say that wiring "is the action program's" as if a task existed — none of A26–A32 (`tasks/action-todo.md:2994-3190`) supplies `unlockStateFor`. It is a missing action-program module, reported there and in `action-enrich-map.md` §Cross-program; until it lands every cost and base reads the authored rung. **Owner id since 2026-09-18: `A33` `battle-holder-wiring`**, a proposed row in [action-map.md](action-map.md) §17 (depends on A26; spec and plan task still owed) |
| **action-corpus A-G1** | ST5 changes A-G1's state from "built" to "live". Five A-G1-citing specs carry the gate inline (`spec-tier-access-gate.md` §7) | ST5 does not edit them. Updating them is part of ST5's done-criteria as a **doc follow-up for action-corpus**, named, not done here |
| **power** | `ssot-power-scale.md` §11 has rows for `rungCap` (line 888) and `powerBudgetMilli` (line 889) | ST2 adds nothing new to the ladder: the window ceiling is an existing tunable (ST3). ST3 owes the §11 row for `scopeWindows` (A-U1 §3.4 named the windows' row; it was never written) |

## 8. What stays out

- A per-player action roll. `spec-action-instance-and-grant.md` Boundaries: *"Never roll per-player"*.
  Actions are rolled once at import (C-5).
- Tier weights `1000/600/300/120/35` inside a window. Every shipped rung window is a single tier
  (`action-rungs.v2.json`, `minTier == maxTier` on all 10 rows), so weights have no effect. ST1 refuses a
  multi-tier window instead of defaulting a weight (§ST1).
- `PoolRolls` → `PrefixRolls`/`SuffixRolls` on the rung row (ideal wiring gap). The composer already puts
  the whole roll on the container's one roll class (`ActionCorpusComposer.cs:118-119`) and nothing in the
  ideal's shape needs the split.
- A tier readout on the wire. No action endpoint exists in `gk-core/src/FusionRpg.Server` today (grep for
  `/api/action` finds none); the ideal defers emissive UI to a surfaces pass.
- Cooldown's rung reading. Timing takes the authored rung's `cdMulti` at catalog build
  (`RpgStore.ActionCatalog.cs:126`). Whether cooldown follows the holder is not in the ideal.
- C1 family-access widening. Still gated on effect-atom D2 (`spec-tier-access-gate.md` §3.4).

## 9. Contradictions found while writing this map

Each is cited to code. Business contradictions were OWNER questions, answered by R7/R8 (§10); technical ones are resolved
in the named module.

| # | Contradiction | Evidence | Resolution |
|---|---|---|---|
| C-1 | The ideal says *"a scope ceiling gates magnitude but not structure today."* The code does the reverse: structure **is** gated (authored `Rung` = window ceiling, read by the guard), and magnitude/cost is **not** (the holder rung ignores the window) | ideal line 56 · `ActionCorpusComposer.cs:57-58,151` · `StructureBudgetGuard.cs:41` · `UnlockLadder.cs:76` · `BattleRunState.cs:636-649` | Technical → **ST2** |
| C-2 | Ruling 4's source question describes A-U1 as "two-sided clamp pricing + `effectiveRung`→guard". A-U1 as specced and built says the guard reading the authored rung is **correct**, forbids changing it, and dropped `minRung` | ideal line 228 · `spec-rung-semantics.md` §3.1, §3.2, §4 · `UnlockLadder.cs:63-70` | Technical, already decided 2026-09-03 → A-U1 stands; ruling 4's precondition ("A-U1 lands first") **is met** |
| C-3 | The signature window: ideal and ruling 4 say **5–10**; A-U1 (2026-09-03) dropped the floor and the shipped planner emits **[1, 10]** | ideal lines 75, 117, 142, 168 · `spec-rung-semantics.md` §3.2 · `distribution_planner/derive.py:381,405-412` | **Closed by R7** (1–10) |
| C-4 | The ideal says A-G1 is "built and wired". It is wired to a production caller whose loaded table has no budget column, so the check skips every action | ideal line 50 · `gk-core/src/FusionRpg.Server/Program.cs`, `RpgHost.cs:225-227` (both `action-rungs.v1.json`) · `RungRow.cs:14-18` (`null` → skip) · `RpgStore.ActionCatalog.cs:96-101` | Technical → **ST5** |
| C-5 | The ideal says the runtime roll is `ActionSeeder` and states *"the runtime rolls concrete per player"*. `ActionSeeder.Generate` has no production caller; the real roll is `ActionCorpusComposer` at import, content-seeded, never per-player | ideal lines 32, 48 · `ActionCorpusComposer.cs:127` · `spec-action-instance-and-grant.md` §Objective 3 and Boundaries | Resolved by precedence: the shipped, owner-approved A21 spec is the more specific rule. Consequence written into ST1: an action's atom tier is fixed by its **authored** rung; a holder's progress shows in `qPower`/cost through the effective rung. The owner may reopen per-player rolls as a new module (A21 Boundaries: "ask first") |
| C-6 | The sealed action ideal and A13 say *"rarity selects `pool_rolls` and the tier window"*. The rung row's `MinTier`/`MaxTier` have **no reader** in `src/`; the composer never sets the container window; `Instantiator.Draw` never reads it | `action-ideal.md:271-276` · `spec-action-seeding.md` §1 · `ActionCorpusComposer.cs:114-121` · `Instantiator.cs:207` (no tier filter) | Technical → **ST1** |
| C-7 | Cost is scaled twice: by the authored rung at compile, then by the holder (or fallback authored) rung in the ledger. At authored rung 10 a cost is multiplied by 329× instead of 18× | `ActionCompiler.cs:61` · `BattleRunState.cs:602` · `CostLedger.cs:148-155` · `spec-cost-scaling-holder-rung.md` §Objective (cost reads the **holder's** rung) · `action-rungs.v1.json` rung 10 `costMulti` 18151 | Technical → **ST2** |
| C-8 | The planner refuses any rung table whose `cap` is not 10, while `ssot-power-scale.md` §11 calls `rungCap` a soft, tunable window | `distribution_planner/derive.py:390` · `ssot-power-scale.md:888` | Technical → **ST3** (validate `1..cap` contiguity, not a literal) |
| C-9 | Ruling 5 treats Checkpoint 4 (smoke batch) as pending. `action-corpus-map.md` §6 marks it ✅. If it has passed, the standing risk's trigger 1 (*"the smoke batch lands and the scalar stays neutral"*) is already live | ideal lines 67, 197 · `action-corpus-map.md` §6 | **Closed by R8** (tune from ST4's first report, before ST5) |

## 10. Rulings applied 2026-09-18 ([spec-rulings-2026-09-18.md](spec-rulings-2026-09-18.md))

1. **R7 — signature window is 1–10** (C-3 closed). ST3 publishes the shipped `[1, 10]`; A-U1 §3.2 stands.
   A floor of 5 would be a hidden tax on a first unlock.
2. **R8 — tune `referencePower` from ST4's first report** (C-9 closed). The passed Checkpoint 4 is the
   resolving event ruling 3 named, so ST4's first reading over the committed corpus decides the scalar,
   published through `gk-core/tools/tuning/publish.py` **before ST5 lands**. Leaving 1000 after that reading is
   the standing risk's trigger 1 and is not an option.

No open questions remain. Every "OWNER Q1/Q2" reference in the module specs is closed by R7/R8; the
strengthen pass removed them.

### 10.1 Strengthen pass 2026-09-18 — what changed and why

| Finding | Where fixed |
|---|---|
| ST3/ST4/ST5/ST2 still deferred to "OWNER Q1/Q2" and ST3 kept "ask first" on window values, contradicting R7, R8 and ruling 4 ("tuned freely from day one") | ST2, ST3, ST4, ST5 |
| Two publishes of `action-rungs` had no order: ST3's v3 and the R8 retune; ST5 pointed at v3, which would load the untuned scalar | §5, §5.1; ST4 contract 6; ST5 contract 1 |
| R8 had no stated rule for *which* value the first report yields | ST4 contract 6: the smallest scalar that rejects no committed action, with outliers listed |
| ST3's retune example `publish.py … "scopeWindows.family=[1,6]"` would store the string `"[1,6]"` (`publish.py` `parse_value` tries int/float/bool only; `set_path` does no type check) | ST3: windows are `{floor, ceiling}` objects so `set scopeWindows.family.ceiling=6` writes an int |
| ST3 said a retuned window makes a prompt "raise"; the three label tables use `.get(key, fallback)` and would silently render *"a tier outside the three known scope windows"* | ST3 contract 4 |
| ST5 claimed byte-identical regeneration; `pool.py:85` emits the rung-table filename into `characteristic-pool.json` | ST5 seedsmith table and test 5 |
| ST2 named `BattleRunState.cs:602` as `ScaledAmount`'s only reader; `ActionCatalogTests.cs:374-375` asserts the pre-scaled amount | ST2 testing strategy (stale test updated to the contract) |
| ST1 did not say what happens to an action already in the store whose brief now refuses | ST1 contract 2 |
| Goldens: ST1, ST2 and `action-base` each move battle goldens with no order between them | §7, `action-enrich-map.md` |

## 11. Success criteria

1. No new column, field named `tier`, vocabulary member, or curve anywhere in the diff (ruling 1, 2).
2. Every imported action's atoms lie inside its authored rung's tier window (ST1).
3. A holder's cost uses exactly one rung reading, bounded by the window ceiling (ST2).
4. The scope windows are a published tunable, and the shipped values regenerate byte-identical briefs
   (ST3).
5. The budget's distance from real content is a published reading before the budget bites (ST4).
6. Production loads the budgeted table; one version across every reader, guarded (ST5).
7. No model call, no hand-edited seed row, no test pinning a population count or a tunable value.
