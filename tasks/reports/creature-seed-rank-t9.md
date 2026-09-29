# Task 9 — display payloads + quality line (in-fence clause landed) — row left OPEN on three denied paths

Lane `cs-rank` (session `creature-seed-rank`, branch `cmdc/cs-rank`), 2026-09-23.
Row: `tasks/creature-seed-todo.md` Task 9. Spec: `docs/architecture/creature-seed/spec-species-rank.md` §5, §6, §7.
Landed: `gk-core/src/FusionRpg.Core/Delve/Encounter/SlotFilter.cs` (`ConcreteAnchor.Rank` + the join carries it),
NEW `gk-core/tests/FusionRpg.Core.Tests/Delve/Encounter/ConcreteAnchorRankJoinTests.cs`.
**The row is NOT closed:** three of its clauses need paths this lane's fence denies (each proven below), and
GAP-5's question is answered here.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| `ConcreteAnchor` join carries rank (filter + throw unchanged) | `dotnet test gk-core/tests/FusionRpg.Core.Tests --nologo --verbosity quiet --filter "FullyQualifiedName~ConcreteAnchorRankJoin\|FullyQualifiedName~EncounterCorpusBuilder\|FullyQualifiedName~EncounterSeedContent\|FullyQualifiedName~EncounterTests\|FullyQualifiedName~SlotFilter"` | **Passed! — Failed 0, Passed 70, Total 70, 1 s** | `SlotFilter.cs` |
| The join never drops or defaults the rank, at real scale | same run — `The_real_corpus_join_carries_each_anchors_own_rank` | every row of the real 700+-row corpus joins a rank equal to its ANCHOR's own (`AnchorRow.Rank`, the independent artifact Task 4 wrote); 0 mismatches, and the corpus is asserted non-empty so an all-null pass cannot satisfy it | `ConcreteAnchorRankJoinTests.cs` |
| A skipped rank joins as null | same run — `A_skipped_rank_joins_as_null_never_a_bottom_rung` and `A_ranked_pair_joins_its_rank_verbatim` | null in → null out (no fabricated `Chaff`); `heirloom` in → `CreatureRank.Heirloom` out | same |
| Rank is read off the expanded species, one resolution path | the same edit | `Rank = species.Rank` — the enum is never re-parsed from the anchor's own string here, so a second parse cannot drift from T5's resolution | `SlotFilter.cs` |

## GAP-5 — answered (spec §7's own ambiguity)

**The quality report's diversity section does NOT read the new tuning vocab generically enough to pick rank
up on its own; an explicit rank dimension must be added — and it cannot be added from this lane.**
`gk-forge/tools/CreatureQualityReport/Program.cs:160-209` is generic in *shape* — `ReportDiversity(field, possible,
observed)` takes the possible set from the declaring source (an enum or a tuning file) and works for any
string-valued field — but the section is driven by an **explicit list of calls** (elementPrimary,
elementSecondary, aptitudePrimary, aptitudeSecondary, rarity, threatBand, deployMode, attackTempo, reach,
side), never by reflection over the anchor record. Measured: `grep -c rank
gk-forge/tools/CreatureQualityReport/Program.cs` = **0**. So the edit is one new call,
`ReportDiversity("rank", CreatureRankLadder.All.Select(r => r.ToString().ToLowerInvariant()),
anchors.Select(a => a.Rank))`, plus the separate reports-only coverage line the acceptance names.

## What blocks this row (exact, and proven)

1. **Catalog projection + roster/codex/summon/preview payloads — two denied paths.**
   `verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Server/CreatureEndpoints.cs') -Session creature-seed-rank
   -PlanOnly` → `path is outside session scope`. The DTO itself is outside the fence too:
   `… -Paths @('gk-core/src/FusionRpg.Contracts/CreatureDtos.cs') …` → `path is outside session scope`
   (`CreatureProfileDto` lives at `gk-core/src/FusionRpg.Contracts/CreatureDtos.cs:6`). `RpgStore.Creatures.cs`
   builds those payloads and IS in fence, but it cannot add a field the DTO does not declare — so the
   payload half needs `gk-core/src/FusionRpg.Contracts/**` and `gk-core/src/FusionRpg.Server/**`, i.e. a fence grant or
   another lane.
2. **The quality-report rank-coverage line and the rank diversity dimension — `gk-forge/tools/CreatureQualityReport/**`
   is outside the fence:** `… -Paths @('gk-forge/tools/CreatureQualityReport/Program.cs') …` →
   `path is outside session scope`. The exact edits are named in the GAP-5 answer above.
3. **Display names.** Spec §5 says display copy lives in the runtime catalog file, never the number file
   (tunables-ssot T7/T8) — the rank display-name catalog does not exist yet, and its reader would be a
   Contracts/Server-adjacent payload field, so it travels with blocker 1.

## NOT proved / declared gaps

- No endpoint payload was exercised: the Server is unreachable from this lane, so "catalog projection,
  roster/codex/preview/summon payloads carry rank id + display name" is **not** claimed.
- `dotnet run --project gk-forge/tools/CreatureQualityReport` was not run (the tool is denied); the GAP-5 answer is
  read from the file, and the zero-match grep above is the measured evidence that no rank dimension exists
  today.
- The Delve filter logic and the null-threat throw are unchanged by this commit — the rank field is carried,
  not read, by the filter (Tasks 10-12 own the remaining gate sites and each has its own pass-through proof).
