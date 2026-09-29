# SE4.25 — Ownership predicate at the last two sites, and kill credit by `EmpireRef`

Spec: save-identity, "One ownership predicate" (last two sites) + kill-credit `EmpireRef`.
`IsOwnedUniqueSourceUnlocked` (`RpgStore.cs`) and `ItemEquipEndpoints.TryResolveSpecimen`
(`:345`) now call `OwnsSpecimenUnlocked`/the new public `RpgStore.OwnsSpecimen`.
`ResolveLawnKillCreditPlayerUnlocked` → `ResolveLawnKillCreditUnlocked` returns the killer's
`EmpireRef`; a non-human killer earns no kill souls, logged (`[souls] non-human kill credit
skipped...`), ingest never throws.

**Real regression found and fixed in this commit**: wiring `OwnsSpecimen` into the real
`ItemEquipEndpoints` host broke 19/33 `ItemEquipEndpointsTests` — `CreateUniqueActor` and
`EnsureUniqueActorForAudit` (`RpgStore.UniqueActors.cs`) predate the `empire_id` column and never
stamped it, so every specimen they mint read NULL and failed `OwnsSpecimenUnlocked`'s own
"NULL never matches" rule (SE4.14) even for its rightful owner. Both now stamp `HumanEmpireOfOrNull`,
matching `MintCreatureUnlocked`'s SE4.14 default — the only other `INSERT INTO rpg_unique_actors` site.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| Species XP from a specimen source uses the predicate; Zomboss claim untrusted | `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~SpecimenOwnership" --nologo` | pass 20/20 (11 SE4.24 + 2 new: Zomboss claim downgraded, human claim trusted — the falsifier) | `RpgStore.cs` (`IsOwnedUniqueSourceUnlocked`) |
| Item equip uses the predicate; Zomboss specimen refused | `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~ItemEquipEndpointsTests" --nologo` | pass 33/33 (32 existing + 1 new: same-save Zomboss specimen → `equip.specimen-not-owned`, table unchanged) | `ItemEquipEndpoints.cs`, `RpgStore.SaveEmpires.cs` (`OwnsSpecimen`) |
| Kill credit returns `EmpireRef`; non-human killer earns no souls, never throws | `dotnet test tests\FusionRpg.Data.Tests --filter "FullyQualifiedName~LawnKillSoulCredit" --nologo` | pass 4/4 (3 existing unchanged + 1 new: Zomboss-empire killer, `Record.Exception` null, run-owner balance unchanged) | `RpgStore.Souls.cs` |
| Regression: CreateUniqueActor/EnsureUniqueActorForAudit consumers | 11 Data.Tests files (`--filter "...Action|Contract|CorpseCache|LawnDeath|Permadeath|ItemGrant|Relic|SpecimenMaterialised|StoragePurge|UniqueActor|UniqueEquipment..."`); 8 Server.Tests files | pass 117/117 (Data); pass 78/79 + 11/11 isolated (Server — the one failure was a transient Kestrel port-bind `SocketException`, confirmed non-reproducing in isolation, unrelated to this change) | — |
| Guards | `.\scripts\guard-dal.ps1`; `python gk-core/scripts/guard-test-substrate.py` | pass — DAL OK; substrate OK | — |
