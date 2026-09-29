# SSH5.10-P2 — the four review notes from the independent H7 read of the `sockets.v2` flip

Disposition: **(a) fixed**, **(b) and (c) declined with reasons** (both are published tuning files), **(d)
needs no change**. The review's own list was incomplete: two `≤ 4` prose sites and two stale TEST pins were
found while doing (a), and the tests were RED at the head.

## (a) Stale prose — fixed

`SocketTuning.cs:55`, `StrainSpliceTuning.cs:14`, `RarityBudgetKeys.cs:59`,
`SocketMaxCheck.cs:11`, `Server/Program.cs:361` ("the structural 4"), `combogen/tuning.py:3,45`,
`combogen/__init__.py:30`, `basetypegen/__init__.py:22`, `gemgen/__init__.py:6` — all re-worded to the current
revision (`SocketTuningFiles.Current` in C#, "the current `sockets` revision" in the Python prose) rather than
to `v2`, so the next publish cannot re-stale them.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| the guard that polices these readers still passes | `dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~TuningRevisionLiteral\|FullyQualifiedName~TuningVersionAgreement"` | **11 passed / 0 failed** | the ten prose sites |
| **extra site found** `SocketTuning.cs:141` ("all ≤ 4") | (above) | re-worded to `≤ StructuralCeiling` | `SocketTuning.cs` |
| **stale test pin 1 found**: `BaseTypeSocketMaxCorpusTests` wrote `socketMax: 3` for `footing` | `dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~BaseTypeSocketMaxCorpus"` | was `Assert.Null()` FAILING (v2 lifts `footing` 2 → 4, so 3 is legal); now the ceiling is read from the loaded revision and the fixture claims `ceiling + 1` → **3 passed / 0 failed** | `gk-core/tests/FusionRpg.Server.Tests/BaseTypeSocketMaxCorpusTests.cs` |
| **stale test pin 2 found**: `CombinationImportTests` used `head-guard` to trigger `host-cannot-hold` | `dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~CombinationImport"` | was `Expected: 1, Actual: 2` recipes accepted (v2's helm holds 4, so the row is legal); the fixture now names `jewel-major` (ceiling 2 in every shipped revision) → **3 passed / 0 failed** | `gk-core/tests/FusionRpg.Server.Tests/CombinationImportTests.cs` |
| whole Server suite after both | `dotnet test gk-core/tests/FusionRpg.Server.Tests` | **758 passed / 0 failed** (was **756 / 2**) | — |
| Core + validator + seedsmith unaffected | `dotnet test gk-core/tests/FusionRpg.Core.Tests -c Release` / `gk-forge/tests/FusionRpg.ItemSeedValidator.Tests` / `PYTHONPATH=gk-forge/tools/seedsmith python -m pytest gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py gk-forge/tools/seedsmith/tests/test_base_types_gen.py gk-forge/tools/seedsmith/tests/test_combogen.py -q` | **15075 / 0**, **97 / 0**, **168 passed** | — |
| build | `dotnet build gk-core/src/FusionRpg.Server -c Release` | **Build succeeded**, 6 warnings | `gk-core/src/FusionRpg.Server/Program.cs` |

## (b) Declined — published tuning files cannot be hand-edited

`gk-core/data/tuning/strain-splice.v1.json:5,8,13` and `gk-core/data/tuning/base-types-gen.v1.json:9` name `sockets.v1.json`
for values that now live in v2. Both are **published** files: AGENTS.md forbids editing `gk-core/data/tuning/*.v{n}.json`
in place (they move through `gk-core/tools/tuning/publish.py`), and a publish cannot rewrite an existing revision —
`publish.py` refuses when the destination exists. The strain-splice prose is rewritten by SSH7.7's
`strain-splice.v2` publish (the same edit that must move the file); the `base-types-gen` `sourceRefs` entry
moves with that domain's own next publish. No commit here changed them.

## (c) Declined — and the trap half discharged

`gk-core/data/tuning/sockets.v2.json:3` carries `"version": 2` while `sockets.v1.json:3` carries `"version": 3`
(v1's field was bumped 2 → 3 by `72607c136`, the species-gear-chain T4 publish, before v2 existed). Same
immutability as (b): neither file can be corrected in place. Mitigation, proved:

| Criterion | Command | Result |
|---|---|---|
| no loader reads the internal `version` field | `grep -rn '"version"\|schemaVersion' gk-core/src/FusionRpg.Core/Items/Sockets/*.cs gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/tuning.py` | **no match** — neither `SocketTuning.Parse` nor `ComboTuning.load` reads it |
| the next publish is monotonic | `sed -n 60,70p;894,895p gk-core/tools/tuning/publish.py` | `latest_version()` takes the max **filename** revision; `new_version = current + 1` → `sockets` v3 writes `version: 3`, and every later revision increases. Monotonic from v2 onward; the v1/v2 pair is history |

## Not proved / open

- **Correction to the SSH5.13 commit message:** it records the validator reading as `2591 warnings`; the
  measured reading is **2589** (3957 → 3960 entries, 2591 → 2589 warnings after the R11 move). The
  fragment's own table carries 2589.
- `verify-change.ps1` exits **1** on this change: its `seedsmith-items` pytest selector stops on the
  pre-existing `test_cli.py::test_actions_check_uses_domain_loader_and_excludes_round_scratch` (an actions
  corpus loader failure, unrelated), so its `core` / `itemseedvalidator` / `server` checks never ran; those
  three were run directly (15075/0, 97/0, 758/0). Its `dal` and `test-substrate` guards printed OK.
- `pwsh -NoProfile -File scripts/run-guards.ps1 -Tier ci`: **18 green / 3 red** — `doc-citations`,
  `magic-numbers`, `population-pin`, the same three as at the base.
- (d) recorded as intentional and left as is, per the review.
