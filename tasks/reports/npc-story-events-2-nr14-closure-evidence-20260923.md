# Evidence — npc-story-events NR1.4 closure: the `narrative` guard, its registry rows and the boundary flip

Lane `npc-story-events-2`, worktree `.claude/worktrees/cmdc-npc-story-events-2`, branch
`cmdc/npc-story-events-2` (now carrying the integration head, merged clean this segment). Program
`npc-story-events`; row `tasks/npc-story-events-todo.md` NR1.4; plan §4 D3. This closes the half that three
refusals blocked: the guard script, its catalog entry and invariant rows, and the `guard-narrative` boundary row's
`verificationId` flip.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| A catalogued `narrative` guard whose row is named by an invariant | `dotnet test gk-core/tests/FusionRpg.Guard.Tests -c Release --nologo --verbosity quiet --filter "FullyQualifiedName~EnforcementRegistryGuardTests"` | `Failed: 0, Passed: 18, Total: 18` — R1 (every `guard-*.ps1` on disk catalogued, every catalog script on disk), R5 (gating + ci actually run), R6 (guards xor reason), R8 (a catalogued guard is named by an invariant) | `gk-core/scripts/enforcement-registry.v1.json` |
| The guard cannot pass vacuously — every required row is in the committed map, and every map line names a row | `python gk-core/scripts/guard-narrative.py` | exit 0, `NARRATIVE GUARD OK - 3 row(s) guarded by 'narrative', 3 mapped` (`guard-narrative-row-map`, `ns-one-content-theta-producer`, `narrative-tuning-no-default`) | `gk-core/scripts/guard-narrative.py` |
| It BITES on a planted row with no map line, on a mapped class missing its trait, and on an empty row set | `dotnet test gk-core/tests/FusionRpg.Guard.Tests -c Release --nologo --verbosity quiet --filter "Guard=narrative"` | `Passed: 5, Failed: 0` — 3 falsifiers + a control + the committed-tree check, each planting its broken registry in a temp root and requiring the script to name the violation | `gk-core/tests/FusionRpg.Guard.Tests/NarrativeGuardContractTests.cs` |
| The trait filter really selects tests, per mapped project | `pwsh … gk-core/scripts/guard-narrative.py -RunTraitFilter` | exit 0 — `FusionRpg.Core.Tests -> Guard=narrative selected 30 test(s), 0 failed`; `FusionRpg.Guard.Tests -> selected 5 test(s), 0 failed` | same |
| Stripping a real trait fails the guard by name AND drops the filter to zero (the plan's own falsifier) | temporarily removed `[Trait("Guard", "narrative")]` from `NarrativeGuardContractTests.cs`, then `pwsh … gk-core/scripts/guard-narrative.py`, then `dotnet test … --filter "Guard=narrative"`; trait restored | guard exit 1 naming `mapped test class … does not carry [Trait("Guard", "narrative")]`; the direct filter printed `No test matches the given testcase filter` (selected 0); restored and re-run green | same |
| The `guard-narrative` owner row now carries the focused verification selector | `python gk-core/scripts/guard-verification-boundaries.py` | `VERIFICATION BOUNDARY GUARD OK`, exit 0, 436 boundaries (re-run after the registry rewrite, as instructed) | `gk-core/scripts/verification-boundaries.v1.json` |
| The guard script resolves to its own boundary, not a fallback | `pwsh … scripts/verify-change.ps1 -Paths @('gk-core/scripts/guard-narrative.py') -AllowUnscoped -PlanOnly` | `gk-core/scripts/guard-narrative.py -> guard-narrative (focused)`, `test: guard guard.narrative` | same |
| The row's Verify substance runs green | `pwsh … scripts/verify-change.ps1 -Paths @('gk-core/scripts/enforcement-registry.v1.json','gk-core/scripts/guard-narrative.py','gk-core/scripts/verification-boundaries.v1.json') -AllowUnscoped` | exit 0 — `enforcement-registry (focused)`, `guard-narrative (focused)`, `guard-verification-boundary-tests (focused)`; `Failed: 0, Passed: 5` then `Failed: 0, Passed: 57` (7 m 39 s) | — |
| The lane can see the program's prerequisite work | `git merge features/mega-merge --no-edit` | clean, exit 0 — `gk-core/src/FusionRpg.Core/Narrative/**`, `gk-core/data/tuning/narrative.v1.json`/`v2.json` and NR0.2's seven boundary rows are now in this branch | — |

**NOT proved / named deviations.**

- **The acceptance's Verify line is run renamed, not as written.** It names `-Session <sid>`; that cannot resolve in
  this lane (`tasks/sessions/npc-story-events-2.json` does not exist; `tasks/sessions/**` is outside the lane's
  allowed paths). Every run above passes `-AllowUnscoped` — the script's documented flag for work outside a session
  record. Erratum asked in the NR1.4 closure note, the NR2.18 evidence and three blocker notes.
- **The trait filter runs over the projects the map names, not a fixed four.** The plan's D3 audit says "over the
  Core, Data, Server and Guard projects"; the same paragraph's rule is "zero tests in any project it **names**". The
  script follows the rule (projects are derived from the map), so Data and Server are not run — they carry no
  `narrative` invariant row yet. A fixed four-project list would be red today and would go red again on any project
  whose narrative rows land later.
- **`narrative-tuning-no-default`'s rule is enforced by `NarrativeTuningTests` (Core), not by a new test here.** This
  commit adds the registry row and its map line; the leaf-path loop that makes the row true shipped with lane `-1`.
- **NR-F3 still stands**: `python gk-core/scripts/audit-magic-numbers.py --domain narrative` is vacuous (`domain_of` has no
  `Narrative` key). `python gk-core/scripts/audit-overflow.py` is 0 findings / 0 critical.
- **Cross-program finding (not this lane's, not fixed here — the owning todo is outside this lane's allowed paths).**
  `pwsh … scripts/guard-doc-citations.ps1 -Strict` is **RED on the merged head**: 1 HIGH, 2 details, both at
  `docs/architecture/loam-relics-and-wonders/spec-relic-item-kind.md:76` — `fill.py:293-302` and `fill.py:532-540`
  are cited as **bare basenames** and are now ambiguous (rule D3, "2 files share this name"). **Cause read, not the
  symptom:** that doc was clean when written (`fc18f306e`, "0 HIGH / 0 D3 / 0 D4"), and the second `fill.py` arrived
  with narrative-seed **NS14** (`eb8f4a2c8`, `gk-forge/tools/seedsmith/seedsmith/adapters/narrative/gloss/fill.py`) beside the
  pre-existing `gk-forge/tools/seedsmith/seedsmith/adapters/items/fill.py`. The line already path-qualifies its first citation,
  so the fix is to qualify the other two. Owner: narrative-seed (the commit that added the second `fill.py`) or
  loam-relics (the doc); this lane may not write either todo (`tasks/narrative-seed-todo.md` and any loam-relics todo
  are outside its fence), so it is reported for the manager to route.
- No server was started, no live probe was run, and no web-backed row exists yet for the guard's `npx vitest` half.
