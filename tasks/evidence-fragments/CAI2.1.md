# CAI2.1 — `replay-identity` A: the stamp, the column, the log (CORE HALF)

Lane `combat-ai-2`, session `combat-ai-20260920`. This lane's file fence covers
`gk-core/src/FusionRpg.Core/**` (Actions/Battle/Balance/Delve), `gk-core/tests/FusionRpg.Core.Tests/**`, `gk-core/tools/CombatSim`,
`gk-core/tools/ProvePredictor`, `gk-core/data/tuning`, `docs/architecture/combat-ai/**`, `docs/DESIGN-GATE.md` and
`tasks/**`. The Data and Server thirds of this row are **outside** it and are filed below, so this
fragment records the Core third only.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| `StampOf` round-trips through `ToCompact`/`TryParse` | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~CombatAiProfileIdentity"` | **11 passed, 0 failed** — `Stamp_round_trips_through_its_compact_form`: the parsed stamp re-emits the identical compact form, `SchemaVersion` is the **publish** counter (1), the hash matches, and `*/default` is a part | `gk-core/src/FusionRpg.Core/Actions/Ai/CombatAiProfileIdentity.cs:53` |
| Same set stamps identically twice, and order-independently | same run | passes — `The_same_set_stamps_identically_twice`; `The_stamp_is_order_independent_across_the_profile_map` builds the same two profiles in both key orders and gets the identical compact form (both levels hash through `ContentHash.TableDigest`, which sorts) | `:53-66` |
| One changed weight → `Mismatch` naming that profile id | same run | passes — `One_changed_weight_is_a_mismatch_naming_that_profile`: same version, `siege/default.weightHitChance` 70 → 999, verdict `Mismatch`, `ShouldRefuse` true, `ChangedTables` contains `siege/default` and not `*/default` | `ContentHashComparison.Compare` (reused, not forked) |
| A profile **added** → `RegistryChanged`, not a refusal | same run | passes — `An_added_profile_is_a_registry_change_and_not_a_refusal`: a publish to `version` 2 adds `siege/default`; verdict `RegistryChanged`, `ShouldRefuse` **false**, `AddedTables` contains the new id | `:53` (SchemaVersion = the publish counter) |
| null/empty → `Match`; corrupted → `Unreadable` + refusal | same run | passes — `Nothing_stamped_is_a_match` (null, `""`, `"   "`) and `A_corrupted_stamp_is_unreadable_and_refused` (`ShouldRefuse` true) | `ContentHashStamp.cs:106-149` (reused) |
| A field added to `CombatAiProfile` cannot escape the hash | same run | passes — `Every_declared_profile_member_appears_in_the_canonical_form` reflects over the record's public members and asserts each name is present in the canonical form | `:78-84` |
| The source seam refuses an unknown version | same run | passes — `The_source_seam_refuses_an_unknown_version_rather_than_falling_back`: `ForVersion` returns null for an unpublished version rather than falling back to `Current` | `gk-core/src/FusionRpg.Core/Actions/Ai/ICombatAiProfileSource.cs` |
| Golden: byte-identical | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~BattleGolden\|FullyQualifiedName~ExpeditionResolver\|Category=BalanceGuard"` | **39 passed, 0 failed** — nothing constructs the identity on a resolution path in this slice; the report carries no new field | — |
| Guards | `pwsh -NoProfile -File scripts/guard-dal.ps1` / `guard-test-substrate.py` / `guard-actor-hub.ps1` / `guard-doc-citations.ps1 -Strict` | all exit 0 (no SQL touched; new tests are in-memory; 0 HIGH) | — |
| Boundary | `pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Core/Actions/Ai/CombatAiProfileIdentity.cs','gk-core/src/FusionRpg.Core/Actions/Ai/ICombatAiProfileSource.cs','gk-core/tests/FusionRpg.Core.Tests/Actions/Ai/CombatAiProfileIdentityTests.cs') -Session combat-ai-20260920"` | `FusionRpg.Core.Tests`: **14915 passed, 4 failed** — the same four pre-existing corpus facts named in `CAI1.14.md` | — |
| The Core/Actions purity scan caught the first draft | `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~ActionsPurityGuard"` | **9 passed, 0 failed** — the first `StampOf` read `tuning.Profiles.Keys`, and `Action_sources_contain_no_wall_clock_ambient_rng_or_dictionary_enumeration` failed (5th red in the boundary run). Rewritten to `foreach (var pair in tuning.Profiles.OrderBy(p => p.Key, StringComparer.Ordinal))`: **no `.Keys`/`.Values` token**, and the explicit sort is the determinism the rule protects. Golden filter (`BattleGolden\|ExpeditionResolver\|Category=BalanceGuard`): **39 passed, 0 failed** | `CombatAiProfileIdentity.cs:55` |

## NOT done — filed with `file:line` and the cause read

1. **The Data third is outside this lane's fence.** One nullable `TEXT` column
   `combat_ai_profile` on `rpg_web_match_log` via `EnsureColumn` beside
   `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs:821` (after the table's own `CREATE`), `WebMatchLogEntry`'s
   trailing `string? CombatAiProfile = null` and the `AppendWebMatchLog`/`SelectLog`/`MapLog` changes in
   `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WebMatches.cs:19,31,203-229`, and the new
   `gk-core/tests/FusionRpg.Data.Tests/WebMatchLogProfileStampTests.cs`. **Cause read:** this lane's allowed
   paths contain no `gk-core/src/FusionRpg.Data/**` and no `gk-core/tests/FusionRpg.Data.Tests/**`.
2. **The Server third is outside this lane's fence.** `gk-core/src/FusionRpg.Server/CombatAiProfileFiles.cs`
   (the `ICombatAiProfileSource` implementation reading every `data/tuning/combat-ai.v*.json`), the three
   stamping call sites in `WebMatchService.cs:125-128,197-200` and
   `DelveBattleSessionManager.cs:200-204`, the five-step pin resolution at the two `if (!created)`
   branches, and the boot-sweep fifth guard (`WebMatchService.cs:246-290`); tests
   `tests/FusionRpg.Server.Tests/WebMatchProfilePinTests.cs`. **Cause read:** no `gk-core/src/FusionRpg.Server/**`
   or `gk-core/tests/FusionRpg.Server.Tests/**` in this lane's allowed paths.
3. **Therefore CAI2.2 is entirely outside this lane** (`Server/CombatAiProfileFiles.cs`,
   `Server/WebMatchService.cs`, `Server/DelveBattleSessionManager.cs`,
   `tests/FusionRpg.Server.Tests/WebMatchProfilePinTests.cs`) — filed, not attempted, and CAI2.2 is not
   marked done.

**NOT proved.** No persistence claim: the column, its migration and the row round-trip are the filed
Data third. No pin claim: `ForVersion` has a Core-side contract test with an in-memory source, but no
file-loading implementation exists in this lane, so the module's whole proof (a cross-publish replay
byte-identical to the fresh resolve) is not run here and is not claimed.

**Deviation from the spec's snippet, stated.** The spec writes `StampOf(CombatAiProfileSet)` and a
`CombatAiProfileSet` type; module 2 shipped `CombatAiTuning`, which already carries `Version` and
`Profiles`, so the stamp takes that type rather than declaring a second wrapper with the same two fields
(recorded in the source doc comment).

## Closure run — CAI2.1's own Verify line (2026-09-20, lane `combat-ai-2`)

The manager's instruction for this lane is to close CAI2.1 against its **Verify line** — *"implement
until its Verify line is green, commit the task"* — because the row's remaining acceptance lines need
`gk-core/src/FusionRpg.Data/**` and `gk-core/src/FusionRpg.Server/**`, which this lane's allowed paths exclude. The
Verify line is `verify-change; guard-dal.ps1; guard-test-substrate.py`. All three, run now:

| Verify command | Result |
|---|---|
| `pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Core/Actions/Ai/CombatAiProfileIdentity.cs','gk-core/src/FusionRpg.Core/Actions/Ai/ICombatAiProfileSource.cs','gk-core/tests/FusionRpg.Core.Tests/Actions/Ai/CombatAiProfileIdentityTests.cs') -Session combat-ai-20260920"` | `FusionRpg.Core.Tests`: **14943 passed, 4 failed** — the four pre-existing corpus facts (`SocketOperationsTests` x2, `UniqueCorpusTests`, `FamilyExpansionTests`), unrelated to these paths |
| `pwsh -NoProfile -File scripts/guard-dal.ps1` | **exit 0** — "no SQLite/SQL outside FusionRpg.Data" |
| `python gk-core/scripts/guard-test-substrate.py` | **exit 0** — "no new swallowed deletes or temp-backed stores in tests/" |
| `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~CombatAiProfileIdentity\|FullyQualifiedName~ContentHash"` | **55 passed, 0 failed** — the 11 identity tests plus every reused-stamp test |

### What this closure does NOT mean — stated so nobody reads `done` as more than it is

`done` here means **the Core half is finished and its Verify line is green**. The row's acceptance still
has two unbuilt lines, and they are **not** proven:

- `rpg_web_match_log.combat_ai_profile` exists, nullable, added idempotently by `EnsureColumn`;
  pre-existing rows keep NULL; a stamped row round-trips through `TryGetWebMatchLog` and
  `ListUnresolvedWebMatches` — **not built** (`gk-core/src/FusionRpg.Data/**` is a denied path).
- `No existing AppendWebMatchLog caller signature broke` — **not tested** (same reason).
- The Server third (`CombatAiProfileFiles`, the three stamping sites, the five-step pin resolution, the
  boot-sweep fifth guard) and every line of **CAI2.2** — **not built** (`gk-core/src/FusionRpg.Server/**`).

Both are filed in `tasks/combat-ai-todo.md` → "Deferred / named follow-ups" with the exact owed edits and
`file:line`, and CAI2.2 is recorded `blocked` on the ledger with that reason. A lane holding
`gk-core/src/FusionRpg.Data/**` and `gk-core/src/FusionRpg.Server/**` (the `combat-ai-build-20260920` session record
already claims both) can finish them without re-deriving anything.
