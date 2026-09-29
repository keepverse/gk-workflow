# Spec: narrative-readings

Status: **DRAFT for owner review, 2026-09-19. Spec phase; no build authorized.** Every `file:line` below was
opened in this session.

Module `narrative-readings`, row 25 of the [npc-story-events map](../npc-story-events-map.md) (`:230`), wave 5.
Depends on `story-ledger`. Implements ideal §11 items 6 and 9 (`npc-story-events-ideal.md` §11) and the map's
readings list (`npc-story-events-map.md:383-387`). Session record: `tasks/sessions/narrative-programs-spec2-20260919.json`.

## Objective

Tell the owner and the content pipeline whether the narrative is working — **locally, with no upload** — from facts
the story ledger already records:

1. **Pick rate** per option per storylet; an option nobody takes, or everybody takes, **flags the storylet for review**;
2. **Success readings**: beats per unit of play per place, first-repeat distance per pool, share of storylets that
   offered a roster or supply option, share of play sessions that met a named character;
3. The **repetition budget** per host: pool size against pulse rate.

Readings guide content volume. **None is a test assertion** (map principle 14, `:118-120`; ideal §11 item 9).

Success looks like: one local command prints and saves a readings report for a save, computed only from ledger facts
and the corpus; a fixture ledger yields exactly the rates its facts imply; nothing leaves the machine; no test
anywhere asserts a reading's value on the committed corpus or a real save.

## Locked anchors

- **Pick rate, locally** (ideal §11 item 6, `npc-story-events-ideal.md`): *"The story ledger already records every
  pick. A local report summarises pick rate per option per storylet; an option nobody takes, or everyone takes, flags
  the storylet for review. Local only, no upload."*
- **Success readings are reported, never asserted** (ideal §11 item 9, `:682`; map locked assumption 11, `:160-165`;
  AGENTS.md hard boundary *"A guardrail validates the CONTRACT … never a population count"*).
- **The repetition budget is pool ÷ pulse** (ideal §4.5 item 4, `:286`; §7, `:608-610`: *"The corpus size is a reading,
  never a test assertion"*).
- **No sharing of data between players; the game is local and offline** (R13 rule 5, `:561`; `spec-counter-doctrine.md`
  §7 guard `ns6-no-enemy-data-sharing` covers `Server/Narrative/**`).
- **Picks and sightings are ledger facts**: `choice.picked` with `{slot, choiceKind, outcomeOrdinal}` and `storylet.seen`
  (`spec-story-ledger.md` §2); every read orders by `seq`; `created_utc` is audit only (`spec-story-ledger.md` §2).
- **Developer surfaces stay out of game navigation** (DESIGN-GATE §1 UI row).

## Design

### 1. Inputs

Only: story-ledger facts for one save (`ListStoryFacts`, `spec-story-ledger.md` §6), the loaded corpus (for choice
kinds and host lists), and `narrative.v1.json` (new) (for cooldowns and fire curves). No telemetry, no network, no game
process. The report runs with the game closed.

### 2. Readings

| Reading | Computed as | Unit |
|---|---|---|
| **Pick rate** per `(storyletId, revision, slot)` | `choice.picked` facts with that slot ÷ answered offers of that storylet revision (lapsed offers counted separately) | per-mille, with `n` |
| **Review flag** | a slot picked in fewer than `readings.pickFloorMilli` or more than `readings.pickCeilMilli` of answers, once `n ≥ readings.minAnswers`; `leave` is excluded from the "everybody" side (always-leave is its own flag, `leave-dominant`) | flag + reason |
| **Beats per host tick** per host kind | `storylet.seen` facts ÷ host-clock advance over the window (turns, rooms, collects, returns) | per-mille per tick |
| **Beats per hour** per host kind | `storylet.seen` count ÷ the `created_utc` span of the host's facts in the window — an **audit-clock estimate**, labelled as such, used by no decision (`created_utc` is audit only) | per hour |
| **First-repeat distance** per host-kind pool | for each storylet seen twice, host ticks between its first and second `storylet.seen`; report min / median | host ticks |
| **Roster/supply option share** | share of `storylet.seen` whose storylet (at its revision) has a `use:` or `bring:` choice | per-mille |
| **Named-character share** | share of **sessions** with at least one `met` fact, where a session is the interval between two `sanctum.returned` facts (`spec-sanctum-hub-host.md` §1) | per-mille |
| **Repetition budget** per host kind | eligible pool size for the host (corpus rows hosting it, non-tombstoned, whose static eligibility is not impossible) ÷ observed fires per host tick = host ticks until the pool is exhausted; compared with `cooldown.perStorylet` for that clock | host ticks |
| **Arc health** | arcs started, finished, stalled (a cast character no longer present, `spec-cast-resolver.md` §4) | counts |

Every reading carries its sample size. A reading with `n` below `readings.minAnswers` prints as "insufficient data",
never as a rate.

### 3. Output

- **Route**: `GET /api/narrative/{playerId}/readings?worldId=` on the local server — a developer read, listed with the
  other developer surfaces and not reachable from game navigation (DESIGN-GATE §1 UI row). It is read-only and
  touches no state: it is neither Game Injector Debug nor RPG Server Debug in the live-probe sense
  (`docs/contributing/live-probe-standard.md`), because it asserts nothing about gameplay; it is a report.
- **Script**: `scripts/narrative-readings.ps1 -PlayerId <id> [-WorldId <id>]` calls the route on `127.0.0.1` and writes
  `docs/research/narrative/_readings-<yyyymmdd>-<playerId>.json` plus a console table. The file is a reading for the
  content pipeline (narrative-seed's `narrative-planner` sizes batches from it); whether to commit a given report is
  the owner's call, like the perf baselines (`docs/runbook/perf-probe-plan.md`).
- **Nothing is uploaded.** The route binds to the local server; the script writes a local file. `ns6-no-enemy-data-sharing`
  already fails any network API under `Server/Narrative/**`.

### 4. What is never done with a reading

- No test asserts a reading's value on the committed corpus or a real save. Tests assert that the **computation** is
  right over a fixture ledger (a contract: "given these facts, this rate"), and that the report's shape is stable.
- No runtime decision reads a reading: selection never adapts weights from pick rates (that would make the corpus
  tune itself invisibly; a weight change is a tuning publish a person makes).
- No reading is pinned into a doc as a constant; the report file is dated and replaced.

## Data shapes

```csharp
namespace FusionRpg.Contracts.Narrative;

public sealed record NarrativeReadingsDto(
    long PlayerId, string? WorldId, long FromSeq, long ToSeq,
    IReadOnlyList<PickRateRow> PickRates,
    IReadOnlyList<HostReadingRow> Hosts,
    ShareRow RosterOptionShare, ShareRow NamedCharacterShare,
    ArcHealthRow Arcs);

public sealed record PickRateRow(string StoryletId, long Revision, int Slot, string ChoiceKind,
    long Picks, long Answers, long? RateMilli, string? Flag);          // RateMilli null below the sample floor
public sealed record HostReadingRow(string HostKind, long Seen, long ClockAdvance, long? BeatsPerTickMilli,
    double? BeatsPerHourEstimate, long? FirstRepeatMin, long? FirstRepeatMedian, long PoolSize, long? BudgetTicks);
public sealed record ShareRow(long Numerator, long Denominator, long? ShareMilli);
public sealed record ArcHealthRow(long Started, long Finished, long Stalled);
```

Tuning **declared in `narrative.v1.json` at wave 0 (plan §4 D4; current version `v2`)**, not added in this module's
build change (report thresholds — they tune what the report
flags, not the game, so they sit with the domain's other keys and follow the same publish rule):

| Key | Unit | Starting value and reason |
|---|---|---|
| `readings.minAnswers` | count | 20: below this a per-mille rate is noise |
| `readings.pickFloorMilli` | per-mille | 50: an option chosen in fewer than one answer in twenty (within this save) is probably dominated or unclear |
| `readings.pickCeilMilli` | per-mille | 900: an option chosen nine times in ten makes the others decoration |

## Numeric types

| Quantity | Type | Why |
|---|---|---|
| counts, clocks, seqs | `long` | ledger-scale counts |
| rates | `long?` per-mille, divide last | integer per-mille math, null below the sample floor |
| beats per hour | `double?` | an estimate from audit timestamps; floating point is allowed and fits a display estimate |

## SOLID notes

- **S:** read facts, compute readings, print; nothing else.
- **O:** a new reading is one computation and one DTO field.
- **D:** depends on ledger reads and the catalog; no store is written.
- No telemetry pipeline, no second event log: the ledger is the source.

## Commands

```powershell
.\scripts\verify-change.ps1 -Paths @('src/FusionRpg.Core/Narrative/Readings/NarrativeReadings.cs','src/FusionRpg.Server/Narrative/NarrativeEndpoints.cs','scripts/narrative-readings.ps1','tests/FusionRpg.Core.Tests/Narrative/Readings/NarrativeReadingsTests.cs') -Session <session-id>
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~Narrative.Readings"
.\scripts\narrative-readings.ps1 -PlayerId 1
```

## Structure

```
src/FusionRpg.Core/Narrative/Readings/NarrativeReadings.cs     (new: pure computations over facts + corpus)
src/FusionRpg.Contracts/Narrative/NarrativeReadingsDto.cs      (new)
src/FusionRpg.Server/Narrative/NarrativeEndpoints.cs           (edited: GET readings, developer surface)
scripts/narrative-readings.ps1                                 (new)
tests/FusionRpg.Core.Tests/Narrative/Readings/NarrativeReadingsTests.cs   (new)
```

## Testing strategy

Game closed; fixture ledgers built in the test (no store for the Core computations).

- **Pick rate:** a fixture of 30 answers with 3 on slot 1 yields 100‰ for slot 1 and flags nothing at the starting
  thresholds; 1 in 30 flags `nobody`; 28 in 30 on a non-`leave` slot flags `everybody`; 28 in 30 on `leave` flags
  `leave-dominant`.
- **Sample floor:** below `readings.minAnswers` the rate is null and the flag absent.
- **First repeat:** fixture sightings at host ticks 3 and 11 give distance 8.
- **Sessions:** facts split by `sanctum.returned` boundaries give the named-character share the fixture implies.
- **Budget:** a fixture pool of 12 with an observed fire rate of 250‰ per tick reports 48 ticks.
- **Order independence:** shuffling the fixture facts before computing (the computation re-sorts by `seq`) gives the
  same report.
- **No decision reads a reading:** a source scan finds no reference to `NarrativeReadings` outside the endpoint and its
  tests.
- **Local only:** covered by `ns6-no-enemy-data-sharing` (`spec-counter-doctrine.md` §7).
- **No population:** no test runs the report over the committed corpus or asserts any reading of it.

## Success criteria

1. One local command reports every reading in §2 for a save, computed from ledger facts only. 2. Flags name storylets
for review; nothing adapts automatically. 3. Nothing is uploaded. 4. No test asserts a reading's value.

## Boundaries

- **Always:** local, read-only, sample sizes printed, audit clock labelled as an estimate.
- **Ask first:** committing a readings file into a doc as evidence for a decision; any automated content action on a
  flag.
- **Never:** upload; feed a reading back into selection or tuning automatically; assert a reading in a test.

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| `GET /api/narrative/{playerId}/readings` → `NarrativeReadingsDto` | `scripts/narrative-readings.ps1` (new), developer surfaces |
| the dated readings file | narrative-seed `narrative-planner` (batch sizing, a reading, filed), the owner's review |

## Contradictions found (report; not fixed here)

1. **"Beats per hour of play" has no play clock.** The map and ideal name an hourly reading (`npc-story-events-map.md:385`;
   ideal §11 item 9); the game keeps no session-duration record and the ledger's `created_utc` is audit only. This spec
   reports beats per host tick as the primary reading and an hourly **estimate** from audit timestamps, labelled.

## Open questions

None for the owner.

## Design-gate checklist

```
[x] Subsystems: story ledger (reader), developer surfaces, content pipeline (consumer of a reading).
[x] Session boundary recorded (narrative-programs-spec2-20260919).
[x] Read this session: map row 25, readings list, principle 14; ideal §4.5, §7, §11 items 6 and 9; DESIGN-GATE §1 UI and
    Live probe rows; AGENTS.md population rule; sibling specs story-ledger, sanctum-hub-host, counter-doctrine,
    cast-resolver.
[x] Every claim cites file:line.
[x] No population pinned — the whole module is readings, and none is asserted.
[x] No cache.
[x] Order: computations re-sort by seq; shuffled input tested.
[x] Actor numbers: none.
[x] No parallel path: the ledger is the only source.
[ ] Registry row: none new (local-only is covered by ns6-no-enemy-data-sharing).
```

## Standards audit (2026-09-19)

Independent adversarial review against DESIGN-GATE §1 (UI row — developer surfaces out of game navigation; Live-probe
row — debug scopes), §2 (9, 12), §3 rule 7, §5; `validation-ssot.md` (readings are never assertions); R13 rule 5;
three clocks (`the-loops.md`).

| # | Severity | Finding | Status |
|---|---|---|---|
| 1 | LOW | The report thresholds (`readings.*`) sit in the game's `narrative.v1.json` (new) though no balance pass tunes the game with them — tunables-ssot's test is "would a balance pass change this" | **Deferred** (kept): the file is the domain's one tuning home and the keys follow its publish rule; a split into a report-config file is not worth a second file today |
| 2 | LOW | The pick-floor rationale said "one player in twenty"; the report reads one save's answers | **Fixed** |
| 3 | LOW | Ideal line citations drifted | **Fixed**: cited by section |

Checked and holding: local only, no upload (`ns6-no-enemy-data-sharing`); no reading feeds selection or tuning (source
scan); no test asserts a reading's value (population rule); the hourly figure is labelled an audit-clock estimate and
drives nothing, so it is not a fourth clock; the route is a report, neither debug scope; dormant and fallen worlds are
read as frozen history (round 4) — nothing is written.

**Registry row proposed** (shared file, not written): `ns-readings-no-decision-reader` → the `NarrativeReadings`
reference scan (no runtime decision reads a reading). **Boundary ask:** `src/FusionRpg.Core/Narrative/Readings/**` →
`FusionRpg.Core.Tests` filter `Narrative.Readings`; `scripts/narrative-readings.ps1` (new) has no test mapping and needs one
(or an explicit unmapped-script entry).
