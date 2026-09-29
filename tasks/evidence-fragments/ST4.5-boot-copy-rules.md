# The published server booted with an empty action catalog — three missing copy rules, and the guards that hid them

Found live 2026-09-19 by the manager, on `features/mega-merge` published to `dist`: `GET
/api/debug/action-budget-report` returned `pricedActionCount: 0`. This is the prerequisite fix, its own
commit, ahead of the ST4.5 reading.

## The defect

`Program.cs` read its three action brief files straight off `AppContext.BaseDirectory` and guarded each
with `File.Exists`. That is the one content read in the file that neither walks up from the exe nor had a
`<Content>` rule in `FusionRpg.Server.csproj` — so on a published build every guard missed, the catalog
imported nothing, and the budget report priced an empty catalog. That reads exactly like a balance fault,
which is why it took the report to make the cause visible.

| Path | Reader | State before | State after |
|---|---|---|---|
| `gk-data/packs/fusion/data/seed/actions/*.json` | `Program.cs` brief loop | **no rule** — 0 actions imported | rule added (top-level only; `_briefs` is 34 MB and `_candidates` is gitignored, both excluded by construction) |
| `gk-data/packs/fusion/data/seed/loot/*.json` | `Program.cs:614`, drop-table corpus, `Directory.Exists` | **no rule** — a published build shipped no drop tables | rule added |
| `gk-data/packs/fusion/data/generated/passive-tree/*.json` | `PassiveTreeImportRunner` at boot (`Program.cs:773`) | **no rule** — resolved only by `FindUp` walking out of the exe into a dev checkout; a player install got the code fallback | rule added |

The audit that found the second and third: every `AppContext.BaseDirectory` literal in `Program.cs` is now
covered by `BootContentCopyRuleTests`. Everything else under `gk-data/packs/fusion/data/seed` and `gk-core/data/tuning` the server reads
at boot already had a rule (`items/**` also covers `_registry/build-themes.v1.json`, `rare-names.json`,
`affixes`, `charms`, `sets`, `recipes`, `gems`, `base-types`, `display-templates`).

## The silence

Both guards skipped without a word. They now warn on stderr, in the existing `[tag]` convention and under
the file's own "never fatal" rule for boot content (a broken tree must not take the server down):

- `[actions] <path> is missing next to the exe — the action corpus was NOT imported and the catalog stays
  empty (check FusionRpg.Server.csproj's data\tuning copy rule)` — the cost template, the import's outer
  gate;
- one line per missing brief file, naming it and its copy rule;
- `[loot] <dir> is missing next to the exe — the drop-table corpus was NOT imported`.

## The guard

`gk-core/tests/FusionRpg.Server.Tests/BootContentCopyRuleTests.cs`: it reads `Program.cs` and the csproj and
requires them to agree.

- `Every_content_path_the_server_reads_at_boot_is_covered_by_a_copy_rule` extracts every
  `Path.Combine(AppContext.BaseDirectory, ...)` literal under a shipped-content root and requires a
  `<Content>` rule whose base covers it; a rule naming no wildcard covers exactly its file, a glob rule
  covers its directory (and the directory itself, since a boot read may name a tree). Content roots only:
  the sqlite dir and `artifacts/` are runtime state, not shipped content.
- `Every_boot_read_path_that_exists_in_the_repo_is_present_next_to_this_test_host` is the other half:
  the copy actually landed, so a rule with a wrong `Link`/`Exclude` fails too.
- Contract, not a count: it never pins a file list or a total, so adding content cannot fail it.

**Planted violation, run for real:** pointing the actions rule at `gk-data/packs/fusion/data/seed/actions/_manifest.json`
instead of the glob makes the first test fail naming exactly `gk-data/packs/fusion/data/seed/actions` — the live defect,
reproduced by the guard. Restored immediately after.

Evidence, exact:

```
dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~BootContentCopyRule"
  → Passed! Failed: 0, Passed: 2, Total: 2
  (with the planted violation: Failed: 1, and the message names gk-data/packs/fusion/data/seed/actions)

dotnet test tests\FusionRpg.Server.Tests
  → Failed: 18, Passed: 534, Total: 552   (the 18 are the recorded pre-T62 baseline; +2 are these)
```

## Owed, not done here

The audit also found the trees a boot reader derives for itself rather than naming as a literal, so the
guard cannot see them: `SeedScanner.AtomFolders` — `gk-data/packs/fusion/data/seed/atoms`, `containers`, `curves`, `rarity`,
`elements`, `channel-policy`, `channel-pools`, `effects/affixes`, `power`, `creatures/species-effects` —
have **no copy rule either**, and `SeedImportRunner.RunSelfHealing` sweeps the copied `gk-data/packs/fusion/data/seed` first,
so a published/deployed server boots on the code fallback rather than the committed content. Measured
cost of copying them: ~0.2 MB total (17 + 4 + 1 + 2 + 2 + 1 + 1 + 1 + 1 + 2 files).

Not folded into this commit because it changes what **every host-booting test** sees — those trees are
absent from the test output today, and tests that assert the fallback path would start seeing real
content. That is a deliberate change that needs its own verification pass, not a rider on this fix. It is
recorded in the ledger rather than left implicit.
