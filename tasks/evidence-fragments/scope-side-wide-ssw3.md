# scope-side-wide SSW3 — the boundary the key deliberately does not cross

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| A `plant:*` / `zombie:*` grant matches NO event | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~StatApplyScope"` | PASS — 10/10, 0 failed; `The_trigger_gate_refuses_a_side_wide_key_while_match_and_type_keys_still_fire` | `gk-core/tests/FusionRpg.Core.Tests/Scope/StatApplyScopeSideWideTests.cs` |
| Non-vacuity control (same event object) | same run | PASS — the same `OnDamageDealt` event IS matched by `match` and `plant:5`, and the same `OnDamageTaken` event by `zombie:9`; only the side-wide key is refused | same |
| Whole contract surface still green | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~StatApplyScope|FullyQualifiedName~Patron"` | PASS — 3038/3038, 0 failed (3037 + this one) | — |

The boundary is a stated decision, not an omission: `EffectOwnerKey.MatchesEvent` gates *triggered*
grants, and a side-wide key names no single owner entity to attribute a proc to. The only producer is
`PatronSecondaryPlugin`'s triggerless `stat.derived` grant, whose mere presence is the effect. A future
producer that wants a triggered side-wide grant now gets a red test here plus the header's own note,
instead of a grant that silently never fires.
