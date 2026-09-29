# TVB4.5 — Map `gk-core/tests/fixtures/**`; switch on

| Subtree | Owner | Evidence |
|---|---|---|
| `gk-core/tests/fixtures/effects/**` | `core-test-fixtures` -> `core` | `gk-core/tests/FusionRpg.Core.Tests/FusionRpg.Core.Tests.csproj:64` (`<None Include="..\fixtures\effects\**\*" ...>`) |
| `gk-core/tests/fixtures/combat/**` | `core-test-fixtures` -> `core` | `gk-core/tests/FusionRpg.Core.Tests/FusionRpg.Core.Tests.csproj:65` |
| `gk-core/tests/fixtures/action-traces/**` | `core-test-fixtures` -> `core` (pre-existing) | `gk-core/tests/FusionRpg.Core.Tests/Actions/ActionAdoptionFixtures.cs:7,20` |
| `gk-core/tests/fixtures/battle-traces/**` | `core-test-fixtures` -> `core` (pre-existing) | `gk-core/tests/FusionRpg.Core.Tests/Battle/Adoption/PreAdoptionFixtures.cs`, `EventSequenceParityTests.cs` |

`core-test-fixtures` already existed (covering `action-traces`/`battle-traces`); extended its `paths`
to add `effects/**` and `combat/**` rather than fragmenting into four ids, since all four subtrees
verify identically (project `core`, module level, no per-subtree selector) — matching S2's "one owner
per fixture subtree" in substance (one real owner, cited once per subtree) without inventing four
ids that would all resolve the same way.

`gk-core/tests/fixtures/**` added to `$Script:EnforcedRoots` (second of the four roots switched on).

Real proof: full `guard-verification-boundaries.py` run (no `--skip-coverage-walk`) passes clean with
`gk-core/tests/fixtures/**` now enforced — every file under all four subtrees resolves through
`core-test-fixtures`.
