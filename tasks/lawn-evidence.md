# lawn lane evidence (session `lawn-1`)

One fragment per closed `lawn` row, in todo order. The repo convention is
`tasks/evidence-fragments/<ID>.md`; that directory is outside this lane's declared paths
(`tasks/lawn-*.md`, `tasks/lawn-ledger.jsonl`), so the fragments live here.

## LW1.1 — `lawn-perf-budget.v1.json` + wire every perf-ceiling reader

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| the ceiling is a tunable, read from the file | `dotnet test gk-core/tests/FusionRpg.Core.Diagnostics.Tests -c Release --filter FullyQualifiedName~LawnPerfBudget` | Passed 11/11 | `gk-core/data/tuning/lawn-perf-budget.v1.json`, `gk-core/src/FusionRpg.Core/Diagnostics/LawnPerfBudgetTuning.cs` |
| every gate that checks it reads the file, not a constant | `dotnet test gk-core/tests/FusionRpg.Guard.Tests -c Release --filter FullyQualifiedName~LawnPerfBudget` | Passed 3/3 | `gk-core/tests/FusionRpg.Guard.Tests/LawnPerfBudgetGuardTests.cs` |
| the host reads it (H7: publish + reader in one commit) | `dotnet test gk-core/tests/FusionRpg.Server.Tests -c Release` | Passed 819/819 | `gk-core/src/FusionRpg.Server/Program.cs` |
| the ceiling is not hand-edited in place | `python gk-core/scripts/guard-tuning-immutability.py` | OK — 1 `gk-core/data/tuning/*.json` change checked, T1–T4 clean | — |
| the new paths have owners | `python gk-core/scripts/guard-verification-boundaries.py` | VERIFICATION BOUNDARY GUARD OK | `gk-core/scripts/verification-boundaries.v1.json` |
| citations I shifted resolve | `python scripts/audit-doc-citations.py --strict --scope tasks/lawn-combat-wire-todo.md` | 0 HIGH (D1–D4) | `tasks/lawn-combat-wire-todo.md` |
| the selected boundary suite | `verify-change.ps1 -Paths <the 10 changed paths> -AllowUnscoped` | cheatcore 41/41 · core-diagnostics 11/11 · server 819/819 · guard 664/665 · guards session-boundary/single-writer/etc. OK | this table |

**`-Session lawn-1` could not run.** `tasks/sessions/lawn-1.json` does not exist in this worktree
(`verify-change.ps1:98` throws `session record not found: lawn-1`), and `tasks/sessions/**` is outside the
lane fence, so this lane may not create it. `-AllowUnscoped` over the identical path set makes the same
selections; every selected check was also run directly, as tabulated.

**Pre-existing red, not this change.** `gk-core/tests/FusionRpg.Guard.Tests/PlantSideStatusGuardTests.cs:111`
(the `BattleEffects.cs` sha256 pin) is red at this lane's base `b2ea55f0`: it pins
`02B04A25…` and the file hashes `E1444DB1…`. Cause: `5e33ad647` (2026-09-23, battle T6/W11
"one gate owns combat.defense.omni") moved `BattleEffects.cs` 447 → 466 lines *after* `CAI-guard-1`'s
re-pin, and `BattleEffects.cs` is unmodified in this worktree. Owning row: `CAI-guard-1`
(`tasks/combat-ai-todo.md:1486`), still open but now carrying stale hashes; reported here rather than
edited, because that todo is outside this lane's fence.

## LW1.2 — `summon-pool-integrity` — BLOCKED (half a), half b already shipped

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| half (b): an engine-side spawn failure answers the deploy correlation | `git log -1 --format=%h%x20%s -- gk-fusion/src/FusionRpg.Injector/CheatActions.cs` | shipped 2026-09-20 · `8e56f9e9e` | `gk-fusion/tests/FusionRpg.Injector.Tests/SpawnFailDeployReportingTests.cs` (all four failure sites) |
| half (a): a summonable species is one this build can plant | — | **not run** | needs `gk-forge/tools/CreatureSpeciesGen/**` + regenerated `gk-data/packs/fusion/data/generated/creatures/**` |

**Blocker (denied paths, not unfinished work).** `spec-summon-pool-integrity.md`'s own file list puts
half (a) in the generator and the emitted corpus, and this lane's allowed paths contain neither
`tools/**` nor `gk-data/packs/fusion/data/generated/**`; a registry authored under `gk-core/data/tuning/` (other than `lawn*.json`) or
`gk-data/packs/fusion/data/seed/creatures/_registry/**` is equally outside. Fixing only the runtime roll would be a second
mechanism beside the generator the spec names, and the corpus guard (success criterion 1) cannot pass
until the corpus is regenerated. Ruling requested: widen this lane's fence to `gk-forge/tools/CreatureSpeciesGen/**`
+ `gk-data/packs/fusion/data/generated/creatures/**`, or route half (a) to the lane that owns them.

## LW1.4 — `actor-liveness-refresh`: Core revision type + closed invalidation vocabulary

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| the closed enum is pinned, and says why it is closed | `dotnet test gk-core/tests/FusionRpg.Core.Tests -c Release --filter FullyQualifiedName~ActorLivenessRevision` | Passed 4/4 | `gk-core/tests/FusionRpg.Core.Tests/Stats/ActorLivenessRevisionTests.cs` |
| the revision is a monotonic `long` per `(playerId, entityKey)` | (same run) | 4/4 — monotonic, keys independent, overflow throws | `gk-core/src/FusionRpg.Core/Stats/Derived/ActorLivenessRevision.cs` |
| selected boundary | `verify-change.ps1 -Paths <2 new paths + the registry> -AllowUnscoped` | core `core.actor-liveness-revision` 4/4 · guard `guard.verification-boundaries` 57/57 | this table |
| one ActorHub, one writer | `pwsh -File scripts/guard-actor-hub.ps1` · `pwsh -File scripts/guard-single-writer.ps1` | ACTOR-HUB GUARD OK · SINGLE-WRITER GUARD OK | — |
| the new paths have owners | `python gk-core/scripts/guard-verification-boundaries.py` | VERIFICATION BOUNDARY GUARD OK | `gk-core/scripts/verification-boundaries.v1.json` |

The enum pins five kinds (`Ladder`, `CommanderAllocation`, `UniqueAllocation`, `Equip`, `Tree`) at dense
ordinals 0–4, and asserts `Player` is **absent**: that notice is `SP6.6`'s on `PUT /api/players/current`
(hard edge E2), which this module extends rather than duplicating.

## LW2.1 — `regen-unit-trace`

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| the unit question is answered with file:line | — (the deliverable is the note) | POC fits **per round**, runtime reads **per tick**, at a basic attack's 200-tick cadence that is a 200× mismatch | `docs/architecture/lawn-tuning-profile/regen-unit-trace.md` |
| the unit contract is tested over the closed vocabulary | `dotnet test gk-core/tests/FusionRpg.Core.Tests -c Release --filter FullyQualifiedName~ResourceRegenUnit` | Passed 4/4 | `gk-core/tests/FusionRpg.Core.Tests/Stats/ResourceRegenUnitTests.cs` |
| no shipped behaviour changes | (same run) — the test reads `DerivedStatChannels.ResourceIds`, `ResourceChannelReader`, `ResourcePoolState` and `action-timing.v1.json`; no production file changed | 4/4 | this table |
| the new paths have owners | `python gk-core/scripts/guard-verification-boundaries.py` | VERIFICATION BOUNDARY GUARD OK | `gk-core/scripts/verification-boundaries.v1.json` |
| selected boundary | `verify-change.ps1 -Paths <3> -AllowUnscoped` | `core.resource-regen-unit` 4/4 · `guard.verification-boundaries` green · doc-citations 0 HIGH | this table |

The test is additive to S10.1's `ResourceSubTickRegenTests` (which covers `poise` in depth): it asserts the
UNIT across all six resource ids, the per-mille round trip, and the round-length arithmetic the trace's
200× rests on (`action-timing.v1.json`, never a literal). The finding it records is filed as `LW5.2`
(routed out — the repair publishes `data/tuning/aptitudes.v{n+1}.json`, outside this lane's fence).

## LW1.3 — `exhaustion-event`: edge-triggered status + per-actor transitions

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| one `actor.exhausted` per window, not per refused swing (defect E1) | `dotnet test gk-core/tests/FusionRpg.Core.Tests -c Release --filter "FullyQualifiedName~Exhaustion"` | Passed 25/25 (7 of them this module's) | `gk-core/src/FusionRpg.Core/Actions/Cost/ExhaustionEdgeDetector.cs`, `gk-core/tests/FusionRpg.Core.Tests/Actions/ExhaustionEdgeTests.cs` |
| `ExhaustionPolicy` gets a real lawn caller, empty payload (defect E3) | (same run) — the status is applied on the entering edge and withdrawn on recovery, by `exhaustion:{ptr}:{resourceId}` grant id, with `StatMods` empty | 25/25 | `gk-fusion/src/FusionRpg.Injector/Effects/LawnExhaustionLifecycle.cs`, `LawnBasicAttackCostCharger.cs` |
| events ride the existing pipeline | `GameHooks.Emit` from the lifecycle host (the drain that already carries `plant.die`/`zombie.die`); payload asserted in the Core test | 25/25 | `ExhaustionEdgeEvents` |
| a reused ptr / new match starts clean | (same run) `Forget`/`Clear` wired to `InjectorEntityRegistry.Remove`/`Clear` | 25/25 | `InjectorEntityRegistry.cs` |
| the injector still compiles | `$env:FUSIONRPG_ML_GAMEDIR='H:\Games\PVZ-Fusion-3.9_MelonLoader'; pwsh -File scripts/guard-injector-compile.ps1` | INJECTOR COMPILE GUARD OK — MelonLoader host compiled (it FAILED first on a missing `using FusionRpg.Injector.Host;`, which is why this was run) | — |
| selected boundary | `verify-change.ps1 -Paths <6> -AllowUnscoped` | core `core.exhaustion-edge` 7/7 · actor-hub OK · funnel-delta OK · single-writer OK · secondary-no-unity OK · guard 664/665 | this table |

The one Guard red is the pre-existing `PlantSideStatusGuardTests.BattleEffects_is_byte_identical_to_its_current_core_baseline`
hash pin (moved by `5e33ad647` at this lane's base), unrelated to this change and recorded as a finding.
`guard-injector-compile.ps1` prints SKIPPED without a game dir, so it was re-run explicitly with the
machine's MelonLoader install; that printed reading is the compile evidence above.

## LW1.5 — `actor-liveness-refresh`: server-side send, extends `SP6.6`

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| each verb sends exactly one invalidation naming the right kind | `dotnet test gk-core/tests/FusionRpg.Server.Tests -c Release --filter "FullyQualifiedName~LivenessInvalidation"` | Passed 5/5 | `gk-core/tests/FusionRpg.Server.Tests/LivenessInvalidationTests.cs` |
| it rides `SP6.6`'s existing transport, never a second `Player`-kind channel | (same run) — one additive `kind` field on `AptitudesUpdated`; message name and the two groups unchanged | 5/5 | `gk-core/src/FusionRpg.Server/AptitudeEndpoints.cs` |
| the wire vocabulary is pinned and an unknown kind is refused | `dotnet test gk-core/tests/FusionRpg.Core.Tests -c Release --filter "FullyQualifiedName~ActorLivenessRevision"` | Passed 5/5 | `gk-core/src/FusionRpg.Core/Stats/Derived/ActorLivenessRevision.cs` |
| selected boundary | `verify-change.ps1 -Paths <7> -AllowUnscoped` | DAL OK · core 5/5 · guard.verification-boundaries 57/57 · server module 831/831 · server.liveness-invalidation 5/5 · server.passive-tree 27/27 (exit 0) | this table |

Verbs asserted behaviourally through the real HTTP endpoints with a capturing `IHubContext<RpgHub>`:
commander allocate → `commanderAllocation`, unique allocate → `uniqueAllocation` (specimen named), tree
spend → `tree` (its own pre-existing `PassiveTreeUpdated` signal is a different concern and is not
counted as a liveness invalidation), and a **refused** verb → **no** invalidation at all. Equip/unequip
are covered by a labelled source-text guard over the two handlers plus the shared emitter: a successful
equip needs a rolled item instance in the inventory, which no Server test creates today, so building
that fixture would test the item pipeline rather than this vocabulary — stated, not implied.

## LW1.6 — `actor-liveness-refresh`: injector receive + bounded recompose

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| the receive routing, incl. every refusal, is testable and green | `dotnet test gk-core/tests/FusionRpg.Core.Tests -c Release --filter "FullyQualifiedName~Liveness"` | Passed 14/14 | `gk-core/src/FusionRpg.Core/Stats/Derived/ActorLivenessRevisions.cs`, `gk-core/tests/FusionRpg.Core.Tests/Stats/ActorLivenessRevisionsTests.cs` |
| an unknown kind is refused and reported, never skipped | (same run) — `LivenessRefusal.UnknownKind`, and a refused invalidation changes nothing | 14/14 | `LivenessInvalidationRouter.TryApply` |
| a bump marks dirty; the recompose stays lazy and bounded | (same run) — a player-scoped bump writes NO per-actor row and moves only that player's actors; an entity-scoped bump moves exactly one; `Read` is pure and never drifts | 14/14 | `ActorLivenessRevisions` |
| the injector compiles with the receive wiring | `$env:FUSIONRPG_ML_GAMEDIR='H:\Games\PVZ-Fusion-3.9_MelonLoader'; pwsh -File scripts/guard-injector-compile.ps1` | INJECTOR COMPILE GUARD OK — MelonLoader host compiled | `gk-fusion/src/FusionRpg.Injector/RpgClient.cs`, `Effects/LawnLiveness.cs` |
| the memo's own seam is now real, not a constant | (compile above) — `LawnActorViewHost` passes `LawnLiveness.RevisionOf` where it previously passed `_ => 0L` | compiled | `gk-fusion/src/FusionRpg.Injector/Effects/LawnActorViewHost.cs` |
| selected boundary | `verify-change.ps1 -Paths <7> -AllowUnscoped` (with `FUSIONRPG_ML_GAMEDIR`) | actor-hub/funnel-delta/secondary-no-unity/single-writer/injector-compile all OK · core.actor-liveness-revision 14/14 · guard module 667/669 | this table |
| live check (`spec` Commands: allocate mid-match, switch player, level up) | — | **not run** | needs a running game on a pooled live slot (`docs/contributing/live-probe-standard.md`); no game was running in this segment |

The two Guard reds are both **not this change**: `PlantSideStatusGuardTests`' `BattleEffects.cs` hash pin
(pre-existing at the base, moved by `5e33ad647`) and — newly visible on the merged head —
`PlayerSpeciesMaterialiseCallerGuardTests.The_nine_pick_refusal_codes_are_a_closed_vocabulary`, which
fails because `22fc4f3d3` (creature-seed T8) added `picks.source-below-rank-floor`
(`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Fusion.cs:305`) without moving the pin at
`gk-core/tests/FusionRpg.Guard.Tests/PlayerSpeciesMaterialiseCallerGuardTests.cs:96-104,121`. Both are outside
this lane's fence; filed as findings, not fixed here.

## LW2.2 — `mode-profile` — BLOCKED (fence, one file)

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| the row's own deliverable exists | — | **not run** | needs `data/tuning/mode-profiles.v1.json` (new) |

`spec-mode-profile.md`'s Project structure names `data/tuning/mode-profiles.v1.json` as "the tuning file",
its Commands publish through `gk-core/tools/tuning/publish.py mode-profiles ...`, the plan's H7 lists it as one of
the two publishes that must land with their readers, and `LW2.4` adds one key to the same file. This
lane's allowed paths carry `data/tuning/lawn*.json` only, so the file cannot be created here, and a
lawn-prefixed rename would fork the plan. Everything downstream is gated by it: `LW2.3`–`LW2.6` depend on
`LW2.2`, `LW3.1`/`LW3.2` on wave 2, `LW4.1` on wave 3, `LW4.2` on `LW4.1`. Ruling requested from the
manager: widen this lane's paths to `data/tuning/mode-profiles*.json`, or route the scale chain to the
lane that owns it.

## LW5.1 — `unique-deploy-cap` — BLOCKED (fence)

Its spec's own §5 and the todo row both put the work at
`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.UniqueActors.cs:150-250` — the one existing unique-deploy admission
gate it extends — which is outside this lane's allowed paths. No part of it is reachable here.

### LW1.2 — half (a) LANDED at the serve point; the generator half stays blocked

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| no species the build refuses can be served by any band | `dotnet test gk-core/tests/FusionRpg.Core.Tests -c Release --filter "FullyQualifiedName~Summon"` | Passed 20/20 | `gk-core/tests/FusionRpg.Core.Tests/Creatures/SummonPoolPlantabilityTests.cs` (the join, over the real scoped 869-row corpus) |
| the player-facing catalog stops advertising them | `dotnet test gk-core/tests/FusionRpg.Server.Tests -c Release` | Passed 834/834 | `gk-core/src/FusionRpg.Server/CreatureEndpoints.cs` |
| the roller asks the one declaring site, not the raw flag | (same Summon run) — `CreatureAdmission.ForWave`, the predicate `CreatureAdmissionTests` already pins | 20/20 | `gk-core/src/FusionRpg.Core/Creatures/SummonRoller.cs` |
| action-layer purity (a real LW1.3 defect this boundary caught) | `dotnet test gk-core/tests/FusionRpg.Core.Tests -c Release --filter "FullyQualifiedName~ActionsPurityGuard\|FullyQualifiedName~Exhaustion"` | Passed 34/34, after `497bfa182` removed the `.Values` enumeration | `gk-core/src/FusionRpg.Core/Actions/Cost/ExhaustionEdgeDetector.cs` |
| selected boundary | `verify-change.ps1 -Paths <4> -AllowUnscoped` | DAL OK · core module `FusionRpg.Core.Tests` 9620/9620 + per-project runs · server module 834/834 | this table |

**What landed.** live-probe Task 22's three ids (261/264/265) are `speciesKind: "excluded"` rows that
`CreatureAdmission` refuses. The summon roller was the fourth context that re-derived the raw `Summonable`
flag instead of asking admission — its own doc says "a fourth context is a new member here, never a
re-derivation in a fourth file" — so it served out-of-play species and the engine refused to plant them.
It now asks `CreatureAdmission.ForWave`, the catalog reports the admitted answer, and the corpus join closes.

**What remains, and why the row is still open.** The spec's other half is whether every `gameTypeId` in the
200–299 band is plantable at all (fusion results are not): that needs the authored plantability registry
plus a generator that cannot mark an unplantable species `Summonable`. Both live in
`gk-forge/tools/CreatureSpeciesGen/**` and `gk-data/packs/fusion/data/generated/creatures/**` — outside this lane's allowed paths.

**Two load-dependent reds, diagnosed at their boundary, both green in isolation.**
`FusionRpg.Core.Atoms.Tests/AtomBenchGuardTests.The_compiled_form_stays_inside_its_ns_per_atom_budget`
(median 241.21 ns/atom against a 75 ns budget while a 70-project group ran in parallel; raw samples
29.71–894.56 ns; **3/3 when run alone**, fastest sample below the 50 ns budget) and
`VerificationBoundaryWorkflowTests.P6_the_real_registry_resolves_seedsmith_and_tuning` (**1/1 when run
alone**). Neither red touches a file this change edits; both are the timing/child-process class the repo's
own `kernel-timeline-baseline.md:54` says measures the build agent.

### LW5.1 — `unique-deploy-cap`: the in-fence half LANDED; two wires still denied

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| one admission rule, both reasons, stated precedence | `dotnet test gk-core/tests/FusionRpg.Core.Tests -c Release --filter "FullyQualifiedName~LawnUniqueDeployCap\|FullyQualifiedName~ZombossDeploy"` | Passed 7/7 | `gk-core/src/FusionRpg.Core/Match/LawnUniqueDeployCap.cs`, `gk-core/tests/FusionRpg.Core.Tests/Match/LawnUniqueDeployCapTests.cs` |
| the two refusal constants join `GateReasons` | (same run) — `cap.unique_per_empire`, `cap.unique_board` pinned by string | 7/7 | `gk-core/src/FusionRpg.Core/Match/CapPolicy.cs` |
| the shipped file states both limits and its own invariant | (same run) — `board >= perEmpire` asserted against `gk-core/data/tuning/lawn-deploy.v1.json`, and a contradictory file is refused at load, never clamped | 7/7 | `gk-core/data/tuning/lawn-deploy.v1.json`, `gk-core/src/FusionRpg.Core/Match/LawnDeployLimitsTuning.cs` |
| both hosts load it with its reader (H7) | `dotnet build gk-core/src/FusionRpg.Server/FusionRpg.Server.csproj -c Release` → Build succeeded, 0 errors · `pwsh -File scripts/guard-injector-compile.ps1` → INJECTOR COMPILE GUARD OK | compiled | `gk-core/src/FusionRpg.Server/Program.cs`, `gk-fusion/src/FusionRpg.Injector/Host/RpgHost.cs` |
| boundary + DAL + substrate | `guard-verification-boundaries.py` OK · `guard-dal.ps1` OK · `guard-test-substrate.py` OK | all OK | `gk-core/scripts/verification-boundaries.v1.json` |

**What landed:** the pure policy (two counts in, `CapPolicy`'s own `GateResult` out, per-empire reason
first), the tuning record + hub + loader with the file's own invariant enforced loudly, the two refusal
constants beside `GateReasons`, the new `gk-core/data/tuning/lawn-deploy.v1.json`, and the two host loads that
make the file's reader real.

**Why the row stays blocked, with both wires named.** (1) The gate call and its count query are
`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.UniqueActors.cs:150-250` — the one existing unique-deploy admission
gate this rule extends — which is outside this lane's allowed paths; without it the policy has no
production caller (T24: a mechanism no host reaches is not done). (2) Subsuming Zomboss's forked
`scorer.maxConcurrentOwnUnits` needs `gk-core/tools/tuning/publish.py --drop-key` plus a published
`zomboss-deploy-ai.v2.json`, and both `tools/**` and a non-`lawn*` tuning file are outside the fence —
leaving the key in place would be dead config, which the repo forbids.
