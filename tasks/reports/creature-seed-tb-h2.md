# TB-H2 — the retired threat ladder: the seedsmith half fixed, the C# half measured and named

Lane `cs-rank` (session `creature-seed-rank`, branch `cmdc/cs-rank`), 2026-09-23, at the integration tip
`71d91012f`. Row: `tasks/creature-seed-todo.md` TB-H2.
Changed: `gk-forge/tools/seedsmith/seedsmith/ladders.py` (the threat ladder's declaring read moves v1 → v2),
NEW `gk-forge/tools/seedsmith/tests/test_ladders_declaring_reads.py`. The row stays OPEN on its C# half, whose every
reader is on a denied path (named below).

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| The seedsmith half of the row's own claim — "the seedsmith side followed" | `python -m pytest tests/test_ladders_declaring_reads.py -q` (in `gk-forge/tools/seedsmith`) | **4 passed in 1.02 s** — the new test derives the expected version from the files ON DISK, so a v3 without a reader move goes red instead of silently declaring a year-old ladder | `ladders.py`, `test_ladders_declaring_reads.py` |
| …and it was only HALF true | same run | `power/bands.py` (the classifier) read v2, but `seedsmith/ladders.py` — this program's own vocabulary leaf, consumed by `schema.py`'s `THREAT_BAND` — still declared from **v1**. Fixed here; the row's claim is now true of both. | same |
| The move is behaviour-preserving (measured, not assumed) | `python - <<'PY' … compare the two shipped versions … PY` | v1 and v2 have **identical rung ids**, **identical `thetaOffset`** and `inferredDefaultRung: 4`; only `maxScore` differs (`[12,24,120,188,432,720,1800,2400,4920,None]` → `[256,326,414,572,850,1320,2480,4840,9760,None]`). The new test pins that reconciliation. | — |
| Every existing consumer still agrees | `python -m pytest tests/ -q -k "anchor or ladder or threat or band"` (in `gk-forge/tools/seedsmith`) | **315 passed, 1 skipped, 4226 deselected, 1187 subtests passed, 51.22 s** | — |
| The row's third box, first half | `dotnet run --project gk-forge/tools/CreatureSpeciesGen -- --check` | `--check: clean, 904 species match` | — |
| The row's third box, second half | `dotnet run --project gk-forge/tools/CreatureCorpusDump -- --verify gk-data/packs/fusion/data/seed/creatures/_dump` | **FAILED — pre-existing and unrelated to the ladder:** "hash mismatch: manifest declares `cc322647cd0118c72d2dc80826cfe7cea7d02077a59aedfb0bb167319d38a10d`, files on disk hash to `6181dc2d5393e44653b4e7b688633bc3c79b97928183eee645bce15b31c05e0a`". Filed as **CS-R4**. | — |

## The corrected premise — this drift is LATENT, not live

The row's premise is "the corpus classifies against a retired threat ladder". Measured:

- **`ThreatRung.MaxScore` has no consumer in C# at all** — `rg -n MaxScore src tools tests --glob "*.cs"`
  returns exactly one hit, the record's own declaration (`CreatureThreatTuning.cs:7`). The score → rung
  classification lives in Python (`power/bands.py:99`, `rung_for_score`) and **already reads v2**.
- The C# readers load the file and consume `RungIds` / `OffsetFor` / `InferredDefaultRung` only — and those
  are byte-identical between the two versions (table above).

So nothing is misclassified today; what is violated is H7/T5's one-version-per-domain rule, and the risk is
the day a v3 moves a rung id or an offset: eight readers would silently keep the old ladder. That makes the
fix mechanical (a version bump in eight literals) **and** explains why it went unnoticed for three days.

## The exact reader list (the row's own list, corrected by measurement)

Still on v1 — **eight** sites, not seven (the row missed two, and one line number has moved):

| Reader | Line |
|---|---|
| `gk-forge/tools/CreatureRecipeDistributionIndex/Program.cs` | 59 |
| `gk-forge/tools/CreatureQualityReport/Program.cs` | 64 |
| `gk-forge/tools/CreatureSpeciesGen/Program.cs` | 73 (plus output copy naming v1 at 170-171) |
| `gk-forge/tools/CreatureRecipeReconcileInput/Program.cs` | 65 |
| `gk-forge/tools/CreatureSpeciesImport/Program.cs` | 71 |
| `gk-forge/tools/ProveHubCombat/Program.cs` | 81 |
| `gk-core/src/FusionRpg.Server/Program.cs` | **131** (the row cites 124) |
| `gk-fusion/src/FusionRpg.Injector/Host/RpgHost.cs` | **179 — NOT in the row's list at all** |

Also on v1: `gk-forge/tools/_TempSeedSpecies/Program.cs:95` (a scratch tool) and seven Core/Server test files
(`SpeciesExpanderTests.cs:36`, `SpeciesCatalogDiffTests.cs:44`, `CreatureRankTuningTests.cs:22`,
`FusionRankFilterTests`' fixture `RealCorpusFixture.cs:39`, `FusionRankFloorTests.cs:36`,
`DungeonTestFiles.cs:25`, `DelveRoomEncounterTests.cs:64/100/173/241`) — while
`SpeciesBuildPlannerTests.cs:201,402` read **v2**: the same test project consumes both ladders today.

Already on v2: `gk-forge/tools/CreatureBuildPlanGen/Program.cs:62,66`.

## What blocks the C# half (exact)

Every one of the eight is outside this lane's fence — `tools/**` except `gk-forge/tools/seedsmith/**`, and
`gk-core/src/FusionRpg.Server/**` / `gk-fusion/src/FusionRpg.Injector/**` (the latter re-proven this segment:
`verify-change -Paths gk-core/src/FusionRpg.Server/FusionEndpoints.cs -Session creature-seed-rank` answers
`path is outside session scope`). No in-fence change can move them, so the row stays open on them.

## Findings filed from this increment

- **CS-R4 (owner: this program, module 1 `corpus-dump`)** — the committed `gk-data/packs/fusion/data/seed/creatures/_dump`
  fails its own `--verify` (numbers above). `CreatureCorpusDump` needs the server's real DB to re-dump and
  has no re-stamp flag (measured from its usage block), so fixing it needs either a live/owner DB run or a
  sanctioned manifest re-stamp decision; hand-editing the manifest would be the forbidden hand-edit of
  generated data. Consequence today: `tests/test_preflight.py::test_hash_matches_the_real_committed_dump`
  is red (a pre-existing red this lane had only mentioned in Task 3's evidence, never filed) and the
  preflight's `dump-is-current` gate cannot pass.
- **CS-R5 (owner: `test-verification-boundary`)** — `TuningVersionAgreementGuardTests.DefaultRoots` is
  `src` + `gk-forge/tools/seedsmith/seedsmith`, so the guard that exists to catch exactly this drift never scans
  `tools/**` (seven of the eight lagging readers live there) or `tests/**`. Its own doc says the roots are
  "where a domain's readers live: production C# and the seedsmith package" — the `tools/**` corpus pipeline
  IS production C#. Not fixed here: widening the roots now would turn a green guard red for a defect this
  lane cannot fix (the guard's own doc forbids asserting agreement before the readers agree).
