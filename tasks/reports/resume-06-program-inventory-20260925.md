# Resume 06 — program inventory and dependency-aware next-lane queue

**Status:** complete — read-only inventory; no product, generated-data, CI, verification-script, task-ledger, or acceptance-artifact edits.

**Snapshot:** `features/mega-merge` at `5bc4964725a56ff013d1742b298d03e69a04ed92` (`2026-09-25T09:59:03+07:00`, `merge: record fresh browser QA spawn`). The inventory worktree is intentionally based at `e3ce4a1a24ad709e23506d6a401a47b11cd1b70c`; the integration ref advanced beyond the first measurement during this read-only pass. The final re-pin includes the accepted TVB-F36 classifier repair, the accepted PassiveTree report/read parity repair, the two ledger-reconciliation rows, and the fresh bounded browser-QA lane; no unlisted product or task implementation was inferred from the moving ref.

## Executive answer

1. The reproducible current **TVB-F20 task-block census** is **118 todo files, 67 nonzero programs, 671 open task blocks, 2,885 done blocks, 1,884 unticked boxes, and 843 shaded boxes**. This is a mechanical reading, not a genuine-work total and not interchangeable with the older convergence census.
2. A genuine adjusted count still cannot be published. TVB-F36 removed the 27 `derived-stats` heading-classifier false positives; the current reading still contains at least four known stale/moot/out-of-fence rows (`battle-derived-wire` T7/T9 and `rpg-simulator` RS-F21/RS-F24), plus contradictory ledgers and owner/live/generated/migration gates. A purely arithmetic ceiling is **667 or fewer** if all four legacy rows are excluded, but that is not a defensible “remaining work” number.
3. The four-row implementation queue is now **partially dispatched**: `resume-11-build-preset-bp1112-20260925`, `resume-12-passive-tree-p11-1r-20260925`, and `resume-13-rpg-simulator-rsf27-20260925` are active. `combat-ai CAI2.2` remains the next bounded implementation candidate, but its Data/Server verification-boundary owner mapping must be repaired before acceptance. The separate TVB-F36 classifier repair is accepted and merged; it is not a product implementation lane.
4. Do not resume BCU2.12 or claim merged-head completion yet. The manager control record still says the current-head post-merge gate remains open; browser proof, live-game proof, and release proof remain separate. The legal BepInEx/MelonLoader preflight is green, but it is explicitly **not** the final merged-head gate, live proof, or release proof.

## Evidence and method

- The source basis is the current `features/mega-merge` tree, not the stale worktree base: capability maps/specs, current `tasks/*-todo.md`, the manager handoff `tasks/reports/mega-merge-deep-audit-20260924.md`, exact-SHA acceptance artifacts, active session records, and the current manager report. The final re-pin is `5bc4964725a56ff013d1742b298d03e69a04ed92`; the earlier `b61e724f910a291d1dff60295dcf186646ab1685`, `1f00bd55cb4dda1a173acf53d4c10883f56696b7`, `e00f7ab4555290198a20ec045421405ee4163050`, and `13052e713fd361edc166e9d795432576f8e9f2ca` measurements are retained only as historical snapshots. The manager control record has not yet absorbed the newer TVB-F36 acceptance or all newly dispatched lane states, so the current session records and exact-SHA artifacts are the lane-state evidence where they conflict.
- The census command is the repository’s authoritative shape-aware instrument:

  ```powershell
  python gk-core/scripts/audit-program-pipeline.py --only todo-task-blocks
  ```

  At the pinned integration snapshot it reports:

  ```text
  TOTAL open=671 done=2885 boxes=1884 shaded=843 unmeasured=2
  ```

  The two unmeasured files are `tasks/player-guide-todo.md` and `tasks/world-map-gaps-followup-todo.md`; their shape is `none`, so the instrument refuses to guess their task-block semantics.
- The older manager headline (`507` open blocks, `456` residue, `19` WIP, `59` programs) is a historical cross-check from `tasks/reports/mega-merge-program-resume-20260925.md`; it is not a replacement for TVB-F20 and must not be compared as if it used the same classifier and head.
- Unchecked acceptance boxes are intentionally not counted as independent work. A shipped task may retain permanently unticked acceptance lines. The report uses task blocks and records the mechanical box count only as a diagnostic.

## Genuine-open disposition

The following groups are the useful inventory. Counts in the first column are the mechanical open-block readings; they are **not** claims that every block is executable.

### Dependency-ready implementation candidates

| Program / exact row | Mechanical reading | Dependency and evidence | Fence / stop condition |
|---|---:|---|---|
| `build-preset` **BP1.11** (`tasks/build-preset-todo.md:127`) and **BP1.12** (`:140`) | 17 program blocks | BP1.10, SE4.12, and SE4.14 are done. The todo explicitly permits the human-only `EmpireRef` guard even if SE4.37 has not landed. The store must be born with `(save_id, empire_id)`, validate references on read, and keep SQL in `FusionRpg.Data`; the spec is `docs/architecture/build-preset/spec-preset-store.md`. | Data-only slice: `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.BuildPresets.cs`, `gk-core/tests/FusionRpg.Data.Tests/BuildPresets/BuildPresetStoreTests.cs`; then Server slice: `gk-core/src/FusionRpg.Server/BuildPresetEndpoints.cs`, `gk-core/src/FusionRpg.Server/Program.cs`, `gk-core/tests/FusionRpg.Server.Tests/BuildPresetEndpointsTests.cs`. Use the row’s `guard-dal`, `guard-test-substrate`, and `verify-change -Paths ... -Session <sid>` boundaries. Stop if implementation needs a new shared DTO, non-human empire semantics, or generated/tuning data; report the exact seam instead of widening. The listed Data/Server implementation and test paths are planned lane paths; each file **does not exist in the integration tree at this snapshot**. |
| `passive-tree-repair` **P11.1r** (`tasks/passive-tree-repair-todo.md:773+`) | 13 program blocks | Code defect is precise: `gk-core/src/FusionRpg.Core/PassiveTree/Resolve/TreeAtomSource.cs:68-75` filters every `stat.modify` atom while `NodeAtom` calls that kind primary. The replacement uses the existing `AtomDerivedSubsystem` fan-in; it must not add a fourth `IActorStatSubsystem`. P7.1/P8.3 remain blocked by this and by the separate status executor/corpus gates. The accepted `resume-08` parity repair only aligns the report with the derived resolver; it explicitly does **not** widen the primary route. | Fence: `gk-core/src/FusionRpg.Core/PassiveTree/Resolve/TreeAtomSource.cs` and focused `gk-core/tests/FusionRpg.Core.PassiveTree.Tests/PassiveTree/tests-PassiveTree/Resolve/TreeAtomSourceTests.cs` (plus only a proven existing parity test). Read `docs/architecture/passive-tree/spec-mechanism-wiring.md`; do not edit `gk-data/packs/fusion/data/seed/**`, `gk-data/packs/fusion/data/generated/**`, tuning, or the generator corpus. Stop at a named mapping ambiguity; do not invent a new subsystem or repair BCU2.12. |
| `rpg-simulator` **RS-F27** (`tasks/rpg-simulator-todo.md:793+`) | 12 program blocks | The four progression-ledger assertions are vacuous on an empty row set. `RpgXpAwardMap.FromActivity` can return no award for victory/stalemate, so the row’s emptiness question is real. The scenario contract and read-back rules are in `gk-core/tools/RpgSim/scenario-format.md`. | Fence: `gk-core/src/FusionRpg.Core/Progression/RpgXpAwardMap.cs`, the existing RpgSim scenario/read-back implementation, and focused RpgSim tests. Assert the contract/closed vocabulary, not a population count; do not edit generated corpus data. Stop if the answer requires an owner policy choice about whether an empty progression ledger is legal; report the alternative rather than adding a flaky `notEmpty`. |
| `combat-ai` **CAI2.2** (`tasks/combat-ai-todo.md:348+`) | 27 program blocks | Core identity and Server source half are already landed. The remaining core is the nullable `combat_ai_profile` Data column/store read and the production pin consumer; the spec is `docs/architecture/combat-ai/spec-replay-identity.md`. This is implementation-ready, not an owner decision. | Data fence: `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs`, `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WebMatches.cs`, and Data tests. Server fence: `gk-core/src/FusionRpg.Server/CombatAiProfileFiles.cs`, `gk-core/src/FusionRpg.Server/WebMatchService.cs`, `gk-core/src/FusionRpg.Server/DelveBattleSessionManager.cs`, and focused Server tests. Keep SQL in Data, use the existing `ContentHashStamp` comparison, and preserve null legacy semantics. Stop if a shared wire DTO or generated tuning publish is required; do not absorb CAI3.5/`RpgHub.Resume` or add a second policy resolver. |

### Lane state at the final re-pin

The current session records and exact-SHA artifacts, not the manager report's older active-lane table, determine state at this snapshot:

- `resume-07-web-browser-qa-20260925` is **abandoned** without a report or browser evidence. No server was claimed and no product files changed.
- `resume-15-web-browser-qa-20260925` is **active** as the fresh bounded replacement. It may write only its report and ignored local build outputs; it must stop on a timeout or occupied port, use no fabricated state, and stop only its own server. Browser proof remains open until that lane produces a real report and read-back.
- `resume-08-passive-tree-binder-20260925` is **abandoned/released** after its narrow report/read parity repair was accepted at reviewed SHA `1984dfcd185a26b7d2127c871b712e4f0f985e5f` and merged at `3aa8d7656a70e159892f9ab17dec397a00f9d39f`. The binder corpus, primary `stat.modify` route, pool resolver, stale generated evidence, and BCU2.12 remain open; that acceptance does not close P11.1r.
- `resume-09-battle-guard-repin-20260925` is **merged** through reviewed SHA `78f4db6f`; artifact `.claude/cmdc-agents/acceptance/resume-09-battle-guard-20260925-78f4db6f.json`.
- `resume-10-delve-persisted-steering-20260925` is **active** on owner-ruled D2.16a persisted steering across Server/Data/reconnect; it explicitly excludes `RpgHub.Resume`/CAI3.5.
- `resume-11-build-preset-bp1112-20260925` is **active** on BP1.11 then BP1.12, with the exact five-file Data/Server fence from its brief.
- `resume-12-passive-tree-p11-1r-20260925` is **active** on P11.1r only, using the existing derived fan-in and stopping on unresolved scale/op or production-seam ambiguity.
- `resume-13-rpg-simulator-rsf27-20260925` is **active** on RS-F27 only, using real scenario read-backs and stopping if empty-ledger legality requires an owner ruling.
- `resume-14-tvb-f36-classifier-20260925` is **merged**. Its exact reviewed SHA is `a3660c664d99c36cc33944df192ad6a2db8534ee`, merged at `7ca9ee8b4ade30309117525e17f3c609d4ea33ff`; artifact `.claude/cmdc-agents/acceptance/resume-14-tvb-f36-20260925-a3660c66.json` records `26` focused tests passing and the corrected `open=671` census.
- `combat-ai CAI2.2` is **queued, not dispatched** at this snapshot. The Data column/store read and Server pin-wire consumer remain bounded, but the verification-boundary owner mapping must be repaired before an implementation lane is accepted.

### Owner, live, legal, browser, or external-environment blocked

These are genuinely open in the ledger but must not be put into an unattended implementation queue without the named evidence:

- `actor-hud` P6, `lawn-combat-wire` task-split audit, `lawn` live-proof rows, `notification-ssot` NS5.13/NS6.8, `scope-side-wide`, `shield` owner run, `strain-splice-host` SSH4.9, `injector-stub` W3, `power` AUDIT-1, and other rows explicitly naming a live slot, browser review, owner review, or RPG Server Debug proof.
- `passive-tree` J10/J13 and `backlog-clean-up` BCU2.12: generated-corpus/model/full-run work. The current binder diagnosis is separate; BCU2.12 remains paused.
- `empire-development` authored content/tuning rows, `narrative-seed` model-spend rows, `npc-story-events` runtime/content rows, and `ip-censor` release/corpus rows: owner decisions, model authorization, generated data, or release gates are named in their own ledgers.
- `party-dungeon` D2.16a is now owner-ruled and actively dispatched; D2.16, D3.31, D4.13, and D4.14 remain separate residuals. Do not fold them into the steering lane.
- `world-stage`, `world-map-runtime`, `effect-pipeline`, and `deployment-hierarchy` have substantial new-program work but are not the bounded next slice; they need their own dependency/order decision rather than being silently promoted.

### Mechanical false positives, stale rows, and ledger contradictions

These explain why no single genuine total is published:

- `tasks/derived-stats-todo.md` has 28 checked `### - [x]` headings and zero unchecked headings. The former classifier defect was **accepted and merged by TVB-F36**; the current reading is **0 open / 28 done**, so those 27 former false positives are no longer counted.
- `tasks/battle-derived-wire-todo.md` explicitly says T7 is **SUPERSEDED/moot** (no production `DelveBattle.Run` caller) and T9 is **BLOCKED** on the item seed→concrete producer. They are not executable battle-derived-wire work.
- `rpg-simulator` RS-F21 and RS-F24 remain open ledger rows outside this queue's fence; RS-F21 is stale after the cited fixture repair, while RS-F24 is a real protected-guard repair for its owning program. Neither should be folded into RS-F27.
- `tasks/onboarding-rift-todo.md` says its header closes the work while 26 headings still say `OPEN`; this is an unresolved ledger contradiction, not 26 ready tasks. It is now explicitly routed as **BCU2-R1**.
- `tasks/npc-story-events-todo.md` header count and row count disagree (the older reconciliation recorded 94 named tasks versus 101 open rows); the owning program must reconcile it.
- `gk-core/scripts/todo-shapes.v1.json` has `none` for `tasks/player-guide-todo.md` and `tasks/world-map-gaps-followup-todo.md`; the census correctly reports them as unmeasured rather than guessing.
- **TVB-F36** is no longer an unrouted finding: the classifier repair is accepted at `a3660c664d99c36cc33944df192ad6a2db8534ee` and merged at `7ca9ee8b4ade30309117525e17f3c609d4ea33ff`. The separate onboarding-rift contradiction remains open under **BCU2-R1**.

### Known residuals from accepted P1 work

The accepted artifacts are exact-SHA evidence, not evidence that every related row is closed:

- Delve `03d8cee8`: server-owned join/pricing accepted; owner-ruled persisted steering is now the active D2.16a lane.
- Battle `7b4e8ef5`: ActorHub/observer/numeric P1 accepted; the H1 byte-pin was separately re-pinned and accepted at `78f4db6f`; live battle proof remains open.
- Web `4ff99673`: recovery/match-isolation code accepted; browser proof is now being rerun in the fresh bounded `resume-15` lane after `resume-07` was abandoned without a report.
- Expedition `ec4773b9`: durable replay/identity accepted; long-path/migration limits remain named residuals.
- Vocabulary `85d2c096`: FamilyExpand vocabulary recovery accepted; `TreeBinder --check` remains a separate current corpus/refusal diagnosis. It is not byte-staleness and is not P11.1r.
- Split-Core mapping `ff934d08`: exact mapping evidence accepted; it does not replace the current merged-head gate.

## Four-lane implementation queue and dispatch state

The queue remains four bounded implementation rows, but the manager has now dispatched three of them. Each lane keeps its persisted report, exact fence, focused verification boundary, and stop condition; no lane may absorb another row or fallback scope. **CAI2.2 is not dispatched until the Data/Server verification-boundary owner mapping is repaired.**

### Lane A — build-preset store and routes

- **Rows:** BP1.11 then BP1.12.
- **Allowed paths:** the five exact files listed in the two row entries above; no generated data, tuning, Contracts, or unrelated Server routes.
- **Hard edges:** save/empire identity from SE4.12/SE4.14; human-only `EmpireRef` refusal; SQL only in Data; validate-on-read; no new DTO without stop/report.
- **Focused boundary:** Data `BuildPreset` tests + `guard-dal` + `guard-test-substrate`; Server `BuildPresetEndpoints` tests + path-owned `verify-change.ps1 -Paths ... -Session <sid>`.
- **Stop:** new schema/DTO/owner semantics, missing identity dependency, or any need to touch generated/tuning files.

### Lane B — passive-tree primary-atom fan-in

- **Row:** P11.1r only.
- **Allowed paths:** `gk-core/src/FusionRpg.Core/PassiveTree/Resolve/TreeAtomSource.cs`, `gk-core/tests/FusionRpg.Core.PassiveTree.Tests/PassiveTree/tests-PassiveTree/Resolve/TreeAtomSourceTests.cs`, and only a pre-existing focused parity test if required.
- **Hard edges:** existing `AtomDerivedSubsystem` fan-in; no new subsystem/order band; `stat.derived` and `stat.modify` both use the existing scale/op contract; do not touch generated trees.
- **Focused boundary:** `dotnet test gk-core/tests/FusionRpg.Core.PassiveTree.Tests --filter "FullyQualifiedName~TreeAtomSource"`; relevant Core balance/parity tests; `guard-actor-hub`, `guard-power`, and `verify-change -PlanOnly` for every changed path.
- **Stop:** unresolved `KMicro`/`ScaleAxis` mapping, need for a new registry/subsystem, or any corpus regeneration request. P7.1/P8.3 remain blocked until this and the separate mechanism executor are real.

### Lane C — simulator progression-ledger contract

- **Row:** RS-F27 only.
- **Allowed paths:** `gk-core/src/FusionRpg.Core/Progression/RpgXpAwardMap.cs`, existing `gk-core/tools/RpgSim` scenario/read-back code, and focused RpgSim/Core tests named by the row.
- **Hard edges:** every verdict is a real read-back; no fabricated rows; no population-count assertion; do not make a random `notEmpty` guard before the emptiness policy is decided.
- **Focused boundary:** RpgSim focused tests plus the scenario contract tests; `verify-change -Paths ... -Session <sid>` and the applicable Core boundary.
- **Stop:** owner decision required about legal empty ledgers, or a requested change to the generated corpus/fixture population.

### Lane D — combat-ai replay identity Data/Server seam

- **Row:** CAI2.2 only.
- **Allowed paths:** `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs`, `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WebMatches.cs`, `gk-core/src/FusionRpg.Server/CombatAiProfileFiles.cs`, `gk-core/src/FusionRpg.Server/WebMatchService.cs`, `gk-core/src/FusionRpg.Server/DelveBattleSessionManager.cs`, and focused Data/Server tests.
- **Hard edges:** one nullable `combat_ai_profile` column; no `profile_id` conflation; existing `ContentHashStamp` semantics; null means pre-profile legacy, unavailable/mismatch refuse; SQL stays in Data; no CAI3.5 or `RpgHub.Resume` widening.
- **Focused boundary:** Data WebMatch tests, Server WebMatch/Delve focused tests, unchanged BattleGolden check, `guard-dal`, `guard-test-substrate`, and path-owned `verify-change`.
- **Stop:** shared wire DTO, tuning publication, or any need to implement automated Delve policy. Report the exact missing seam.

**Dispatch state at the snapshot:** Lane A is active as `resume-11-build-preset-bp1112-20260925`; Lane B is active as `resume-12-passive-tree-p11-1r-20260925`; Lane C is active as `resume-13-rpg-simulator-rsf27-20260925`; Lane D remains queued behind the verification-boundary mapping repair. TVB-F36 was a separate manager-pipeline lane and is already merged.

## Findings and receiving rows

The former `TVB-F36` classifier finding is resolved by exact-SHA acceptance and merge, so it is no longer unrouted. The remaining findings below are not edits made by this session. Their target row/file is the recommended owner location; a manager should route them in the owning ledger rather than silently folding them into a product queue lane.

| Finding | Evidence / exact current location | Receiving owner / target |
|---|---|---|
| `onboarding-rift` header/heading contradiction | `tasks/onboarding-rift-todo.md:30` says all boxes are closed; 26 task headings still read `OPEN` (for example `:38`). | Existing **BCU2-R1** in `tasks/backlog-clean-up-todo.md:357`; the onboarding-rift owner must declare whether the header or headings are authoritative, then reconcile the todo in one bookkeeping change. Do not tick implementation rows. |
| BCU2.12 generated-corpus state is paused, not healthy | `tasks/backlog-clean-up-todo.md` BCU2.12; current manager record says the full run is paused pending a terminal head gate. The binder report is a code/gate diagnosis, not a corpus-health claim. | Existing **BCU2.12** row; do not create a duplicate. Add a checkpoint only if the manager must distinguish binder diagnosis from corpus rerun. |
| CAI2.2 Data third and production pin consumer are outside prior combat-ai fences | `tasks/combat-ai-todo.md:348`; `docs/architecture/combat-ai/spec-replay-identity.md:36-38,62-67,179-217` names `RpgStore.cs`, `RpgStore.WebMatches.cs`, and Server replay paths. | Existing **CAI2.2** row, with the explicit Data/Server fence above. No new row; the old “Server third unbuilt” wording is stale. Dispatch remains gated on the verification-boundary mapping. |
| CAI2.2 citation-routing findings | `tasks/combat-ai-todo.md` CAI-cite-4/CAI-cite-5; broken citations are in `action`, `action-enrich`, `action-skill-tiers`, `class-system`, `battle-engine-ssot`, and evidence-fragment paths. | Existing **CAI-cite-4/CAI-cite-5** rows; route each citation to the named owning program. Do not put doc re-anchoring in CAI2.2’s Data/Server implementation commit. |
| `TreeBinder --check` is a separate diagnosis | `gk-forge/tools/TreeBinder -- --check` was reproduced with 42 displayed tree verdicts failing on current corpus/refusal semantics; accepted vocabulary recovery artifact is `85d2c096`. | Passive-tree P6/P8 follow-ups. Do not relabel it as byte-staleness and do not attach it to P11.1r. |
| Verification-boundary mapping gap for new Data/Server paths | `gk-core/scripts/verification-boundaries.v1.json` has focused build-preset Core/tuning mappings but no focused owner for the candidate Data/Server paths; the manager control record still records a `VERIFICATION BOUNDARY MISSING` gap. | A dedicated TVB registry-repair row/lane before CAI2.2 or build-preset acceptance; do not silently widen another program’s fence. |
| Manager control-record drift | `tasks/reports/mega-merge-program-resume-20260925.md` still lists browser/binder as running and omits TVB-F36 acceptance plus `resume-11`–`resume-13`, while current session records/artifact `.claude/cmdc-agents/acceptance/resume-14-tvb-f36-20260925-a3660c66.json` are newer. | Manager-owned control-record refresh. Do not use its older active manifest as current lane evidence. |
| Current-head final gate is not yet terminal | The manager report says current-head merged-head proof remains open; active implementation lanes 10–13 are still recorded. | Manager-owned final gate, not a product row. Run only after active lanes stabilize, with the legal environment from `tasks/reports/legal-interop-preflight-20260925.md`. |
| Browser/live/release evidence remains absent | Web artifact `4ff99673` leaves browser proof open; battle/expedition/passive-tree rows name live proof; legal preflight says it is not live or merged-head proof. | Keep the existing browser/live/release rows open. Do not create synthetic evidence or close them from unit/CI results. |

## Blocked evidence that must stay open

- **BCU2.12:** blocked; the captured run remains below the current unresolved threshold and the generic `wither` refusal remains unresolved. It must not be called healthy from a partial run.
- **TreeBinder:** current `--check` is red because the current corpus/verdict semantics refuse or fail; this is not proof of generated-byte drift and is not fixed by P11.1r.
- **Merged-head gate:** no terminal GREEN at this report’s snapshot. The earlier post-merge report is stale after subsequent merges; rerun the fail-closed gate on the final stable integration head with the legal environment.
- **Browser:** no browser proof is claimed here. `resume-07` was abandoned without a report or evidence; fresh lane `resume-15` is active, but proof remains open until it records a real bounded run.
- **Live game/legal injector:** legal BepInEx and MelonLoader builds passed in the separate preflight with `pvzrh-3.9`, but no running-game proof is inferred. Live proof requires the owner-approved slot and normal RPG Server Debug read-back.
- **Release:** no release proof is claimed. Release/CI evidence must be read from the final terminal gate, not from this inventory.
- **Owner decisions:** rows that explicitly require an owner ruling, owner review, model spend, or content judgment remain open; this report does not answer them by inference.

## Stale records and stale evidence

The following active-looking records/branches are already ancestors of the integration ref and must not be counted as additional open implementation work or independently re-dispatched:

- `resume-00c-split-core-mapping-20260925` (accepted mapping `ff934d08`),
- `resume-01-delve-owner-20260925` (accepted Delve P1 `03d8cee8`; its residual is now owner-ruled D2.16a),
- `resume-05-vocabulary-recovery-20260925` (accepted `85d2c096`; TreeBinder remains separate),
- `combat-ai-4` / `cmdc/cai4`,
- `arch-d-20260922` / `cmdc/arch-d`,
- the four historical `rpg-simulator` idea/map/slice records already ancestral to integration.

The manager’s historical preflight counts, old convergence census, and prior merged-head report are evidence from earlier heads. They are useful context but are not current-head proof. The manager control record remains evidence for its own historical state, but its active-lane manifest is stale; current session records and exact-SHA artifacts supersede it where they conflict.

## Verification boundary for this report

This session made no implementation change, so the correct validation is read-only:

```powershell
python gk-core/scripts/audit-program-pipeline.py --only todo-task-blocks
python scripts/session-boundary-check.py --session resume-06-program-inventory-20260925
 git diff --check HEAD..features/mega-merge
```

Observed at the final read:

- census: `118` todo files, `67` nonzero, `671` open, `2885` done, `1884` boxes, `843` shaded, `2` unmeasured;
- TVB-F36 acceptance artifact: reviewed SHA `a3660c664d99c36cc33944df192ad6a2db8534ee`, merged SHA `7ca9ee8b4ade30309117525e17f3c609d4ea33ff`, `26` focused audit tests passed, and the corrected census exited `0`;
- session boundary: clean for `resume-06-program-inventory-20260925`;
- integration diff check: clean;
- only permitted local write: this report (the tracked session record was already the inventory session’s permitted record and was not edited in this pass).

The exact census command was run at the reviewed TVB-F36 SHA and the current integration classifier was replayed against the final tree; both produce the same `671/2885/1884/843/2` reading. No product test suite was run because this was an inventory-only change. Do not turn this report into a green merged-head, browser, live-game, or release claim.

## Recommended manager order

1. Let active `resume-10`, `resume-11`, `resume-12`, and `resume-13` finish within their existing fences; accept or stop each on its own evidence. Treat the accepted TVB-F36 repair as closed, not as a fifth implementation lane.
2. Complete the manager-owned `BCU2-R1` onboarding-rift reconciliation and refresh the stale manager active-lane manifest. Do not turn the contradiction into product work.
3. Repair the verification-boundary owner mapping for the candidate Data/Server paths before accepting CAI2.2 (and before accepting any lane whose path-owned verifier still reports `VERIFICATION BOUNDARY MISSING`).
4. Dispatch CAI2.2 only after the mapping repair; keep it separate from the already active build-preset, passive-tree, simulator, and persisted-steering fences.
5. On a stable integration head, run the fail-closed merged-head gate with the legal preflight environment, then separately perform browser and live-game proof. Only a terminal GREEN and real read-back can move the corresponding blocked rows.

<<<REPORT {"status":"done","snapshot":{"branch":"features/mega-merge","sha":"5bc4964725a56ff013d1742b298d03e69a04ed92","date":"2026-09-25T09:59:03+07:00","subject":"merge: record fresh browser QA spawn"},"census":{"todo_files":118,"nonzero_programs":67,"open_task_blocks":671,"done_task_blocks":2885,"unticked_boxes":1884,"shaded_boxes":843,"unmeasured_files":2},"genuine_open_total":"not published; TVB-F36 removed 27 classifier false positives, while BCU2-R1, contradictory ledgers, stale/out-of-fence rows, and unmeasured files remain","queue":{"active":["resume-10-delve-persisted-steering-20260925","resume-11-build-preset-bp1112-20260925","resume-12-passive-tree-p11-1r-20260925","resume-13-rpg-simulator-rsf27-20260925","resume-15-web-browser-qa-20260925"],"queued":["combat-ai CAI2.2 after Data/Server verification-boundary owner mapping repair"],"accepted_and_merged":["TVB-F36 at reviewed a3660c664d99c36cc33944df192ad6a2db8534ee, merged 7ca9ee8b4ade30309117525e17f3c609d4ea33ff"],"abandoned_or_released":["resume-07-web-browser-qa-20260925 without browser evidence","resume-08-passive-tree-binder predecessor after accepted parity repair"]},"changed_files":["tasks/reports/resume-06-program-inventory-20260925.md"],"verification":["TVB-F36 artifact .claude/cmdc-agents/acceptance/resume-14-tvb-f36-20260925-a3660c66.json: 26 focused audit tests passed; exact census exit 0","python gk-core/scripts/audit-program-pipeline.py --only todo-task-blocks at reviewed TVB-F36 SHA: open=671 done=2885 boxes=1884 shaded=843 unmeasured=2","current integration classifier replay at 5bc4964725a56ff013d1742b298d03e69a04ed92: same 671/2885/1884/843/2 reading",".\\scripts\\session-boundary-check.py --session resume-06-program-inventory-20260925 — clean","git diff --check HEAD..features/mega-merge — clean"],"open_issues":["exact genuine open count remains blocked by BCU2-R1, contradictory ledgers, stale/out-of-fence rows, and two unmeasured todo files","CAI2.2 remains queued until the Data/Server verification-boundary owner mapping is repaired","BCU2.12 remains paused; TreeBinder --check remains a separate red binder/resolver diagnosis","current-head fail-closed post-merge gate has no terminal GREEN at this snapshot","browser lane resume-15 is active; browser, live-game, and release evidence are not yet complete","manager control record active-lane manifest is stale relative to current session records and acceptance artifacts"],"next_steps":["let resume-10, resume-11, resume-12, resume-13, and resume-15 finish or stop on their own evidence","complete BCU2-R1 and refresh the manager control record without ticking implementation rows","repair the Data/Server verification-boundary mapping, then dispatch CAI2.2","run the fail-closed merged-head gate with the legal preflight environment","perform browser, live-game, and release proof separately; do not infer one from another"]} REPORT>>>
