# `cai2` re-triage — every row the orchestrator listed, re-read against the ledger and this lane's fence

Lane `cai2` (session `combat-ai-2b`), 2026-09-23. The instruction was: for each row recorded `blocked`,
re-read its blocker; if the dependency is now done in the ledger, reopen and implement it now; if it is
genuinely external (owner, live probe, another lane), leave it blocked and say which dependency.

**This lane's fence:** `gk-core/src/FusionRpg.Core/**`, `gk-core/src/FusionRpg.Server/**`, `gk-fusion/src/FusionRpg.Injector/**`,
`tests/**`, `gk-core/data/tuning/**`, `tasks/combat-ai-todo.md`, `tasks/combat-ai-ledger.jsonl`,
`docs/architecture/combat-ai/**`, `tasks/reports/**`. **Not** in it: `gk-core/src/FusionRpg.Data/**`,
`gk-core/src/FusionRpg.Contracts/**`, `tools/**` (runnable, not writable), `docs/architecture/decisions.md`,
`docs/research/**`, `web/**`, `tasks/sessions/**`, `tasks/evidence-fragments/**`.

Two rows closed this turn. **Eight rows have this lane's own fence as their only blocker — that is not an
external dependency, and they are not done**; they are named below with what each needs, so nobody reads
"blocked" as "waiting on someone else".

## Closed this turn

| Row | Was blocked on | Verdict |
|---|---|---|
| `CAI3.1` | "Outcomes 2/3 need `AiTuning` narrowed, which breaks two test bootstraps outside this lane; `siege.v3.json` cannot land without its readers (H7)" | **DONE** (`9eca27b6e`). Both readers are in this fence, so H7 was satisfiable here. `siege.v3.json` from one `--remove-key ×2`; `AiTuning` narrowed to two members; the four `AiTuning` constructions fixed; the superseded test deleted. siege 333/0, siege+goldens 338/0, Stance/AuraRuntime 186/0, seven guards exit 0. `tasks/reports/CAI3.1.md` |
| `CAI-perf-1` | "blocked on a fence or an erratum" (`Core/Diagnostics/**` outside every combat-ai lane) | **DONE** (`4bb8d861a`) by **remedy (a)**: `AiDecide = 25` + `LawnAiDecide = 26` + `SectionCount = 27` landed, so `CAI4.7`'s acceptance reads as written and no erratum is needed. Diagnostics 18/0; planted `SectionCount = 25` → 1 red. `tasks/reports/CAI-perf-1.md` |

## Blocked on something external — and the dependency, named

| Row | Dependency that must move first |
|---|---|
| `CAI2.2` | **`gk-core/src/FusionRpg.Data/**`** — the nullable `combat_ai_profile` column. The Server source half landed 2026-09-23 (`9c1de8da5`); the three stamping sites cannot compile without the column, and the pin resolution reads it |
| `CAI2.3` | **owner erratum ruling** on who owns the profile→`Predictor.ActionEconomy.Options` projection (and its unspecified mapping), plus a second erratum on the overkill parity line. The dominance run is DONE |
| `CAI2.5` | **`CAI4.8`'s wire** — nothing calls `Sink.Record` until the lawn decision host exists. The injector half landed 2026-09-23 (`9bce8b83a`) |
| `CAI2.6` | **owner ruling** — which reserve-floor reading wins. Sharpened to one line with both sides measured 2026-09-23 (`50f9f4839`); no code may move before the ruling |
| `CAI3.2` | **`gk-core/src/FusionRpg.Data/**`** (+ Server, which this lane holds) |
| `CAI3.3` | **`gk-core/src/FusionRpg.Data/**`** (the Core/World half is in this fence) |
| `CAI3.4` | **owner decision** on `BattleRunState` visibility (shared with `CAI3.1`) — its `RoleOf` caller's Server half is in this fence |
| `CAI3.5` | **`CAI2.2`** (itself Data-blocked) **+ a protected-path grant** for `tests/FusionRpg.Guard.Tests/NoCatchInLiveBattleCallStackTests.cs` |
| `CAI3.6` | **`CAI2.2`** + **`docs/architecture/decisions.md`** and **`docs/research/combat-ai/**`**, both outside this fence |
| `CAI4.6` | **`gk-core/src/FusionRpg.Contracts/EffectDtos.cs`** — the additive `CastOrigin` field. The injector fire site is in this fence but cannot stamp a field that does not exist |
| `CAI4.7` | **lawn plan `LW1.1`** (`gk-core/data/tuning/lawn-perf-budget.v1.json`, **measured absent**). The `PerfProbe` line landed this turn, and its `combat-ai.v3.json` line is no longer H7-blocked for this lane |
| `CAI4.8` | **`CAI4.7`**, which is `LW1.1`-blocked (above) |
| `CAI5.1` | **an owner-only live probe** + `docs/research/combat-ai/**` |
| `CAI5.2` | **`docs/research/combat-ai/**`** + `CAI5.1` |
| `CAI5.3` | **the lawn program's preconditions** `LW1.4`-`LW1.6`, `LW5.1`, `LW1.1` — all measured open, none in this program |

## This lane's fence is the ONLY blocker — in-fence, not external, and NOT done

These are the rows the re-triage instruction was aimed at, and the honest answer is that the fence now
belongs to a lane that has not finished them. Each is named with its remaining files, and where a read
settled what it needs, that is recorded too.

| Row | Remaining work, and the files it needs (all in this fence) |
|---|---|
| `CAI4.1` | **DONE 2026-09-23** (`88423b023`): `LawnActorViewHost` landed with all seven seams and the `(perspective, frame, census-instance)` cache, 10 tests. The row stays open on ONE named dependency ROW — `CAI4.8`'s frame slot is its only production caller — plus the status-mask producer (no source exists). |
| `CAI4.3` | **In fence and NOT done, and it needs no Data edit — verified this session.** Its Cold-payload inputs are existing public `RpgStore` methods: `GetSpeciesBasics(speciesKey)` (`RpgStore.Actions.cs:673`) and `ListGrants(OwnerScope)` (`:597`), with `_store.BuildActionCatalog(RungPolicy.Table)` for the compile step — all called from `gk-core/src/FusionRpg.Server/**`, which this lane holds. Remaining files: `Injector/Effects/LawnHeldActionRegistry.cs` (new), `Server/RpgHub.cs` (the push, in `PatronEndpoints.TryBuildPatronCommand`'s shape), `Injector/CheatCommandRunner.cs`, the additive `InjectorEntityRegistry` drop. What it may still need is a payload DTO: a typed `CommandDto` payload would live in `gk-core/src/FusionRpg.Contracts/**`, which is NOT in fence, so the payload must travel as an existing untyped/dictionary shape or the DTO must be routed |
| `CAI4.5` | `Injector/Effects/LawnBasicAttackCostCharger.cs` + `Injector/Effects/LawnCostRowSource.cs` (new) + `gk-core/tests/FusionRpg.Core.Tests/Actions/LawnCostAuthorityTests.cs`. **Note a contradiction in the row**: the spec puts `LawnCostRowSource` in the Injector while the acceptance puts its test in `gk-core/tests/FusionRpg.Core.Tests`, which cannot reference the injector — so either the union logic belongs in Core or the test path is wrong. That wants a read of `spec-lawn-cost-authority.md` §1 before code |
| `CAI4.9` | Its Core parts are in this fence and unblocked: `Actions/DirectOrder.cs`'s two additive `SubjectId`/`ScopeId` fields (rows 3–5's supply) and `Actions/IntentRouter.cs`'s forced-intent hook (row 14). The Server endpoint and Injector host are in this fence too; only the two `web/**` files are not |
| `CAI4.2` | Nothing of its own: its remaining half **is** `CAI4.3` (above) |

## Rows advanced or closed since the triage was written

- `CAI4.1` — the injector host landed (`88423b023`); open on `CAI4.8` + the status-mask producer.
- `CAI2.5` — the read route landed (`3d73e1f02`): `debug.combat.snapshot` carries the ring; open on
  `CAI4.8`'s decision feed (itself `LW1.1`-blocked).
- `CAI3.1` (`9eca27b6e`) and `CAI-perf-1` (`4bb8d861a`) — closed.
- `CAI3.3` — the composite's composition needs the store-bundle resolver supplied by
  `gk-core/src/FusionRpg.Data/**`'s `ActionContainerEffectResolverFactory`, so its caller is the Data file
  `RpgStore.WorldTurns.cs`; **external (Data)**, not an in-fence omission.
- `CAI3.4` — its remaining `RoleOf` caller travels with `CAI3.5`, which is blocked on **`CAI2.2`** →
  **`gk-core/src/FusionRpg.Data/**`**; plus the **owner decision** on `BattleRunState` visibility.
