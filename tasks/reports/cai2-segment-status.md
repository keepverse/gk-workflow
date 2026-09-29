# `cai2` — every remaining combat-ai row's blocker, as of 2026-09-23

Lane `cai2` (session `combat-ai-2b`). Written because the orchestrator's method now is *"if a row cannot be
finished, record that as the row status -- blocked with the exact reason -- in a commit, and move to the
NEXT row"*, and because every remaining row now terminates on something that is NOT work this lane has left
undone. Each line names the category the instruction allows: a path outside the fence, a specific owner
ruling, or a named dependency row.

## Closed or advanced by this lane

| Row | State |
|---|---|
| `CAI2.6` | **CLOSED** (`e39f8db11`) — ruled from `combat-ai-ideal.md:318` (§6.1 step 3), quoted by `spec-action-schedule-twin.md` §2; the seam now compares the post-payment balance |
| `CAI3.1` | **CLOSED** (`9eca27b6e`) — `siege.v3.json` + both readers in one commit (H7) |
| `CAI-perf-1` | **CLOSED** (`4bb8d861a`) — `AiDecide = 25` + `LawnAiDecide = 26` + `SectionCount = 27` |
| `CAI2.5` | injector half (`9bce8b83a`) + read route (`3d73e1f02`) |
| `CAI4.1` | injector view host (`88423b023`) |
| `CAI4.5` | Core half of the two row sources (`5e06a5ce9`) |
| `CAI4.9` | rows 3–5's supply (`3742306b1`), row 14's forced-intent hook (`3e42f17e3`), the Server order endpoint (`0634448b0`) |
| `CAI2.2` | Server source half (`9c1de8da5`) |
| `CAI2.3`, `CAI3.5` | rulings/blockers sharpened with measured evidence |

## Every row still open, and EXACTLY what blocks it

| Row | Blocker, and its category |
|---|---|
| `CAI2.2` | **Path outside the fence:** `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WebMatches.cs` + `RpgStore.cs`'s `EnsureColumn` (the nullable `combat_ai_profile` column). The three Server stamping sites cannot compile without it. There is NO injector half — `spec-replay-identity.md` §2/§5 name only Server files |
| `CAI2.3` | **Owner ruling:** who owns the profile→`Predictor.ActionEconomy.Options` projection and what its mapping is; plus the overkill parity acceptance line, which cannot pass as written |
| `CAI2.6` | closed (above) |
| `CAI3.2` | **Path outside the fence:** the one home must be `RpgStore.EquippedActionIdsFor` in `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Loadouts.cs` |
| `CAI3.3` | **Path outside the fence:** its caller is the Data file `RpgStore.WorldTurns.cs` |
| `CAI3.4` | **Owner ruling** on `BattleRunState` visibility, shared with CAI3.1; plus **named dependency row `CAI3.5` → `CAI2.2` → Data** |
| `CAI3.5` | **Two measured blockers:** (1) its tuning acceptance is unsatisfiable — `AiRole` declares no `Enemy`, pinned by `CombatAiTuningTests.AiRole_has_four`, so `delve/enemy` cannot parse (an **owner ruling**: a reviewed vocabulary change or an erratum); (2) the only battle `IBattleView` is `BattleRunState`, a private nested class whose own comment records the nesting as deliberate (**the same owner ruling as CAI3.1/CAI3.4**). Plus dep CAI2.2 (Data) and a **protected path** for `NoCatchInLiveBattleCallStackTests.cs` |
| `CAI3.6` | **Named dependency row `CAI2.2`** (Data) + **paths outside the fence:** `docs/architecture/decisions.md`, `docs/research/combat-ai/**` |
| `CAI4.1` | **Named dependency row `CAI4.8`** → lawn `LW1.1` (measured absent); plus the status-mask producer, which has no source anywhere in `src/` |
| `CAI4.2` | its remaining half IS `CAI4.3` |
| `CAI4.3` | **A missing mechanism no row owns:** the injector cannot construct `LawnHeldActionSets` — it has no `ActionCatalog` and no feed for one (`ActionCatalogHost` has zero users in `src/`; `grep` finds no `ActionCompiler`/`ActionRow` reference in `gk-fusion/src/FusionRpg.Injector/` at all; the only builder is `RpgStore.BuildActionCatalog`, Data-side). **Needs a routing or erratum decision.** This one blocker also holds CAI4.2's other half, CAI4.5's injector half and CAI4.9's injector half |
| `CAI4.5` | Core half landed; its injector half shares `CAI4.3`'s blocker |
| `CAI4.6` | **Path outside the fence:** `gk-core/src/FusionRpg.Contracts/EffectDtos.cs`'s `CastOrigin` field — measured absent from `src/` entirely, and the acceptance's mutation test is written against it. The fire site and the two guards are in fence and named as ready |
| `CAI4.7` | **Named dependency row `CAI4.8`** → lawn `LW1.1` (its `PerfProbe` line landed) |
| `CAI4.8` | **Named dependency row `CAI4.7`** → `LW1.1` |
| `CAI4.9` | row 14 + the Server endpoint landed; remaining = the Injector verb/host/registry (shares `CAI4.3`'s blocker) + two `web/**` files (**outside the fence**) |
| `CAI5.1` | **Owner-only live probe** + `docs/research/combat-ai/**` (outside the fence); deps CAI4.9 + lawn `LW2.4` |
| `CAI5.2` | **Path outside the fence:** `docs/research/combat-ai/**`; dep CAI5.1 |
| `CAI5.3` | **Named dependency rows in another program:** lawn `LW1.4`–`LW1.6`, `LW5.1`, `LW1.1` — all measured open |

## The two decisions that would unblock the most

1. **The injector's action-catalog feed** (CAI4.3, and with it CAI4.2's other half, CAI4.5's injector half
   and CAI4.9's injector half). Either a Cold push carrying the compiled catalog is sanctioned (and
   `CompiledAction`'s predicate-tree JSON problem solved), or an erratum names the owning row.
2. **The `BattleRunState` visibility ruling** (CAI3.1's and CAI3.4's last two tests, and CAI3.5's
   `DelveAutomatedPolicy`). One ruling unblocks three rows.
