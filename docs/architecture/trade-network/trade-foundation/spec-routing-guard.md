# Spec: `routing-guard`

**Status: written against shipped code 2026-09-19.** Every `file:line` below was opened this session on
`features/mega-merge`. Module id `routing-guard`, §2.3 of the
[trade-foundation map](../trade-foundation-map.md) (approved 2026-09-19; no dependencies). Umbrella
invariant 8 ([../../trade-network-map.md](../../trade-network-map.md) §5): *"routing never calls the
O(V⁴) `ReconnectionCost` sweep"*. Ideal §9.2 rule 3.

## Objective

`ReconnectionCost` is an all-pairs sweep that takes 606–700 ms at 128 nodes and already runs per map-view
request. Logistics must recompute paths on graph change only, bounded. This module lands a **source-scan
guard before the logistics namespace exists**, so the first routing file is born under it: no file in a
guarded path may reference `ReconnectionCost`, and no new caller may appear anywhere outside an
allow-list that can only shrink.

Success looks like: a falsifier file containing `ReconnectionCost.For(` under a guarded path turns the
guard red; the same text inside a comment does not; the guard is catalogued, named by an invariant row,
and run by the CI guard runner.

## Scope and non-goals

In scope: `scripts/guard-logistics-routing.ps1`, its registry `scripts/logistics-routing.v1.json`, its
falsifier tests, one catalog entry and one invariant row in `gk-core/scripts/enforcement-registry.v1.json`, one
verification-boundary row.

Not in scope: changing any current caller; optimising `ReconnectionCost`; the path cache itself
(`logistics-flow` `path-cache`).

## What already exists

### Built

| Finding | Evidence |
|---|---|
| The sweep, O(V⁴) | `gk-core/src/FusionRpg.Core/World/Topology/ReconnectionCost.cs:18-19` |
| Measured 606.5–700.0 ms at 128 nodes | `docs/architecture/world/spec-world-topology.md:57-63` |
| Three code callers | `gk-core/src/FusionRpg.Core/World/Ai/SeveranceScore.cs:32`; `gk-core/src/FusionRpg.Core/World/Ai/ValueMap.cs:167`; `gk-core/src/FusionRpg.Server/WorldEndpoints.cs:864` |
| Two more files name it only in doc comments | `gk-core/src/FusionRpg.Core/World/Topology/AllPairsCost.cs:11`; `gk-core/src/FusionRpg.Core/World/Topology/ArticulationPoints.cs:7` |
| Shared comment-and-string stripper for guard scripts | `gk-core/scripts/cscan.py:246` (`strip_comments_and_literals_preserving_layout`), `gk-core/scripts/guard-battle-responsibility.py:101` (`source_files`) |
| Precedent: an ownership-shaped guard with its own JSON registry and a `-Root`/`-RegistryPath` override for fixtures | `gk-core/scripts/guard-battle-responsibility.py:1-40`; its tests drive it as a process with a fixture root, `gk-core/tests/FusionRpg.Guard.Tests/BattleResponsibilityGuardTests.cs:22-60` |
| The enforcement registry catalogues **scripts**: `guards` is a map of id → `scripts/guard-*.ps1`, and R1 fails an uncatalogued guard on disk; R6 needs every invariant guarded xor reasoned; R8 needs every guard named by an invariant | `gk-core/scripts/enforcement-registry.v1.json` (`guards`, `invariants`); `gk-core/tests/FusionRpg.Guard.Tests/EnforcementRegistryGuardTests.cs:53`, `:177`, `:199` |
| CI runs every gating `ci` guard through one runner | `gk-core/.github/workflows/ci.yml:422-433` (`run_guards.py -Tier ci`) |

### Real gap

No guard names `ReconnectionCost`.

### Correction to the map

The map (§2.3) placed the guard in `tests/FusionRpg.Guard.Tests/LogisticsRoutingGuardTests.cs` with
"one row" in the enforcement registry. A registry row cannot name an xunit test: guard ids resolve to
`scripts/guard-*.ps1` entries only. So the guard is a **script**, catalogued and run by
`run_guards.py`, and the xunit file holds its falsifiers — the `battle-responsibility` shape.

## Design

### 1. Registry — `scripts/logistics-routing.v1.json` (new, hand-authored)

```json
{
  "schemaVersion": 1,
  "symbol": "ReconnectionCost",
  "guardedPaths": [ "src/FusionRpg.Core/World/Logistics/**" ],
  "allowedCallers": [
    "gk-core/src/FusionRpg.Core/World/Ai/SeveranceScore.cs",
    "gk-core/src/FusionRpg.Core/World/Ai/ValueMap.cs",
    "gk-core/src/FusionRpg.Server/WorldEndpoints.cs"
  ],
  "_meta": { "owner": "docs/architecture/trade-network/trade-foundation/spec-routing-guard.md" }
}
```

`guardedPaths` is a list so `trade-ai` adds `src/FusionRpg.Core/World/Ai/Trade/**` in its own change
(ask T-A4) without touching the script. `ReconnectionCost.cs` itself is exempt by construction (it
declares the symbol; the scan looks for uses of `ReconnectionCost.` member access).

### 2. The scan — `scripts/guard-logistics-routing.ps1`

1. Load the registry; enumerate `*.cs` under `src/` with `Get-GuardSourceFiles`.
2. Strip comments and string literals with `Remove-CSharpCommentsAndStrings`.
3. For each file with a remaining match of `\bReconnectionCost\s*\.`:
   - under a guarded path → violation *"routing must not call ReconnectionCost (trade-network invariant 8)"*;
   - elsewhere and not in `allowedCallers` → violation *"new ReconnectionCost caller — add it only with a
     reason, the list may only shrink"*.
4. An `allowedCallers` entry whose file no longer references the symbol → violation *"stale allow-list
   entry — remove it"*. That is what makes the list shrink-only: a caller that stops calling must leave.
5. Exit 1 with one line per violation; exit 0 otherwise. Parameters `-Root` and `-RegistryPath` exist so
   tests run it against a fixture tree.

### 3. Enforcement registry

- `guards["logistics-routing"] = { "script": "scripts/guard-logistics-routing.ps1", "tier": "ci",
  "status": "gating", "backlogModule": null, "localReason": null }`.
- `invariants += { "id": "tn-routing-no-reconnection-cost", "source":
  "docs/architecture/trade-network-map.md §5 invariant 8", "guards": ["logistics-routing"],
  "unguardableReason": null }`.

## Tunables

None.

## Acceptance criteria (contract)

1. A fixture tree with `ReconnectionCost.For(` in a file under a guarded path makes the guard exit 1 and
   name that file.
2. The same text inside a `//` comment, a `///` doc comment, a `/* */` block or a string literal makes it
   exit 0.
3. A fixture caller outside every guarded path and absent from `allowedCallers` makes it exit 1.
4. An `allowedCallers` entry whose file has no remaining reference makes it exit 1.
5. On the real tree the guard exits 0.
6. The allow-list names **paths**, never a count; no test asserts how many callers exist.
7. `EnforcementRegistryGuardTests` R1, R5, R6 and R8 pass with the new entry and row.

## Test plan and verification boundary

- `tests/FusionRpg.Guard.Tests/LogisticsRoutingGuardTests.cs` (new),
  `[Trait("VerificationId", "guard.logistics-routing")]`, driving the script as a process against fixture
  trees (the disk is the thing under test, which the test-substrate rule allows; each fixture is deleted
  and a failed delete fails the test).
- `gk-core/scripts/verification-boundaries.v1.json` owner row `guard-logistics-routing`: paths
  `scripts/guard-logistics-routing.ps1`, `scripts/logistics-routing.v1.json`, the test file; project
  `guard`; verificationId `guard.logistics-routing`; guards `["logistics-routing"]`. The registry edit
  already maps to `enforcement-registry` (`guard.enforcement-registry`), confirmed by
  `verify-change.ps1 -PlanOnly` this session.
- `tests/FusionRpg.Guard.Tests/LogisticsRoutingGuardTests.cs` (new),
  `[Trait("VerificationId", "guard.logistics-routing")]`, driving the script as a process against fixture
  trees (the disk is the thing under test, which the test-substrate rule allows; each fixture is deleted
  and a failed delete fails the test).
- `gk-core/scripts/verification-boundaries.v1.json` owner row `guard-logistics-routing`: paths
  `scripts/guard-logistics-routing.ps1`, `scripts/logistics-routing.v1.json`, the test file; project
  `guard`; verificationId `guard.logistics-routing`; guards `["logistics-routing"]`. The registry edit
  already maps to `enforcement-registry` (`guard.enforcement-registry`), confirmed by
  `verify-change.py -PlanOnly` this session.
- Verify: `.\scripts\verify-change.py -Paths <changed files> -Session <id>`;
  `.\scripts\guard-logistics-routing.ps1`.
- **Never:** exempt a guarded path; count callers in a test.

## Dependencies and interface

**Depends on:** nothing.

| Exposed | Consumer |
|---|---|
| `guardedPaths` in `scripts/logistics-routing.v1.json` | `logistics-flow` (its namespace is born guarded, `logistics-flow/spec-path-cache.md`), `fleet` (`spec-carried-goods.md` places its Core files under `World/Logistics/**`), `trade-ai` (adds `World/Ai/Trade/**`, ask T-A4) |

## DESIGN-GATE §5 checklist

```
[x] Subsystems: world topology (read), guard scripts, enforcement registry, verification registry.
[~] Session boundary: trade-network-idea-20260919 covers this doc; boundary check not re-run.
[x] Read this session: trade-foundation map §2.3, umbrella §5, ideal §9.2; the enforcement-registry
    meta-test's header and rule list; the battle-responsibility guard as precedent.
[x] decisions.md: no lock on guard placement; the registry contract is the meta-test.
[x] Every factual claim cites file:line.
[x] audit-doc-citations.py --scope run on this file; see the session report.
[x] Verified against code: all current ReconnectionCost references (grep over src/, three calls and two
    doc-comment mentions); the registry's script-only guard shape.
[x] Surrounding sections read (the meta-test's R-rules; SourceText.ps1's functions).
[x] No untested constraint claimed.
[x] No §2 invariant contradicted.
[x] Corrections propagated: the "xunit guard" wording is corrected in the map's corrections section.
[x] No population pinned: paths, not a caller count.
[x] No event-refreshed cache.
[x] No ordering-fixed criterion.
[x] ActorHub: not touched.
[x] No SOLID fork: reuses SourceText.ps1 and the guard runner.
[x] New rule has a registry row: guard "logistics-routing" and invariant tn-routing-no-reconnection-cost.
```
