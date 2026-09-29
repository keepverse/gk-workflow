# Evidence — npc-story-events NR2.18 (Θ per host through the one composer)

Lane `npc-story-events-2`, worktree `.claude/worktrees/cmdc-npc-story-events-2`, branch
`cmdc/npc-story-events-2` (base `57e29b4b3`). Program `npc-story-events`; row
`tasks/npc-story-events-todo.md` NR2.18; spec `docs/architecture/npc-story-events/spec-host-content-theta.md`
§3–§5 (read in this session), anchors `power/ssot-power-scale.md` §5/§8.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| `ForSector` equals the one composer for bands 0–6 with non-zero parent terms | `dotnet test gk-core/tests/FusionRpg.Core.Tests -c Release --nologo --verbosity quiet --filter "FullyQualifiedName~Narrative.Hosts"` | `Failed: 0, Passed: 16, Total: 16` (191 ms) — 7 theory cases, each asserting `PowerIndexComposer.ContentExplain(power, ctx).Total` | `gk-core/tests/FusionRpg.Core.Tests/Narrative/Hosts/HostContentThetaTests.cs` |
| `ForDelveRoom` passes the room's Θ and context through | same run (`ForDelveRoom_passes_the_room_theta_and_context_through_unchanged`) | pass — same `ContentContext` **reference** (`Assert.Same`), Θ unchanged | same |
| `ForHomeworld` equals a band-0 sector | same run (`ForHomeworld_equals_a_band_zero_sector`) | pass — equal Θ and equal context | same |
| Θ does not decrease as the band rises | same run (`Theta_does_not_decrease_as_the_band_rises`) | pass for bands 0→6 (a relation, no literal) | same |
| One producer of `ParentWorldTerms` | same run (`One_producer_of_parent_world_terms`) | exactly `["gk-core/src/FusionRpg.Core/Narrative/Hosts/ParentWorldTermsSource.cs"]` in `src/**` (zero sites before this change) | `gk-core/src/FusionRpg.Core/Narrative/Hosts/ParentWorldTermsSource.cs` |
| No `Narrative` type builds a `ContentContext` outside the host arm | same run (`No_narrative_type_builds_a_content_context_outside_host_content_theta`) | exactly `["gk-core/src/FusionRpg.Core/Narrative/Hosts/HostContentTheta.cs"]` | `gk-core/src/FusionRpg.Core/Narrative/Hosts/HostContentTheta.cs` |
| Both scans bite on a planted violation | same run (`The_producer_scan_names_a_planted_second_construction_site`, `The_narrative_scan_ignores_a_mention_inside_a_comment`) | pass — a planted second site is named; a comment mention is not a site | same |
| Each missing term's owner is named in code | read `ParentWorldTermsSource.cs` (doc list) + `ParentWorldTermsSourceTests`-side check `Parent_world_terms_are_zero_today_and_that_is_the_named_absence_not_a_guess` | `WorldTier`/`ZombossLevel` → world-map (no field on `WorldState`); `RealmsAdvanced` → power/empire (no column; `ServerPowerIndexProvider.cs:16-18` hardcodes 0) | `ParentWorldTermsSource.cs` |
| Registry row `ns-one-content-theta-producer` → `["narrative"]` + its map line | `python gk-core/scripts/guard-narrative.py` | exit 0, `NARRATIVE GUARD OK - 2 row(s) guarded by 'narrative', 2 mapped` | `gk-core/scripts/enforcement-registry.v1.json`, `gk-core/scripts/guard-narrative.py` |
| The guard's runtime half covers both mapped projects | `python gk-core/scripts/guard-narrative.py -RunTraitFilter` | exit 0 — `FusionRpg.Core.Tests -> Guard=narrative selected 16 test(s), 0 failed`; `FusionRpg.Guard.Tests -> selected 5 test(s), 0 failed` | same |
| Path-owned verification | `pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Core/Narrative/Hosts/HostContentTheta.cs','gk-core/src/FusionRpg.Core/Narrative/Hosts/ParentWorldTermsSource.cs','gk-core/tests/FusionRpg.Core.Tests/Narrative/Hosts/HostContentThetaTests.cs','gk-core/tests/FusionRpg.Guard.Tests/NarrativeGuardContractTests.cs','gk-core/scripts/enforcement-registry.v1.json') -AllowUnscoped"` | exit 0 — 63 project test runs, `passed=16134 failed=0`, zero `Failed!` lines | — |
| No balance literal, no overflow in the new files | `python gk-core/scripts/audit-overflow.py` · `python gk-core/scripts/audit-magic-numbers.py --domain narrative` | `total 0 finding(s), 0 critical` · `total 0 finding(s), 0 high` (see NOT proved: the narrative domain is vacuous — lane `-1`'s finding NR-F3) | — |
| Ask A5 (`ssot-power-scale.md` §8 row 6 wording) | read `docs/architecture/power/ssot-power-scale.md` §8 row 6 | **nothing to file**: the row already carries the owner's 2026-09-20 correction — "each dispatch tier gets a `dangerBand` in the expeditions tuning and feeds the same `mapLevel = 5 · DangerBand` term as row 7". The propagation the spec's standards audit deferred is in the file | `docs/architecture/power/ssot-power-scale.md` §8 |

**NOT proved / not closable.**

- **NR2.18 is not ticked.** Its *Verify* line is `verify-change.ps1 … -Session <sid>`; measured,
  `-Session npc-story-events-2` throws `session record not found: npc-story-events-2`
  (`tasks/sessions/npc-story-events-2.json` does not exist and `tasks/sessions/**` is outside this
  lane's allowed paths). The run above is the same script over the same paths with `-AllowUnscoped`
  (the script's documented flag for work outside a session record). Erratum ruling requested: accept
  `-AllowUnscoped` for a lane whose session record is not in its fence, or add
  `tasks/sessions/<session>.json` to the fence.
- **The focused boundary is not in this tree.** `verify-change.ps1 -PlanOnly` resolves the two new
  `src` paths to `core-fallback (module)` and the new test path to `core-tests-fallback (module)` —
  the whole 62-project core group, not NR0.2's intended `core-narrative` (focused, `core.narrative`)
  row, which lives only on lane `npc-story-events-1`. So the 63-run number above is the fallback's own
  selection; after `-1` merges, the same command selects the focused row instead.
- **NR2.19 is NOT done** (the next row, and the reason `ForExpedition` is absent here): it publishes
  `gk-core/data/tuning/expeditions.v2.json` and adds `ExpeditionTierDef.DangerBand`, which
  `HostContentTheta.ForExpedition` needs. Named dependency, not a gap.
- `gk-core/data/tuning/**` was not touched by this row; no server, no live probe, no web surface.
