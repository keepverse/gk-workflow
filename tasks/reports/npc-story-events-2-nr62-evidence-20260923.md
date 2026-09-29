# Evidence — npc-story-events NR6.2 (the fog-correct reading, R18)

Lane `npc-story-events-2`, worktree `.claude/worktrees/cmdc-npc-story-events-2`, branch `cmdc/npc-story-events-2`.
Program `npc-story-events`; row `tasks/npc-story-events-todo.md` NR6.2; spec `spec-counter-doctrine.md` §1 (Owner
ruling R18), read this session.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| 60% observed fire members read `element:fire` | `dotnet test gk-core/tests/FusionRpg.Core.Tests -c Release --nologo --verbosity quiet --filter "FullyQualifiedName~DoctrineReadingTests"` | `Failed: 0, Passed: 12, Total: 12` (112 ms) — 6 fire of 10 observed members ⇒ `600‰` and `LeanKey == element:fire` | `gk-core/src/FusionRpg.Core/Narrative/Doctrine/DoctrineReading.cs` |
| 30% fire against 30% ice reads no lean | same run (`Thirty_percent_fire_against_thirty_percent_ice_is_a_tie_and_reads_no_lean`) | pass — shares `300/300` (with 200/200 behind them); a tie at the top is no lean, because the top must be STRICTLY above every other share | same |
| A fire lean kept off his `Exact` observation and out of every battle he fought or saw reads no lean; the same lean on observed ground does | same run (`A_fire_lean_he_never_saw_reads_no_lean_...`) | pass | same |
| A glimpsed force adds nothing | same run (`A_glimpsed_force_adds_nothing_to_a_share`) | pass — `Exact=false` records produce an EMPTY share list | same |
| A battle he fought out of sight counts; one he neither fought nor saw counts for nothing | same run (`A_battle_he_fought_out_of_sight_counts`, `A_battle_he_neither_fought_nor_saw_counts_for_nothing`) | pass — the id's sides are read from `BattleKinds.IdFor`'s shape; a battle with neither side his and a sector outside his latest observation contributes nothing | same |
| Nothing observed is no lean | same run (`Nothing_observed_is_no_lean`) | pass — the empty result, no lean, share 0 | same |
| Two worlds differing only in battle winners, or in which antagonist entity fought, read identically — and a counting battle equals seeing the same forces on the ground | same run (`Two_worlds_differing_only_in_battle_winners_read_identically`, `Which_antagonist_entity_fought_does_not_change_the_reading`, `A_counting_battle_reads_the_same_as_seeing_the_same_forces_on_the_ground`) | pass — the winner lives in the entry's `Detail`, which the reading never opens | same |
| A reflection test pins `Of`'s parameters | same run (`The_read_takes_world_state_this_turns_battles_and_two_faction_ids`) | pass — `(WorldState, IReadOnlyList<TurnReportEntry>, string, string)` exactly | same |
| The output is aggregate only, with a falsifier | `dotnet test gk-core/tests/FusionRpg.Guard.Tests -c Release --nologo --verbosity quiet --filter "FullyQualifiedName~NarrativeDoctrineReadingGuardTests|FullyQualifiedName~EnforcementRegistryGuardTests"` | `Failed: 0, Passed: 22, Total: 22` (116 ms) — 4 new guard tests + 18 registry; the leak rule is a pure text scan and the planted `EntityId` member proves it bites | `gk-core/tests/FusionRpg.Guard.Tests/NarrativeDoctrineReadingGuardTests.cs` |
| The registry row and the guard's map line land together | `python gk-core/scripts/guard-narrative.py` | `NARRATIVE GUARD OK - 6 row(s) guarded by 'narrative', 6 mapped` | `gk-core/scripts/enforcement-registry.v1.json` (`ns6-reading-aggregate-only`), `gk-core/scripts/guard-narrative.py` |
| The trait filter really selects the new tests | `pwsh … gk-core/scripts/guard-narrative.py -RunTraitFilter` | `FusionRpg.Core.Tests -> Guard=narrative selected 79 test(s), 0 failed` (67 before this row); `FusionRpg.Guard.Tests -> selected 9 test(s), 0 failed` (5 before) | same |
| The boundary guard still holds after the registry rewrite | `pwsh … gk-core/scripts/guard-verification-boundaries.py` | `VERIFICATION BOUNDARY GUARD OK` | — |
| Path-owned verification | `pwsh … scripts/verify-change.ps1 -Paths @(<the 5 changed paths>) -AllowUnscoped` | exit 0 — every path resolves FOCUSED (`core-narrative` ×2, `guard-narrative`, `enforcement-registry`); `core core.narrative` **130 passed**, `guard guard.enforcement-registry` **18 passed**, `guard guard.narrative` **5 passed** = **153 passed, 0 failed** | — |

**Design notes.**

- **Two observation sources and nothing else** (spec §1): his faction's latest observation (`LastSeenTurn ==
  turn − 1`, because the study step runs in `Events` before this turn's `Intel` — one turn late is correct) and this
  turn's battle entries he took part in or saw. The winner is never read, an enemy identity is never read, no character
  is read. Members come from the entity as it stands (intel carries no species roster, and a roster can only shrink
  between his observation and `Events`), which is the smallest faithful read.
- **Shares are per key family with their own denominators** (observed members for elements, observed legions for
  posture, observed player-held sector slots for ground), and the lean must be at or above the SHIPPED threshold
  (400‰, read from `NarrativeTuningHub`) and strictly above every other share.
- **The reading is pure and memoryless** — recomputed every call from the world and the report it is handed, so
  keeping a lean out of his sight is real counter-play (R18).
- **The Guard.Tests half is a source scan, not a reflection test over Core types**, because
  `FusionRpg.Guard.Tests` references no Core assembly; the type-level reflection assertion lives in
  `DoctrineReadingTests` (which does). The gap is stated in the guard file itself rather than implied.
- `CreatureSpeciesCatalog` is read for a member's primary element; the wire spelling is the shipped element table's
  (the same one `DoctrineCatalog.ElementKeys` pins), and a species the catalog does not know reads `unknown` rather
  than a guessed element.

**NOT proved / named deviations.**

- The row's Verify line is run renamed: `-Session <sid>` cannot resolve in this lane (no session record;
  `tasks/sessions/**` is outside the allowed paths), so it passes `-AllowUnscoped`.
- **The study bar, adoption and the counter-play setback are NOT this row** (NR6.3/NR6.4/NR6.5): nothing yet stores
  a doctrine on a faction or advances the bar, so `DoctrineReading` has no production caller until NR6.3 lands —
  which the row itself declares with `Depends: NR6.2` on NR6.3's side. The reading is landed with its full case set
  now because NR6.3's bar cannot be built without it.
- **The reading was validated against the FIXTURE registries, not the committed corpus**: `NarrativeTuningLoader`
  joins the registries at parse time, and the committed corpus is the shape/semantic mismatch NR1.5's real-corpus
  read filed this segment (arrays vs the spec's keyed object; `host-kinds.v1.json`'s `climates: []`). The tuning
  values themselves are read from the committed `gk-core/data/tuning/narrative.v2.json`.
