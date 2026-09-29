# Evidence — npc-story-events NR2.19 (`expeditions.v2.json`, tier danger bands and encounter chances)

Lane `npc-story-events-2`, worktree `.claude/worktrees/cmdc-npc-story-events-2`, branch
`cmdc/npc-story-events-2` (base `57e29b4b3`). Program `npc-story-events`; row
`tasks/npc-story-events-todo.md` NR2.19; spec `spec-host-content-theta.md` §4,
`spec-expedition-lead-host.md` §6, plan §4 D4. **One publish whose readers switch in the same commit.**

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| The version is published, never hand-edited | `python gk-core/tools/tuning/publish.py expeditions --label "NR2.19: tier danger bands and the encounter chances" --add-key 'tiers.scout-30m:dangerBand=1' --add-key 'tiers.forage-4h:dangerBand=2' --add-key 'tiers.hunt-8h:dangerBand=3' --add-key 'tiers.warpath-20h:dangerBand=4' --add-key ':encounter={"wildCreatureMetMilli":250,"quietMilli":50}'` | `published expeditions (v1 -> v2, 5 change(s)); v1 stays on disk for revert` — 5 `ADDED` lines | `gk-core/data/tuning/expeditions.v2.json` |
| The four danger bands and both encounter chances are required, by name | `dotnet test gk-core/tests/FusionRpg.Core.Expeditions.Tests -c Release --nologo --verbosity quiet` | `Failed: 0, Passed: 36, Total: 36` (249 ms) — 6 deletion cases each asserting the exception names its own path, the whole-block case (`$.encounter`), the non-integer case, the v1 case | `gk-core/tests/FusionRpg.Core.Expeditions.Tests/Expeditions/ExpeditionTuningTests.cs` |
| `tiers.hunt-8h.dangerBand` rejects naming it | same run (`Deleting_a_key_rejects_naming_its_path(container: "tiers", tierId: "hunt-8h", …)`) | pass — `tiers.hunt-8h.dangerBand` in the message | same |
| Every loader reads v2 | `grep -rno "expeditions\.v[0-9]\.json" src/ tools/ tests/` (excluding `obj/`, `bin/`) | the five readers name **v2**: `RpgHost.cs:165`, `Program.cs:103`, `ProveHubCombat/Program.cs:73`, `_TempSeedSpecies/Program.cs:84`, `AptitudeChannelModsTests.cs:139`; the two v1 hits are a prose comment (`ExpeditionResolverTests.cs:256`) and the deliberate rejection test (`ExpeditionTuningTests.cs:137`) | 8 paths |
| A reader left on v1 cannot load at all | `dotnet test gk-core/tests/FusionRpg.Core.Expeditions.Tests …` (`The_superseded_v1_file_can_no_longer_be_parsed_at_all`) | pass — parsing the committed v1 throws `ExpeditionTuningRejection` naming `dangerBand`, so the reader switch is mechanically checkable rather than a promise | same |
| The catalog passes the band through from the configured tuning | same run (`The_catalog_passes_each_tiers_band_through_from_the_hub`) | pass — every tier's `ExpeditionTierCatalog.Get(id).DangerBand` equals the hub's, with an anti-vacuity guard that at least one band is non-zero | `gk-core/src/FusionRpg.Core/Expeditions/ExpeditionTierCatalog.cs` |
| `ForExpedition` composes through the one composer | `dotnet test gk-core/tests/FusionRpg.Core.Tests -c Release --nologo --verbosity quiet --filter "FullyQualifiedName~Narrative.Hosts\|FullyQualifiedName~Expedition\|FullyQualifiedName~Power"` | `Failed: 0, Passed: 69, Total: 69` (404 ms) — `ForExpedition_composes_through_the_one_composer_from_the_tiers_own_band` asserts equality with `PowerIndexComposer.ContentExplain` and that the context carries the tier's band | `gk-core/src/FusionRpg.Core/Narrative/Hosts/HostContentTheta.cs` |
| The resolver's tier hashes are byte-identical with v2 loaded | `dotnet test gk-core/tests/FusionRpg.Core.Expeditions.Tests …` (the four pinned `ScoutHash`/`ForageHash`/`HuntHash`/`WarpathHash` tests in `ExpeditionResolverTests`) | pass, unchanged — the resolver never reads `DangerBand` | `gk-core/tests/FusionRpg.Core.Expeditions.Tests/Expeditions/ExpeditionResolverTests.cs:286-289` |
| The `core` boundary group still passes (the shared bootstrap moved) | `dotnet test gk-core/tests/FusionRpg.Core.Tests -c Release --nologo --verbosity quiet` then the other 60 `core` projects one per invocation | `Passed: 9614, Failed: 0` (7 m 33 s) plus chunks of `passed=2670`, `1941`, `1307`, all `failed=0` — **15,532 passed, 0 failed** over 61 projects | `gk-core/tests/FusionRpg.Core.Tests.Shared/ContractTuningTestBootstrap.cs` |
| The `server` boundary still passes (a reader moved there) | `dotnet test gk-core/tests/FusionRpg.Server.Tests -c Release --nologo --verbosity quiet` | `Failed: 0, Passed: 814, Total: 814` (9 m 13 s) | `gk-core/tests/FusionRpg.Server.Tests/AptitudeChannelModsTests.cs` |
| The `guard` boundary still passes | `dotnet test gk-core/tests/FusionRpg.Guard.Tests -c Release --nologo --verbosity quiet` | `Failed: 0, Passed: 598, Total: 598` (6 m 54 s) | — |
| The `narrative` guard's runtime half still selects tests | `python gk-core/scripts/guard-narrative.py -RunTraitFilter` | exit 0 — `FusionRpg.Core.Tests -> Guard=narrative selected 17 test(s), 0 failed`; `FusionRpg.Guard.Tests -> selected 5 test(s), 0 failed` | `gk-core/scripts/guard-narrative.py` |
| Every guard the plan selects for these paths is green | `pwsh … scripts/guard-{actor-hub,dal,funnel-delta,injector-compile,secondary-no-unity,single-writer}.ps1` | all exit 0; `injector-compile` prints `SKIPPED — no MelonLoader game dir … injector NOT compiled` (a reported skip, no game install on this machine) | — |
| The published version does not rewrite v1 | `python gk-core/scripts/guard-tuning-immutability.py` | `TUNING IMMUTABILITY GUARD OK — 1 gk-core/data/tuning/*.json change(s) checked, T1-T4 clean` | `gk-core/data/tuning/expeditions.v1.json` (untouched) |
| No overflow, no balance literal in code | `python gk-core/scripts/audit-overflow.py` · `python gk-core/scripts/audit-magic-numbers.py --domain narrative` · `python gk-core/scripts/audit-magic-numbers.py --domain expeditions` | `total 0 finding(s), 0 critical` · `0 high` · `0 high` | — |
| The verification registry still resolves every changed path | `pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths @(…all 12…) -AllowUnscoped -PlanOnly"` and `pwsh … gk-core/scripts/guard-verification-boundaries.py` | no `VERIFICATION BOUNDARY MISSING`; resolutions: `tuning-expeditions`, `core-area-expeditions`, `core-expeditions`, `core-residual`, `core-tests-shared`, `injector-fallback`, `server-fallback`, `server-tests-fallback`, `temp-seed-species-tool`, `prove-hub-combat-tool`, `core-fallback`, `core-tests-fallback`; `VERIFICATION BOUNDARY GUARD OK` | — |

**NOT proved / blocked.**

- **The wrapper run is not quoted as one command.** `verify-change.ps1 … -Session npc-story-events-2` cannot
  resolve here (`tasks/sessions/npc-story-events-2.json` does not exist; `tasks/sessions/**` is outside this
  lane's allowed paths — the erratum ask from the NR2.18 evidence stands), and two attempts at the same
  `-AllowUnscoped` run were killed by harness interruptions. The table above therefore runs **the boundaries'
  own selections as separate commands** (the same set the plan prints: `core` group, `core-residual`,
  `core-expeditions`, `server`, `guard`, the six guards). Nothing in the plan's selection is unrun.
- **`injector-compile` was SKIPPED, not passed** — no MelonLoader game dir on this machine, so the Injector was
  not compiled after its one-line reader change. The change is a string literal inside a
  `File.ReadAllText(Path.Combine(tuningDir, …))` call; it is not compile-verified here.
- **The `expeditions` real-tree agreement row is blocked.** `gk-core/tests/FusionRpg.Guard.Tests/TuningVersionAgreementGuardTests.cs`
  is refused by the pipeline guard as a protected guard file, outside this lane's grant
  (`scripts/guard-*.ps1`, `gk-core/scripts/enforcement-registry.v1.json`, `scripts/run-guards.ps1`,
  `gk-core/scripts/verification-boundaries.v1.json`). The file's own convention says the row lands "in the commit that
  switched every reader to v4/v2" — that commit is this one, so the row is owed to the orchestrator or to a lane
  whose grant includes guard tests. Blocker note filed.
- **`core-fallback` is still what `gk-core/src/FusionRpg.Core/Narrative/Hosts/**` resolves to** (the 61-project group
  above), because NR0.2's focused `core-narrative` row is unmerged in this worktree. Recorded, not worked around.
- No server was started and no live probe was run; `gk-core/data/tuning/expeditions.v1.json` is untouched.
