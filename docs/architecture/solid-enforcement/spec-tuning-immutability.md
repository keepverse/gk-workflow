# Spec: `tuning-immutability`

**Program:** [`solid-enforcement`](../solid-enforcement-map.md) · **Wave 2** · depends on:
`guard-runner`.

## Objective

`AGENTS.md` and `CLAUDE.md` both state it: *"`gk-core/data/tuning/**` is authored but never hand-edited in
place: a balance change publishes `v{n+1}` through `gk-core/tools/tuning/publish.py`."* Nothing enforces it.
The cost is measured:

- **2026-09-17, `a60706c0`:** the owner's lawn-permadeath ruling was applied by editing
  `lawn-attrition.v1.json` in place, under a `_meta` note that granted itself an exemption. Found by
  an audit a day later, and fixed on 2026-09-18 (`44a18fdc`) by restoring v1 and publishing v2.
- **2026-09-12:** four test-output files (`loopwarntest13c4c662.v{1,2}.json`,
  `loopwarnteste194b09f.v{1,2}.json`, 62–65 KB each) were committed into the balance surface by bulk
  "update seeds" commits (`dcabac32`, `52713f44`). They are now copied into every test and tool
  `bin/` (see any `*.csproj.FileListAbsolute.txt`).

This module adds the guard that makes both impossible, and clears the backlog (the four files, plus
the test that writes them) before the guard gates.

## Design

### The guard: `gk-core/scripts/guard-tuning-immutability.py`

It is diff-based and shaped exactly like `guard-generated-seed.py` (same `-BaseRef` / `-Range`
parameters, same working-tree default), so the runner's `{ciRange}` substitution serves it unchanged.
One convention for "compare this change against its base", not two.

| Rule | Check | Failure it prevents |
|---|---|---|
| **T1 — published values are immutable** | A **modified** `gk-core/data/tuning/<d>.v<n>.json` may change only keys under `_meta` (a normalised JSON comparison with `_meta` removed must be equal) | The `a60706c0` in-place edit |
| **T2 — versions are contiguous** | An **added** `<d>.v<n>.json` requires `<d>.v<n-1>.json` to exist (n > 1) | Publishing v5 over a missing v4, or a hand-rolled version number |
| **T3 — no deleted versions** | A **deleted** `gk-core/data/tuning/*.json` fails | Losing the revert target T4 exists to provide |
| **T4 — only real domains** | Every file matches `^[a-z0-9-]+\.v\d+\.json$` **and** its domain is not listed in `gk-core/scripts/tuning-domain-denylist.v1.json` | Test pollution: throwaway domains named `loop*test*` |

**T4's denylist is a pattern list, not a domain allowlist.** An allowlist of 104 domains is a
population that grows every time a program adds a domain, which is exactly the kind of number the
contract-not-population rule forbids pinning. The denylist holds shapes that are never real, such as
`^loop.*test` and `^tmp-`, and is a small closed vocabulary.

**The sanctioned escape for T1/T3:** a commit whose message contains
`tuning-immutability: correction <reason>` passes T1/T3 **for the files it names**. It exists for
exactly one case: undoing an in-place edit, the way `44a18fdc` restored `lawn-attrition.v1`. The guard
prints every use loudly, so it is visible in review and cannot be silent.

### Clearing the backlog

1. **Delete the four `loopwarntest*` files.** This is itself a T3 violation, so the deletion commit
   carries the correction marker (*"test pollution, never a published domain"*).
2. **Fix the test that writes them.** `ResidualFitLoopTests` publishes throwaway domains
   (`loopchaintest…`, `loopwarntest…`) into the **real** `gk-core/data/tuning/`, and cleans up with
   `try { File.Delete(…); } catch { /* best effort */ }`. That breaks two rules at once. The
   test-substrate rule says *"a failed temp-delete is a **failure**, never `catch { }`"*. And writing
   into a tracked tree means a crashed or killed run leaves files behind, which is how the four got
   committed. Fix:
   - The residual-fit tool gains `--tuning-dir <path>` (default: `gk-core/data/tuning`). Its publish step
     writes there, and **only** there, taking its target from the same input as its measurement. That
     is the lesson recorded in memory `feedback_measure-input-must-drive-publish-target`.
   - The test copies `aptitudes.v1.json` into a **temp directory** and passes `--tuning-dir`, then
     deletes with a checked delete that fails the test if the delete fails (the disk *is* the thing
     under test here, so a temp dir is legitimate; a swallowed failure is not).
3. **Extend `guard-test-substrate.py`, don't fork it.** Its swallowed-delete rule covers
   `Directory.Delete`. Add `File.Delete` inside a `try` whose `catch` is empty or comment-only. This
   is the pattern that let this leak through, and extending the existing guard is the Open/Closed way.
   Clear any other hits it finds in this module (green-first).

### Registry

`tuning-immutability` added as `ci` / `backlog` → this module when the script lands, then
`ci` / `gating` once the backlog is clear. `test-substrate` stays `gating` throughout. Its extension
lands only after its own new hits are cleared, in the same commit.

## Commands

```powershell
python gk-core/scripts/guard-tuning-immutability.py                    # working tree vs HEAD
python gk-core/scripts/guard-tuning-immutability.py -Range HEAD~1..HEAD
.\scripts\run-guards.ps1 -Only tuning-immutability,test-substrate
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~ResidualFitLoopTests"
dotnet test tests\FusionRpg.Guard.Tests --filter "FullyQualifiedName~TuningImmutability"
```

## Project structure

| Path | Change |
|---|---|
| `gk-core/scripts/guard-tuning-immutability.py` | **new** |
| `gk-core/scripts/tuning-domain-denylist.v1.json` | **new** (closed pattern list) |
| `gk-core/tests/FusionRpg.Guard.Tests/TuningImmutabilityGuardTests.cs` | **new** |
| `data/tuning/loopwarntest*.json` (4) | **deleted** under the correction marker |
| residual-fit tool (the script `ResidualFitLoopTests.Run` invokes; locate at build time) | `--tuning-dir` |
| `gk-core/tests/FusionRpg.Core.Balance.Tests/Balance/ResidualFitLoopTests.cs` | temp dir plus checked delete |
| `gk-core/scripts/guard-test-substrate.py` | `File.Delete` swallowed-catch rule |
| `gk-core/scripts/enforcement-registry.v1.json` | new row |

## Code style

The normalised comparison T1 needs, in the guard's PowerShell:

```powershell
function Strip-Meta($json) {
    $o = $json | ConvertFrom-Json -AsHashtable
    $o.Remove('_meta') | Out-Null
    return ($o | ConvertTo-Json -Depth 64 -Compress)
}
if ((Strip-Meta $before) -ne (Strip-Meta $after)) {
    $failures += "T1 $path — a published tuning version changed outside _meta. Publish v$($n+1) through gk-core/tools/tuning/publish.py instead."
}
```

`ConvertTo-Json` key order follows the input. Both sides come from the same file shape, so the order
is stable. **The build must confirm this against a real round-trip.** If it is not stable, sort keys
recursively before comparing.

## Testing strategy

`TuningImmutabilityGuardTests` builds a **temporary git repository** (checked cleanup), commits a
`d.v1.json`, and asserts:

- A `_meta`-only edit passes, and a value edit fails T1.
- Adding `d.v3.json` without `d.v2.json` fails T2; adding `d.v2.json` passes.
- Deleting `d.v1.json` fails T3, and passes with the correction marker in the commit message.
- Adding `loopfootest.v1.json` fails T4.

On the real tree: the guard passes at HEAD once the backlog commit lands, and
`guard-test-substrate` passes with its extension.

## Boundaries

- **Always:** publish balance changes through `publish.py`, extending it when a shape is missing.
- **Ask first:** adding a pattern to the denylist, or using the correction marker for anything except
  undoing an in-place edit or removing pollution.
- **Never:** turn the denylist into a domain allowlist. Never write test output under `data/`.

## Success criteria

- [ ] The four pollution files are gone and nothing recreates them. The test publishes to a temp dir
      and fails on a failed delete.
- [ ] T1–T4 each have a passing and a failing case in the temporary-repository test.
- [ ] The guard gates in CI. `guard-test-substrate` catches swallowed `File.Delete`, with its backlog
      cleared.

## Self-audit — the debate

**Objection: "The correction marker is a hole in the wall."** It is a door with a sign on it. Without
it, the only way to undo an in-place edit is to publish v{n+1} containing v{n-1}'s values, which
leaves the bad version in history as if it were legitimate. That is exactly the "no file to revert
to" problem, moved one version up. The marker is loud, scoped to named files, and has one documented
purpose.

**Objection: "T1's `_meta` exemption lets someone hide a value inside `_meta`."** A loader never reads
`_meta`: every tuning loader in the repo ignores it. A number hidden there changes nothing. The
exemption exists so annotations like `restored20260918` can be added to an old version, which is
exactly what `44a18fdc` needed.

**Objection: "Why not fix `publish.py` so tests can't write to the real directory?"** Because the leak
is not `publish.py`'s. The residual-fit tool chose its output directory, and the test pointed it at
the tracked tree. The fix goes where the choice is made: the tool takes an explicit directory, and the
test passes a temp one.

## Gaps found and closed while writing

- **An allowlist of domains** was the first draft of T4. It would pin a population (104 domains and
  growing). Replaced by a denylist of never-real shapes.
- **Deleting the pollution trips the new guard's own T3.** Resolved by landing the deletion with the
  correction marker, in the same commit that introduces the marker. No module-internal red state.
- **The root cause was not the files but a swallowed delete,** which the existing test-substrate guard
  did not cover because it only knew `Directory.Delete`. Extended here, so the class is closed, not
  just this instance.
- **Key-order stability** of `ConvertTo-Json` is assumed by T1. It is flagged for verification at
  build time, with a fallback.
