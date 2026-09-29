# CC5 — Empire progression live (plan line 150)

Verdict: **PARTIAL.** The merged half (EP1.1–EP1.19: priced unique/commander respec) is proven live
end to end, including through the browser. Empire level, earned free respecs and creature commanders
are **not in the merged tree** (EP3/EP4 unmerged), so those cannot be probed.

| Criterion | Command / ids | Executed result | Scope |
|---|---|---|---|
| Real specimen created through the real route | `POST /api/unique/actors {"playerId":1,"side":"plant","typeId":0}` | `instanceId=bd9fccd28d514555a50ad5c815398c2b`, Lv 1 → XP route → Lv 6, budget 30 | rpg-server-debug |
| Addition is free | `POST /api/aptitudes/unique/allocate {"shares":{"Might":10}}` | `priced=false priceAmount=0`, souls unchanged 130; GET reads back `spent=10 Might=10 isDefault=false` | rpg-server-debug |
| Priced unique respec charges through PriceOf | `POST /api/aptitudes/unique/allocate {"shares":{"Might":5},"correlationId":"qa-cc5-unique-1"}` | `priced=true priceAmount=50 respecCount=1 soulBalance=80`; ledger id 131 `-50 reason=respec-unique refId=qa-cc5-unique-1`; GET reads back `Might=5` | rpg-server-debug |
| Respec quote preview | `POST /api/aptitudes/respec-quote {"scope":"unique",...}` | `{"isRespec":true,"soulPrice":50,"respecCount":0}` | rpg-server-debug |
| Priced commander respec (API) | `POST /api/aptitudes/allocate {"playerId":1,"shares":{"Might":1},"correlationId":"qa-cc5-commander-1"}` | addition free (souls 80); take-back `priced=true priceAmount=50 soulBalance=30`; GET reads back `Might=1` | rpg-server-debug |
| Priced commander respec (WEB, real browser) | playwright: Commanders → Crazy Dave → sheet → Aptitudes → Might 1→0 → Confirm | toast **"Respec cost — Taking points back costs 75 souls."**; API read-back souls 85→10, ledger `-75 reason=respec-commander`; GET `Might=0` | web + rpg-server-debug |
| Soul balance is real play income | `POST /api/debug/kill` on live zombies (Game Injector Debug trigger) | each kill credits `reason=kill` via the real activity-fact path (earnedTotal 130) | game-injector-debug → rpg-server-debug |
| Web visibility | `#/sanctum`, `#/sanctum` Commanders sheet | sanctum shows `✦ 30` souls and specimen `#bd9fcc Lv 6`; aptitudes tab shows `Scope: Commander · Ladder 7`, `Leftover 20 · 1/21` | web |

Screenshots: `cc5-sanctum.png`, `cc5-commander-aptitudes.png`, `cc5-web-respec-toast.png`.

**Not implemented on this branch (not a probe failure — absent code):** no `EmpireLevelGrants.cs`, no
`RpgActorKinds.Empire` (5 members, no `empire`), no `xpCurve.empire` in `gk-core/data/tuning/progression.v2.json`;
no `CommanderRole`/`ICommanderRoster`/`rpg_commander_role`. `tasks/empire-progression-todo.md`:
19/68 tasks ticked (EP1.1–EP1.19 only); CP2/CP4/CP5/CP6 unchecked. The plan's "EP CP1–CP6 merged"
premise does not hold for EP3/EP4.

Falsified by: a respec returning `priced:false`/0, a soul balance that did not drop, or no
`respec-*` ledger row.
