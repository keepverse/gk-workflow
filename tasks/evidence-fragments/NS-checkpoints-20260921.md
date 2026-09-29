# NS checkpoints + wave-5 status errata (2026-09-21) — no code

The deliverable IS the doc (spec status lines, a gate-status paragraph, two checkpoint lines, the parent
CC7 row). Each claim below was checked in this session, on the merged head.

| Claim | Command | Result |
|---|---|---|
| `WorldStage.tsx` holds no notification state (Checkpoint 5 line 2) | `grep -c "notifyItems" gk-web/web/fusion-rpg-web/src/stages/world/WorldStage.tsx` | `0`; the stage renders `useNotificationFeed` → `railItemsFrom` → `worldLatestTurn` (`WorldStage.tsx:52-54`, `:153`, `:159`) |
| `stages/world/notify/` holds only the translator, the debt adapter and their tests (Checkpoint 5 line 2) | `ls gk-web/web/fusion-rpg-web/src/stages/world/notify/` | `legacyCaptureLoss.test.ts legacyCaptureLoss.ts worldTranslator.test.ts worldTranslator.ts` — exactly those four |
| Catalog: both hosts name the same version (Checkpoint 5 line 3 / Checkpoint 6 line 3) | `sed -n '417p' gk-core/src/FusionRpg.Server/Program.cs`; `sed -n '4p' gk-web/web/fusion-rpg-web/src/shell/notify/catalog.ts` | both `notification-catalog.v3.json` (v3 since NS6.4's H7 bump; the check asks for the same `vN`, not for v2 specifically) |
| `WorldTurnReportFogTests` unmodified and green (Checkpoint 5 line 1, fog half) | NS5.2's own run | `Passed! 5/5` with `git status` empty on the test file — unchanged |
| spec prose that said the module was still gated | — | fixed: `spec-world-notify-source.md` header (A1/A2 accepted 2026-09-21, wave 5 built, G2 blocked on the missing world-creation route), `spec-notify-client.md` (the rail move landed), the map's module-7 row, and a new gate-status paragraph under the map's Gates table |
| citations must not regress | `powershell -NoProfile -Command ".\scripts\guard-doc-citations.ps1 -Strict"` | `D1 19 HIGH · D2 1 HIGH · D3 1 HIGH` — **0 inside this lane's fence**; each remaining one is filed with its owner (`notification-ssot-ideal.md` → NS-fence-1, npc-story-events → DOC-NS5.7, trade-network → DOC-NS5.7, legion-build → DOC-NS5.2, world-stage `spec-world-notify.md` → WS-cite-1) |

**NOT proved:** nothing here is a build or test result — no code changed. The two checkpoint lines that
stay unticked are unticked on purpose: NS5.13 (G2) is blocked on the missing real world-creation route,
and the full suite is `not_run` (killed twice with no output).

## Anchor and manager-report rows (same commit)

| Claim | Command | Result |
|---|---|---|
| the anchor's queue state matches the todo | `grep -cE "^- \[ \]" tasks/notification-ssot-todo.md`; `grep -cE "^- \[x\]" tasks/notification-ssot-todo.md` | `13` open / `72` done — the anchor now names the nine task rows with their blocker, keeps `✓`/`withdrawn` markers on the rest, and its `Next:` no longer says `NS0.1` (answered 2026-09-21) |
| the manager's report carries this program's current counts | the same two counts | its §1 row and its per-program table now read `13 / 72` (was `26 / 55`), with the lane note `ns-1 — waves 0–6 landed; G2 blocked on WS-live-1, centre gated` |

## Follow-ups on the errata commit (same lane, next commit)

| Claim | Command | Result |
|---|---|---|
| the volume-row requirement now sits in the owning program's queue | `tail -8 tasks/world-stage-todo.md` | **WS-vol-1** added: `world-stage-map.md`'s rail row still claims an End Turn flush; ask A1's own terms include replacing it with the `worldLatestTurn` reason, which NS5.11 may not edit from this lane |
| the FE-boundary finding is carried by its owner | `grep -n "TVB-F1" tasks/test-verification-boundary-todo.md` | `tasks/test-verification-boundary-todo.md:406` carries the same finding, so `NS-fence-3` is marked **ROUTED** rather than left as a duplicate |
| citations: 0 HIGH inside this lane's fence | `powershell -NoProfile -Command ".\scripts\guard-doc-citations.ps1 -Strict"` | `D1 18 HIGH · D2 1 · D3 1` — none in this program's files (the last in-fence one needed the "GONE" marker on the *same line* as the citation, which the audit's own exemption requires) |
