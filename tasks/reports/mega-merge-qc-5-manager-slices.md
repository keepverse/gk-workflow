# Mega-merge QC 5 — manager-merged slices re-verified on current HEAD

**QC date:** 2026-09-24 · **Head:** features/mega-merge · **Method:** solo, no agents.
Re-run of every merge gate after later merges landed. No live game.

## Verdict: GREEN (guards: same single pre-existing red)

| Slice (merge) | Re-verification on current HEAD | Result |
|---|---|---|
| tvb-f25 fixtures (`43f7127c5`) | E2E `WorldTurnFixtureTests` + Server `Commander` filter | 1/1, 41/41 |
| L3b slice-2 (`1ff07a9f3`) | full `gk-core/tests/FusionRpg.Core.Tests` | 9746/9746 (+6 from other merges, all green) |
| creature-seed T8/T9 (`e2ede8ae6`) | `DelveWildEndpoints` filter + `CreatureStore` filter | 14/14, 8/8 |
| party-dungeon (`dd606368c`) | `Delve` filter | 1765/1765 |
| Guards Tier ci | `run-guards.ps1 -Tier ci` | 24/25 — sole red `doc-citations`, pre-existing D3 drift in untouched `spec-species-rank.md`, identical to pre-merge attribution |

No slice regressed under later merges. Open items unchanged: T16 + SSH6.8 deferred, T12 raised-floor clause open with named defect.

## Fix cycles 8–10 (2026-09-24) — all three open items closed

- **T16** (ip-censor IC-4.1): fixed in fix cycle 9 — see QC 11.
- **SSH6.8** (sockets v3 publish + BalanceGuard): fixed in fix cycle 8 — see QC 9.
- **T12** (creature-seed raised-floor clause): fixed in fix cycle 10 — the reverted
  `wild.below-rank-floor` caller wire was re-landed after the reopen diagnosis resolved to a
  **test-fixture bug, not the gate**: the below-floor test's shared `WildSpecies` fixture resolved
  to a **Sunwoven** species (the top rung, always structurally excluded), so the endpoint refused
  for the structural reason before ever reaching the rank floor. `DelveWildEndpoints` 15/15
  (incl. a below-floor test asserting the exact `wild.below-rank-floor` reason), whole
  `FusionRpg.Server.Tests` 862/862. See `tasks/reports/creature-seed-rank-t12.md` close-out.
  The QC 5 slice row `creature-seed T8/T9` re-verifies at **15/15** now (was 14/14).
