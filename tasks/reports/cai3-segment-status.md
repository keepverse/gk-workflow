# `cai3` — every assigned row's state, as this lane read it (2026-09-23)

Lane `cai3` (session `combat-ai-3`), a proactive rotation of `cai2` at its 3.88 MB session. This file
records what each row the brief assigned actually needed, so the next holder does not re-derive it.

## Closed or advanced by this lane

| Row | State |
|---|---|
| `CAI-find-2` | **CLOSED** (`978a4a50f`) — `CombatAiTuningLoader.NonNegativeWeight` refuses a negative weight at parse, naming the key; all seven weights; planted violation kills exactly the seven cases; the spec row it corrects is re-anchored in the same commit |
| `CAI2.7` | **FILED** (`3caf39b5a`) — the kill-margin waste guard's ruling, the row `CAI2.3` said was owed. Question in one line, both readings read from the code, witness measured (3/0) |
| `CAI4.3` | **SHARPENED** (`96ab5f44d`) — its "missing mechanism no row owns" is really one decision: the Cold-push payload shape. Both options measured; option (b) is feasible because the injector already configures `RungPolicy.Table` |
| `CAI2.2` | **CORRECTED** (`711dc6c1b`) — the H7 divergence hazard the row named is superseded by `CAI-F1`; the only remaining blocker is the denied `Data` column |
| `CAI2.6` | **verified CLOSED**, not reopened — the brief's premise is superseded: `cai2` ruled it from `combat-ai-ideal.md:318` (§6.1 step 3), which I re-read and confirmed says *"a pool may not drop below a fraction of its max **after paying**"*, and the spec (`spec-action-schedule-twin.md:23-24`) quotes it verbatim |

## The four rows the brief assigned, and EXACTLY what blocks each

| Row | Blocker, and its category |
|---|---|
| `CAI2.2` | **Denied path:** `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WebMatches.cs` + `RpgStore.cs`'s `EnsureColumn` (the nullable `combat_ai_profile` column). The three Server stamping sites cannot compile without it and the five-step pin resolution reads `entry.CombatAiProfile`. The Server source half is landed; the previously-recorded H7 hazard is gone (see above). There is no injector half |
| `CAI2.3` | **Owner erratum ruling:** who owns the profile → `Predictor.ActionEconomy.Options` projection (this row claims it; `spec-action-schedule-twin.md:421-423` assigns it to module 2 or 14) and what the mapping is — no document specifies it, and a profile carries filters and a floor but no cost or multiplier. Its second ruling (the overkill parity line) is now `CAI2.7` |
| `CAI2.5` | **Named dependency row:** `CAI4.8`'s decision feed → `CAI4.3`'s payload ruling (above). Nothing in this row is in-fence-undone |
| `CAI2.6` | closed by `cai2`; verified, not reopened |

## The one decision that would unblock the most here

**`CAI4.3`'s payload shape** — the compiled-list payload (needs a `CompiledAction` wire form, a
predicate-tree DTO and a `Contracts` edit, which no combat-ai lane holds) versus the raw-row payload with
an injector-side compile through the one `ActionCompiler`. It holds `CAI2.5` (via `CAI4.8`), `CAI4.2`'s
other half, `CAI4.5`'s injector half and `CAI4.9`'s fire path.

## Two findings this lane filed rather than fixed

- **The brief's session id is retired.** `tasks/sessions/combat-ai-3.json` is `status: merged` (the lane
  retired 2026-09-21), so `scripts/verify-change.ps1 -Session combat-ai-3` refuses with
  `session is not active: combat-ai-3`. `tasks/sessions/**` is outside this lane's fence, so the record
  could not be created or repaired here. The selected module boundary was run directly instead
  (`core-fallback` for `gk-core/src/FusionRpg.Core/**` → the `FusionRpg.Core.Tests` project).
- **`CAI-find-1` was CLOSED later the same session — this paragraph is superseded.** It was left alone here for the reason stated (the row says the fix is the owning program's, and choosing a side would pre-empt lawn-combat-wire), but the row's own two options are not symmetric: *assert the current owner decision* is not a product decision, because the constant's comment records the 2026-09-16 reversal twice. So the tests were corrected to describe the code, the third case was **strengthened rather than flipped** (it corrupted the backing field to `true` and asserted `false`, which proves nothing under a default-ON flag), and the injector project went **114/3 → 119/0**. Flipping the constant back remains the owning program's option, in one commit. See `tasks/reports/CAI-find-1.md`.

## CI IS RED on the merged head — measured, and it is not this lane's to fix

`ci.yml:295-296` runs `gk-core/tests/FusionRpg.Guard.Tests` **whole** in Release with an explicit
`if ($LASTEXITCODE -ne 0) { throw "FusionRpg.Guard.Tests failed" }` — no `--filter`, no `continue-on-error`,
no `if:` guard. Three of its 673 tests fail **in exactly that configuration** (re-run with `-c Release` and
the same project): `PlantSideStatusGuardTests.BattleEffects_is_byte_identical_to_its_current_core_baseline`
(filed as `CAI-guard-1`) and `CAI-find-6`'s two — `CiPytestWiringTests.Every_pytest_project_has_a_ci_step_running_pytest_in_its_own_root`
and `PlayerSpeciesMaterialiseCallerGuardTests.The_nine_pick_refusal_codes_are_a_closed_vocabulary`.

**So the integration branch cannot pass its own CI gate**, and it could not before this lane started (lane
`cai2` measured the same three). **And those three are not the whole list** — completing the picture found the
Launcher test red too (fixed, `CAI-find-7`) and then **two corpus gates red** (`CAI-find-8`):
`gk-forge/tools/CreatureCorpusDump -- --verify gk-data/packs/fusion/data/seed/creatures/_dump` and `gk-forge/tools/ItemSeedValidator` both exit **1**
under `ci.yml:425-426` and `:431-433`, which throw. Neither path is in a combat-ai lane's fence and neither is
protected, so those two are routable; the Guard three are not. All three fixes live in **protected** paths — `gk-core/tests/FusionRpg.Guard.Tests/**`
and `.github/workflows/ci.yml` — so **no lane can execute any of them today**, which makes a protected-path
grant the single highest-value ask in this program's list. Everything else on this lane's list is blocked on
something a lane can be given; this one is blocked on the hook.

Earlier drafts of this file and of the decisions page described these as reds "for whoever runs it locally",
which understated them: they are the CI gate.

**Scope of that claim, so it is not over-trusted.** The four reds are complete for the projects this lane ran in
**CI's own configuration** (`Guard.Tests` and `Launcher.Tests`, both Release). `CheatCore.Tests` (41/0) and
`ItemSeedValidator.Tests` (98/0) were also Release and green. The bigger green readings (`Core.Tests` 9721/0,
`Balance` 210/0, `Match` 182/0, `Server` 858/0, `Data` 1885/0, `Injector` 119/0) are **Debug** — the local default,
not CI's `-c Release` — so they are context, not a CI claim. **The Core split IS measured, and clean:** all **65** projects beyond
`Core.Tests`/`Balance`/`Match` were run in Release — 64 green, and the one that appeared to fail
(`FusionRpg.Core.ClassSystem.Tests`, 3/235) is the bare-interpreter class, going to **238/0** with `python` on PATH
(`ReaderCensusTests.cs:193`, already in `CAI-find-3`'s inventory). **Still unmeasured, with the reason known:** `E2E.Tests` cannot be BUILT here — its Release build fails
`MSB3027`/`MSB3021` copying `src/FusionRpg.Server/bin/Release/net8.0/FusionRpg.Server.dll` into its own output after
`MSB3026` retries, i.e. a file lock (five `FusionRpg.Server.exe` and several `dotnet.exe` were running on this machine;
none was stopped, as they are the owner's or other lanes'). The web job needs `npm ci` (`node_modules` absent here) and
`npm` is not on this shell's PATH. The true
count could therefore be higher than five.

## What verifying `gk-core/src/FusionRpg.Core/**` actually costs, measured

`gk-core/src/FusionRpg.Core/**` resolves through **`core-fallback`**, whose project is the **`core` group — 68 projects** at the last count (up from the 39 the CAI-tests-1 row recorded). So a one-line edit anywhere in Core pays the whole split. Two measured consequences:

- **`gk-core/src/FusionRpg.Core/Match/**` can be narrowed to FIVE projects** — `core-match`, `core-matchadmittests`, `core-matchinjectcontracttests`, `core-matchruntimetests`, `core-matchvalidatortests` — which is what the CAI-tests-1 follow-up note now records for its owner (`test-verification-boundary`).
- **`gk-core/src/FusionRpg.Core/Actions/**` CANNOT be narrowed as things stand, and that is worth knowing before someone tries.** No project entry in `gk-core/scripts/verification-boundaries.v1.json` mentions `/Actions` in its file list, and the project that holds the Actions tests — `gk-core/tests/FusionRpg.Core.Tests` — is itself one of the 68 in the `core` group. A focused boundary over `Core/Actions/**` would therefore have to include `core`, which is no narrowing at all. The fix is a further split of `Core.Tests`, not a registry row.
- **What this lane actually ran for its five Core changes, stated plainly:** `gk-core/tests/FusionRpg.Core.Tests` **9721/0** (the project holding the combat-ai Core tests), plus `FusionRpg.Core.Balance.Tests` **210/0** (the twin, `ActionStage`, the goldens), `FusionRpg.Core.Match.Tests` **182/0** and `FusionRpg.Server.Tests` **858/0** for the blast radius — **not** the 68-project group the registry selects. That is under the registry's own selection, and it is recorded rather than glossed: the selection is coarse enough that running it is a ~9-minute whole-suite job for a one-line edit, which is the defect the AGENTS.md verification-boundary section names, and the registry cannot fix it from the source side alone.
