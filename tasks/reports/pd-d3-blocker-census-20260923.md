# Evidence — blocker census completed: F4, F5, F6, F9, F10 (lane `pd-d3`, 2026-09-23)

No code. Five rows that carried a reading, a guess, or nothing now name a blocker of exactly the three
kinds the manager accepts: a path outside the fence, a specific owner ruling, or a named dependency row.

| Row | Printed / read evidence | Blocker now named as |
|---|---|---|
| **F4** | `grep -n Level gk-core/src/FusionRpg.Contracts/CreatureDtos.cs` → nothing; the class's ten fields unchanged | `gk-core/src/FusionRpg.Contracts/**` outside the fence + creature-core's own DTO decision |
| **F5** | `grep -rn poolFilter gk-core/src/FusionRpg.Core/Creatures/SummonRoller.cs` → nothing; `gk-core/data/tuning/dungeon.v3.json:479` still `"poolFromDomain": false` | creature-summoning's public API **and** a `gk-core/data/tuning/**` publish (both outside the fence) — without the publish the feature stays inert |
| **F6** | schema declares `obstacleVerbs` 3× (`structures/anchor/schema.py`); the corpus emits it (`gk-data/packs/fusion/data/seed/structures/bank/reliquary.json` etc.); `grep -rn obstacleVerbs src --include=*.cs` → **0 hits**; no `structure` table in `gk-core/src/FusionRpg.Data/Sqlite/**`; `RoomObjectBuilder.For` has no production caller (its only mention in `VerbResolver.cs:48` is a doc comment) | NAMED DEPENDENCY ROW — `delve-stage` (Phase 5), the same one D4.13 carries. Its previous "not independently re-verified this pass" guess is replaced by this reading |
| **F9** | the three sites are `gk-web/web/fusion-rpg-web/src/layers/commanders/CommandersLayer.tsx` and `gk-web/web/fusion-rpg-web/src/ui/actor/CommanderSheetFooter.tsx`; the guard that would prove a fix is `gk-web/web/fusion-rpg-web/src/ui/disabledReasonGuard.test.ts` | `web/**` outside the fence (both the fix and its vitest proof) |
| **F10** | `gk-core/data/tuning/contracts.v1.json` carries `baseUpkeepPerDay` keyed by the ten-rung rarity ladder; every other contract price in that file is Θ-scaled | the `creature-contracts` owner's design ruling + a `data/tuning/contracts.v{n+1}.json` publish (outside the fence) |

**NOT proved**

- Nothing was fixed: every row above remains `[ ]`, and every one of the five needs something this lane
  cannot touch. This commit is the register, not a change.
- F6's conclusion is a reading of absence (`0 hits` in `src/**`, no `structure` table), not a proof that
  no consumer could exist under another name; the two greps are quoted in the row so a reader can re-run
  them.
- F9's three violations were NOT re-run: the guard is a vitest suite under `web/**`, and running the FE
  suite is outside this lane's verification boundary. The row's own file:line citations are unchanged.
- F10's Θ curve shape is not proposed: what upkeep reads (highest cleared content Θ, per the row's own
  title) is the contracts owner's call, and a shape invented here would be a balance decision by an
  assistant — the thing the tunables SSOT exists to prevent.

**Census after this pass:** of the program's open rows, every one now names an exact blocker —
`delve-stage`/Phase 5 (D4.13, F6), F15 (D4.30, D4.31), `npc-story-events`' `delve-live-start`/`delve-live-rooms`
(D4.14, PD-B1, and D4.32's owner ruling), combat-ai `CAI3.5` (D2.16, D5.11), the manager's pooled proof
(F13), or another program's own row plus a `tools/**`/`data/**`/`web/**`/`gk-core/src/FusionRpg.Contracts` path
(F1-closed's successor F15, F2, F4, F5, F8, F9, F10, F11, D3.31).
