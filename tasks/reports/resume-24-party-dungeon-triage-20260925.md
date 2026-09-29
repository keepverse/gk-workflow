# Resume 24 — party-dungeon dependency triage

**Status:** read-only dependency triage. The accepted D2.16a steering work is not reopened, no
product/test/generated-data/tuning/CI/ledger file is changed, and no browser, live-game, or full-suite
claim is made.

## Executive answer

1. **The next unchecked task block in todo order after the accepted persisted-steering work is D3.31.**
   D2.17–D2.23 are already checked (`tasks/party-dungeon-todo.md:1341-1413`); D3.31 is the next open
   block (`tasks/party-dungeon-todo.md:2320-2351`). D3.31 is a **generator/schema repair**, not a
   `C#` event-dispatch defect, and it is outside the party-dungeon lane fence.
2. **There is no currently unblocked party-dungeon implementation row that can be absorbed into this
   steering follow-up.** D3.31 needs a seedsmith/narrative-seed owner decision; D4.32 and D4.14 need the
   external `npc-story-events` live path first; D4.13 is a live-simulation/coverage proof after the Phase
   5 run loop exists. The shortlist below separates those categories instead of turning absence of a
   browser/live run into a code defect.
3. **Recommended dispatch order:** (a) route D3.31 to the dungeon generator owner, (b) let
   `npc-story-events` land NR2.20 → NR2.21 → NR2.24, (c) obtain the D4.32 route-placement ruling and
   split/build the retained room-clear/extraction slice, (d) wire D4.14's report/verdict seam, then
   (e) run D4.13's 32-seed solo-autopilot coverage gate. D2.16/CAI3.5 remains a separate combat-ai lane.

The persisted-steering evidence is accepted for D2.16a's persisted record and focused Data/Server/Core
checks, while explicitly leaving live proof, `RpgHub.Resume`, and CAI3.5 open
(`tasks/reports/resume-16-delve-persisted-steering-acceptance-20260925.md:5-6`, `:80-86`). This report
treats that as the handoff boundary; it does not rewrite the row or its evidence.

## Dependency graph

```text
accepted D2.16a persisted steering
        │
        ├── independent content/generator gate ──► D3.31 (seedsmith/narrative-seed owner)
        │
        └── external live path: NR2.20 boot import
                         └──► NR2.21 /start reaches CreateDelve
                                  └──► NR2.24 room entry
                                           └──► D4.32 retained room-clear/extraction routes
                                                    └──► D4.14 DelveReport + quest verdicts
                                                           └──► D4.13 coverage after a full
                                                                Phase-5 solo-autopilot run loop

D2.16 ──► CAI3.5 / RpgHub.Resume (excluded from this shortlist)
```

D4.17/D4.30/D4.31 and their F15 content blockers remain a separate G4/content dependency for the later
Phase-5 work; they are not silently promoted into the next bounded implementation row. The map's
one-way build order places `dungeon-stage` after the live/content read models
(`docs/architecture/party-dungeon-map.md:130-143`).

## Dependency-ordered shortlist

### 1. D3.31 — event outcome atom-family generator repair (**primary next dispatch; deterministic**)

**Why this is next:** D3.9's non-event-atom-kind preflight is already implemented and intentionally
refuses the shipped corpus. `CheckEventOutcomeAtomKinds` builds the resolved container, reads the real
atom kind, and emits a named non-event-kind rejection
(`gk-core/src/FusionRpg.Core/Delve/Events/EventDeckPreflight.cs:231-277`). The current event schema still
offers only `grantable_atom_families` (`gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/briefs.py:276-289`),
and that reader is explicitly the unbound item-affix family set
(`gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/registries.py:158-178`). The pinned C# test records the
finding rather than a false green (`gk-core/tests/FusionRpg.Core.Tests/Delve/Events/EventSeedContentTests.cs:90-133`).

**Owner and exact future fence:** route this to the `narrative-seed`/`seedsmith` owner, whose
`dungeon-generator-repair` owns the event generator (`tasks/narrative-seed-todo.md:248-260`). A bounded
implementation lane may touch only the event generator and its focused tests, plus regenerated event
output:

```text
gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/briefs.py
gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/registries.py
gk-forge/tools/seedsmith/seedsmith/adapters/dungeon/pipelines.py
gk-forge/tools/seedsmith/tests/test_dungeon_event_briefs.py
gk-forge/tools/seedsmith/tests/test_dungeon_event_pipelines.py
gk-forge/tools/seedsmith/tests/test_dungeon_registries.py
gk-core/tests/FusionRpg.Core.Tests/Delve/Events/EventSeedContentTests.cs
 gk-data/packs/fusion/data/seed/dungeon/events/**       # regenerated through the generator; never hand-edited
```

The exact event-family implementation is intentionally not chosen in this report. The owner must choose
between the spec-preserving generator repair (an event-specific, event-legal atom-family vocabulary) and
a spec/dispatch ruling that would make `stat.modify` legal for an out-of-room event. D3.31 itself names
those two branches and forbids widening the preflight (`tasks/party-dungeon-todo.md:2343-2351`).

**Focused verification for that future lane:**

```powershell
$env:PYTHONPATH = 'gk-forge/tools/seedsmith'
python -m pytest gk-forge/tools/seedsmith/tests/test_dungeon_event_briefs.py gk-forge/tools/seedsmith/tests/test_dungeon_event_pipelines.py gk-forge/tools/seedsmith/tests/test_dungeon_registries.py -q
dotnet test gk-core/tests/FusionRpg.Core.Tests --no-restore --filter "FullyQualifiedName~EventSeedContentTests|FullyQualifiedName~EventDeckPreflightTests|FullyQualifiedName~EventOutcomeDispatchTests"
python gk-core/scripts/audit-magic-numbers.py --domain dungeon
python gk-core/scripts/audit-overflow.py
```

Then regenerate the event corpus through its owner command, run the real-content validator, and only
after that flip the pinning test from its intentional finding assertion to the acceptance assertion.
This is deterministic content/generator work; it does **not** require a browser or a running game.

**Hard edges and blockers:** no hand edits under `gk-data/packs/fusion/data/seed/dungeon/events/**`; no acceptance of
`stat.modify` by quietly changing `EventDeckPreflight` or `EventOutcomeDispatch`; no C# event-owner
files, tuning, or `RpgHub` changes; stop on the owner choice or an unresolved regeneration rather than
shipping a partial vocabulary. Current focused Python evidence is 80/80 passing, but that only proves
the current generator contract and does not close D3.31.

### 2. NR2.20 → NR2.21 → NR2.24 — live start and room-entry dependency (**external implementation, not party-dungeon**)

These rows are the prerequisite for any real Delve that D4.32/D4.14 can exercise. The owner ruling moved
the live path to `npc-story-events`; its task rows require boot domain import, five `/start` delegates,
and the room-entry route (`tasks/npc-story-events-todo.md:507-526`, `:561-569`). NR2.23's
`EnterRoomWithDraw` is landed as a store method, but it still has no production route caller until
NR2.24 (`tasks/party-dungeon-todo.md:4350-4353`). NR2.22 owns the quest offer/tracker route, not the
remaining D4.14 verdict half (`docs/architecture/npc-story-events/spec-delve-live-start.md:94-107`).

**Exact owner fence for the external lane:**

```text
src/FusionRpg.Data/Seed/DungeonDomainImportRunner.cs
gk-core/src/FusionRpg.Server/Program.cs
gk-core/src/FusionRpg.Server/DelveEndpoints.cs
src/FusionRpg.Server/Delve/DelveParentTerms.cs
src/FusionRpg.Server/DelveEventEndpoints.cs
src/FusionRpg.Contracts/Delve/DelveEventDto.cs                 # only when NR2.27 text wiring is taken
 focused npc-story-events Data/Server tests named by NR2.20–NR2.27
```

The focused checks are the path-owned verifier plus the named Server/Data filters in
`docs/architecture/npc-story-events/spec-delve-live-start.md:138-145` and
`docs/architecture/npc-story-events/spec-delve-live-rooms.md:152-159`. The live proof must use a real
`POST /api/delve/start` row, then the real room route, and read state through the normal query path; the
live specs explicitly prohibit fabricated rows/debug-only evidence
(`docs/architecture/npc-story-events/spec-delve-live-rooms.md:201-207`).

**Hard edges and blockers:** this lane must not absorb D4.32's room-clear/extraction routes, D4.14's
remaining verdict assembler, `RpgHub.Resume`, or CAI3.5. NR2.20/21/24 are open and are a named external
dependency, not a party-dungeon code defect. A browser failure or a missing game process is evidence
about the environment, not permission to invent a route or call a unit test live.

### 3. D4.32 — retained room-clear and extraction routes (**first party-dungeon-owned implementation candidate after the live path**)

D4.32 is explicitly retained by the transfer note and is not a duplicate of NR2.24: NR2.24 enters a
room, while D4.32 owns clearing a room and extracting the raid
(`tasks/party-dungeon-todo.md:4305-4349`). The current store already has `RecordClear` and
`CloseDelve`; `RecordClear` commits the depth watermark and optional boss grant
(`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Delve.cs:1935-1973`), while `CloseDelve` owns the ordered
settlement transaction (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Delve.cs:1103-1133`). What is missing is
the production route/caller seam and the per-room kill record, not a new settlement rule.

**Bounded dispatch rule:** do not send the whole D4.32 row as one task. Split it into (a) the retained
room-clear route/transaction, (b) the retained extraction route, and (c) the per-room battle-result
record required by D4.14. The first two share a route-placement ruling; (c) is a deterministic Data/Core
read-model seam that must still be fed by a real room-clear caller.

**Exact party-dungeon fence if the ruling keeps the routes here:**

```text
gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Delve.cs
gk-core/src/FusionRpg.Core/Delve/Report/DelveReport.cs
gk-core/src/FusionRpg.Server/DelveEndpoints.cs
gk-core/src/FusionRpg.Server/Program.cs
 focused gk-core/tests/FusionRpg.Data.Tests/Delve/**
 focused tests/FusionRpg.Server.Tests/Delve*/**
```

No `web/**`, `RpgHub.cs`, generated/tuning files, or
`DelveEventEndpoints.cs` (this path does not exist in this checkout; it is a future NR2.24 module)
belong in this slice unless the owner explicitly moves the route to the
`npc-story-events` fence. Do not create a second room-clear route beside NR2.24.

**Focused verification:** first run the in-memory Data transaction tests for clear/extract idempotency
and the per-room result read-back; then run the real endpoint sequence
`NR2.20/NR2.21 → NR2.24 → room-clear → extraction` and read the resulting `GET /api/delve/{id}` state.
The first group is deterministic implementation evidence; the second is live RPG Server proof. The
acceptance line requires the real endpoints, not direct store calls
(`tasks/party-dungeon-todo.md:4333-4336`).

**Owner/live blockers:** an owner ruling still decides whether these routes sit beside NR2.24's
`DelveEventEndpoints` or in party-dungeon, and NR2.20/21/24 must exist before a meaningful route test.
Those blockers are real; they are not evidence that the store methods are defective.

### 4. D4.14 — `DelveReport` assembly and quest verdicts (**deterministic, dependent on D4.32**)

The offer/verdict storage primitives are real: `WriteQuestVerdicts` merges into the stored offer and
cannot grow or reorder it (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Delve.cs:887-909`), and the report
model already has the six named slices (`gk-core/src/FusionRpg.Core/Delve/Report/DelveReport.cs:33-46`). The
remaining implementation is to assemble that report from real rows and call the verdict writer from the
real close path. The exact unresolved slice is `Kills`: the report declares the record, but the task's
measured search found no producer and no per-room battle-result store row
(`gk-core/src/FusionRpg.Core/Delve/Report/DelveReport.cs:9-11`; `tasks/party-dungeon-todo.md:3340-3357`).

**Exact party-dungeon fence for the verdict half:**

```text
gk-core/src/FusionRpg.Core/Delve/Report/DelveReport.cs
gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Delve.cs
 focused gk-core/tests/FusionRpg.Core.Tests/Delve/Quests/**
 focused gk-core/tests/FusionRpg.Data.Tests/Delve/**
```

The offer and tracker route are explicitly **not** in this fence; NR2.22 owns them
(`docs/architecture/npc-story-events/spec-delve-live-start.md:94-107`). Do not reopen D2.16a or touch
`RpgHub.Steer` while assembling this seam.

**Focused verification:** Core report/quest-evaluation tests (including all six slices and replay
equality), Data transaction tests for report assembly plus verdict merge, `guard-dal`,
`guard-test-substrate`, and path-owned `verify-change.ps1 -PlanOnly`. After D4.32, the real proof must
enter through the actual start/room-clear/extraction routes and read `quests_json` through the normal
Delve query path. A direct `WriteQuestVerdicts` fixture is deterministic proof, not live proof.

**Hard edges and blockers:** no fabricated `DelveReport`, no hand-built row called a live run, no second
tracker route, and no claim that the current absent browser/live environment is a code defect. D4.14
stays open until the per-room kill producer and production `CloseDelve` caller exist; the earlier
`hungerExhaustedStatusId` concern was corrected as already sourced and is not part of this slice
(`tasks/party-dungeon-todo.md:4354-4360`).

### 5. D4.13 — `QuestCoverage.Report` (**live-simulation/coverage gate, not the next code task**)

`QuestPreflight.Run` and the pure regression-band predicate are already real. The remaining
`QuestCoverage.Report` half must simulate 32 solo-autopilot delves per shipped domain and therefore
needs the full room→event→loot→pack→extraction orchestrator owned by Phase 5/delven-stage
(`tasks/party-dungeon-todo.md:3306-3314`; `gk-core/src/FusionRpg.Core/Delve/Quests/QuestCoverage.cs:4-11`).
The spec's metric is a coverage/completion measurement, not a target or a browser UI assertion
(`docs/architecture/party-dungeon/spec-delve-quests.md:306-308`).

**Fence:** no party-dungeon implementation fence is authorized now. Once the Phase-5 run-loop owner is
named, the narrow future change should be limited to
`gk-core/src/FusionRpg.Core/Delve/Quests/QuestCoverage.cs` and its focused tests, with the run-loop owner
providing the real orchestrator; it must not build a second run loop inside `delve-quests`.

**Focused verification after that dependency:** run the focused `QuestCoverage` tests, then the real
32-seed/domain solo-autopilot scenario and normal close/read-back for every domain. The existing
`WithinRegressionBand` test does not close D4.13. A browser run is a separate G5/UI proof; its absence
does not diagnose the Core coverage function.

**Owner/live blockers:** `delve-stage`/Phase 5 and a real solo-autopilot loop are required first. This
row is therefore a later live-simulation proof, not an invitation to fabricate a passing metric from
fixtures.

## Explicitly excluded: D2.16 / CAI3.5 / `RpgHub.Resume`

D2.16 remains open only because `RpgHub.Resume` still throws and its automated-policy wiring belongs to
combat-ai CAI3.5 (`tasks/party-dungeon-todo.md:1316-1328`). CAI3.5 has two separate owner/design
blockers: the `delve/enemy` role is not in the closed tuning vocabulary, and the battle view is held by
a deliberately private nested type (`tasks/reports/CAI3.5.md:6-50`). Neither is absorbed into D3.31,
D4.32, D4.14, D4.13, or any live proof in this report. No `RpgHub.Resume` implementation, `CAI3.5` tuning
publish, `CoreIntentPolicy` wiring, or `BattleRunState` visibility change is proposed here.

## Live-proof ledger for this triage

| Claim class | Current status | Correct next evidence |
|---|---|---|
| D3.31 generator/contract behavior | deterministic blocker, not live | owner-selected generator fix, regeneration, real-corpus validator |
| D4.32 clear/extract store and route code | deterministic tests possible; production route absent | in-memory transaction tests first, then real start/room/clear/extract/read-back |
| D4.14 report/verdict assembly | deterministic seam possible after D4.32 | report/transaction tests, then real close and normal `quests_json` read-back |
| D4.13 coverage | not code-verifiable yet | full Phase-5 solo-autopilot 32-seed/domain run |
| browser/game absence | environment/proof status only | do not call it a defect or fabricate a substitute |
| D2.16a persisted steering | accepted focused evidence; live proof still open | leave its accepted evidence untouched; a future live multi-party probe is separate |

## Verification performed by this triage

These are read-only checks run from this worktree; they do not close any residual row.

```text
python gk-core/scripts/audit-program-pipeline.py --only todo-task-blocks
# 118 todo files; open=671, done=2885, unticked boxes=1884, shaded=843, unmeasured=2

$env:PYTHONPATH='gk-forge/tools/seedsmith'; python -m pytest gk-forge/tools/seedsmith/tests/test_dungeon_event_briefs.py gk-forge/tools/seedsmith/tests/test_dungeon_event_pipelines.py gk-forge/tools/seedsmith/tests/test_dungeon_registries.py -q
# 80 passed in 0.79s

dotnet test gk-core/tests/FusionRpg.Core.Tests --no-restore --filter "FullyQualifiedName~EventSeedContentTests|FullyQualifiedName~EventDeckPreflightTests|FullyQualifiedName~EventOutcomeDispatchTests"
# exit 0

dotnet test gk-core/tests/FusionRpg.Core.Tests --no-restore --filter "FullyQualifiedName~QuestCoverage|FullyQualifiedName~QuestPreflight"
# exit 0
```

The two `dotnet test` invocations produced no console count in this runtime, so only their exit status is
claimed. No browser, live game, full aggregate, generated-data, tuning, CI, or ledger check was run.

## Boundary result

Only `tasks/reports/resume-24-party-dungeon-triage-20260925.md` is intended to be edited. D2.16a and
its accepted evidence are untouched. The report leaves implementation, owner rulings, and live proof
with their named receiving owners rather than laundering them into a false-green next task.

<<<REPORT {"status":"done","summary":"Read-only party-dungeon dependency triage completed after the accepted D2.16a persisted-steering handoff. D3.31 is the next unchecked task block and is correctly routed to the dungeon generator owner; NR2.20/NR2.21/NR2.24 are the external live-path prerequisites; D4.32 and D4.14 are the next party-dungeon-owned deterministic implementation seams after that path; D4.13 is a later live-simulation coverage gate. D2.16/CAI3.5/RpgHub.Resume is explicitly excluded, and browser/live absence is not treated as a code defect.","changed_files":["tasks/reports/resume-24-party-dungeon-triage-20260925.md"],"verification":["python gk-core/scripts/audit-program-pipeline.py --only todo-task-blocks — exit 0; 118 todo files, open=671, done=2885, boxes=1884, shaded=843, unmeasured=2","$env:PYTHONPATH='gk-forge/tools/seedsmith'; python -m pytest gk-forge/tools/seedsmith/tests/test_dungeon_event_briefs.py gk-forge/tools/seedsmith/tests/test_dungeon_event_pipelines.py gk-forge/tools/seedsmith/tests/test_dungeon_registries.py -q — 80 passed in 0.79s","dotnet test gk-core/tests/FusionRpg.Core.Tests --no-restore --filter FullyQualifiedName~EventSeedContentTests|FullyQualifiedName~EventDeckPreflightTests|FullyQualifiedName~EventOutcomeDispatchTests — exit 0","dotnet test gk-core/tests/FusionRpg.Core.Tests --no-restore --filter FullyQualifiedName~QuestCoverage|FullyQualifiedName~QuestPreflight — exit 0","git diff --check — exit 0","python scripts/audit-doc-citations.py --scope tasks/reports/resume-24-party-dungeon-triage-20260925.md --strict — exit 0; 12 resolvable citations, 0 HIGH"],"open_issues":["D3.31 requires an owner choice between generator repair and a spec/dispatch ruling; its future fence is outside this report boundary","D4.32/D4.14 require the npc-story-events live path and a route-placement ruling","D4.13 requires the Phase-5 solo-autopilot run loop before its coverage metric is meaningful","D2.16 remains blocked on CAI3.5 and RpgHub.Resume","no browser/live-game/full-aggregate proof was run or claimed"]} REPORT>>>
