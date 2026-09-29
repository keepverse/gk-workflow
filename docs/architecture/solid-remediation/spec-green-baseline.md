# spec — `green-baseline`

**Module 1 of `solid-remediation`.** Map: [../solid-remediation-map.md](../solid-remediation-map.md).
Register entries: none — this module fixes no register defect. It makes the gate real.

## Objective

Every test project CI runs, every boundary guard, and the web suites are green, so the per-module gate
"ends green" means what it says. Until that is true a later module can be perfect and still fail its own
exit criteria on failures it did not cause, and the gate teaches everyone to ignore it.

**Owner ruling 2026-09-17:** clear the reds; do not freeze a known-red baseline and gate on "no new red".

## Measured starting state — 2026-09-17, `features/mega-merge`

All twelve C# projects CI runs, plus web. This is a reading, not a constant; re-measure, do not trust
this table.

| Project | Result |
|---|---|
| Core | 13940 / 13943 — **3 fail** |
| Data | 1571 / 1576 — **4 fail** |
| **SquadHarness** | 120 / 193 — **73 fail** |
| E2E | 218 / 221 — **3 fail** |
| Server, Guard, CheatCore, Launcher, ItemSeedValidator, AtomImporter, ElementEnumGen, TreeBinder | green |
| web (shell + app) | 144 / 144 |

**83 failures, four projects.** Six of the twelve had never been measured when this program was scoped;
`SquadHarness` alone carried 73 and was invisible.

### Already fixed while measuring (committed)

| Commit | What |
|---|---|
| `57255f4b` | `LadderRestatementGuardTests` scanned build output and `.tmp-*` dirs and died on the first unreadable one. It now scans source only. **It was masking a real T-2 defect**: `generate_themes.py` restated all ten rarity rungs instead of reading `gk-data/packs/fusion/data/seed/rarity/ladder.v1.json` |
| `57255f4b` | `keymapGuard` failed on a *comment* documenting that F10 is deliberately unbound. It strips comments before matching now, so it tests code |
| `fd9f9357` | `FamilyExpansion` emitted `duration = ms / 1000.0`; `duration` is a `ParamKind.Value` and `AtomJson` refuses non-integer magnitudes, so 56 of 70 rows were rejected. It also emitted no `trigger`, which `status.apply` requires — rejecting all 70. **A seed import is all-or-nothing, so one generated file failed the entire tree.** Fixed in the generator, regenerated, never hand-edited |
| `fd9f9357` | Magic-number guard was failing (M1=1, M2=8) and it gates `deploy-play.py`, so no deploy could run |
| `6a8d4c99` | The test pinning the atom defect asserted `duration == 2.0` / `7.683` — it pinned a value the validator refuses. Restated as the contract |

## Work

### 1. `SquadHarness` — 73 failures, one defect ✅ DONE

62 × `BattleRuleset: no 'atk' entry in data/tuning/power-scale.v{n}.json's channels block` and
9 × `ChannelAnchor.UnknownChannelPin: no pin published for channel 'combat.power.omni'`.

**The cause was NOT the missing bootstrap.** This spec first said the defect was
`FusionRpg.SquadHarness.Tests` calling `TuningBootstrap.Configure()` by hand, with three classes never
calling it. That was a hypothesis from reading, and the fix was applied and **measured: still 73/193
failing, an identical split.** A probe then showed the hub *was* configured — with 14 channels whose
keys were `arm1Max`, `combat.power.{variant}`, … and no `atk`.

**The real cause is a name collision that "latest wins" cannot see.**

| File | What it is | Channels |
|---|---|---|
| `power-scale.v2.json` | the **curve** production pins in both hosts | `atk`, `defense` |
| `power-scale.v3.json` | *"Pins, not curves"* — a channel's composed value at the Θ=20 reference, owned by passive-tree-repair; its own `_meta` says **"v2.json frozen"** | 14 template keys, **no `atk`** |

v3 is **not a successor to v2**. Every real consumer loads it by explicit path (`FamilyExpandGen`,
seedsmith `vocab.py`, a Core test). But `LatestTuningFileName` assumes `v{n}` means succession, so the
harness resolved `power-scale` to the pin table and measured a tuning the game never loads.

**Three tools shared the defect** — `SquadHarness`, `HybridViability`, `DominanceBaseline`, all running
`PowerTuningHub.Configure(PowerTuningLoader.Parse(Read("power-scale")))`. Only SquadHarness has tests,
so the other two were silently wrong. All three now pin `power-scale.v2.json`, matching production and
the repo's convention, with the reason recorded at the call site.

The `[ModuleInitializer]` bootstrap was kept: it is the right shape regardless (Core.Tests and
Data.Tests both use it), and it removed 58 hand-written `Configure()` calls plus 5 dead helpers, so no
future class can forget one. It simply was not the defect.

**Evidence:** 193/193; `AggregationTests` 8/8, `CoverageTests` 6/6, `ResolutionTests` 10/10 **run in
isolation**, which is what proves the order-dependence is gone rather than reshuffled; all three tools
build.

### 2. `combat.power.omni` needs no pin — corrected 2026-09-17

An earlier draft of this spec called the 9 `UnknownChannelPin` failures a **content gap** and told the
implementer to decide whether to publish a pin. **That was wrong, and following it would have published a
tuning value this program forbids.**

Traced instead of assumed:

- `ChannelAnchor.AnchorFamilyOf` maps any `combat.power.*` channel to the family **`atk`**
  (`ChannelAnchor.cs:34`).
- `atk` **is** pinned in the shipped tuning — `power-scale.v1.json` and `v2.json` both carry it.
- So the throw is not "this channel is unpinned". It is `tuning.ChannelsOrEmpty` being **empty**, because
  `PowerTuningHub` was never configured in that assembly.

**All 73 SquadHarness failures are the single bootstrap defect in §1.** There is no second defect and no
number to publish.

Production already tolerates a genuinely unpinned channel on purpose: `TreeBinderRun.cs:74` catches
`UnknownChannelPin` and continues — its own comment calls that *"a stated scope gap, never a silently
wrong price"*. `gk-core/tools/SquadHarness/TreeChannelModel.cs:73` does not catch it, which is why the harness
turns a tolerated gap into 9 failures. That asymmetry is deliberate on production's side and is **not** a
defect to fix here.

### 3. Core — 3 failures

`ExpeditionResolverTests.Tier_goldens_are_locked`, and two `GrantedActionTextTests`
(`Every_committed_action_carries_a_description_key_that_resolves_to_real_prose`,
`Every_committed_action_name_key_resolves_and_matches_the_corpus_name`). Diagnose each individually. A
golden that moved is either a real regression or a stale golden; an action-text failure is either a
corpus gap or a stale assertion. **Neither is fixed by re-blessing the expected value** without saying
which of the two it was.

### 4. Data — 4 failures

`StoragePurgeTests.Summary_counts_archives_and_open_runs`,
`ActionCorpusRealContentQualityTests.ImportingTheRealShippedCorpusSucceedsExactlyWhereItsFamiliesResolveAndRejectsHonestlyElsewhere`,
`CacheRetrievalTests.Two_missions_racing_one_cache_partition_rows_exactly_once`,
`CreatureSpeciesImportCliTests.A_real_import_against_the_real_committed_tree_succeeds_and_writes_a_real_store`.

⚠️ Two `CacheRetrievalTests` failures cleared between runs with no code change, so **at least one of this
group is load-sensitive**, not a defect. 31 concurrent `dotnet` processes were observed during one run.
Re-run each in isolation before diagnosing; a flake fixed as a defect is a change with no reason.

### 5. E2E — 3 failures

218 / 221. Diagnose individually. Note for the record: a prior memory claimed E2E was 206/207 failing —
**that is stale and was propagated into this program's first scoping.** The registry issue behind it was
fixed.

### 5b. The web suite — measured, and five failures are out of this program's scope

Measured 2026-09-17 for the first time as a whole (earlier runs in this program were subsets, which is
the same mistake that hid SquadHarness's 73): **`npx vitest run` is 3064/3069, with 5 failing guard
files.**

| Guard | What it refuses |
|---|---|
| `contractGuard` | a REST DTO type imported under `stages/`, `layers/` or `ui/` |
| `delveViews` | the same rule for D5.3's sixteen view types |
| `hexGuard` | a hex colour literal outside `src/theme/` |
| `pendingCopyGuard` | dev jargon in player-facing pending reasons |
| `disabledReasonGuard` | a disabled control with no accessible reason (GG-55) |

They name **24 files**, mostly `ui/actor/**` and `ui/gui-lego/**`. **None is a file this program touched**
— the program's only web changes are `AppShell.tsx`, `stageScrollLock.ts`, `SanctumStage.tsx`,
`OnboardingReveal.tsx` and `keymapGuard.ts`, and none appears in any violation list.

**⚠️ This contradicts this spec's own "Never mark a failure pre-existing and move on", and the
contradiction is resolved by the owner's scope ruling, not by me.** `web/**` is **out of scope for
remediation and in scope for tracking** (owner, 2026-09-16: *"solve the BE first… the FE is ugly, so I
want to refactor it almost completely, so we don't really do it now, but track it"*). Every one of
these five is FE architecture — DTO leakage into the view layer, colour literals outside the theme,
copy and a11y rules — which is exactly what the planned rebuild replaces. Fixing them here is effort
spent twice, and it is remediation work on a surface the owner excluded.

So `green-baseline`'s web criterion is: **no web failure caused by this program**, and the five
pre-existing guard failures are rows in the **FE debt register** (T1.3), which is where the FE program
inherits them. That is a narrower gate than "npm test green", stated openly rather than quietly met.

### 6. Session record and boundary

Create `tasks/sessions/solid-remediation-<date>.json` so `verify-change.ps1 -Session …` is runnable for
every later module, and mark the 14 stale records merged or abandoned so `session-boundary-check.py` is
clean. Owner ruling 2026-09-17: no other agents are on this tree, so the ~15 crossing claims are stale
metadata, not live conflicts. A boundary check that is permanently dirty is one everyone learns to ignore.

## Closed 2026-09-17 — CP0 evidence, and two named load-sensitive tests

| Project | Result |
|---|---|
| Core | 13943 / 13943 |
| Data | 1573 / 1576 in the sweep, **1575 / 1576 alone** (1 skipped) |
| CheatCore 41, Guard 339, Launcher 165, ItemSeedValidator 83, AtomImporter 33, ElementEnumGen 17, SquadHarness 193, TreeBinder 45, Server 550, E2E 221 | all green |
| Guards | 8 / 8, including `guard-magic-numbers` — which had been blocking `deploy-play.py` outright |
| `deploy-play.py --no-server --no-game` | completes, exit 0 |
| Generated trees | `CreatureSpeciesGen --check` clean (904 species); `TreeBinder --check` exit 0; `FamilyExpandGen --check` clean |

**Two tests are load-sensitive under a back-to-back twelve-project sweep and pass in isolation.** Named
here so no later module re-litigates them:

- `CacheRetrievalTests.Two_missions_racing_one_cache_partition_rows_exactly_once` — despite the name it
  spawns no threads; "racing" is two domain missions over one cache, resolved sequentially. Passes
  alone and at class level.
- `CreatureSpeciesImportCliTests.A_stale_committed_file_refuses_the_whole_import_and_writes_nothing` —
  fails as *"CreatureSpeciesImport did not exit within 300s"*, a subprocess **timeout**, not an
  assertion. Passes alone in 2s.

⚠️ **What CP0's closing sentence does and does not claim.** It claims that a module's **scoped**
`verify-change.ps1` can be read as a fact about that module's own change — which holds, because a
scoped boundary runs one project, not twelve back to back. It does **not** claim that a twelve-project
sweep on a loaded machine is deterministic; these two tests say it is not, and 31 concurrent `dotnet`
processes were observed during one such run. A module that sees either of these must re-run it in
isolation before treating it as its own defect.

## Boundaries

- **Always:** fix the generator, never the emitted seed JSON. Restate a test to the contract, never
  re-point it at a new number. Re-run a suspected flake in isolation before calling it a defect.
- **Ask first:** publishing any `gk-core/data/tuning/<domain>.v{n+1}.json` — this program introduces no tunables,
  and the `combat.power.omni` pin is exactly the case that will tempt someone.
- **Never:** mark a failure "pre-existing, out of scope" and move on. This module is the one place where
  that is not available; that is its entire purpose.

## Verification

```powershell
.\scripts\verify-change.ps1 -Paths <changed files> -Session solid-remediation-<date>
```

Exit criteria, all measured in one pass, not remembered from separate ones:

- [ ] All twelve CI C# projects green
- [ ] All six boundary guards green, plus `audit-magic-numbers.py` (it gates `deploy-play.py`)
- [ ] `npm test` green in `gk-web/web/fusion-rpg-web`
- [ ] `SquadHarness.Tests` green **per class**, proving order-independence
- [ ] `session-boundary-check.py` clean
- [ ] `deploy-play.py` runs to completion

## Success criteria

The next module can run `verify-change.ps1` and read the result as a fact about its own change, with no
"except for the known ones" caveat. If that sentence is not literally true, this module is not done.
