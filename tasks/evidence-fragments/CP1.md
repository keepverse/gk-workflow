# CP1 — the shared core checkpoint (wave 1), measured 2026-09-21

Six rows, measured rather than recalled. Every number below is from the command on its own row.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| CP1.1 one additive score | `grep -rn "class AiScoring" --include=*.cs src/ tests/ tools/` | **0 hits** — the class is gone (`SiegeAi.cs` keeps only the historical name in prose). `CandidateScorer.Score` (`Actions/Ai/CandidateScorer.cs:132`) is the one additive score; `grep -rn "CandidateScorer.ChooseTarget" --include=*.cs src/` finds exactly the two rank walks (`Actions/Ai/CoreIntentPolicy.cs:356`, `Battle/Siege/SiegeAiIntentSource.cs:337`) and both go through it | — |
| CP1.2 DESIGN-GATE row | `grep -n "decides what an actor does" docs/DESIGN-GATE.md` | present at `docs/DESIGN-GATE.md:57`, naming `battle-engine-ssot.md` §3c, `combat-ai-map.md` and the ideal, with the 11 closed vocabularies and their counts | — |
| CP1.2 ideal clock | `sed -n '129p' docs/architecture/combat-ai-ideal.md` | the row reads `KernelDriveHost.NowTicks` / `SimulationClock` for **scheduling** and names `AdvancedEffectClock` as the **wall-clock-seeded status-expiry** clock, "NOT the decision clock" — the two-clock sentence the row asks for | — |
| CP1.3 publishes and readers | `ls gk-core/data/tuning/ \| grep combat-ai\|siege`; `grep -rn "combat-ai.v1.json" --include=*.cs src/`; `grep -rn "siege.v2.json" --include=*.cs src/` | `combat-ai.v1.json`, `siege.v1.json`, `siege.v2.json` all present. `combat-ai.v1.json` is read by **both hosts**: `gk-fusion/src/FusionRpg.Injector/Host/RpgHost.cs:89` and `gk-core/src/FusionRpg.Server/Program.cs:237`. `siege.v2.json` is read by `gk-core/src/FusionRpg.Server/Program.cs:231` | — |
| CP1.4 siege suites | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~Siege"` | **333 passed, 0 failed, 0 skipped** | — |
| CP1.4 unedited | `git diff 28537b6d2^ HEAD -- gk-core/tests/FusionRpg.Core.Tests/Battle/Siege/ \| grep "^-" \| grep -E "Assert\.\|\[Fact\]\|\[Theory\]"` | the only removed assertion lines are (a) CAI1.1's `AiScoring.*` → `CandidateScorer.*` renames, (b) CAI1.10's `SiegeIntentSource` dispatch tests, ported test-for-test to `Actions/IntentRouterTests.cs`, and (c) CAI1.13's two `EffectiveTier` out-of-range `Assert.Throws<ArgumentOutOfRangeException>` — the single permitted throw assertion | — |
| CP1.5 battle goldens | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~BattleGolden"` | **5 passed, 0 failed** | — |
| CP1.5 balance goldens | `dotnet test gk-core/tests/FusionRpg.Core.Balance.Tests --filter "FullyQualifiedName~Dominance\|Category=BalanceGuard\|FullyQualifiedName~ActionSchedule\|FullyQualifiedName~Predictor"` | **66 passed, 0 failed** (the `Balance/**` tests moved to `FusionRpg.Core.Balance.Tests` in lane tvb58's split, so the check runs there) | — |
| CP1.5 unblessed | `git diff --stat 28537b6d2^ HEAD -- gk-core/tests/FusionRpg.Core.Tests/Battle/BattleGoldenTests.cs` | **empty** — the four constants (`StompHash`/`CloseHash`/`WipeHash`/`SeedSweepHash`, `:74-77`) are byte-unchanged since the program's first commit `28537b6d2`, so nothing in wave 1 re-blessed them | — |
| CP1.6 overflow audit | `python gk-core/scripts/audit-overflow.py --targets A3`; `python gk-core/scripts/audit-overflow.py` | `--targets A3` prints **no line** (0 rows for `Actions/Ai/`). Full run at this checkpoint: `A2=0 A3=0 A4=0 A5=0 A6=1`, 0 critical, exit 0 — the one A6 was `Actions/Ai/CoreIntentPolicy.cs:323`, removed later the same day by **`CAI-mask-1`** (see below); the whole-repo total is now `A2=0 A3=0 A4=0 A5=0 A6=0`, 0 findings | `gk-core/src/FusionRpg.Core/Actions/Ai/Lawn/LawnBattleView.cs:156` |
| CP1.6 magic-number audit | `python gk-core/scripts/audit-magic-numbers.py --summary` | table empty, `TOTAL 0 0 0 0 0`, exit 0 — no row for `Actions/Ai/` or anywhere else | — |
| Boundary (this lane's changed path) | `pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Core/Actions/Ai/Lawn/LawnBattleView.cs') -Session combat-ai-3"` | plan `core-fallback (module)` → 12 projects → **15108 passed, 0 failed, 0 skipped**, exit 0 | — |
| Guards | `python gk-core/scripts/guard-battle-responsibility.py`; `... guard-actor-hub.ps1`; `... guard-single-writer.ps1` | `BATTLE RESPONSIBILITY GUARD OK (19 mechanisms, 1588 files scanned)` / `ACTOR-HUB GUARD OK` / `SINGLE-WRITER GUARD OK`, exit 0 each | — |
| Guards (pre-existing red, not this program's) | `pwsh -NoProfile -File scripts/guard-doc-citations.ps1 -Strict` | exit 1: `D1 19`, `D2 2`, `D3 2`, `D4 1` — **0 in `docs/architecture/combat-ai/**`**; every D1 is the notify-rail file move in notification-ssot / npc-story-events / trade-network / world-stage docs, already filed in their owning todos | — |

## The one code change this checkpoint carries

`LawnBattleView.cs:156` was a live A3 row the checkpoint's sixth criterion fails on. `HpMilliOf` returns a
**bounded 0..1000 per-mille ratio**, so `int` is its correct type and the multiply already runs in `long`
(both `ILawnUnitView` HP members are `long`) — the finding is the audit's name heuristic reading `int` +
`hP` in `HpMilliOf` as a magnitude. Fixed with the audit's own authored-exemption mechanism
(`// overflow-bounded:`, 22 existing uses in `src/`), the same shape as
`gk-core/src/FusionRpg.Core/Delve/Events/EventFacts.cs:66`'s `HpMilliOf`, and the final narrowing is now `checked`
per CLAUDE.md ("narrowing is checked or reported"). No guard, allowlist or registry was touched.

## Not proved

- **CP1.6 was not clean when this lane measured it.** The row existed because CAI4.1 (`d4e39791`,
  2026-09-21, lane `combat-ai-2`) added `LawnBattleView.cs` *after* wave 1 closed. No fragment recorded the
  A3 list at the exact CP1 tip, so "wave 1 itself left A3 empty" is inferred from the file's own date, not
  measured. What **is** measured: after this commit `--targets A3` is empty.
- **The A6 row at `gk-core/src/FusionRpg.Core/Actions/Ai/CoreIntentPolicy.cs:323` was open when this checkpoint was
  measured and is now CLOSED.** It was the `unchecked((long)selfFacts.StatusMask)` widening of a `ulong`
  bitfield, which CAI1.13's fragment had already recorded as pre-existing and unchanged by that task; A6's
  line-level filter matched it because `TargetHpMilli` sits on the same line. CP1's sixth row names
  `--targets A3` specifically, so it was never covered by this row — but it was **fixed at the root** the
  same day by `CAI-mask-1` (`AiRowFacts`'s two masks are now `ulong`, so the cast is gone), which is why
  the audit's whole-repo total above is 0 rather than 1.
- **"Unblessed" is proved at the file level for `BattleGoldenTests.cs` only.** The four constants' bytes are
  unchanged; that no other wave-1 commit re-blessed a *different* golden file is not swept here.
- **`gk-forge/tools/DominanceBaseline` was not run** — it is outside this lane's fence. CP1.5 needs no dominance
  number (that is CAI2.3's acceptance), so this is a scope note, not a gap in CP1.
