# `combat-ai` — every pending decision, in one place

Lane `cai3` (session `combat-ai-3`), 2026-09-23. Written because the program's remaining work terminates
almost entirely on decisions rather than on work, and each one is currently buried in a different row's
prose. Every entry names **the question in one line, what the evidence actually says, what is recommended,
and what it unblocks** — so an owner can rule from this page without re-reading the rows, and a lane can
pick up a ruled item without re-deriving it.

`tasks/reports/cai3-segment-status.md` is the per-ROW view; this is the per-DECISION view.

---

## D1. `CAI2.7` — the kill-margin waste guard's rule

**Question.** When the kill-margin waste guard fires, does the actor go IDLE — `ActionIntent.None`, which is
what the shipped `ActionStage.TryPick` does — or fall through to the FREE option, which is what the twin's
`ActionSchedule.Choose` does?

**What the documents say, and do not.** The ideal puts the waste guards in the same pass as the reserve
floor and is **silent** on what happens when no row passes (`combat-ai-ideal.md:319`). Module 9's spec
states the free-fallback invariant as its own success criteria — under the heading **Waste guard**,
*"round k takes the free option while rounds before it are unchanged"* (`spec-action-schedule-twin.md:300-302`),
plus `:295`, `:298` and the reason at `:140-143` — and `ActionSchedule` **enforces** it at construction
(`:107-109`: it refuses an option list with no cost-free entry, naming *"a dry actor has nothing to do"*).
Module 1's spec — the seam's own — is **silent** on the aftermath (`spec-core-scorer.md:269-271,466`); no
sentence anywhere says a refusal means `ActionIntent.None`. So the seam's idling is an **implementation
choice**, and it contradicts the invariant module 9 relies on. This is the opposite of `CAI2.6`, whose
deciding sentence was verbatim.

**Recommended (not taken).** A **cost-free action is never refused by a waste guard** — `ActionStage.PassesWasteGuards`
returns pass when `action.Costs.Count == 0` (measured: the parity fixture's free action carries ZERO cost
rows, not a zero-amount row). The seam fix is one line; the witness's `real` expectation flips to parity;
`ActionStageTests`' two kill-margin cases need a COSTED fixture, because theirs is cost-free and would stop
testing the guard.

**Cost / risk.** Goldens are **byte-identical today under either ruling** (the shipped profiles author
`killMarginMilli: 0`, so the guard fires only at `HpMilli <= 0`); the golden filter must be run in the
ruling's commit to decide whether a 0-HP candidate with a cost-free action exists in a golden battle.

**Unblocks.** `CAI2.3`'s overkill parity acceptance line, and the question of whether `Predictor.MixedStrike`
can be wired to `fightEndsThisRound` at all. Detail: `tasks/reports/CAI2.7.md`.

---

## D2. `CAI4.3` — the Cold push's payload: a ROUTING decision, not a design choice

**Question, reframed.** The design question is **already answered by the spec**: `spec-lawn-held-actions.md:73-80`
says in numbered steps that *the server* assembles (`:75`), *resolves each `AssembledAction.ActionId` to a
`CompiledAction` through the same `ActionCatalog` path battle uses* (`:76-78`), sorts (`:79`) and *"pushes the
compiled list"* (`:80`); its Boundaries repeat it (*"push from the server keyed by species / instance, never
by ptr"*) and `:239` adds *"the injector only binds a ptr to a set Core produced."* So the compiled-list
payload is the spec's answer, and the raw-row alternative is an **erratum** rather than a free choice.

**What actually blocks it is one file's fence.** The compiled list needs a wire form: `CompiledAction` is a
21-member record whose `Condition` is an interned `ICompiledPredicate` tree, `grep -rn "CompiledAction"
gk-core/src/FusionRpg.Contracts/` returns **nothing**, and a typed DTO belongs in `gk-core/src/FusionRpg.Contracts/**` — which
no combat-ai lane may edit. **So the action is to grant that path to a combat-ai lane, or route the DTO to a
lane that holds it.** The raw-row option's only real attraction is that the injector already configures
`RungPolicy.Table` from `action-rungs.v4.json` (`RpgHost.cs:278`), so `ActionCompiler.Compile` *could* run
injector-side — recorded as the erratum's supporting evidence, not as a recommendation. A narrowed
projection is rejected outright: `CoreIntentPolicy` reads `Condition`, `Costs`, `Envelope` and `Targeting`,
so narrowing changes decision semantics rather than transport.

**Unblocks — the most of any entry here.** `CAI2.5`'s decision feed (via `CAI4.8`), `CAI4.2`'s other half,
`CAI4.5`'s injector half, `CAI4.8`'s decision step, `CAI4.9`'s fire path. Detail:
`tasks/reports/CAI4.3-wire-format.md`.

---

## D3. `CAI2.3` — who owns the profile→`ActionOption` projection

**Question.** Does the projection from a `CombatAiProfile` into `Predictor.ActionEconomy.Options` belong to
this row (which claims it) or to module 2 / module 14 (which `spec-action-schedule-twin.md:421-423` assigns
it to) — and what is the mapping?

**The mapping is DERIVED, so the ruling is a yes/no.** `ActionOption`'s seven fields take **three** inputs:
module 16's compiled held list gives `Id` and `Priority` (through the same `ActionTagPreference.Compare`
both compile paths use); the ledger and `ActionBaseDerivation` give `CostShareOfOutputMilli` and
`DamageMultiplier` at the actor's `EffectiveRungOf`; and the profile gives only the `AiActionFilter` plus
`ReserveFloorMilli` and `MinTargets`. The profile alone has **no cost and no multiplier** — which is the fact
the erratum turns on, and why "the mapping is not mechanical" was true of the profile alone and false of the
composition.

**Recommended (not taken).** Ownership goes to **module 14's re-fit (`CAI3.6`)**, because the projection is a
composition of a loadout, the profile and the ledger — not an analytic twin's job, whose contract is to
follow the core policy. If ruled that way, `CAI2.3`'s acceptance line 7 should be struck.

**Unblocks.** `CAI2.3`'s acceptance line 7 and `CAI3.6`'s one-cause commit. Detail:
`tasks/reports/CAI2.3-projection-mapping.md`.

---

## D4. `CAI4.9` item (4) — when the order key is published

**Question.** Publish `lawn.order.lifetimeTicks` now — a file and a parser with no consumer until the fire
path — or in the same commit as the lawn router that reads it (H7's own rule)?

**What was measured.** `LawnOrderQueue.Expire` has exactly **ONE** caller in `src/`
(`IntentRouter.cs:226`) — the lawn's router, i.e. the fire path D2 holds. `lawn.order.queueCap` is
**structural**, and already the correctly-commented code const (`LawnOrderQueue.Cap = 16`,
`tunables-ssot.md` T2), so it stays out of the file exactly as module 19's four structural values do.

**Recommended (not taken).** Publish with the router: publishing now creates a parsed value nothing
consumes, which is the dead-config shape the spec's own plan correction 2 forbids.

---

## D5. `BattleRunState` visibility (owner decision, shared by three rows)

**Question.** Give `BattleRunState` (a private nested class inside `BattleEngine` — `BattleRunState.cs:1601`
records the nesting as deliberate, per B13's deviation note) a seam so a view probe can reach it — or add a trailing optional
probe on `Resolve`, the shape `IStanceCheck? stance` already gained?

**Unblocks.** `CAI3.1`'s last two tests, `CAI3.4`'s `RoleOf` caller, and `CAI3.5`'s `DelveAutomatedPolicy`.
Detail: `CAI3.4`/`CAI3.5`'s rows.

---

## D6. `AiRole.Enemy` (owner decision: a reviewed vocabulary change, or an erratum)

**Question.** `CAI3.5`'s acceptance asks for four `delve/*` rows including `delve/enemy`, but `AiRole`
declares exactly four members — `Default`, `Frontliner`, `Support`, `Striker` — with **no `Enemy`**, pinned
by `CombatAiTuningTests.AiRole_has_four`. So three of the four keys are expressible and the fourth needs
either a fifth member (a reviewed change that breaks its own pinned count) or an erratum naming a different
key.

---

## Not rulings — hard dependencies

| Dependency | Blocks |
|---|---|
| The nullable `combat_ai_profile` column in `gk-core/src/FusionRpg.Data/**` | `CAI2.2`'s remainder (its Server source half landed and has no production caller); `CAI3.2`'s one home; `CAI3.3`'s caller; `CAI3.5` and `CAI3.6` by dep |
| `EffectEventDto.CastOrigin` in `gk-core/src/FusionRpg.Contracts/**` | `CAI4.6`'s fire site (and its acceptance's mutation test is written against exactly that field); `CAI-find-5`'s swing feed, whose discriminator must not be inferred from a trigger name |
| The two `web/**` files in `CAI4.9` | the FE half of the order path (out of every combat-ai lane's fence) |

## Two things needing routing, not a ruling

- **`CAI-find-6`** — a new pytest project (`gk-core/tests/tools/test_audit_program_pipeline.py`, registered as
  `tools-audit-tests`) with no `python -m pytest` CI step at `working-directory: .`, and a grown
  pick-refusal vocabulary (`RpgStore.Fusion.cs:305`) whose guard pin was not updated. Both fixes are in
  **protected** paths, and the registry was deliberately NOT edited to silence the guard.
- **`CAI-find-3`** — 78 bare-interpreter spawn sites repo-wide (`dotnet` 32, `powershell` 27, `python` 18,
  `npm` 1), including four in `scripts/verify-change.ps1` itself. A CI project reports **15** reds to a shell
  without those interpreters and **3** with them, so the finding is the environment dependence, not the reds.

---

## The one ask that gates everything: CI is red, and its fixes are protected

**`ci.yml` runs every gate below with an explicit `throw` on failure, and FIVE fail** — three test projects'
tests and two corpus tools. The three tests are in `gk-core/tests/FusionRpg.Guard.Tests` (673 tests), measured 2026-09-23 with `-c Release` on that project:
`PlantSideStatusGuardTests.BattleEffects_is_byte_identical_to_its_current_core_baseline` (`CAI-guard-1`) and
`CAI-find-6`'s two (`CiPytestWiringTests`, `PlayerSpeciesMaterialiseCallerGuardTests`). So **the integration
branch fails its own CI gate**, and all three fixes are in **protected** paths
(`gk-core/tests/FusionRpg.Guard.Tests/**`, `.github/workflows/ci.yml`) that no lane may edit. This is the only ask on
this page that a lane cannot act on even after being handed a fence — it needs the hook to grant
`--allow-protected` — which makes it the first thing to decide.

**A fourth was found and FIXED in the same lane (`CAI-find-7`), and it is recorded here because it was the one that proved the pattern.** It was `MelonHostGapTests.PlayerPackProbe_accepts_Melon_nested_drop` in `gk-fusion/tests/FusionRpg.Launcher.Tests`
(`-c Release` reads 1 failed / 165 passed), and unlike the three it is NOT in a protected path** — so it is
routable today. `PlayerPackProbe.RequiredContentDirs` gained a third entry on 2026-09-23 (`Server/data/generated/creatures`,
under an owner ruling the comment names `CS-F3`), the change updated one of the two synthetic-pack fixtures
(`PlayerPackProbeTests.cs:89`, which even asserts the missing-dir message at `:61`) and missed the other
(`MelonHostGapTests.cs:173-176`); the fix was one `Directory.CreateDirectory` line copied from the sibling — and because `tests/**` is in a combat-ai lane's fence, this lane landed it: `FusionRpg.Launcher.Tests` now reads **166/0 in Release**, with the line's planted removal killing exactly that test. So the Launcher red is gone — and **two further gates were then found red, both routable** (`CAI-find-8`): `gk-forge/tools/CreatureCorpusDump -- --verify gk-data/packs/fusion/data/seed/creatures/_dump` exits **1** (*"hash mismatch: manifest declares `cc322647…`, files on disk hash to `6181dc2d…`"*; `ci.yml:425-426` throws) and `gk-forge/tools/ItemSeedValidator` exits **1** (*"FAIL — 498 errors across 35 partitions"*, the fatal class being `SameStageReference` at 498; `ci.yml:431-433` throws). Neither path is in a combat-ai lane's fence and neither is protected, so both are routable; both remedies are "fix the generator and regenerate", never a hand-edit of `gk-data/packs/fusion/data/seed/**`.

**Scope of that "FOUR", stated so it is not over-trusted.** The four are complete for the .NET projects this lane
actually ran **in CI's own configuration** — `gk-core/tests/FusionRpg.Guard.Tests` (3 reds, Release) and
`gk-fusion/tests/FusionRpg.Launcher.Tests` (1 red, Release) — and the projects it ran in **Release** and found green are
`FusionRpg.CheatCore.Tests` (41/0) and `FusionRpg.ItemSeedValidator.Tests` (98/0). The larger green readings
(`Core.Tests` 9721/0, `Balance` 210/0, `Match` 182/0, `Server` 858/0, `Data` 1885/0, `Injector` 119/0) were taken in
**Debug**, which is the local default rather than CI's `-c Release`, so they are context rather than a CI claim.
**The Core split is now measured too, and it is clean.** All **65** Core projects beyond `Core.Tests`/`Balance`/`Match`
were run in **Release** (CI's configuration): **64 passed and one appeared to fail — `FusionRpg.Core.ClassSystem.Tests`
at 3 failed / 235 passed — and that failure was the bare-interpreter class, not a red.** Re-running it with `python`
on PATH gives **238 passed / 0 failed**, which is `CAI-find-3`'s pattern reaching a *Core split project*: its
`ReaderCensusTests` spawns a bare `python` (`gk-core/tests/FusionRpg.Core.ClassSystem.Tests/ClassSystem/ReaderCensusTests.cs:193`,
already in that row's inventory) and the shell this lane runs in does not carry it. CI does, so this is not a CI red —
but it is a second, sharper instance of the class: a project that a lane cannot verify locally without a PATH fix.
**Still not measured, and the REASON is now known rather than "an infrastructure error":** `FusionRpg.E2E.Tests`
cannot even be BUILT in this worktree — its Release build fails with `MSB3027`/`MSB3021`, *"Could not copy
`src/FusionRpg.Server/bin/Release/net8.0/FusionRpg.Server.dll` to `bin/Release/net8.0/FusionRpg.Server.dll`"*, after a
run of `MSB3026` retries — i.e. a **file lock**, not a test failure. This machine had **five `FusionRpg.Server.exe`
processes and several `dotnet.exe`** running at the time; none was stopped (they are the owner's or other lanes', and
stopping a server is not this lane's call), so E2E stays unmeasured and the reason is recorded for whoever can run it
on a quiet machine. The web job is unmeasured for the other reason: `npm ci` first (`node_modules` is absent here) and
`npm` is not on this shell's PATH. **So the true CI-red count could still be higher than five**; what is established is
that it is at least five, each with its fix named above, and that the whole Core split is green in Release.

**Two of the three are mechanical once the grant exists, and the third is a one-line re-pin whose cause is now named.** `CAI-guard-1`: the pin at `PlantSideStatusGuardTests.cs:114` is `02B04A25…` (re-pinned 2026-09-21 for CAI1.12), while the file is now **465 lines** hashing to **`E1444DB11BDD6EEFEFDCE9FCC4A0AC8195753FB35DA9835E8FB28799CA6733F8`** — moved by exactly one commit since, **`5e33ad647`** (2026-09-23, "fix(battle): T6 (W11) one gate owns combat.defense.omni"), so the re-pin is the deliberate one the pin exists to force. `CAI-find-6`'s `CiPytestWiringTests`: the registry's `tools-audit-tests` entry is correct and `gk-core/tests/tools/test_audit_program_pipeline.py` exists, so the missing half is a `python -m pytest` step at `working-directory: .` in `ci.yml`. `CAI-find-6`'s `PlayerSpeciesMaterialiseCallerGuardTests`: the expected list needs `"picks.source-below-rank-floor"` (returned by `RpgStore.Fusion.cs:305`), which `FusionInheritancePicksTests.cs:410` already asserts by name.

## Two verification-cost asks (measured 2026-09-23, lane `cai3`)

Not rulings and not blockers — but they are the only remaining items that would change how fast every lane
working on this program can verify itself, and both were measured rather than estimated.

**V1 — `gk-core/src/FusionRpg.Core/Match/**` can be narrowed from 68 projects to five.** It resolves through
`core-fallback`, whose project is the `core` group — **68 projects** at the last count, up from the 39 the
`CAI-tests-1` row recorded — so a one-line lawn-AI edit pays the whole split. The Match family is exactly
five projects (`core-match`, `core-matchadmittests`, `core-matchinjectcontracttests`,
`core-matchruntimetests`, `core-matchvalidatortests`), so a `core-match-group` plus a focused boundary turns
68 into 5. **Owner: `test-verification-boundary`** (the `CAI-tests-1` row names it), and this lane did not
make the edit although it holds the registry file: it does not hold the registry's *policy*, and
under-selection is the dangerous direction.

**V2 — `gk-core/src/FusionRpg.Core/Actions/**` cannot be narrowed by the registry at all.** No project entry in
`gk-core/scripts/verification-boundaries.v1.json` mentions `/Actions` in its file list, and the project that holds
the Actions tests — `gk-core/tests/FusionRpg.Core.Tests` — is itself one of the 68 in the `core` group. A focused
boundary would therefore have to include `core`, which is no narrowing. **The fix is a further split of
`Core.Tests`, not a boundary row** — worth knowing before someone tries V1's shape here.

**What this lane therefore ran for its five Core changes, stated plainly:** `FusionRpg.Core.Tests` 9721/0
(the project holding the combat-ai Core tests) plus `FusionRpg.Core.Balance.Tests` 210/0,
`FusionRpg.Core.Match.Tests` 182/0 and `FusionRpg.Server.Tests` 858/0 for the blast radius — **not** the
68-project group the registry selects. The gap is recorded rather than glossed, and its cause is V1/V2.
