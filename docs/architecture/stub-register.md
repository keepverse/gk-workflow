# Stub register

**What this is.** The file the owner asked for — *"stub feature this need to find it own plan to update
(not complete), a own file to track debt and remove stub"*. Created 2026-09-17 by `solid-remediation`
T1.1; every module of that program appends to it **as it runs**, not at the end.

**Why it exists.** A register written last is an audit. A register written as the work happens is a
measurement, and the next program inherits it instead of repeating the investigation.

---

## The distinction this file exists to record

| | Definition | Disposition |
|---|---|---|
| **stub** | Refuses **by design**, waiting on a **named** external finding | Registered here. Completing it is its own program |
| **dark** | Built, compiles, reachable or registered nowhere — it *works* and is simply unreached | A **wiring gap**. In scope for remediation, registered here only so the owning program sees it |
| **unowned** | A responsibility the law names with **no implementation anywhere** | Registered here. Added 2026-09-17 by `battle-responsibility-guard`: a responsibility with no owner is a different finding from one with two, and neither *stub* nor *dark* describes it — nothing refuses, and nothing is built to be unreached |
| **solid** | A **shape** that violates a SOLID invariant and is known, measured and unfixed. It usually works, and that is precisely why it stays: nothing fails | Registered here with the `solid-enforcement` module that removes it; `waits-on` names that module. Added 2026-09-19 by `solid-enforcement` SE0.8. Not *dark*: a dark feature is unreached and needs wiring, while a `solid` row is **reached and working** and its **shape** is the defect |
| **red** | A **committed test that fails on a clean HEAD; the test is right and the tree is wrong**. Nothing refuses by design and nothing is unreached — the assertion is correct and the content or code it checks has not caught up | Registered here as a `knownRed` entry in `gk-core/scripts/verification-boundaries.v1.json` (`python-test-lane` D6), so a local run of the failing test still passes with a printed `KNOWN RED` line instead of silently deselecting it. Added 2026-09-19 by `python-test-lane` D6. Closed by fixing the tree, never by weakening the test — the moment it passes, the `knownRed` entry becomes stale and must be removed in the same commit |
| **neither** | Prose that *references* a stub — a comment or a doc line | **Not a row.** Recorded in prose below so nobody re-counts them |

**A dark feature is not a stub, and misfiling one as the other hides a shipped feature behind a debt
list.** Fusion picks are the canonical example: built, validated, nine refusal codes, reachable from the
FE, and rendering nothing because one upstream writer lost its caller. That is defect S5 and it is fixed
by this program — it is not a row here.

---

## Schema

Every row carries all six fields. A row missing any of them is not debt, it is a to-do.

| Field | Meaning |
|---|---|
| `id` | Stable short id, referenced by plans and commits |
| `kind` | `stub`, `dark`, `unowned`, `solid` or `red` |
| `what` | What refuses, or what is unreached |
| `where` | `file:line` |
| `waits-on` | The **named** finding or prerequisite. Never "someday" |
| `owner` | The program that will resolve it |
| `ships-on-it` | Whether anything reachable by a player depends on it today |

---

## Rows

<!-- citations-historical: gk-core/src/FusionRpg.Core/Commanders/CommanderId.cs was deleted (commander-identity SE4.2/SE4.3); the faction is EmpireId, the unit is CommanderRef, and every display name/scope key/empire/default comes from data through ICommanderDirectory -->


| id | kind | what | where | waits-on | owner | ships-on-it |
|---|---|---|---|---|---|---|
| `SR-01` | stub | `DomainStaleness` needs `validated_json` parsed from a real `dungeon_domain` row | `gk-core/src/FusionRpg.Server/DelveEndpoints.cs:211` | D4.16 | party-dungeon | no — `dungeon_domain` has no rows |
| `SR-02` | stub | `RungOffer.For` needs `ParentWorldTerms`, never built from live state anywhere | `gk-core/src/FusionRpg.Server/DelveEndpoints.cs:212` | D4.21 | party-dungeon | no |
| `SR-03` | stub | No rung display-name registry exists anywhere in the codebase | `gk-core/src/FusionRpg.Server/DelveEndpoints.cs:213` | D4.19 | party-dungeon | no |
| `SR-04` | stub | No almanac keyed by creature species id — only PvZ's own `(side, type_id)` shape | `gk-core/src/FusionRpg.Server/DelveEndpoints.cs:214` | D4.19 | party-dungeon | no |
| `SR-05` | stub | `provisionable[]` pricing is not yet specified | `gk-core/src/FusionRpg.Server/DelveEndpoints.cs:219` | spec-delve-stage.md §18 ask 6, Phase 5 | party-dungeon | no |
| `SR-06` | stub | Preflight `StalenessFor` — same prerequisite as `SR-01` | `gk-core/src/FusionRpg.Server/DelveEndpoints.cs:229` | D4.16 | party-dungeon | no |
| `SR-07` | stub | Preflight `ComposeRungs` — same prerequisite as `SR-02` | `gk-core/src/FusionRpg.Server/DelveEndpoints.cs:236` | D4.21 | party-dungeon | no |
| `SR-08` | stub | `DelvePrices.Provisioning` needs a composed row-0 Θ | `gk-core/src/FusionRpg.Server/DelveEndpoints.cs:245` | D4.21 | party-dungeon | no |
| `SR-09` | stub | `ContentTermsJsonFor` needs `ParentWorldTerms` from live state | `gk-core/src/FusionRpg.Server/DelveEndpoints.cs:247` | D4.21 | party-dungeon | no |
| `SR-10` | stub | `DelveGraphRoll.Roll` needs a `DomainAnchor` type distinct from `DomainRow` | `gk-core/src/FusionRpg.Server/DelveEndpoints.cs:249` | D4.21 | party-dungeon | no |
| `SR-11` | stub | `RpgHub.Resume(matchKey)` — resuming a frozen fight | `gk-core/src/FusionRpg.Server/RpgHub.cs:236` | the delve freeze/resume path | party-dungeon | no — the FE declares intent but never reaches it |
| `SR-12` | dark | `AchievementEvaluator` is a `BackgroundService` that is **never registered** — `Program.cs` does not mention it, and it has no reference anywhere in the tree | `gk-core/src/FusionRpg.Server/Achievements/AchievementEvaluator.cs` | the achievement-title program is half-built | achievement-title | no — it never runs |
| `SR-13` | unowned | Responsibility 10, **equipment damage in battle** — no durability mechanic exists anywhere; every "durability" hit in source is an unrelated word-sense. The register carries it as mechanism 10 with an empty `owner` | `gk-core/scripts/battle-responsibility.v1.json` | the `species-gear-chain` program, which is half-built | species-gear-chain | no — nothing can depend on it |
| `SR-14` | dark | The battle mid-round derived recompose is built, tested and correct, and its **producer** is missing: `setup.ActiveAuras` is assigned in exactly two files, both tests, so no production battle ever fills the ledger it recomposes from. Resolving an aura id to an `ActiveCommanderAura` needs a magnitude the content catalog does not carry | `gk-core/src/FusionRpg.Core/Battle/BattleRunState.cs` | `aura-skill` T13, which owns the live aura toggle and the magnitude resolution | aura-skill | no — the consumer is inert until a producer exists |
| `SR-15` | stub | `TryResolveCargoWeight` is the named server-side mass lookup for every cargo verb (load, unload, claim, deposit, withdraw) and for voided-cache retrieval. Its only supplier is `RpgStore.TestCargoWeightProbe`, a static field **no production code ever assigns** — declared at line 51, read at line 61, written nowhere outside `tests/`. So every production mass lookup misses and refuses `cargo.weight-unknown`, by design and loudly, rather than zero-filling (D3 locked) | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.CargoCommands.cs:51` | a real mass source, named by `empire-development` 4A.1 and tracked in `tasks/empire-development-plan.md:789` | drop-volume | no — every cargo verb refuses, so nothing player-reachable moves mass today |
| `SR-16` | stub | **Capture** refuses `capture.not-landed` because its seal-cost item row does not exist (`CrossProgramLandedFlags.ItemCostRowLanded = false`). The chance math, the gate and the roll comparison are all built and tested; what is missing is the external A3 item-cost row and the action-dispatch entry that would let a live battle invoke it | `gk-core/src/FusionRpg.Core/Battle/Capture/CaptureAction.cs` | the A3 item-cost row, named by `spec-wild-room.md` §5 as an external ask on `action-map.md` | party-dungeon | no — it refuses by construction, and `solid-remediation` T4.7 deliberately did not change that |
| ~~`SR-17`~~ | dark | **CLOSED 2026-09-17 by owner ruling — the lawn's tuned permadeath ladder is wired.** The row's original claim (*"the lawn has no settlement call site at all, so no lawn actor is ever settled"*) was wrong and taken from a comment rather than the code: the lawn settled EVERY death, inlining the delve's own `case Retire:` branch, so every unique actor that died on the lawn was permanently lost. The owner ruled: *"Use damage scale and low chance permanent death, that mode is casual, dont kill all player unique demon, so injury also low too."* Now: the seam asks `MemberSettlementRules.Decide` with the tuned `LawnPermadeathLadder`; a death that misses the roll recovers to Roster with gear still worn and no corpse cache, and only a death that makes it retires and caches. `gk-core/data/tuning/lawn-attrition.v2.json` drops permadeath 150→**40‰** and injury 400→**120‰** (published through `gk-core/tools/tuning/publish.py` on 2026-09-18; the ruling first landed as an in-place edit of `v1`, which the versioning rule forbids — `v1` is now back to its shipped 400/150 so this pass can be reverted by restoring a file). `LawnAttritionTuningHub` is now loaded at server startup — nothing anywhere called `Configure` before, the second half of the same debt. The roll is derived from (instanceId, matchKey, occurrenceId), so re-ingesting a die event cannot flip a specimen between alive and dead | `gk-core/src/FusionRpg.Core/Battle/Attrition/LawnPermadeathLadder.cs` | nothing — closed. The INJURY half of the curve is still unbuilt and is tracked as its own gap: it needs a per-actor damage-taken accumulator across a run, which the DEATH path never needed (a dead specimen took a full bar by definition, so it evaluates at 1000‰ exactly) | death-and-injury | **YES, and the direction reversed.** Every lawn death used to be permanent; now ~96% are survivable |
| `SR-18` | dark | **`creditEmpire` is emitted and read by nothing.** T4.3 (D9) resolves the owning empire of every kill at `BattleReportEmitter.cs:73` — the one point every mode's die event passes through — and writes it onto the payload. A repo-wide search for `creditEmpire` (`.cs`, `.ts`, `.tsx`, `.md`, worktrees and build output excluded) returns the emitter, its own test, the spec sentence that asked for it, and two todo lines. **No production reader exists, in the server, the store or the web client.** The attribution is correct and it is inert. **STILL OPEN after the 2026-09-17 souls ruling, and the distinction matters:** the owner ruled *"Sr-18 owner of unique actor"* and lawn souls now credit the killing specimen's owner — but that fix used `killerPtr`, **not** this field. `BattleReportEmitter.cs:73` still writes an empire id no production code reads, so the dark carrier survives its own ruling. CP4's progression clause closed anyway, because progression reaches the right earner in every mode that awards any; an unread redundant field is debt, not a mis-credit. **This claim is ENFORCED, not narrated** (`DarkCarrierGuardTests`, 2026-09-17): a guard asserts `creditEmpire` has exactly one production site and that it is the emitter. It is a canary and is SUPPOSED to go red the day a real consumer lands — that is the signal to close this row, not to allowlist the new reader. Proven to fire by injecting a second mention and observing the failure, then reverting. **Scope corrected 2026-09-17:** this is the BATTLE side specifically. The lawn already credits progression per specimen — `AwardUniqueLawnKillUnlocked` writes XP to the unique actor that got the kill, resolved by `killerPtr` against opposing still-bound specimens. So the earning gap is **souls**, not progression-in-general, and not the lawn. **And the souls half is a PROJECTION gap, not a missing capture signal** — checked 2026-09-17: the killer identity arrives live (`EffectEventAdapterCore.cs:215` reads `killerPtr`, falling back to `damageFrom`) and the unique-actor path already consumes it, but `PvzActivityKinds.FromCaptureKind` projects `zombie.die` into a `ZombieKilled` fact that carries only ptr/col/row/t/lifecycleOccurrence. The attribution is dropped at the projection, and `ApplySoulEarnFromActivityUnlocked` then has nothing to credit but the run's owner | `gk-core/src/FusionRpg.Core/Battle/BattleReportEmitter.cs:73` | a consumer that spends it — the natural one is soul EARNING, which is the other half of CP4's *"progression credited to whoever earned it"* clause. `RpgStore.Souls.ApplySoulEarnFromActivityUnlocked` credits the player who owns the run, and on the lawn it cannot do otherwise: the same `RpgStore.Souls.cs:17-27` comment `SR-17` turns on records that a `ZombieKilled` fact carries no attribution at all. So the battle side has an unspent credit and the lawn side has no credit to spend | species-empire-scope | no — nothing reads it, so no player outcome differs today |
| `SR-19` | dark | **The item head-field tables are built, tuned and tested, and nothing in production calls them.** `PotentialTable.DeriveMax`, `DurabilityTable.DeriveMax` and `CraftRiskPolicy.StageFor` (the first two in `HeadDerivationTables.cs`, the third in `CraftRiskPolicy.cs`) have zero callers outside their own files and their tests (checked 2026-09-18 by a repo-wide search of `src/**/*.cs`). The same holds for the tuning keys that feed them in `gk-core/data/tuning/deployment-hierarchy.v2.json` (`durabilityBaseByClass`, `potentialBaseByClass`, the two rarity multiplier tables, `potentialOverrides`, `craftWearPerAttemptMilli`, `potentialCostPerVerb`). The file's loader is now called at server startup, but only because solid-enforcement SE3.14 moved the corpse-cache decay and retrieval curves into it on 2026-09-18. Before that move, only tests parsed this file. The cache blocks are read in production; the head-field blocks still are not | `gk-core/src/FusionRpg.Core/Items/Materials/HeadDerivationTables.cs` | a mint or craft path that stamps `durabilityMax` / `potentialMax` on a new item and asks `CraftRiskPolicy` before a craft verb | species-gear-chain | no — no item carries a derived head field today, so no player outcome depends on it |
| ~~`SR-21`~~ | solid | **CLOSED — `commander-identity` SE4.1-SE4.3 (`b0b46579`, `1588875d`) deleted the enum.** `CommanderId` was a closed two-member enum for what the owner ruled is a **population** (*"a commander literally a unique creature"*); SE4.2 deleted it and its switches, splitting the two meanings into `EmpireId` (faction, replacement in `EmpireId.cs`) and `CommanderRef` (unit, replacement in `CommanderRef.cs`), with display name, empire, default and allocation scope key resolved from the authored registry through `ICommanderDirectory`. Found by this task's own doc-citation audit: the row's exact line citation had gone stale, because the file is now a 2-line tombstone — what a struck-but-never-updated row looks like once its target is deleted | `gk-core/src/FusionRpg.Core/Commanders/CommanderId.cs` | nothing — closed | solid-enforcement | closed — every lawn run now resolves a commander through `ICommanderDirectory` instead |
| ~~`SR-20`~~ | solid | **CLOSED 2026-09-19 by the owner's ruling retiring `progression.bonus.atk`** (*"my design don't have atk, it only have power and defense, seem like atk is adundant need to retire"*). The second attack channel is gone: `DerivedStatChannels.Retired` drops the id from registration, `AptitudeTuning.Parse` drops any edge naming it (a typo or a genuinely unknown channel still throws), `aptitudes.v9` ships without the two Might/Ferocity edges, `ActorHub.MergeAppliedCombat` no longer merges a `bonusAtk` term, and the standalone sim (`SimEngine.cs:247,313`, the one caller `SR-20`'s own player-outcome column named) now applies `final.Atk` with no bonus — the sim-only mismatch this row existed to track is closed, not papered over. `class-system` G3 (Might/Ferocity feeding both `combat.power.*` and `progression.bonus.atk`) is unchanged and reports clean on the real tree; its falsifier still plants the exact violation and proves the rule fires | nothing — closed. The 16 passive-tree nodes that named the channel as their only effect re-target to `combat.power` deterministically (`retire-atk` R5); species magnitudes regenerate clean | `retire-atk` (closed: R1/R2 `5172e9e6`, R3 `243b2aa6`, R4 `325191c0`, R5 `fd650d07`, R6/R7 closed in this commit) | solid-enforcement | no — the sim-only bonus is gone, matching what lawn and battle already paid |
| ~~`SR-22`~~ | solid | **CLOSED 2026-09-19 by `tuning-immutability` (SE2.1/SE2.2).** The four `loopwarntest*.v{1,2}.json` files are deleted (correction-marked commit `d76b11fa`/`b73f6f8e`), and `ResidualFitLoopTests`' own two throwaway-domain tests no longer write into the tracked `gk-core/data/tuning/` at all — `gk-core/tools/ResidualFitLoop`'s new `--tuning-dir` flag (threaded through to `gk-core/tools/tuning/publish.py`'s own matching flag) redirects both the fit and its publish step into a real temp directory, cleaned up with a checked `Directory.Delete`. `guard-tuning-immutability.py` now gates T1-T4 in CI, so the class of defect (test pollution landing in the balance surface) cannot recur silently | nothing — closed. The four files are gone from every `bin/` on the next clean build | `tuning-immutability` (closed, `d76b11fa`/`b73f6f8e`) | solid-enforcement | no — the tracked corpus shrank by four files, nothing reads them |
| ~~`SR-23`~~ | solid | **CLOSED 2026-09-19 by owner ruling — the git gate was retired, so there is no commit policy left to make green.** The owner retired `scripts/commit-tool/`, `.githooks` and the `commit-policy` guard itself (`6b9f6d21`): the tool blocked prompts that merely mentioned a git command, stalled merges on other sessions' untracked files, and needed an MCP bridge per agent runtime, so it cost more than it protected. The five GitHub web-merge commits it was red on are now simply ordinary commits, and the attribution invariant (`pr-commit-attribution`) carries an `unguardableReason` in the enforcement registry instead of a guard. The module `commit-policy-green` is retired with it — SE1.2 is *retired, not built* | nothing — closed. The guard, the policy file and the module are gone, not repaired | `commit-policy-green` (retired 2026-09-19, `6b9f6d21`) | solid-enforcement | no |
| `SR-24` | solid | **Eight C# files over 1,500 lines and five non-test TSX over 600** — single responsibility (measured 2026-09-19; `RpgStore.cs` is 3,979 lines) | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs` | `srp-file-budget` | solid-enforcement | no |
| `SR-25` | red | `RealCommittedCorpusCleanPassTests` fails 5 of its 11 tests on the real, committed action corpus (confirmed 2026-09-19: `test_load_committed_reports_zero_loader_findings`, `test_content_field_missing_is_clean_on_the_real_corpus`, `test_every_real_committed_action_carries_provenance`, `test_resumed_plan_is_empty_now_that_every_real_action_has_a_description`, `test_automatic_backfill_makes_zero_model_calls_and_writes_nothing_when_all_done`). Two real actions (`act.attack`, `action.family.academic.004`) carry no content description, and `act.attack`'s `atomFamilies` names an unregistered value (`atom.fx-overlay-damage`). The tests are right — a committed action without a description or with an unregistered atom family is exactly what they exist to catch | `gk-forge/tools/seedsmith/tests/test_actions_description_completeness.py:106` | the description backfill for the committed action corpus | seedsmith-actions | no — a generation-pipeline content gap, not a player-reachable behavior |

### Counted and deliberately not rows

Three `NotImplementedException` matches are **prose referencing the stubs above**, not code that
refuses: `web/.../delve/liveSession.ts` (naming `SR-11`), `web/.../delve/labels.ts` (naming `SR-03`)
and `web/src/contract/types.ts` (naming `SR-05`). They are correct documentation and need no work; they
are listed here only so the next measurement does not count 14 and wonder which three vanished.

---

## Module statements

Each module says what it added, so "no rows" is a recorded decision rather than an omission nobody
noticed.

| Module | Rows added |
|---|---|
| `stub-register` (G1) | `SR-01`..`SR-12`, the seed measurement |
| `battle-responsibility-guard` (G2) | `SR-13`, and the `unowned` kind it needed |
| `verification-boundaries-extend` (G3) | none |
| `fe-debt-register` (X4) | none here — its rows are in the FE register |
| `elemental-resolver` (D14) | **none.** D14 closed as a fix, not a stub: the registered vocabulary
  and the implemented vocabulary are now the same set, asserted by `PerElementChannelClosureTests` |
| `battle-effect-math` (D1) | **none.** Two gaps were found and both have owning modules already —
  the battle basic attack cannot reflect, and `BattleStatusSpec` cannot express an element. Both are
  wiring inside modules this program owns (`battle-mode-parity`), so neither is a stub, a dark feature
  or an unowned responsibility |
| `retaliation-shared` (D2, D8) | none |
| `battle-mode-parity` (D3, D4, D5, D6) | **`SR-14`** — D6's producer. The mid-round derived recompose
  is built, tested and correct; `setup.ActiveAuras` is assigned in exactly two files, both tests, so
  nothing in production ever fills the ledger it recomposes from. The consumer was kept and gated on an
  empty ledger rather than deleted, per this program's own "a dark feature is a wiring gap" rule |
| `species-empire-scope` (S1, S3, S8) | **`SR-15`** — found by this module's own four-project verification run, not by reading source: two Data suites went red only under full-suite parallel load. The red was a test-substrate race (one static probe, five suites), fixed here; the *register* finding is the production hole it exposed — the mass lookup has no supplier outside tests |
| `capture-as-extension` (D12) | **`SR-16`** — the hand-off its own spec asks for. The module relocated capture into the engine (`Core/Battle/Capture/`) and deliberately left it refusing: relocating a mechanism and completing a feature are different work with different owners |
| `species-carrier` (S4, S5, S6) | none — S4 and S5 were wired (a production caller and a composer join); S6's deletion was refused because zero readers was disproved, which is a finding in the module spec, not debt |
| `death-and-injury` (D10, D15) | **`SR-17`** — the lawn ladder is built, tuned and unreached. Found by checking CP4's *"a cost in every mode"* clause against call sites rather than against the tasks, which were all individually satisfied |
| `species-empire-scope` (D9, and T4.1's three seams) | **`SR-18`** — `creditEmpire` is resolved correctly at the one seam every mode shares, and spent nowhere. Found the same way `SR-17` was: by checking a CP4 clause against readers instead of against the task list. T4.3's own acceptance was *attribution*, and it met it — the clause asks for *earning*, which no task in this phase owned |
| `estimator-parity` (D7, X5) | none — D7 was a fix and X5 a completed move. The `ProvePredictor` actions+status red (9.222E-004 against its own 1e-4 gate) was recorded in the todo rather than here, because a measured disagreement between two live implementations is not a stub or a dark feature. **CLOSED 2026-09-17** (`79e63f49`): it was a real defect in the port and internal to it — `Predictor.Predict` carried each side's DoT into the damage RATE but passed the raw `swing*.Mean` into `ShieldEffectiveHp`/`RecoveryPerRound`, so one fight counted a DoT as damage for how fast HP fell and not for how long the shield lasted. Now **8.836E-007**, exactly the actions-only figure, all four axes green, tool exits 0. The earlier "drift owned by `class-system`" reading was wrong twice over: nothing regressed, and ownership was an assumption about location rather than a measurement |
| `vocabulary-single-declaration` (X1, X2) | **none.** Both closed as fixes, not debt: `IdOf` is an alias of the one declaration and the catalog bootstrap reads the one registry. The `""` return is gone rather than registered — a silent wrong answer is a defect to remove, never debt to track |
| `numeric-single-source` (X3) | **none.** The duplicated pool-max expression was removed by routing, and no third owner existed to delete |
| `file-move-tool` | **none**, as its own spec states up front. The tool is new capability; the four misfiled files it was justified by were already resolved by T0.6, re-measured at **0 remaining** |

---

> **Why neither `SR-17` nor `SR-18` is being "half built" while its decision waits (2026-09-17).**
> Both have an obvious partial move available: build the per-actor damage-taken tally `SR-17`'s curve
> needs, or add the killer field `SR-18`'s souls path needs, and leave the decision for later. Doing
> that would produce a tally nothing reads and a field nothing spends — **which is precisely the shape
> every `dark` row in this register records**, including these two. Building them now would close two
> entries by creating two more, and the next audit would file them exactly as these were filed.
>
> This is not the same as "blocked on an owner". It is the register's own rule applied to itself: a
> carrier with no consumer is debt, whoever writes it and however good the reason. So both wait for the
> decision that gives them a consumer — a balance ruling for `SR-17`, an economy ruling for `SR-18` —
> and the work lands as one change that is wired end to end, the way `T4.6` landed `species-passive`.

## Hand-off (T6.4, 2026-09-17)

`solid-remediation` is finished with this register. It does not own any row below; each names the program
that does. **The rows are the plan** — a next program starts by reading its own rows here, not by
re-running the investigation that produced them.

| Owner program | Rows | What it inherits |
|---|---|---|
| `party-dungeon` | `SR-01`..`SR-11`, `SR-16` | Delve endpoint stubs waiting on D4.16/D4.19/D4.21, and capture's A3 item-cost row |
| `achievement-title` | `SR-12` | A `BackgroundService` that is never registered |
| `species-gear-chain` | `SR-13` | Responsibility 10 — equipment damage in battle, with no implementation anywhere |
| `aura-skill` | `SR-14` | D6's producer: the mid-round recompose is correct and nothing fills its ledger |
| `drop-volume` (item) | `SR-15` | `TryResolveCargoWeight` has no production supplier, so every cargo verb refuses |
| `death-and-injury` | `SR-17` | The lawn ladder is built, tuned and unreached — **blocked on a capture signal, not a call site** |
| `species-empire-scope` | `SR-18` | `creditEmpire` is emitted at every mode's die event and read by nothing — **needs a spender, and on the lawn needs the same capture signal as `SR-17`** |

**`SR-17` and `SR-18` are related but NOT the same problem — corrected 2026-09-17.** An earlier version of this paragraph said both were halves of one missing lawn capture signal, and that the lawn carried "neither a per-actor figure nor a roster of who was deployed". **Half of that is false, and checking the code rather than the comment is what showed it.** The lawn *does* have a deployed roster — it is `phase = ActiveBound AND match_key`, and the die path already queries it. The lawn *does* have per-actor kill attribution — `TryRecoverActiveByPtr` resolves the killer by `killerPtr` among opposing, still-bound specimens in the same match and calls `AwardUniqueLawnKillUnlocked`, which writes XP to that specimen with an idempotency receipt. What is genuinely missing is narrower than recorded: a **per-actor damage-taken figure** (SR-17's curve input), and a **spender for the battle-side `creditEmpire`** (SR-18). They are separate asks with separate owners, and treating them as one signal would have sent whoever picked them up looking for a roster that already exists.

**`SR-17` is the one to read first**, because its shape is the least obvious: `RpgStore.Souls.cs:17-27`
records that a lawn `MatchEnded` fact carries only a result string, so the lawn has neither a per-actor
damage-taken figure nor a roster of deployed actors. Adding a settlement call would not close it.

**The registers were populated as the work happened**, which the commit history shows rather than
asserts: `SR-15` landed with the substrate fix that surfaced it, `SR-16` with the capture relocation,
`SR-17` with the CP4 assessment that found it. A register written at the end is an audit; one written
during is a measurement.

### Residuals recorded here but owned by the owner (added 2026-09-19)

Neither is row-shaped debt a module can remove, so neither is a row — a row would falsely promise it.
They are **owner items**:

- **Phase 1 — `actor-hub-and-combat-power-solid-fixing`:** its one open item is *"Owner accepts program
  close — genuinely owner-only, cannot be self-closed"*. No later program can close it; it needs the owner.
- **Phase 2 — `solid-remediation` T4.4 S7:** deferred by the owner on 2026-09-17 into
  `species-progression`'s level-up-grants sub-program. Scheduled, not stalled, and tracked there.

---

## The append rule

Every module of `solid-remediation` states, in its spec and in its commit, which rows it added — or that
it added none. A module that finds a stub and does not register it has left the next program an audit
to redo.

**A `solid` row is closed by the module named in `waits-on`, in that module's last commit.** The row is
struck through (`~~SR-nn~~`), never deleted, and its `waits-on` cell gains the closing SHA — the form
`SR-17` already uses.

**Assert the schema and the closure, never the row count.** The number of rows is a reading that grows
whenever work uncovers debt; what must hold is that every row names a finding and an owner.