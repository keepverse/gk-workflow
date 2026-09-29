# TVB3.9 — Seedsmith wrappers B: `gen-structure-contract`, `gen-creature-report`, `gen-creature-metrics`, `gen-creature-preflight`

| Criterion | Result |
|---|---|
| Four wrappers, `script` projects, seams per the D5 table | added: `gen-structure-contract` (seam on `.../adapters/structures/**`), `gen-creature-report` (seam on `.../adapters/creatures/**` AND `.../report/**`, per D5's two-path row), `gen-creature-metrics` (seam on `.../adapters/creatures/**`), `gen-creature-preflight` (seam on `.../adapters/creatures/**`) |
| Each runs from `gk-forge/tools/seedsmith`, matching `working-directory: gk-forge/tools/seedsmith` in `ci.yml` | verified for all four steps |
| Guard passes | `guard-verification-boundaries.py` direct run -> `VERIFICATION BOUNDARY GUARD OK` |
| Parity test green | `GeneratorCheckCiParityTests` auto-discovers the four new `scripts/checks/gen-*.ps1` files, no test-file edit needed |
| Wrappers exit 0 where CI's step is green | `gen-structure-contract.ps1`: exit 0, clean (21 fields, 0 findings). `gen-creature-metrics.ps1`: exit 0, 12 `[GAP] CreatureRoster/*` findings, all informational (`gates=False`) — matches `ci.yml`'s own comment that this step "exits 0 ... none `gates=True`". `gen-creature-report.ps1`: exit 0, 2 `[GAP] Coverage/EmptyPartition` + 26 `[NOT_MEASURED]`, all informational |

**Third real, pre-existing, out-of-scope finding (not fixed here), same drift class as TVB3.6's
CreatureSpeciesGen finding and TVB3.8's fusion-recipe finding:** `gen-creature-preflight.ps1` real
run: exit 1. `python -m seedsmith creatures preflight --skip-model` reports "NOT READY — 0
refusal(s), 1 thing(s) to ask about" — check 2 `dump-is-current` observes a hash
(`6181dc2d...`) that does not match the recorded hash (`cc322647...`) for
`gk-data/packs/fusion/data/seed/creatures/_dump`, with the tool's own suggested fix: `dotnet run --project
gk-forge/tools/CreatureCorpusDump -- <server data dir> gk-data/packs/fusion/data/seed/creatures/_dump`. Checks 1, 3, 4, 7, 8, 9 all
pass. This is the same downstream-cascade drift memory already names
(`demon-seed-cascade-after-anchor-fix`: "fixing an anchor field needs the WHOLE chain re-run
gen->import->replan->fusion-recipe...") — another lane's recent `gk-data/packs/fusion/data/seed/creatures/**` changes
propagated through `CreatureSpeciesGen` (TVB3.6's 11-species finding) and the fusion-recipe seed
(TVB3.8's finding) without a corresponding `CreatureCorpusDump` re-run+commit. Since the wrapper runs
CI's exact command with no flags added or removed, `ci.yml`'s own "Creature preflight, CI mode" step
would hit the identical `NOT READY` result on this tree today — this is corpus drift, owned by
whichever program most recently touched `gk-data/packs/fusion/data/seed/creatures/**` (`creature-seed`), not this one.

Scoped verify: guard-verification-boundaries.py direct -> OK; scoped `dotnet test
gk-core/tests/FusionRpg.Guard.Tests --filter
"FullyQualifiedName~GeneratorCheckCiParityTests|FullyQualifiedName~VerificationBoundaryWorkflowTests|FullyQualifiedName~GuardVerificationBoundaries"`.

## Checkpoint 3 — Python lane (schema 4)

All twelve `script`-runner wrappers (TVB3.6-3.9) now exist and are registered. `gk-forge/tools/seedsmith/**`
and `gk-core/tools/tuning/*.py` resolve through D1-D4's pytest-runner boundaries (TVB3.1-3.5); none maps to
Guard.Tests. `schemaVersion` 4 is still the only accepted value (unchanged by this wave). Remaining
Checkpoint 3 items (TVB3.10's testing-standard.md paragraph) still open.
