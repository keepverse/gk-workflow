# SP2.2 — blocked at Ask-first: LadderScale.Micro moves two AtomCompiler goldens

## What SP2.2 asked for
Wire `AtomCompiler.cs`'s `powerLadder` kMicro branch (`gk-core/src/FusionRpg.Core/Effects/Atoms/AtomCompiler.cs:618-628`)
through `LadderScale.Micro` (SP2.1's ladder-scale-parity function), the same call
`AptitudeReadFunctions.Magnitude` already uses, so a projected 2b atom resolved at Theta equals the
live aptitude resolve at Theta by construction (map C6, the one `k*P(Theta)` product).

## Correction (recorded after further tracing, same session, before any downstream task relied on the
## original claim): the branch is NOT exercised by real content today
The original version of this section claimed `gk-data/packs/fusion/data/generated/passive-tree/*.json` (40 files, found via
`grep -rl '"kMicro"' data/`) exercises `AtomCompiler.cs`'s `powerLadder`/`kMicro` branch. That is wrong,
caught while investigating SP3.7's own "read the container back through the atom path" acceptance line:

- Those 40 files are `gk-forge/tools/TreeBinder/ReportWriter.cs`'s own **report** shape — a flat `kMicro` field
  on a `NodeAtom`-shaped JSON object (`kindId`/`attachPoint`/`channelId`/`op`/`kMicro`/`scaleAxis`/
  `unitClass`), a **different model** from `AtomRow`/`ContainerRow`. They ARE loaded back, by
  `PassiveTreeCatalogLoader.LoadAtom` (`PassiveTreeCatalogLoader.cs:353`, `var kMicro = GetLong(el,
  "kMicro")`) — but into `NodeAtom.KMicro`, never into an `AtomRow.ParamsJson` `{"powerLadder":
  true,"kMicro":K}` ValueSpec.
- `spec.PowerLadderKMicro` (the field `AtomCompiler.cs`'s branch actually reads) is populated ONLY from
  the literal JSON key `"powerLadder"` inside an `amount` object (`AtomJson.cs:58-83`). `grep -rl
  '"powerLadder"' data/` — the actual key this branch depends on — returns **zero files**. No committed
  seed or generated content anywhere uses this ValueSpec shape.
- The real passive-tree kMicro read path is a THIRD, independent implementation:
  `TreeAtomSource.cs:92`, `(double)atom.KMicro * ladder.Value(...) / 1_000_000.0 * fMultiplier` —
  `double` arithmetic, calling neither `AtomCompiler.cs`'s old truncating code nor `LadderScale.Micro`.
  (Worth a name for a later session — this repo now has three independent `k·P(Θ)/1_000_000`
  implementations: `LadderScale.Micro`, `AtomCompiler.cs`'s own inline code, and `TreeAtomSource`'s
  float version — but reconciling that is out of scope for species-progression and is NOT done here.)

**What still holds, unchanged:** `PowerLadderKMicroTests.cs`'s two exact-value unit tests are real
goldens in the shipped test suite, and they DO move (`2575->2576`, `753->754`) when `AtomCompiler.cs`'s
branch is wired through `LadderScale.Micro`. The spec's own gate ("every moved value is listed... if a
golden moves, stop at Ask-first") is about exactly this — a golden in the suite, not a claim that real
game data changes today. The block stands on that basis alone; the "real content" framing below is
struck as inaccurate, not the underlying decision.

## The change
Old (`checked` long multiply, plain integer division, truncates toward zero):
```csharp
result[key] = checked(spec.PowerLadderKMicro * pThetaValue / 1_000_000);
```
New (SP2.2, calls the SSOT ladder function):
```csharp
result[key] = LadderScale.Micro(spec.PowerLadderKMicro, pThetaValue);
```
`LadderScale.Micro` (`gk-core/src/FusionRpg.Core/Power/LadderScale.cs`) widens through `decimal` and rounds
**once, away from zero** (not truncation) before narrowing back to `long`. That rounding difference
is the entire behavior delta — the multiply-then-divide magnitude is otherwise identical.

## Moved goldens (confirmed, isolated, reproducible)
`dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~PowerLadderKMicroTests"` on top
of this change, 2 of 10 tests fail — both are exact-value pins on this exact formula:

| Test | Expected (old, truncating) | Actual (new, `LadderScale.Micro`) |
|---|---|---|
| `PowerLadderKMicroTests.The_compiler_resolves_kMicro_to_kMicro_times_PowerLadder_Value_over_1_000_000` | 2575 | 2576 |
| `PowerLadderKMicroTests.A_tier_1_gated_deep_style_share_that_rounds_to_zero_kMilli_is_nonzero_at_kMicro` | 753 | 754 |

Both moves are `+1` — the fractional remainder of `kMicro * P(Theta) / 1_000_000` sits at or above
`0.5` for these two fixture inputs, so round-half-away-from-zero bumps up where truncation held flat.

## Blast radius confirmed narrow (not a systemic passive-tree break)
Ran with the change applied, foreground, each green:
- `gk-core/tests/FusionRpg.Core.Tests` filtered to `PassiveTree|TreeAtomSourceParityTests`: 412/412 passed.
- `gk-forge/tests/FusionRpg.TreeBinder.Tests` filtered to `ReportWriterTests`: 14/14 passed (TreeBinder computes
  kMicro coefficients at author time but does not itself call `AtomCompiler.Compile`, so it never
  observes this rounding).
- `gk-core/tests/FusionRpg.Data.Tests` filtered to `TreeCatalogImportTests|TreeCatalogMigrationTests|
  TreeStateReconcilerStoreTests|PassiveTreeImportRunnerTests|TreeRespecStoreTests`: 40/40 passed.

Only `PowerLadderKMicroTests.cs`'s own two exact-integer pins move. No other suite in Core.Tests,
TreeBinder.Tests, or the passive-tree slice of Data.Tests pins an exact kMicro-resolved magnitude.

## Why this is Ask-first, not a unilateral re-bless (H1)
H1 requires re-blessing goldens in the same commit as the change that moves them, with the mover
proven. That part is done here (both moves reproduced and isolated). What is NOT this implementer's
call: whether `+1` on these two fixture magnitudes is the *correct* new number for this branch (parity
with the live aptitude read's rounding rule, ahead of any real content ever using this ValueSpec shape)
or a regression (the old truncating division was the intentionally shipped rounding rule for this
specific compiler branch, and only the *read* side, `AptitudeReadFunctions.Magnitude`, was meant to
gain rounding). Both are defensible as the FIRST real content that DOES use `powerLadder`/`kMicro`
ships — correction above: no shipped content uses it yet, so today this is a decision about which
rounding rule a not-yet-exercised branch should carry forward, not a live player-facing number.

## Decision needed
1. **Adopt LadderScale.Micro here too** — re-bless `PowerLadderKMicroTests.cs`'s two literals
   (2575->2576, 753->754) in the same commit as the AtomCompiler.cs change, and note in
   `gk-core/data/tuning`/docs that TreeBinder-generated `kMicro` coefficients round rather than truncate from
   this version forward.
2. **Keep AtomCompiler.cs's kMicro branch on its own truncating division** — do not route it through
   `LadderScale.Micro`; SP2.1's parity claim (aptitude-read vs projected-atom-resolve) only holds up to
   this 1-unit rounding difference, which SP2.1's own evidence should note as a known bounded delta
   rather than exact byte-identity for this one branch.

## Current state
`gk-core/src/FusionRpg.Core/Effects/Atoms/AtomCompiler.cs`'s SP2.2 edit and the started-state ledger line are
stashed (`git stash list`, entry "SP2.2 in progress: AtomCompiler.cs LadderScale wiring + ledger
started note") rather than committed or left applied in the working tree — the merged branch's test
suites all stay green while this is blocked. Nothing else in this fragment's evidence required
reverting; the stash already isolates the one file the decision affects.
