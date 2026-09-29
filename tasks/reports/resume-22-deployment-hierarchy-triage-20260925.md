# Resume 22 — deployment-hierarchy dependency triage

**HEAD:** `6d77888cca860805e5a11e617e201847e01c16b7`
**Scope:** current code, tests, and the deployment-hierarchy map/specs/plan/todo. This is a read-only triage report; no product, test, generated-data, tuning, CI, or ledger file was changed.

## Verdict

**No existing `DH1.1`–`DH3.3` row is both genuinely buildable and bounded at this HEAD.** The first product row must not be dispatched yet.

The narrow next prerequisite is a **new coordination slice, `DH-P0`: name and own the shared per-battle settlement/carry handoff**. It is not permission to design that seam here, and it is not an implementation row in the current todo. `DH-P0` must decide which program owns the handoff, how a `BattleReport`/`BattleActorResult` becomes the next delve room's `DelveMemberState` and `BattleActorSetup`, and how the exactly-once/idempotency boundary works across web, expedition, and delve. The current `deploy-carry` spec explicitly leaves the setup-builder location unlocated (`spec-deploy-carry.md:155-168`), while the live delve start path is still absent.

Once that contract is agreed, **DH1.1 is the first product row in the map's order**. `DH3.1` is the first durability row that can consume the same settlement contract, not a substitute for it. Starting `DH3.2` or `DH3.3` first would either invent a caller or create a second durability path.

The plan's “all three durability rows are buildable now” statement is therefore too strong for the current tree. It correctly notices that `PackGrid` has shipped, but it does not establish the field-repair caller or the shared battle-settlement owner.

## Current state, by subsystem

### Carry-in — partially built, not independently wireable

The pure substrate is real and tested:

- `PartyPoolsCarry.SplitForCarryIn`, `BuildForBattle`, and `CarryOut` exist at `gk-core/src/FusionRpg.Core/Delve/Attrition/PartyPoolsCarry.cs:19-71`; `CarryOut` also checks the one-`hp`-seat invariant.
- `DelveCarryIn.Apply` exists at `gk-core/src/FusionRpg.Core/Delve/Battle/DelveCarry.cs:24-36`; it maps `CurrentHp`, statuses, and shield, but deliberately does not set `CarryInPools` (`DelveCarry.cs:15-22`).
- The optional `BattleActorSetup.CarryInPools` field is declared at `gk-core/src/FusionRpg.Core/Battle/BattleModels.cs:202-207`.
- The pure tests are present under `gk-core/tests/FusionRpg.Core.Tests/Delve/{Attrition,Battle}` (the actual current paths are `Delve/Attrition/PartyPoolsCarryTests.cs` and `Delve/Battle/DelveCarryTests.cs`).

What is absent is the production composition. A source scan at this HEAD found zero `CarryInPools =` assignments in `src/`, zero `DelveCarryIn.Apply` production calls, and zero `PartyPoolsCarry.` production calls. The result model says the same thing explicitly: `BattleActorResult.CarryOut` exists but its population is “not wired here yet” (`BattleModels.cs:628-643`). `DelveBattleSessionManager.StartSession` is implemented (`gk-core/src/FusionRpg.Server/DelveBattleSessionManager.cs:183-255`), but no production caller reaches it; its own class documentation calls the room-arrival trigger future work (`:25-35`). `DelveEndpoints.HandleStart` still returns HTTP 501 for the write arm (`gk-core/src/FusionRpg.Server/DelveEndpoints.cs:80-105`), and `RpgHub.Resume` still throws for the missing automated policy (`gk-core/src/FusionRpg.Server/RpgHub.cs:267-289`).

There is also a specification/task mismatch. `DH1.1` says every battle/delve/lawn/siege setup builder must populate the field (`tasks/deployment-hierarchy-todo.md:14-19`), while `spec-deploy-carry.md:71-80` says this module wires the delve path only and leaves lawn/siege/expedition follow-on work to their owning programs. Implementing the todo literally would widen the row beyond its own module spec; implementing the spec literally does not satisfy the todo's every-builder acceptance. That needs reconciliation before a bounded implementation can be named.

**Carry conclusion:** DH1.1 is blocked by the missing live setup/settlement seam; DH1.2 and DH1.3 inherit that block. The already-built pure functions must not be edited merely to make the rows look implemented.

### Injury tiers — absent, and DH2.1 is wider than its todo entry

There is no `WoundPolicy`, `WoundGrading`, `wound.*` catalog family, wound container, or wound counter in the current source. The existing `StatusCatalogBootstrap` stops at the three `nerve.*` rows (`gk-core/src/FusionRpg.Core/Status/StatusCatalogBootstrap.cs:62-68`), and `StatusCategoryRegistry` has no wound ids (`gk-core/src/FusionRpg.Core/Status/StatusCategoryRegistry.cs:30-35`). The live host catalog is injected from `gk-core/data/tuning/status-catalog.v1.json` by both Server (`gk-core/src/FusionRpg.Server/Program.cs:89-101`) and Injector (`gk-fusion/src/FusionRpg.Injector/Host/RpgHost.cs:123-135`); the C# bootstrap is explicitly a migration/parity shim, not the live source (`status-ssot.md:59-76`). Adding only a C# bootstrap row would not make wounds live.

The todo's DH2.1 file list (`tasks/deployment-hierarchy-todo.md:40-45`) therefore cannot meet its own “joins the closed status vocabulary” acceptance without a source/catalog/registry decision and synchronized Server/Injector readers. That is more than the listed bounded slice and needs a reviewed catalog propagation rule, not a guessed edit. The status count and documentation also move with a vocabulary change (`status-ssot.md:74-76`; `DESIGN-GATE.md:51`).

DH2.2 is additionally not ready as written: the spec explicitly leaves the `base + %lost × scale` severity binding and its `ssot-power-scale.md` §10 row owed (`spec-injury-tiers.md:38-50,193-200`). DH2.3 depends on DH2.2 and on a wound-bearing deployment target; the spec's world/legion target is itself a named real gap (`spec-injury-tiers.md:122-130`). No current row supplies the durable wound table or the carry/settlement path needed to prove next-deployment effect.

**Injury conclusion:** DH2.1–DH2.3 are not buildable as bounded rows now. A catalog slice could be carved separately, but that would be a new row with a live-catalog contract, not permission supplied by the planned DH2.1 text.

### Durability — substantially partial, but the three remaining rows are not closed

The durability work must not be reported as wholly absent. At this HEAD the following are already shipped:

- `effect_instance.durability_max/current` columns and derive/backfill seams (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.InstanceOps.cs:31-45,93-102,154-162`).
- `DurabilityTable` derivation and its refusal/overflow tests (`gk-core/src/FusionRpg.Core/Items/Materials/HeadDerivationTables.cs:54-78`; `gk-core/tests/FusionRpg.Core.Items.Tests/Items/DurabilityTests.cs`).
- The unique-equipment at-zero filter at `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Items.cs:939-955`.
- The shared `RepairPolicy` and real workbench repair path (`gk-core/src/FusionRpg.Core/Items/Materials/RepairPolicy.cs:14-59`; `gk-core/src/FusionRpg.Server/ItemWorkbench.cs:1051-1131`).
- The commander assignment/materialization substrate, including `MaterializeRolledCommanderEquipRuntime` (`RpgStore.Items.cs:1001-1034`) and its real lawn sync caller (`gk-core/src/FusionRpg.Server/ItemEquipEndpoints.cs:490-509`).
- The corpse-cache/decay family and the `CloseDelve` death settlement hook (`RpgStore.CorpseCache.cs:150-197`; `RpgStore.Delve.cs:1103-1224`). These are not substitutes for a per-battle settlement hook.

The remaining gaps are still real:

- `DeploymentHierarchyTuning` has `craftWearPerAttemptMilli` and `repairDestroyChanceMilli`, but no `wearPerBattleMilli`, `repairRatioMilli`, or field `tierCapMilli` fields, and the parser does not read them (`gk-core/src/FusionRpg.Core/Items/Materials/DeploymentHierarchyTuning.cs:12-25,63-103`). The v5 JSON only mentions `wearPerBattleMilli` in a reservation note (`gk-core/data/tuning/deployment-hierarchy.v5.json:4,97-113`); it is not an active key.
- There is no battle-wear function or settlement caller. `CraftRiskPolicy.WearFor` is craft wear only (`gk-core/src/FusionRpg.Core/Items/Materials/CraftRiskPolicy.cs:21-51`).
- `ICarriedSupplyCheck` does not exist in `src/`, and there is no field-repair endpoint or call site. The durability spec itself says the interface is “only” and that the exact field endpoint is named after an implementation exists (`spec-item-durability-repair.md:213-221,314-321`). `PackGrid` now exists (`gk-core/src/FusionRpg.Core/Delve/Pack/PackGrid.cs:46-113`), so the todo's stale “PackGrid unbuilt” claim is corrected, but its presence does not supply a live party-pack reader, tool/material identity, or repair transaction.
- Commander materialization is not battle wear. There is no unique-gear battle-wear path to which DH3.3 can be made mechanically identical. Adding a commander-only decrement would create the second path that `battle-engine-ssot.md:141-157` and the task's own acceptance forbid.

**Durability conclusion:** DH3.1 is blocked by the absent shared per-battle settlement hook; DH3.2 is blocked by an unspecified field-repair contract/caller; DH3.3 is blocked by the absence of the unique battle-wear mechanism it claims to mirror. The todo's `deps: —` on DH3.3 is not true at current HEAD.

## Recommended prerequisite: `DH-P0` shared settlement/carry handoff

This is a coordination and contract slice, not a product edit under the present report fence. It should answer, with code evidence and owner ownership:

1. Which existing host owns conversion of a resolved `BattleReport` into the per-battle settlement fact, without adding a mode-local wear or carry mechanism?
2. How does the delve room-arrival path construct the next `BattleSetup` from `DelveMemberState`, `CarryOut`, and the persisted idempotency key?
3. Which paths are deliberately in scope now (web/expedition versus delve), and how will a future mode consume the same contract?
4. Does the bridge require CAI3.5/party-dungeon changes to `RpgHub`, `DelveBattleSession`, `DelveBattleSessionManager`, `DelveBattle`, or `BattleRunState`?

The current code does not answer these questions. `WebMatchService.ResolveAndIngest` is a real exactly-once ingest point for web/expedition (`gk-core/src/FusionRpg.Server/WebMatchService.cs:386-468`), but the delve session's completed `Task<BattleReport>` is not routed through it (`DelveBattleSession.cs:70-73,198-212`). A web-only durability hook would be an incomplete mode implementation, not DH3.1.

## Exact path fence

### This triage session

Only:

```text
tasks/reports/resume-22-deployment-hierarchy-triage-20260925.md
```

No session record was created in this worktree because the brief already supplied the report-only boundary and the record is not present at this HEAD. No other path is authorized for this task.

### A future DH1.1/DH-P0 implementation session

There is no honest exact product fence to dispatch from the current todo. The setup builder is deliberately unlocated in `spec-deploy-carry.md:155-168`, and the likely delve composition seam overlaps CAI3.5-owned Server/Core paths. Before implementation, a new session must claim and reconcile at least the following **cross-program conflict set**, not edit them from this report:

```text
gk-core/src/FusionRpg.Server/DelveBattleSessionManager.cs
gk-core/src/FusionRpg.Server/DelveBattleSession.cs
gk-core/src/FusionRpg.Server/RpgHub.cs
gk-core/src/FusionRpg.Core/Delve/Battle/DelveBattle.cs
gk-core/src/FusionRpg.Core/Battle/BattleRunState.cs
gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Delve.cs
gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs
focused Core/Data/Server tests for the named settlement and carry path
```

That list is a **future coordination fence**, not authorization for this session and not a recommendation to widen this report. `tasks/combat-ai-todo.md:861-886` and `tasks/reports/CAI3.5.md:33-56` identify CAI3.5 as the owner of the blocked automated-policy/Server seam. The prerequisite must be scheduled with that owner rather than absorbed here.

## Rejected alternatives

| Candidate | Why it is rejected now |
|---|---|
| DH1.1 | Pure carry functions and the field exist, but no production setup builder, no `CarryOut` producer, no live delve start caller, and the todo's all-modes acceptance conflicts with the module spec. |
| DH1.2 | Depends on DH1.1; changing `DelveCarryIn.Apply` to read pools would contradict its locked design note and still would not create a production caller. |
| DH1.3 | Depends on DH1.2; `EventOutcomeDispatch` appends status specs (`gk-core/src/FusionRpg.Core/Delve/Events/EventOutcomeDispatch.cs:220-245`) but no next-room consumer exists. |
| DH2.1 | Wound implementation is absent, and the listed C#-only slice cannot satisfy the host-injected live status catalog or the closed category registry. |
| DH2.2 | Depends on DH2.1 and leaves the severity-to-power binding/§10 row unresolved; it also needs durable state and settlement wiring. |
| DH2.3 | Depends on DH2.2 and names a world/legion target that does not exist. |
| DH3.1 | The workbench/craft durability path is real, but battle wear has no tuning reader or shared settlement caller. A `WebMatchService`-only hook would not cover delve. |
| DH3.2 | `PackGrid` is shipped, but the interface, supply semantics, and field-repair caller are absent; selecting it would turn a planned placeholder into an invented design. |
| DH3.3 | Commander materialization exists, but no shared battle-wear mechanism exists to mirror. A commander-only write would be a second durability path. |
| DH-B1 | The injector host assembly-name collision is real, but it is a separate build-infrastructure row and the todo records an unresolved owner choice about whether the collision is intentional. It is not a carry/injury/durability dispatch and should not be used to bypass this triage. |

## H1 / H2 / H7 implications

These are the parent convergence hard edges defined in `tasks/summoner-convergence-plan.md:97-109` and `:155-167`.

- **H1 — one golden cause per commit.** The deployment plan says carry inheritance is additive to an inert field and that a golden move is a defect, not something to re-bless silently (`tasks/deployment-hierarchy-plan.md:74-80`). A future DH1.1 must prove room-one fixtures and replay hashes remain byte-identical; if a battle golden moves, stop and report the cause rather than bundling a second re-bless. A DH3.1 settlement change likewise must not combine a golden correction with an unrelated tuning publish.
- **H2 — save-identity migration before re-keyed writes.** None of the current carry/injury/durability rows needs to write the re-keyed `(save_id, empire_id)` progression/XP tables, so H2 is not the present blocker. A future settlement design must not introduce such a write as a side effect; if it does, `SE4.20` must land first (`summoner-convergence-plan.md:102`).
- **H7 — publish and reader switch together.** `wearPerBattleMilli` is not currently parsed. A future DH3.1 must publish the next `deployment-hierarchy.v6.json` through `gk-core/tools/tuning/publish.py`, add the reader field/validation, and switch the Server reader in `Program.cs:255-259` in the same change. The deployment-hierarchy file is currently read by Server, not Injector. The status catalog is a separate case: Server and Injector both read `status-catalog.v1.json`, so a wound-vocabulary change must keep both readers on the same catalog source and update the registry/count/docs coherently. No file-only or reader-only publish is acceptable.

## Focused verification boundary

### Evidence used for this triage

Read-only source/test checks run at this HEAD:

```text
git rev-parse HEAD
# 6d77888cca860805e5a11e617e201847e01c16b7

dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~DelveCarry|FullyQualifiedName~PartyPoolsCarry" --no-restore
# exit 0

dotnet test gk-core/tests/FusionRpg.Core.Items.Tests --filter "FullyQualifiedName~Durability|FullyQualifiedName~RepairPolicy" --no-restore
# exit 0

dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~HeadPairTests|FullyQualifiedName~CraftWearInstanceOpTests" --no-restore
# exit 0

dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~DelveBattleSession" --no-restore
# exit 0

source scan: CarryInPools assignments, DelveCarryIn.Apply/PartyPoolsCarry production calls,
ICarriedSupplyCheck, WoundPolicy, and WoundGrading
# zero production hits for each named missing seam; the scan's textual wearPerBattleMilli hits
# are reservation notes in tuning JSON, not a parsed key
```

The test commands were used to confirm that the existing pure/substrate tests still pass; they do not prove a production caller exists. The source scans and the explicit zero-caller comments are the evidence for that separate claim.

### Future DH1.1 boundary, once the path is named

Run only the path-owned selection, for example:

```powershell
.\scripts\verify-change.ps1 -Paths <every concrete DH1.1 code/test path> -Session <new-session-id>
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~DelveCarry"
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~BattleGolden"
dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~DelveBattleSession"
.\scripts\guard-actor-hub.ps1
.\scripts\guard-dal.ps1
python gk-core/scripts/guard-battle-responsibility.py
```

Do not run a broad suite for this ordinary row. The full unfiltered suite remains CI/nightly/release-owned. A future DH3.1 must additionally select the deployment-tuning reader tests and the unique/commander durability tests, but only after the shared settlement owner is named.

## Unresolved owner/program questions

1. **Settlement ownership:** should the shared per-battle settlement/carry bridge be owned by deployment-hierarchy, party-dungeon, or combat-ai/CAI3.5, and what is the exact cross-program contract?
2. **DH1.1 scope:** is the acceptance deliberately delve-only, as the module spec says, or must one bounded row cover every battle/deployment setup kind as the todo currently says?
3. **Injury severity:** before DH2.2, bind the `base + %lost × scale` rule to an existing potency/power read and approve the required `ssot-power-scale.md` §10 row. The current spec explicitly leaves this owed; this report does not choose a curve.
4. **Field repair:** what exact live party-pack/actor-inventory read, tool/material identity, repair caller, and transaction/idempotency key implement `ICarriedSupplyCheck`? `PackGrid` alone is not that contract.
5. **DH-B1:** is the duplicate `FusionRpg.Injector` assembly name intentional? Keep it as a separate owner/build decision rather than folding it into a deployment row.

## Final verification

The required final checks are run after this report is written:

```text
python gk-core/scripts/audit-program-pipeline.py --only todo-task-blocks
# exit 0; deployment-hierarchy reports 10 open task blocks, 0 done blocks, and 14 unticked boxes

git diff --check
# exit 0
```

The final report block records the actual outcomes and the single changed path. No commit, push, or branch operation is part of this brief.

<<<REPORT {"status":"done","summary":"Triaged deployment-hierarchy at HEAD 6d77888: carry-in is pure/tested but has no production setup or settlement caller; injury tiers are absent and DH2.1 needs a live-catalog contract beyond its listed slice; durability storage, derivation, repair, unique filtering, and commander materialization are partial/real, but battle wear, field repair, and commander battle-wear parity remain blocked. No existing DH1.1-DH3.3 row is genuinely bounded now. Recommend a new DH-P0 shared settlement/carry handoff prerequisite, then DH1.1; do not absorb CAI3.5.","changed_files":["tasks/reports/resume-22-deployment-hierarchy-triage-20260925.md"],"verification":["HEAD confirmed at 6d77888cca860805e5a11e617e201847e01c16b7","focused carry, durability, repair, and Delve battle-session dotnet test commands exited 0","source scans found zero CarryInPools assignments, zero production DelveCarryIn.Apply/PartyPoolsCarry calls, no ICarriedSupplyCheck, no WoundPolicy/WoundGrading, and no parsed wearPerBattleMilli key","python gk-core/scripts/audit-program-pipeline.py --only todo-task-blocks exited 0; deployment-hierarchy has 10 open task blocks and 0 done blocks","git diff --check exited 0"],"open_issues":["DH-P0 shared settlement/carry ownership and exact setup-builder seam are unresolved","CAI3.5 remains blocked and is outside this fence","DH1.1 todo acceptance conflicts with the delve-only module spec","DH2.2 injury severity power binding remains owed","DH3.2 field-repair contract and DH3.3 shared battle-wear prerequisite remain absent","DH-B1 remains a separate owner/build decision"],"next_steps":["have deployment-hierarchy, party-dungeon, and combat-ai owners name the DH-P0 contract before scheduling DH1.1","schedule DH1.1 only after a new exact path fence and CAI3.5 crossing are reconciled"]} REPORT>>>
