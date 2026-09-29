# Evidence — party-dungeon F14 (lane `pd-d3`, 2026-09-23)

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| F14's acceptance, verbatim: "opens a database built from the OLD schema and asserts `dungeon_domain.first_clear_ref` exists after `Init`" | `dotnet test gk-core/tests/FusionRpg.Data.Tests --filter "FullyQualifiedName~DomainSchemaMigrationTests"` | `Passed: 2, Failed: 0` | `gk-core/tests/FusionRpg.Data.Tests/Delve/Domains/DomainSchemaMigrationTests.cs` |
| F14's acceptance, second half: "fails against the pre-fix `EnsureDomainsSchemaUnlocked`" | same filter, with `EnsureColumn(db, "dungeon_domain", "first_clear_ref", "TEXT")` commented out | `Failed: 1, Passed: 1` — `Assert.Contains() Failure: Item not found in collection`; restored byte-identical (`git diff --stat` empty), 2/2 green | — |
| "with the Data suite green" | `dotnet test gk-core/tests/FusionRpg.Data.Tests` | `Passed: 1852, Failed: 0` (the f13 report's own 1850 + these 2) | — |
| Test-substrate rule (in memory, nothing to delete) | `python gk-core/scripts/guard-test-substrate.py` | `TEST SUBSTRATE GUARD OK` | — |
| DAL boundary (no production file changed) | `pwsh -NoProfile -File scripts/guard-dal.ps1` | `DAL GUARD OK` | — |

**What the test pins, and why the shape matters**

`dungeon_domain.first_clear_ref` is in the `CREATE TABLE IF NOT EXISTS dungeon_domain` DDL, but
`CREATE TABLE IF NOT EXISTS` is a no-op against a table that already exists — so an install whose table
predates the column never gains it while `ReadDomains` selects it. The test seeds that exact legacy shape
in memory through `DataTestStore.CreateWithPreInitHot` (the repo's own "a save written by an older
build" helper), including one row written by the older build. That row's survival is load-bearing: it
proves `Init` WIDENED the existing table rather than recreating it, so the column assertion cannot pass
by accident. It then calls the real `ReadDomains()` — the call that 500'd on the owner's real file.

**NOT proved**

- The owner's real 546 MB `rpg-hot.sqlite` is not touched by this test (nor could it be: the substrate
  rule is memory-first). The real-file proof remains
  `tasks/reports/f13-schema-upgrade-proof.ps1` (`PROOF OK`: 15→16 columns, `ReadDomains -> 0 rows`),
  which F13's own row cites.
- F13's other acceptance clause — `scripts/prove-slot-connection.ps1 -Session <id>` printing both
  `CONNECTION PROVEN True` and `DATA PATH HEALTHY True` — is a live-slot proof and stays the manager's;
  F13 therefore stays `[ ]` and its row already names that owner. This row did not change F13's state.
- The test names only `dungeon_domain.first_clear_ref`. It does not re-assert the f13 lane's own
  finding that `pvz_activity_facts.player_id` was a stale-binary artefact rather than a missing column
  (that finding is recorded in F13's row and its report).
