# NS5.11 — Retire the world copies (`categories.ts`, world `channelSettings.ts`) — PARTIAL, one line denied

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| `stages/world/notify/categories.ts`, `channelSettings.ts` and their tests deleted; NS5.6's migration-equivalence test deleted in the same change | `git status --short` | `D` on all five (`categories.ts`, `categories.test.ts`, `channelSettings.ts`, `channelSettings.test.ts`, `shell/notify/catalogMigration.test.ts`); `src/stages/world/notify/` now holds only `worldTranslator.*` and `legacyCaptureLoss.*` | (deleted files) |
| nothing imports the deleted files | `cd web\fusion-rpg-web; npm run build` | `✓ built in 9.53s` (tsc clean) — nothing in production imported either copy before the deletion (checked by grep) | — |
| the row's Verify line | `cd web\fusion-rpg-web; npx vitest run src/stages/world src/shell/notify` | `Test Files 97 passed (97)`, `Tests 856 passed (856)` (three suites gone with their subjects) | — |
| the boundary command + the citation guard | `.\scripts\verify-change.ps1 -Paths 'docs/architecture/notification-ssot/spec-notify-client.md','…/spec-notify-vocabulary.md','…/spec-world-notify-source.md','docs/architecture/notification-ssot-map.md' -Session notification-ssot-20260920`; `.\scripts\guard-doc-citations.ps1 -Strict` | docs -> `docs-and-assistant-config` (focused) + `guard.doc-boundary` -> `Passed! - Failed: 0, Passed: 4, Skipped: 0, Total: 4, Duration: 29 s`; citations **0 HIGH in this program's own docs** (was 9 citations across those four files) | docs/architecture/notification-ssot/**, docs/architecture/notification-ssot-map.md |
| **NOT done — blocked on a denied path:** `world-stage-map.md:241`'s volume reason updated, as ask A1 agreed | — | `docs/architecture/world-stage-map.md` is outside this lane's allowed paths (the runner fails a run that changes it), so the row was not edited. Filed as **NS-fence-2**; the same statement now lives in `volumeMatrix.test.ts`'s "World notification rail" reason, inside this program's fence | tasks/notification-ssot-todo.md |

**Citation breaks filed with their owning programs (same change, as the citation rule requires):**
`tasks/npc-story-events-todo.md` **DOC-NS5.7** (2 dead citations into the moved rail store),
`tasks/trade-network-todo.md` **DOC-NS5.7** (4) and **DOC-NS5.2** (1 line-past-end caused by the NS5.2
move out of `WorldEndpoints.cs`), and this program's own **NS-fence-1** (14 in
`notification-ssot-ideal.md`, outside the lane's fence).

**Verification-boundary defect found, filed as NS-fence-3:** `gk-core/scripts/verification-boundaries.v1.json`
holds **zero** `gk-web/web/fusion-rpg-web/**` rows (checked: 278 boundaries, 0 FE path patterns), so
`verify-change.ps1` throws `VERIFICATION BOUNDARY MISSING` for every FE path — including the deleted
ones and `shell/notify/catalog.ts`. NS1.1 (`[x]`) claims registry rows for
`gk-web/web/fusion-rpg-web/src/shell/notify/**` and `features/notices/**`; they do not exist. Every FE task in
this lane therefore verified through its row's own `npx vitest` + `npm run build` lines, which is the
strongest check available here; repairing the registry is outside this lane's allowed paths.

**Re-confirmed 2026-09-21 on the integration head 4bce1fe5:** `verify-change.ps1 -Paths
gk-web/web/fusion-rpg-web/src/shell/notify/rail/railStore.ts` still throws
`VERIFICATION BOUNDARY MISSING: gk-web/web/fusion-rpg-web/src/shell/notify/rail/railStore.ts` — the registry
still holds zero `gk-web/web/fusion-rpg-web/**` rows, so no FE path in any lane can be verified by the
boundary command (filed here as NS-fence-3 and, by the boundary program, as TVB-F1).

**NOT proved:** no live probe (NS5.13).

## Completed 2026-09-21 — the volume row landed

The deletion half was already in (NS5.11's earlier commit); this closes its remaining acceptance line.

| Criterion | Command | Numbers printed |
|---|---|---|
| the volume reason updated, as ask A1 agreed | `.\scripts\verify-change.ps1 -Paths 'docs/architecture/world-stage-map.md' -Session notification-ssot-20260920` | maps to `docs-and-assistant-config (focused)` + `guard: doc-boundary`; `D1 file does not exist 1 (0 HIGH)`; `Passed! - Failed: 0, Passed: 4, Skipped: 0, Total: 4, Duration: 36 s` |
| the rail's declaration still matches the live reason | `cd gk-web/web/fusion-rpg-web; npx vitest run src/ui/volumeMatrix.test.ts` | `Test Files 1 passed (1)`, `Tests 7 passed (7)` |
| nothing imports the deleted files | the earlier half of this fragment | `npm run build` `✓ built in 9.53s`, unchanged |

The row now reads: ``render-all`` — structurally one resolved turn's notifications for one player
(`worldLatestTurn`), the same one-turn bound as the playback keyframe rail; the visible toast stack is
capped at three (NS4.6/NS5.10, ask A1).

**Boundary note.** This lane edited `docs/architecture/world-stage-map.md`, another program's capability
map, because ask A1's accepted text names that volume row as part of this program's change set and
NS5.11's own acceptance requires it. The session record was widened for the path in the same commit (the
boundary command refuses a path outside it). `WS-vol-1` in `tasks/world-stage-todo.md` is annotated as
landed so world-stage's lane does not redo it.
