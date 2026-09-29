# NS5.4 — Web world translator + the `supply.besieged` playback row (ask A6)

| Criterion | Command | Result |
|---|---|---|
| `worldTranslator.ts` (domain `world`) is the one reader of the entry token, body via `describePlaybackEntry`, title from the catalog `displayName`, `target` = sector ref; `samples()` for `world.turn-entry` (one per mapped prefix) and `world.release-forecast` | `cd web\fusion-rpg-web; npx vitest run src/stages/world/notify/worldTranslator.test.ts` | `Test Files 1 passed, Tests 10 passed` |
| `playbackTable.ts` gains the `supply.besieged` row beside `supply.cut`; registered in `translators.ts`; no raw token reaches rendered output | `npx vitest run src/stages/world/playbackTable.test.ts src/shell/notify/format` | `Test Files 6 passed, Tests 63 passed` (inventory count reviewed 22->23, a real reviewed addition per DESIGN-GATE §3 rule 7, not a drift) |
| `npm run build` | `cd web\fusion-rpg-web; npm run build` | `✓ built in 24.48s`, no TS errors |

`samples("world.turn-entry")` covers all 15 of the classifier's mapped prefixes (not just the 8
categories), so a deleted/renamed `playbackTable.ts` row breaks this translator's own test, not
only the coarser per-category coverage guard. The domainToken wire convention this translator
owns (a plain `{kind,subject,detail,sectorId}` object, not a double-encoded string) is documented
in the file — `WorldReportNotificationSource` (NS5.3, blocked on A2) must build its draft the same
way when it lands.
