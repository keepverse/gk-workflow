# Evidence — npc-story-events NR6.1 (the doctrine catalog and view)

Lane `npc-story-events-2`, worktree `.claude/worktrees/cmdc-npc-story-events-2`, branch `cmdc/npc-story-events-2`.
Program `npc-story-events`; row `tasks/npc-story-events-todo.md` NR6.1; spec `spec-counter-doctrine.md` §3 (read this
session). R13/NS6: a doctrine changes **what** the Rotwright's faction fields, never **how strong** it is.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| The vocabulary is closed and pinned with its reason | `dotnet test gk-core/tests/FusionRpg.Core.Tests -c Release --nologo --verbosity quiet --filter "FullyQualifiedName~DoctrineCatalogTests"` | `Failed: 0, Passed: 14, Total: 14` (64 ms) — the file's ids equal `DoctrinesCatalog.ReviewedIds` (8: six `ward.{element}` + `siegecraft` + `raiders`), the six wards are one per shipped element, and each ward biases TOWARD a resisting element above neutral and AWAY from its own below it (a relation, not a pinned number) | `gk-data/packs/fusion/data/seed/narrative/_registry/doctrines.v1.json`, `gk-core/src/FusionRpg.Core/Narrative/Doctrine/DoctrinesCatalog.cs` |
| A row with any other key refuses `doctrine.magnitude-key` | same run (`A_row_key_that_names_a_magnitude_is_refused_by_rule` ×4: `maxHp`, `atk`, `level`, `rarity`) | pass — `NarrativeVocabularyRejection` whose message carries `doctrine.magnitude-key` | `gk-core/src/FusionRpg.Core/Narrative/Vocabulary/DoctrineCatalog.cs` |
| An effect key outside its family's closed vocabulary refuses | same run (`An_effect_key_outside_its_closed_vocabulary_is_refused` ×3: `plasma`, `Fire`, `teleport`) | pass — same rule id; the families key against vocabularies that already exist (the shipped element table's six ids; `WorldCommandKinds.All`), asserted by `The_two_families_key_against_the_vocabularies_that_already_exist` | same |
| `DoctrineView` exposes only biases and weights | same run (`The_view_exposes_only_biases_and_weights`, `The_view_reads_a_named_bias_and_weights_an_unnamed_one_neutral`) | pass — reflection shows exactly `DoctrineId`, `SpeciesElementBiasMilli`, `OrderWeightMilli`, and no member name carries Hp/Attack/Damage/Rarity; an unnamed element or order kind reads the neutral 1000, never 0 | `gk-core/src/FusionRpg.Core/Narrative/Doctrine/DoctrineView.cs` |
| The registry row and the guard's map line land together | `python gk-core/scripts/guard-narrative.py` | `NARRATIVE GUARD OK - 5 row(s) guarded by 'narrative', 5 mapped` | `gk-core/scripts/enforcement-registry.v1.json` (`ns6-doctrine-no-magnitude`), `gk-core/scripts/guard-narrative.py` |
| The trait filter really selects the new tests | `pwsh … gk-core/scripts/guard-narrative.py -RunTraitFilter` | `FusionRpg.Core.Tests -> Guard=narrative selected 67 test(s), 0 failed` (53 before this row); `FusionRpg.Guard.Tests -> selected 5 test(s), 0 failed` | same |
| The enforcement registry and the boundary guard still hold | `dotnet test gk-core/tests/FusionRpg.Guard.Tests --filter "FullyQualifiedName~EnforcementRegistryGuardTests"` and `pwsh … gk-core/scripts/guard-verification-boundaries.py` | `Failed: 0, Passed: 18, Total: 18`; `VERIFICATION BOUNDARY GUARD OK` (re-run after the registry rewrite, as instructed) | — |
| Path-owned verification | `pwsh … scripts/verify-change.ps1 -Paths @(<the 7 changed paths>) -AllowUnscoped` | exit 0 — every path resolves FOCUSED (`seed-narrative-registry`, `enforcement-registry`, `core-narrative` ×5) with `test: core core.narrative` and `test: guard guard.enforcement-registry`; **136 passed, 0 failed** | — |
| No balance literal, no overflow | `python gk-core/scripts/audit-magic-numbers.py --domain narrative` · `python gk-core/scripts/audit-overflow.py` | `total 0 finding(s), 0 high` · `total 0 finding(s), 0 critical` | — |

**One stale assertion found and fixed in this commit (a stale test, not a defect):**
`CharacterRegistryTests.Doctrine_catalog_loads_the_committed_empty_file` asserted `DoctrineCatalog.All` is EMPTY on
the committed file. The file is an **authored registry** (`gk-data/packs/fusion/data/seed/narrative/_registry/**`, AGENTS.md's
hand-authored class), so adding the reviewed rows is the sanctioned path and the emptiness was that ship's state, not
the property. The test now asserts the committed file parses/validates/configures and still refuses an unknown id, and
the SHAPE property it actually proved moved to `An_empty_doctrine_list_is_a_legal_configured_catalog` (an in-memory
empty list configures; every id is then unknown).

**Named deviations.**

- **The row's Files list omitted `gk-core/src/FusionRpg.Core/Narrative/Vocabulary/DoctrineCatalog.cs`.** It had to be
  extended: it is the file's ONE reader and `NarrativeRegistryHub` configures it at boot, and it accepted only
  `description`/`negative` keys — so adding the effect keys without extending it would have made the hub reject its own
  committed file, and giving the new module catalog a second parser of the same file is the "second vocabulary" defect
  spec §3 warns about. The shape+closure live in that one reader; `DoctrinesCatalog` adds what the vocabulary module
  cannot (which ids are REVIEWED, and typed per-element / per-order-kind reads) and `DoctrineView` is the consumer
  surface. This is the same class of Files-list omission the plan audit flagged for NR2.15's `LeadNames.cs`.
- **`DoctrineView.For(world, factionId)` is not built, and that is a named dependency, not an omission:** the active
  doctrine has to live on the faction for a pure read of hashed state to find it, and `WorldFaction` carries no doctrine
  member today (`WorldState.cs:70-93`); adoption is the study bar's own row. `Of(DoctrineDef)` is the shape the policy
  ask consumes once that field exists, and the class doc says so.
- **Nothing consumes the doctrine in the field yet.** Per spec §3 that is world-map's filed ask
  (`FrontierRulesPolicy.Decide` weights, `RaiseResolver.SpeciesFor`), so a doctrine is adopted and visible but changes
  nothing until that lands — the spec's own words, carried in the view's doc.
- The row's Verify line is run renamed: `-Session <sid>` cannot resolve in this lane (no session record;
  `tasks/sessions/**` is outside the allowed paths), so it passes `-AllowUnscoped`.
- **Duplicate keys are now refused** (`'{id}' carries key 'X' twice` / `'{id}.family.X' appears twice`) — found while
  planting a refusal case: without it, a duplicate key silently let the LAST value win, which is how a refused key
  would have disappeared.
