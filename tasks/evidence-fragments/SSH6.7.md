# SSH6.7 — the boot computes what it loaded and checks the pricing's provenance

New `gk-core/src/FusionRpg.Server/ComboPricingBoot.cs` (the testable seam the boot calls); `Program.cs` captures
the three tuning FILENAMES it reads and, once every input is loaded, computes the loaded revisions +
corpus digest and calls `RequireVerified` BEFORE anything binds. Core gains
`SocketTuningFiles.RevisionOf(fileName)` (the FILENAME revision, never a file's internal `version`) and
`CombinationCorpus.Digest(recipes, grants)` — SHA-256 over the accepted set's ids, ingredient families,
grants and host pins, sorted.

## Acceptance

| Criterion | Command | Result |
|---|---|---|
| the boot computes the digest (ids, families, grants, host pins) and calls `Check`; today's files boot unchanged | `dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~ComboPricingBoot"` | **3 passed / 0 failed**. `Today_s_files_boot_unchanged_with_no_measured_pricing`: versions **2 / 1 / 4** (filename revisions), `circuitSize` 4, a 64-hex digest, and `RequireVerified(null, …)` does not throw |
| `boot_refuses_a_revision_or_corpus_the_pricing_was_not_measured_against`, one field at a time, by name | (above) + the row's own filter | 3 named tests; the boot-refusal test varies each of `socketsVersion`, `strainSpliceVersion`, `materialsVersion`, `circuitSize`, `combinationCorpusDigest` ALONE and asserts `socket.combo-pricing-stale` with that field in the message; an exact match binds |
| the digest is a reading of the whole set, order-independent | (above) | `The_digest_covers_ids_families_grants_and_host_pins_and_is_order_independent`: shuffled recipes + reversed grants give the same digest; changing any ONE of the four (id, an ingredient family, a grant, a host pin) moves it |
| the row's Verify filter | `dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~ItemPreviewEndpoints\|FullyQualifiedName~ComboPricing"` | **14 passed / 0 failed** |
| the whole Server suite still boots | `dotnet test gk-core/tests/FusionRpg.Server.Tests` | **761 passed / 0 failed** |
| scoped verification boundary | `pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Core/Items/Sockets/CombinationCorpus.cs','gk-core/src/FusionRpg.Core/Items/Sockets/SocketTuningFiles.cs','gk-core/src/FusionRpg.Server/ComboPricingBoot.cs','gk-core/src/FusionRpg.Server/Program.cs','gk-core/tests/FusionRpg.Server.Tests/ComboPricingBootTests.cs') -Session strain-splice-host-20260921"` | exit **0** — `core-fallback` **15091 passed / 0**, `server-fallback` **758 passed / 0** (the profile filter), DAL guard OK |

## Decision recorded (the row's `deps: SSH4.4`)

SSH4.4 (the one-acceptance-set **container build** at boot) is still open, and this row does not wait on
it: the acceptance's four digest fields (ids, ingredient families, grants, host pins) are all readable
from the **accepted recipe set the store holds** (`store.GetComboRecipes()`, filtered to Strain/Splice)
plus `CombinationCorpus.ReadGrants` over the corpus text — no container build needed. The digest is taken
over that accepted set. When SSH4.4 lands, the accepted set it defines is the same set this reads, so the
digest does not move because of it.

## Not proved / open

- **No `sockets.v3.json` exists**, so the boot has never seen a published `measuredAgainst`: the passing
  path is exercised with a matching fixture record, and the refusing paths one field at a time.
- The `strain-splice.v1.json` / `materials.v4.json` literals in `Program.cs` and the test are the
  revisions the boot reads TODAY; SSH7.1 and SSH8.4 add the constants that replace them (the mechanical
  swap SSH5.3 proved), and the test says so in its own comment.
- The digest's *shape* is asserted; the measurement that will populate `measuredAgainst` is SSH6.8's.
