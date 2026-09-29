# AU2 — author the twelve aura containers

Real `world-buff.aura-*` containers (`gk-data/packs/fusion/data/seed/containers/aura.json`) + their `stat.derived` atoms
(`gk-data/packs/fusion/data/seed/atoms/aura-content.json`), delivered through Phase 1's producer (BP1-BP3), no hand-picked
per-aura constants — every channel's amount is an `externalRef` resolved by
`AuraMagnitude.ReferenceChannelValue` (Core, new) from `AuraMagnitude.Compute` (the same shared formula
every real magnitude uses) reading `gk-core/data/tuning/aura.v1.json` + `power-scale.v2.json` +
`aptitudes.v*.json` — a balance-pass edit to any of those three files changes the shipped number with
no code or content edit (proved by `Changing_the_rung_tuning_changes_the_shipped_value...`).

**Named limitation, not hidden:** the reference uses `AuraTuning.MinRung` (7, the floor) and `share=1.0`
(full) — a structural reference point, not yet the enabling commander's own live aptitude state. Live
per-commander scaling needs aptitude-state reads this backlog task does not build; named as a follow-up
in `AuraMagnitude.ReferenceChannelValue`'s own doc comment. Focus (0 declared channels, reverses onto
the commander's own cooldowns per `spec-aura-content.md` S4.1) gets a deliberately empty container —
binds, does nothing, never crashes.

| Check | Command | Result |
|---|---|---|
| Even-split reference function (single channel, two-channel conservation, floor-not-ceiling, tuning-driven, range refusals) | `dotnet test --filter FullyQualifiedName~AuraMagnitudeReferenceChannelValueTests` | 7/7 |
| Real corpus parses/validates (id collisions, orphans, schema) | `dotnet test --filter FullyQualifiedName~ContentValidationTests` | 34/34 |
| End-to-end through Phase 1 — real seed import, real `/enable` endpoint, real `AtomPushService` compile, single-channel value, two-channel split+conservation, disable removes the def, Focus binds inert | `dotnet test --filter FullyQualifiedName~AuraContentDeliveryTests` | 4/4 |
| Full Core suite | `dotnet test tests\FusionRpg.Core.Tests` | 14532/14532 |
| Full Server suite | `dotnet test tests\FusionRpg.Server.Tests` | 660/660 |
| Magic-number audit | `python gk-core/scripts/audit-magic-numbers.py --summary` | 0 findings |
| Overflow audit | `python gk-core/scripts/audit-overflow.py` | 0 findings |
| Boundary guards | dal / single-writer / secondary-no-unity / funnel-delta / actor-hub | all 5 OK |

**Found and fixed while wiring (not invented):** `RungSemanticsTests.MinRung_has_zero_hits_outside_the_unrelated_aura_ladder_constant`
pinned "exactly one file in `src/` mentions `MinRung`" — a population-count assertion that broke the
moment `AuraMagnitude.cs` became a second, legitimate caller of the SAME `AuraTuning.MinRung` constant.
Fixed to assert the CONTRACT (no *different*, unrelated `MinRung` concept exists) against an explicit,
order-independent expected set, not a caller count — the guard's own intent per its doc comment.

**Closes T16's second ground** (per-aura balance coefficients) — its first ground ("nothing reads a
`world-buff.*` container") was already void before this task, per `spec-aura-delivery-path.md`'s own
2026-08-30 spike finding.
