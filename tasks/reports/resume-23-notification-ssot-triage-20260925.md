# Resume 23 — notification-ssot dependency triage

**Date:** 2026-09-25
**Scope:** read-only dependency triage. No product, FE, world, generated-data, tuning, CI, or ledger changes.

## Verdict

There is **no notification-ssot product row that is genuinely buildable now**. The next
implementation row is conditional, not cleared: **NS6.11** can start only after the delegated
`gui-lego` piece review is accepted and dated. **NS5.13** remains a real external/live gate: it needs
a production world-creation path and an authored starvation scenario, then a real live probe. Do not
turn either blocked row into a debug-fabricated proof.

The smallest safe fanout is therefore:

1. **No implementation fanout now.** Keep the centre and the live probe closed.
2. After the piece review, dispatch **NS6.11 as one cohesive FE slice**; do not split its surface,
   Chronicle mount, and designed-state contract across competing lanes.
3. Treat **NS6.12** as sequential follow-up after NS6.11. Treat the world-creation work as a
   separate `world-continuity` dependency, not a notification-ssot implementation.

## Current reading

The required census was run in this worktree:

```text
python gk-core/scripts/audit-program-pipeline.py --only todo-task-blocks
# notification-ssot | R-bold | open blocks=5 | done blocks=63 | unticked boxes=9 | shaded=0
```

The five open task blocks are `NS5.13`, `NS6.8`, `NS6.11`, `NS6.12`, and `NS-fence-4`
(`tasks/notification-ssot-todo.md:346-357,405-439,473-487`). The census is a task-block reading,
not a claim that every open row is executable.

The older anchor and plan are stale on one point: they still describe **NS5.11** as blocked
(`tasks/notification-ssot-anchor.md:10-20`; `tasks/notification-ssot-plan.md:108-113`), while the
current todo marks it complete and records the world-stage volume-row handoff as landed
(`tasks/notification-ssot-todo.md:334-338`; `tasks/world-stage-todo.md:4277-4286`). Use the current
row plus its evidence, not the stale anchor, when dispatching work.

Current code checks agree with the blocked-row reading:

- `git grep -n -E "WorldCreationService|/api/world/begin|world/begin" -- gk-core/src/FusionRpg.Server gk-core/src/FusionRpg.Core gk-core/src/FusionRpg.Data` returned no matches.
- `git grep -n "CreateWorld(" -- gk-core/src/FusionRpg.Server` returned only `gk-core/src/FusionRpg.Server/WorldEndpoints.cs:602`, the SIM-only route. The route itself is documented as SIM-only at `WorldEndpoints.cs:585-610`.
- `Test-Path` returned `False` for both `web/fusion-rpg-web/src/features/notices/NoticesSurface.tsx` and `NoticesSurface.test.tsx`.
- `ChronicleLayer.tsx:7-11` still has only Runs, Growth, and Fusion sheet tabs; the current volume matrix has no Notification-centre row (`gk-web/web/fusion-rpg-web/src/ui/volumeMatrix.test.ts:15-127`), and the current e2e volume file contains the Creatures fixture only (`gk-web/web/fusion-rpg-web/e2e/volume-fixtures.spec.ts:62-160`).

## Coordination asks and their actual disposition

| Ask | Recorded disposition | Consequence |
|---|---|---|
| A1: relocate `world-notify` and widen the category vocabulary | **Accepted 2026-09-21** (`notification-ssot-map.md:197-204`; `notification-ssot-todo.md:25-29`) | NS5.7–NS5.11 landed. It does not clear the centre or the live probe. |
| A2: move the fog rule to Core | **Accepted 2026-09-21** (`notification-ssot-map.md:199-204`; `notification-ssot-todo.md:31-35`) | NS5.2/NS5.3 landed. It does not supply a production world. |
| A3: add `claim.lost:` with the previous owner as audience | **Declined; default applied** (`notification-ssot-map.md:201`; `notification-ssot-todo.md:37-41`) | NS7.3 is withdrawn; the named web debt adapter remains. |
| A4: add an audience to `legion.starved:` | **Declined; default applied** (`notification-ssot-map.md:202`; `notification-ssot-todo.md:43-47`) | NS7.4 is withdrawn; that report line stays unmapped. |
| A5: add read-only cache-decay reads | **Accepted/default applied** (`notification-ssot-map.md:203`; `notification-ssot-todo.md:49-53`) | NS6.1–NS6.5 landed. No centre or live probe dependency remains here. |
| A6: add the `supply.besieged` playback row | **Accepted/default applied** (`notification-ssot-map.md:204`; `notification-ssot-todo.md:55-59`) | NS5.4 landed. |

The two non-A1–A6 coordination gates are different:

- **Production world creation is external.** The world-continuity spec owns a
  `WorldCreationService` and `POST /api/world/begin`, and says the only current caller is the SIM
  route (`docs/architecture/world-continuity/spec-world-creation.md:18-25,38-48,71-84`). Its own
  test plan names `WorldContinuityRulesTests.cs`, `WorldStoreTests.cs`, and
  `WorldCreationEndpointTests.cs` (`.../spec-world-creation.md:256-270`). The current tree has no
  `tasks/world-continuity-*` plan/todo files and no such service/route in `src/`. This is an
  external program dependency, not a notification-ssot row that can be unblocked here.
- **The piece review is still owner/gui-lego-gated.** The queue row exists and was owner-added on
  2026-09-23 (`docs/architecture/gui-lego/menu-refactor-queue.md:21-24`;
  `tasks/notification-ssot-todo.md:405-409`), but the review artifact is explicitly
  `pending-resolver-acceptance`, and criterion 5 says React waits for the dated acceptance
  (`docs/design/gui-lego/recipes/notices.ACCEPTANCE.md:1-9,21-29`). The centre spec also says the
  step-7 review is before React (`docs/architecture/notification-ssot/spec-notify-centre.md:58-88`).
  A queue row is not the piece review. The manager handoff line saying the dependency is “already
  met” (`tasks/run-board-20260920.md:784-788`) conflicts with the authoritative acceptance artifact;
  this triage keeps NS6.11/NS6.12 gated rather than silently treating that line as owner acceptance.

## Row-by-row disposition

### `NS6.8` — recipe half complete, review still owner-gated

This is not a React row and there is no safe implementation remaining in it. The recipe, assembled
surface, new `notice-row` piece draft, piece contract, and review checkpoint already exist:

- `docs/design/gui-lego/recipes/notices.json`
- `docs/design/gui-lego/recipes/notices.ACCEPTANCE.md`
- `docs/design/gui-lego/surfaces/notices.html`
- `docs/design/gui-lego/pieces/notice-row.html`
- `docs/architecture/gui-lego/spec-notice-row.md`
- `docs/architecture/gui-lego/menu-refactor-queue.md`

The todo’s `recipes/notices.html` wording is stale after the recorded move to `surfaces/`; use the
current acceptance file and actual paths above. The prescribed recipe/schema check is
`cd web\fusion-rpg-web; npx vitest run src/features/gui-lego`; it is not a substitute for the
resolver’s acceptance. The remaining act is an external dated review of piece boundaries,
payloads, and the assembled look (`notices.ACCEPTANCE.md:31-53`).

### `NS6.11` — first conditional implementation row, not buildable yet

Once the resolver’s dated acceptance exists, this is the smallest safe product slice. Keep it as
one FE lane because the surface, host tab, designed states, and selection persistence form one
contract. The row’s exact paths are:

- `web/fusion-rpg-web/src/features/notices/NoticesSurface.tsx`
- `web/fusion-rpg-web/src/features/notices/NoticesSurface.test.tsx`
- `gk-web/web/fusion-rpg-web/src/layers/chronicle/ChronicleLayer.tsx`
- `gk-web/web/fusion-rpg-web/src/i18n/locales` (Lingui extract output)

The prescribed checks are:

```text
cd web\fusion-rpg-web
npm test -- layers/chronicle features/notices shell/notify
npm run build
npm run extract
```

The row must consume the already-built `foldNoticesVm`, closed bus, and history hook; it must not
fetch or read SignalR inside a piece, add a route/rail entry, or create a new layer. Those boundaries
are in `spec-notify-centre.md:58-88,162-169` and the GUI Lego decision is in
`docs/architecture/decisions.md:131-131`. `NS6.9` and `NS6.10` are already done
(`notification-ssot-todo.md:417-426`), so they are not additional fanout work.

### `NS6.12` — sequential after NS6.11, also owner-gated

Do not start this alongside the React surface. It needs the real centre DOM to measure. Exact paths
are:

- `gk-web/web/fusion-rpg-web/src/ui/volumeMatrix.test.ts`
- `gk-web/web/fusion-rpg-web/e2e/volume-fixtures.spec.ts`

Prescribed checks:

```text
cd web\fusion-rpg-web
npm test -- ui/volumeMatrix
npm run test:e2e -- volume-fixtures
```

The required centre strategy is `virtualize`, with a fixture at 10/100/1000 rows
(`notification-ssot-todo.md:435-439`; `spec-notify-centre.md:97-107,148-160`). The current volume
file has only the Creatures fixture, so this row is not a safe standalone fanout.

### `NS5.13` and `NS-fence-4` — live proof blocked externally

There is no notification product file for this row. The evidence/runbook paths are
`tasks/notification-ssot-probe-runbook.md` and `tasks/evidence-fragments/NS5.13.md`; the live action
must use a real product creation route, a real commit, the normal notification read-back, and the
real screen (`spec-world-notify-source.md:271-274`; `notification-ssot-probe-runbook.md:20-59`).

Two prerequisites are still missing:

1. The production route and its world-continuity implementation are not in this tree. The only
   current `CreateWorld` caller is the SIM route (`WorldEndpoints.cs:585-610`), and the spec assigns
   the production service/route to world-continuity (`spec-world-creation.md:18-25,57-84`).
2. The probe needs an **authored** starvation scenario. The recorded measurements found no
   `loam.shortfall` in 25 real turns and no player command path to produce one on the shipped
   template (`notification-ssot-probe-runbook.md:10-18`;
   `tasks/evidence-fragments/NS5.13.md:132-159`). A route alone is not enough.

The live-probe standard requires a real subject, real operation, persistence/read-back through the
normal path, and a separate live-engine check where applicable
(`docs/contributing/live-probe-standard.md:41-72,161-178`). The existing in-process `NS5.12` and
`NS6.5` results are useful chain evidence, but they do not satisfy G2’s live acceptance. Do not use
`/api/test/world/create` or a debug fabricator to close the row.

## Smallest safe fanout

### Now

Dispatch no notification implementation worker. The safe parallel work is read-only coordination:

- `gui-lego` resolver reviews the existing artefacts and records a dated acceptance.
- `world-continuity`/manager confirms the production creation path and the authored scenario owner;
  this is outside notification-ssot’s boundary.

Those are independent handoffs, but neither authorizes a UI or world change in this report’s lane.

### After the gates

- **NS6.11 alone** is the first notification product fanout slice, using the four paths and three
  commands listed above.
- **NS6.12 follows NS6.11**; it must observe the shipped centre, not a parallel mock.
- **NS5.13 follows both external prerequisites** and is a separate live-evidence lane using the
  runbook. It is not a substitute for NS6.11 and must not be faked with server/unit evidence.

## Owner questions still open

1. **Gui-lego resolver:** accept or amend `notice-row`’s field set, the four designed states, and
   the assembled look; record the acceptance date in the recipe or queue row. Until then NS6.11
   remains explicitly owner-gated.
2. **World-continuity owner/program:** when will the production `WorldCreationService` and
   `POST /api/world/begin` path land, with the spec’s stamp/replay dependencies satisfied? The
   notification lane cannot substitute the SIM route.
3. **Owner/manager:** provide an authored starvation scenario (or explicitly reword G2’s
   acceptance). The current shipped world has no probe-scale path to `loam.shortfall`.
4. **Manager:** reconcile the stale anchor/plan/run-board status lines above without changing the
   authoritative owner-gated state. The full-suite line for NS5.13 also needs the program’s normal
   final-checkpoint disposition; it is not a reason to run a live proof now.

No UI, world behavior, generated data, tuning, CI, or ledger was changed by this triage.

<<<REPORT {"status":"done","summary":"Triage complete: no notification-ssot product row is buildable now. NS6.11 is the first conditional FE slice after a dated gui-lego piece review; NS6.12 follows it. NS5.13 remains blocked on the external production world-creation path, an authored starvation scenario, and a real live probe. Current code and coordination records were re-read; no product or UI/world behavior was implemented.","changed_files":["tasks/reports/resume-23-notification-ssot-triage-20260925.md"],"verification":["python gk-core/scripts/audit-program-pipeline.py --only todo-task-blocks — notification-ssot open blocks=5, done blocks=63, unticked boxes=9, shaded=0","git grep -n -E \"WorldCreationService|/api/world/begin|world/begin\" -- gk-core/src/FusionRpg.Server gk-core/src/FusionRpg.Core gk-core/src/FusionRpg.Data — no matches","git grep -n \"CreateWorld(\" -- gk-core/src/FusionRpg.Server — only gk-core/src/FusionRpg.Server/WorldEndpoints.cs:602","$paths | ForEach-Object { \"$_ : $(Test-Path $_)\" } for NoticesSurface.tsx and NoticesSurface.test.tsx — both False","Get-ChildItem -Path tasks -Filter 'world-continuity-*' -Name — no files","git diff --check — exit 0; git diff --no-index --check -- /dev/null tasks/reports/resume-23-notification-ssot-triage-20260925.md — no whitespace diagnostics (the command's exit 1 is the expected diff result for an untracked file)"],"open_issues":["gui-lego piece review is not dated; NS6.11/NS6.12 remain owner-gated","production world creation is not present; world-continuity owns the route","no authored starvation scenario is available for NS5.13","NS5.13 live proof and the stale coordination records remain open"],"next_steps":["obtain dated gui-lego acceptance, then dispatch NS6.11 as one FE slice","after NS6.11, run NS6.12 volume verification","after both NS5.13 prerequisites exist, run the real live probe and record read-back/evidence"]} REPORT>>>
