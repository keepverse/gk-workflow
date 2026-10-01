# Spec: `enforcement-registry`

**Program:** [`solid-enforcement`](../solid-enforcement-map.md) · **Wave 0** · depends on: nothing.

## Objective

Every rule this repo calls binding gets **one row** in one machine-readable file. The row says which
guard enforces the rule, where that guard runs, whether it gates today, and, if it doesn't, which
module brings it to green. A meta-test keeps the file honest, so "we have a rule but nothing enforces
it" becomes a failing test instead of a surprise.

Today that knowledge is spread over three hand-kept lists (CI, `deploy-play`, `verify-change`) and
nobody's head. The inventory behind this program found **9 of 18 guards that CI never runs**, and
nothing anywhere could have reported it.

**User:** every session that adds, wires or retires a guard, plus the owner reading one table to
learn what is actually enforced.

## Design

### The file: `gk-core/scripts/enforcement-registry.v1.json`

It has two sections: a **guard catalog** (what each guard is) and an **invariant table** (what each
rule is enforced by).

```jsonc
{
  "schemaVersion": 1,
  "guards": {
    "single-writer": {
      "script": "gk-fusion/scripts/guard-single-writer.py",
      "tier": "ci",              // ci | local
      "status": "gating",        // gating | backlog
      "backlogModule": null,     // required when status = backlog: a module id in this program's map
      "localReason": null        // required when tier = local
    },
    "class-system": {
      "script": "gk-core/scripts/guard-class-system.py",
      "tier": "ci", "status": "backlog", "backlogModule": "retire-atk", "localReason": null
    },
    "game-profile": {
      "script": "gk-fusion/scripts/guard-game-profile.py",
      "tier": "local", "status": "gating", "backlogModule": null,
      "localReason": "needs the game install (-GameDir); CLAUDE.md hard boundary keeps game binaries off CI runners"
    }
  },
  "invariants": [
    { "id": "dg-4-single-writer", "source": "docs/DESIGN-GATE.md §2.4",
      "guards": ["single-writer"], "unguardableReason": null },
    { "id": "dg-16-cache-trigger-set", "source": "docs/DESIGN-GATE.md §2.16",
      "guards": [], "unguardableReason": "needs a per-cache trigger declaration; no scan can tell which edges a cache should hear" }
  ]
}
```

**Why a guard catalog lives here and not in `verification-boundaries.v1.json`.**
`verification-boundaries.v1.json` already maps 11 guard ids to scripts under its own `guards`
section. Two id→script maps would be a DRY defect in the enforcement layer itself. Dependency
direction settles it: *which invariant a guard enforces and where it runs* is the guard's identity,
and *which path a guard verifies* is a consumer of that identity. So this registry **owns the
catalog**, and `guard-runner` moves `verify-change.py` onto it and removes the duplicate section. This
module only asserts that the two agree (see the meta-test), so it can land without touching
`verify-change`.

### Seeded content

- **The guard catalog** holds all 18 `scripts/guard-*.ps1` plus `session-boundary` →
  `scripts/session-boundary-check.py` (already in `verification-boundaries.v1.json`'s map).
  Initial `tier`/`status` come straight from the inventory in the map:
  - The 8 guards CI already runs: `ci` / `gating`.
  - `debug-scope`, `magic-numbers`, `overflow`, `power`, `stat-pairs`: `ci` / `backlog` →
    `wire-green-guards`. They are green, just unwired.
  - `class-system`: `ci` / `backlog` → `retire-atk`.
  - `commit-policy`: `ci` / `backlog` → `commit-policy-green`.
  - `game-profile`, `injector-compile`: `local` / `gating`, each with its `localReason`.
  - `verification-boundaries`, `session-boundary`: they run through `verify-change`. Seeded as
    `ci` / `gating` if `ci.yml` invokes them, otherwise `ci` / `backlog` → `wire-green-guards`.
    **Measure at build time** rather than trusting this sentence.
- **The invariant table** holds one row per `DESIGN-GATE.md` §2 invariant (1–16) and per `CLAUDE.md`
  hard rule not already covered by one of those: RPG-layer-only, one ActorHub, SOLID, buy-before-build,
  `/plan` paths, contract-not-population, generated-seed, debug-API scope, numeric range, tuning
  immutability, doc citations.
- **Rows for guards this program will build** (`tuning-immutability`, `repo-boundary`,
  `pvz-write-surface`, `vocabulary-mirror`, `population-pin`, `doc-citations`, `srp-file-budget`)
  are **not** pre-seeded as `backlog`. There is no script yet, and a row pointing at a missing file
  is exactly the lie this module refuses. Each of those modules adds its own row when it adds its
  script.

### The meta-test: `gk-core/tests/FusionRpg.Guard.Tests/EnforcementRegistryGuardTests.cs`

It sits beside `CiWiringGuardTests.cs` and uses the same approach: read the tree, assert the contract.

| # | Assertion | Failure it prevents |
|---|---|---|
| R1 | Every `scripts/guard-*.ps1` on disk has a catalog entry, and every entry's `script` exists | A guard written and never registered, which is how nine went unwired |
| R2 | `tier` ∈ {`ci`,`local`}, `status` ∈ {`gating`,`backlog`}. These are closed vocabularies and their sizes are pinned | Inventing a third state such as "advisory" to dodge the policy |
| R3 | `status: backlog` ⇒ `backlogModule` names a module id listed in `solid-enforcement-map.md` | A permanent report-only guard (owner ruling 2) |
| R4 | `tier: local` ⇒ non-empty `localReason` | "Local" used as a quiet exemption |
| R5 | `tier: ci` ∧ `status: gating` ⇒ CI actually runs it: for now, the script path appears in `ci.yml`; after `guard-runner`, the runner runs every `ci`/`gating` row | A registry that claims enforcement CI doesn't do |
| R6 | Every invariant row has ≥1 guard id that exists in the catalog, **or** a non-empty `unguardableReason`, never both and never neither | An invariant quietly covered by nothing |
| R7 | Every guard id in `verification-boundaries.v1.json`'s `guards` map exists in this catalog with the same `script` (removed by `guard-runner` once that map is gone) | Two id→script maps drifting apart |
| R8 | Every catalog guard is named by ≥1 invariant row | A guard enforcing nothing anyone recorded |

**What the test does *not* assert:** the number of guards or invariants. Both are populations that
grow as the program runs. Only the two closed vocabularies in R2 have their sizes pinned, with the
reason written beside the pin (`CLAUDE.md`: the contract, never a count).

## Commands

```powershell
dotnet test tests\FusionRpg.Guard.Tests --filter "FullyQualifiedName~EnforcementRegistryGuardTests"
.\scripts\verify-change.ps1 -Paths @('gk-core/scripts/enforcement-registry.v1.json','gk-core/tests/FusionRpg.Guard.Tests/EnforcementRegistryGuardTests.cs') -Session <id>
```

## Project structure

| Path | Change |
|---|---|
| `gk-core/scripts/enforcement-registry.v1.json` | **new** |
| `gk-core/tests/FusionRpg.Guard.Tests/EnforcementRegistryGuardTests.cs` | **new** |
| `gk-core/scripts/verification-boundaries.v1.json` | add an owner boundary for the two new files |
| `docs/DESIGN-GATE.md` §5 | one checklist line: *"A new rule has a registry row: a guard, or an `unguardableReason`."* |

## Code style

The test follows `CiWiringGuardTests`: plain file reads, `FindRepoRoot()`, and one `[Fact]` per
assertion so a failure names its rule:

```csharp
[Fact]
public void R3_backlog_guard_names_a_module_in_the_map()
{
    var registry = EnforcementRegistry.Load(FindRepoRoot());
    var modules = MapModuleIds(FindRepoRoot());   // parsed from the map's module table
    var orphans = registry.Guards
        .Where(g => g.Value.Status == "backlog" && !modules.Contains(g.Value.BacklogModule ?? ""))
        .Select(g => g.Key).ToList();
    Assert.True(orphans.Count == 0,
        "backlog guards with no owning module (report-only is never a finishing state): " + string.Join(", ", orphans));
}
```

## Testing strategy

- **Falsifiers, one per assertion.** Each rule gets a test that feeds a deliberately broken registry
  (built in memory, never written to disk: test-substrate rule) and asserts that rule fails. A
  meta-test that has never been seen failing proves nothing.
- The real registry passes all eight.

## Boundaries

- **Always:** keep this file the single guard catalog. Every later module in this program edits its
  own row.
- **Ask first:** adding a third `tier` or `status` value. Those are closed vocabularies, and a new
  member is a reviewed change.
- **Never:** pre-seed a row for a script that does not exist yet. Never pin the number of rows.

## Success criteria

- [ ] All 19 current guard scripts are catalogued, with `tier`/`status`/`backlogModule`/`localReason`
      matching the measured inventory.
- [ ] One invariant row per `DESIGN-GATE.md` §2 item and per uncovered `CLAUDE.md` hard rule. Every
      row is guarded or carries an `unguardableReason`.
- [ ] R1–R8 pass on the real tree, and each has a falsifier that fails on a broken tree.
- [ ] `verify-change.py` maps both new files.

## Self-audit — the debate

**Objection: "This is a document pretending to be enforcement. A JSON file doesn't stop anything."**
It stops two things, and nothing else in the repo does. R1 catches a guard written but never
registered. R5 catches a registry that claims CI enforcement CI doesn't perform. Both are exactly
how nine guards ended up unwired. The registry is not the guard: it is the guard *on the guards*,
which is the one layer that was missing.

**Objection: "Parsing the map's module table in a test couples the test to Markdown formatting."**
True, and it is the weakest joint here. The alternatives are worse: a second copy of the module list
in JSON is a DRY defect, and dropping R3 re-opens permanent report-only. **Mitigation:** the parser
reads only the first backtick-quoted token of each row under `## Modules`, and the test fails loudly
("cannot find the module table") rather than passing vacuously when the table's shape changes.

**Objection: "R7 only asserts agreement. Why not delete the duplicate map now?"** Because
`verify-change.py` reads it, and editing the verification path belongs to `guard-runner`, which is
the module that owns *how guards are invoked*. Deleting it here would give one module two
responsibilities. R7 makes the duplication safe until then.

**Objection: "Invariant rows for rules like 'buy before build' can't be guarded."** Then they carry
an `unguardableReason`, and that is the honest outcome. The registry's claim is "everything is
accounted for", not "everything is scannable" (map decision D2).

## Gaps found and closed while writing

- **The first draft pre-seeded rows for the seven future guards as `backlog`.** R1 would have failed,
  because their scripts don't exist, and "fixing" that by loosening R1 would gut it. Changed: each
  future module adds its own row together with its script.
- **`session-boundary-check.py` isn't named `guard-*.ps1`.** R1 would have missed it, and R7 would
  then have failed on a script the catalog doesn't list. Changed: the catalog keys on *ids*, R1 scans
  `guard-*.ps1` **plus** every script any catalog or boundary entry names.
- **R5 needs a transitional form.** Before `guard-runner` exists, CI lists guards by hand. R5 checks
  the script path appears in `ci.yml` until the runner lands, and after that checks the runner reads
  the registry. The test carries both branches, keyed on whether `gk-core/scripts/run_guards.py` exists, so
  this module is green on the day it lands.
- **Found in the program-level review: one guard legitimately runs in its own CI step.**
  `guard-verification-boundaries.py` gates the registry `verify-change` reads, and `ci.yml` isolates
  it deliberately. The schema gains an optional `ciEntry: "own-step"` with a required `ciEntryReason`.
  R5 accepts a direct `ci.yml` call only for such rows, and `guard-runner` skips them under
  `-Tier ci`. Without this, R5 would have forced either a double run or the loss of a documented
  isolation.
