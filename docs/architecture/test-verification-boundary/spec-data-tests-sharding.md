# Spec: `data-tests-sharding`

**Program:** [`test-verification-boundary`](../test-verification-boundary-map.md) · depends on:
nothing · closes map gap G13 · the ideal's lever 2. **Status: specified; the CI half is approved by
R15** ("the `Data.Tests` line replaced by the sharded runner with its catch-all shard", map §7.1 E4).

## Objective

`FusionRpg.Data.Tests` is the measured burden: 96.7% of summed test time (`test-burden-audit.md` §1).
The cause is a **process-global** mutex in SQLite's in-memory VFS, so its stores cannot parallelise
inside one process at all; two concurrent `dotnet test` processes over disjoint halves ran in **23.9s
vs 47.4s** sequential (`test-architecture-audit.md` §5). A thread cap is the rejected symptom
treatment (`test-burden-audit.md` §6, first row, marked superseded). CI runs Data.Tests as one process
(`ci.yml:155`).

This module makes "N concurrent processes over a complete, disjoint partition" a reusable runner, and
adopts it in CI and in local module-level Data runs.

**User:** CI; any contributor whose change resolves to `data-fallback`
(`verification-boundaries.v1.json:1667`).

## Design

### H1 — the shard manifest: `gk-core/scripts/test-shards.v1.json` (new)

```jsonc
{
  "schemaVersion": 1,
  "projects": {
    "data": {
      "maxParallelThreads": 2,           // intra-process optimum, test-burden-audit.md §2 table
      "shards": [
        { "id": "a", "prefixes": ["FusionRpg.Data.Tests.Items.", "FusionRpg.Data.Tests.Delve."] },
        { "id": "rest", "remainder": true }
      ]
    }
  }
}
```

- `prefixes` are namespace or class prefixes **ending in `.`**, turned into
  `FullyQualifiedName~<prefix>` joined with `|`. **`~` is a substring (contains) match, not a
  prefix match.** That is VSTest's filter semantics, and the design leans on it only where it is
  safe. Every FQN in this assembly starts with `FusionRpg.Data.Tests.`, so a key that starts with
  that root and ends in `.` can only match inside the namespace/class it names. One consequence,
  stated so nobody is surprised: a nested test class's FQN is `Outer+Inner.Method`, so a class key
  `…Outer.` does not match it, and it lands in the remainder. That is harmless to completeness and
  only costs balance.
- Exactly one shard is `remainder`. Its filter is the conjunction `FullyQualifiedName!~<p>` over every
  prefix of every other shard. **Completeness is by construction:** the remainder is the exact
  complement of the union of the named shards (the same predicates, negated), so a test in no named
  shard is in the remainder. A new test class can never fall out of CI, and a stale or mistyped
  prefix only moves tests into the remainder. **Disjointness between named shards** is a rule
  (H-T2: no key is a substring of another key) **and** a per-run check (H2 step 4), because
  contains-matching makes a rule over the keys alone weaker than it looks.
- Data.Tests has 109 root-namespace files and 16 sub-namespaces (readings), so root classes are named
  by class prefix when a shard needs them. A class list is a population, but the remainder makes a
  stale list harmless to correctness — it only costs balance, which is re-measured, not asserted.
- **Initial shape: 2 shards**, the only count measured (`test-architecture-audit.md` §6: "4 or 8
  shards were not tried"). A build-time task measures 2 vs 4 on this machine with an idle-ish box and
  records the walls in the manifest's `_meta.measured` note; the count is structural CI config
  (ideal §"Tunables"), not `gk-core/data/tuning`.
- `maxParallelThreads` is passed per shard run as `-- xUnit.MaxParallelThreads=<n>`, so it applies to
  sharded runs only; unsharded default-profile runs are unchanged.

### H2 — the runner: `gk-core/scripts/test_sharded.py` (new)

`-Project <csproj path>` `[-Configuration Release] [-ExtraFilter <profile filter>]`. The manifest's
`projects` keys are registry project ids; the runner resolves the given csproj to its id through the
verification registry's `projects` map and refuses a csproj with no shard entry.

1. `dotnet build <csproj> -c <cfg>` once (never test stale assemblies — `test-burden-audit.md` §5.2).
2. Start one process per shard: `dotnet test <csproj> -c <cfg> --no-build --filter "<shard filter>[&<extra>]"
   --blame-hang --blame-hang-timeout 10min --logger "trx;LogFileName=<shard>.trx" -- xUnit.MaxParallelThreads=<n>`,
   each with its own `--results-directory` under one per-run temp root.
3. Wait for all; print per-shard exit code and wall; exit non-zero if any shard failed, naming it.
   No early kill of siblings — a report of every failing shard is worth more than seconds.
4. **Overlap check, every run:** read each shard's TRX and collect executed test ids. If any id
   appears in two shards, exit non-zero naming the id and both shards. A test run twice is not a lost
   test, but it double-counts and hides a manifest defect. The temp root is removed in `finally`
   with a throwing delete (`testing-standard.md` R3).
5. An empty named shard (zero tests executed, e.g. every class under a prefix was deleted) is a
   manifest defect and fails the run, the same rule as pytest's exit 5 in `python-test-lane` D3.
   An empty **remainder** is legal.

`-ExtraFilter` lets the local default profile reuse it (`Category!=DiskSemantics&Category!=Heavy`,
owned by `gk-core/scripts/test_fast.py:81` — the runner reads it from there rather than restating it).

### H3 — adoption

- **CI (approved, R15; map §7.1 E4):** `ci.yml:155-156` becomes exactly

  ```yaml
          .\scripts\test-sharded.ps1 -Project gk-core/tests/FusionRpg.Data.Tests/FusionRpg.Data.Tests.csproj
          if ($LASTEXITCODE -ne 0) { throw "FusionRpg.Data.Tests failed (sharded)" }
  ```

  The script ends with `exit <code>`, so `$LASTEXITCODE` carries its verdict into the existing
  per-line pattern. The csproj path stays literally on the CI line, so `CiWiringGuardTests.cs:45-71`
  still finds it, and truthfully, because the project is run there. No `--filter` appears in
  `ci.yml`, so the no-filter assertion (`:210-219`) is untouched **and still true in spirit**: the
  partition is complete. The leak-alarm re-run (`ci.yml:196`) is left as is. It reuses the Release
  build that step 1 of the runner produced, which is what its `--no-build` needs.
  `release.yml:44` keeps its plain `dotnet test` (map §7.1).
- **Landing order:** the manifest, runner and H-T1–H-T4 land first, with the one-time completeness
  proof. The CI line lands in a second commit, and H-T5 lands with it.
- **Local:** when `verify-change.py` selects a **module**-level check on a project that has a shard
  manifest entry, the runner calls `test-sharded.ps1 -ExtraFilter <default profile>` instead of one
  `dotnet test`. Focused (`VerificationId`) runs are unchanged — they are small.

## Commands

```powershell
.\scripts\test-sharded.ps1 -Project gk-core/tests/FusionRpg.Data.Tests/FusionRpg.Data.Tests.csproj     # full profile, CI shape
.\scripts\test-sharded.ps1 -Project gk-core/tests/FusionRpg.Data.Tests/FusionRpg.Data.Tests.csproj -ExtraFilter "Category!=DiskSemantics&Category!=Heavy"
dotnet test tests\FusionRpg.Guard.Tests -c Release --filter "FullyQualifiedName~TestShardManifestTests"
```

## Project structure

| Path | Change |
|---|---|
| `gk-core/scripts/test-shards.v1.json` | (new) |
| `gk-core/scripts/test_sharded.py` | (new) |
| `gk-core/scripts/verify-change.py` | module-level runs on a sharded project delegate to the runner |
| `gk-core/scripts/verification-boundaries.v1.json` | owner boundary for the two new files (`guard` project, `guard.test-shards` VerificationId) |
| `gk-core/tests/FusionRpg.Guard.Tests/TestShardManifestTests.cs` | (new) |
| `.github/workflows/ci.yml:155-156` | the two lines above (approved, R15) |
| `docs/contributing/testing-standard.md` §6 "Wall-clock is its own axis" | one paragraph: the sharded runner is the process-boundary lever |

## Code style

```powershell
$named  = @($shards | Where-Object { -not $_.remainder })
$filter = if ($shard.remainder) {
    ($named.prefixes | Sort-Object | ForEach-Object { "FullyQualifiedName!~$_" }) -join '&'
} else {
    ($shard.prefixes | Sort-Object | ForEach-Object { "FullyQualifiedName~$_" }) -join '|'
}
if ($ExtraFilter) { $filter = "($filter)&($ExtraFilter)" }
```

## Testing

`TestShardManifestTests` (Guard, reads the committed manifest — no store, no disk writes):

| # | Asserts |
|---|---|
| H-T1 | every project entry has exactly one `remainder` shard |
| H-T2 | every prefix starts with the project's root namespace and ends with `.`; no prefix is a **substring** of another (contains semantics) |
| H-T3 | every namespace prefix is declared by some `namespace` line, every class prefix by some class, in the project's sources (join) |
| H-T4 | shard ids unique; project ids exist in the verification registry's `projects` |
| H-T5 | the CI Data.Tests line invokes `test_sharded.py` with the csproj path, and the next line is the exit check (lands with the CI commit) |
| H-T6 | runner logic over **planted TRX files** (no `dotnet test`): an id in two shards fails; an empty named shard fails; an empty remainder passes |

Never asserted: tests per shard, shard walls, number of shards — readings. The one-time
**completeness proof** on the real project is a Success criterion, and it compares **sets, not
counts** (`validation-ssot.md`; the leak alarm's own set-diff rule, `ci.yml:193-194`). The union of
the shards' executed test ids must equal the id set of one unsharded run with the same filter, and
the pairwise intersection must be empty. A count match could hide one test lost and another run
twice. The run is recorded in the commit body.

## Boundaries

- **Always:** build once, then `--no-build` shards; report every shard; keep the remainder shard;
  check overlap on every run.
- **Ask first:** none. The `ci.yml` edit is approved (R15).
- **Never:** a thread cap as the fix; a shard filter written into `ci.yml`; a shard selected by
  `Category` (that would change *which* tests run, not *how*); converting in-memory stores to files to
  gain parallelism (`test-architecture-audit.md` §6 says not without measurement).

## Success criteria

- [ ] `test-sharded.ps1 -Project gk-core/tests/FusionRpg.Data.Tests/FusionRpg.Data.Tests.csproj` is green on a clean tree, and
      the union of its shards' executed test ids equals an unsharded run's id set, with no id in two
      shards (recorded once, as a reading).
- [ ] Wall-clock for 2 and 4 shards measured and written to `_meta.measured`; the manifest uses the
      faster count.
- [ ] A local `data-fallback` change runs the sharded runner with the default-profile filter.
- [ ] H-T1–H-T4 and H-T6 green; H-T5 green in the CI commit; the first CI run after it is green.
- [ ] Verified with `.\scripts\verify-change.ps1 -Paths gk-core/scripts/test-shards.v1.json,scripts/test-sharded.ps1,scripts/verify-change.ps1,gk-core/tests/FusionRpg.Guard.Tests/TestShardManifestTests.cs -Session <id>`.

## Open questions

None. The CI edit was approved by R15.
