# Spec: storylet-selection

Status: **DRAFT for owner review, 2026-09-19. Spec phase; no build authorized.** Every `file:line` below was
opened in this session.

Module `storylet-selection`, row 10 of the [npc-story-events map](../npc-story-events-map.md) (`:216`), wave 2.
Depends on `storylet-contract` (rows, `IsNegative`, arcs), `narrative-predicates` (eligibility and specificity) and
`story-ledger` (seen, cooldown and fairness history; arc pins); calls `cast-resolver`. Consumed by
`choice-resolution` and every host. Session record: `tasks/sessions/narrative-programs-spec2-20260919.json`.

## Objective

One selection procedure, identical for every host, that answers *"which storylet happens here, now"*:

1. **Tier** — a spine beat pre-empts (at most one per pulse); then priority storylets (consequences, the next arc
   or chain link after its predecessor was seen); then the pool.
2. **Pool pick** — a seeded weighted draw, weight = frequency band × specificity, unplayed before played, the pool
   resetting without resetting cooldowns.
3. **Fire chance with pity** for sparse hosts, `p = min(1000, p0 + n × step)` per-mille.
4. **Cooldowns** per storylet and per kind on the host's own clock.
5. **Fairness** — no two negative storylets in a row on one host.

A host decides **when** to ask and passes its site; it never decides which storylet or what it pays (ideal §6.2,
`npc-story-events-ideal.md:375-377`).

Success looks like: the same seed, ledger and corpus revision select the same storylet; a fixture spine beat
always pre-empts the pool; an arc's next link is chosen before texture; the pity counter needs no stored state;
filters give the same survivors in any order.

## Locked anchors

- Selection, in order (ideal §6.2, `npc-story-events-ideal.md:346-356`): tier, pool pick, fire chance with pity,
  cooldowns. Fairness rules (`:357-359`).
- The Delve's filters are pure set intersections, proven order-independent
  (`gk-core/src/FusionRpg.Core/Delve/Events/EventFilters.cs:5-11`, `ApplyAll` at `:111-125`); the draw goes through
  `WeightedChoice.Pick` on a named stream (`gk-core/src/FusionRpg.Core/Delve/Events/EventDraw.cs:42-66`;
  `gk-core/src/FusionRpg.Core/Actions/Seeding/WeightedChoice.cs:25`).
- One frequency vocabulary: the item registry's `dropBand` weights 1000/300/90/25/7
  (`party-dungeon/spec-event-deck.md:44-47`; passed in today as a table, `gk-core/src/FusionRpg.Core/Delve/Events/EventDeck.cs:204-208`).
- Three clocks, not a fourth (map principle 4, `:83-85`); no real-time cooldown.
- Pacing limits are structural consts (`spec-narrative-vocabulary.md` §4): one spine beat per pulse.
- Draw-time seen: *"Rows are written with the room's `event_id` at the draw … a wipe does not un-see an event"*
  (`party-dungeon/spec-event-deck.md:252-264`); the draw spends the repeat-scope slot whatever the player later
  chooses (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Delve.cs:428-438`).

## Design

### 1. Inputs

```csharp
namespace FusionRpg.Core.Narrative.Selection;

public sealed record SelectionRequest(
    IStoryletHost Host,                  // spec-storylet-reseam.md §2
    string SlotKey, string SlotKind,     // the host site ("{sectorId}:{slotIndex}", a room key, "sanctum")
    long HostClock,                      // the host clock's current value
    ulong Seed,                          // world seed, delve seed, or the save seed (spec-cast-resolver.md §5)
    NarrativeFactView Facts,             // built once per pulse from the ledger, the cast and the party
    string? Climate,                     // the site's climate; null when climate-neutral
    IReadOnlyList<SpineBeatCandidate> SpineBeats);   // from spine-progress; empty until wave 4

public abstract record SelectionResult
{
    public sealed record Quiet(string Reason, long PityMisses) : SelectionResult;            // no storylet this pulse
    public sealed record Chosen(EventRow Storylet, StoryletCast Cast, SelectionTier Tier,
                                long Weight, int Specificity) : SelectionResult;
}

public enum SelectionTier { Spine, Priority, Pool }
```

`NarrativeFactView` (`spec-narrative-predicates.md` §4) exposes the ledger reads this module needs:
`LastSeenClock(storyletId)`, `LastKindClock(kind)`, `LastFiredAtSite()`, `Played(storyletId)`,
`ArcProgress(arcRef)`. It is a per-pulse value, not a cache.

### 2. The procedure

```text
if world host and WorldNarrativePhase(world) != Live:   -> Quiet("world-dormant" | "world-frozen")    # round 4
candidates  = catalog rows where hostKind ∈ row.Hosts and not row.Tombstone and host.KindFits(slotKind, row.Kind)
survivors   = candidates ∩ repeatScope ∩ cooldown ∩ eligibility ∩ castable ∩ fairness          # §3; pure sets

if SpineBeats has an eligible beat:                     -> Chosen(first by spine order, tier Spine)   # bypasses fire chance
priority    = survivors where IsPriority(row)           # §4
if priority non-empty:                                  -> Chosen(weightedPick(priority), tier Priority) # bypasses fire chance
if not FireRoll(host, site, clock):                     -> Quiet("fire-miss", n)                      # §6
pool        = survivors; if unplayedFirst and any unplayed: pool = unplayed
if pool empty:                                          -> Quiet("empty-pool") — or refuse on a dense host (§7)
                                                        -> Chosen(weightedPick(pool), tier Pool)
```

Owner ruling 2026-09-19 (round 4): a world host never draws for a `Dormant` (hibernating or idle) or `Frozen`
(fallen) world; the request carries the world's derived `WorldNarrativePhase` (`spec-narrative-vocabulary.md` §3).
World-continuity's `world-event-budget` resolves hibernating events inside its own `CoarseStep`; any fact it emits is
its record, appended through the ledger's `coarse:` source (`spec-story-ledger.md` §5), not a draw by a host here.

Spine beats and priority storylets bypass the fire roll on purpose: a consequence the player earned must not be lost
to a quiet roll, and the spine is at most one beat per pulse (`SelectionBounds.SpineBeatsPerPulse`).

### 3. Filters (commutative set operations)

| Filter | Keeps a storylet when | Reads |
|---|---|---|
| repeat scope | it has not been seen in its scope (table below) | `storylet.seen` facts |
| cooldown | `HostClock − LastSeenClock(id) ≥ cooldown.perStorylet[clock]` and `HostClock − LastKindClock(kind) ≥ cooldown.perKind[clock]` | `storylet.seen` facts' `host_clock` |
| eligibility | its compiled eligibility tree evaluates true against a frame filled for it | `narrative-predicates` |
| castable | `CastResolver.CastStorylet` returns `Cast` (not `Uncastable`, not `Forbidden`) | `cast-resolver` |
| fairness | not (`row.IsNegative` and the last `fairness.maxNegativeInARow` storylets fired at this site were negative) | `storylet.seen` facts at the site |

The Delve's `delve.room` clock has no `cooldown.*` keys: its per-kind cooldown is the existing recent-cells filter
(`EventFilters.cs:94-106`), which the Delve host keeps supplying through `EventSeenSets`
(`gk-core/src/FusionRpg.Core/Delve/Events/EventDeck.cs:24-35`).

**Repeat scope on every host.** `repeatScope` is event-deck's three-member vocabulary (`per-delve`, `per-domain`,
`once-per-player`, `EventFilters.cs:76-91`). Read against a host's own clock:

| `repeatScope` | Delve host | world hosts | expedition / sanctum hosts |
|---|---|---|---|
| `per-delve` | not twice in one delve (today) | not twice at one host site in one world | not twice in one expedition / return |
| `per-domain` | not twice in one domain (today) | not twice in one world | not twice in one save |
| `once-per-player` | never again for the save (today) | never again for the save | never again for the save |

The Delve column is unchanged. The other columns are this module's generalization and are recorded as a reading of
the existing vocabulary, not a new one.

Order independence is required and tested: every filter is a pure predicate over one row plus the view, so any
order leaves the same survivors (the property `EventFilters` already proves for its four, `:5-11`).

### 4. Priority

A survivor is **priority** when any of these holds:
- it is arc link `k ≥ 2` and link `k − 1` of the **same arc instance** has a `storylet.seen` fact (`ArcProgress`),
  or a legacy row whose `chainRef` predecessor has been seen — today no draw path reads `ChainRef` at all
  (ideal §3.2, `npc-story-events-ideal.md:161`), so chains go live here; or
- it is a **consequence**: its eligibility tree requires a story fact — a `StoryFlagSet` or `DoctrineStudying` leaf
  (the leaves a widened `eligibility` list compiles to, `spec-narrative-predicates.md` §5; Alignment 2026-09-20: was
  `StoryFlagSet` or `CharacterStateIs`, but `character-state-is` is a slot condition in the seed contract and never
  reaches `eligibility`) that is a direct child of the top-level `And` (or the whole tree). This is computed once at
  load, from the tree's shape, so a storylet that merely *can* react to state is not promoted; one that *requires* a
  state is; or
- it **teaches a mechanic this save has not been taught** (Owner ruling 2026-09-20: story is also the tutorial): its
  `Teaches` (`spec-storylet-contract.md` §2, from `narrative-seed/spec-storylet-vocab.md` §3.8) names a value for which
  the save has no `mechanic.first-seen` fact. Once per save per mechanic: when a teaching storylet is **answered**
  (any choice, `leave` included) or a teaching scene is **acknowledged** (a skip included), the same transaction
  appends `mechanic.first-seen` (save scope, subject `mechanic:{value}`, dedupe `mechanic:{value}`;
  `spec-narrative-vocabulary.md` §3) for each value it teaches, so the priority lapses. Being drawn is not being
  taught — an offer the player never answers keeps the mechanic untaught. Teaching never gates: `Teaches` is read here
  and nowhere else — no eligibility, unlock or checkpoint reads it — and every teaching storylet keeps its `leave`.
  The first-session checkpoints are `docs/architecture/standalone/spec-first-session-progression.md`'s; no `teaches`
  value duplicates one (`storylet-vocab` §3.8 boundary).

Arc link `k ≥ 2` resolves from its pin (`spec-story-ledger.md` §4), not from the live catalog. The first link of an
arc is ordinary pool content; choosing it writes `arc.started` with the cast (`spec-cast-resolver.md` §4) and the
pins, in one ledger transaction.

### 5. Weight

```text
freq        = dropBandWeight[ tuning.selection.kindFrequencyBand[row.Kind] ]        # 1000/300/90/25/7, int
specificity = number of eligibility leaves that evaluate true for this row          # 0..16 (MaxNodes)
affinity    = EventDraw.WeightMilliFor(row, climate, match, none, off)              # existing, ‰ (EventDraw.cs:30-35)
weight      = freq × (1000 + specificityStepMilli × specificity) × affinity / 1_000_000
```

Computed in `long` with `checked`, with **one** division at the end (Audit 2026-09-19: the first draft divided by
1000 twice, truncating twice — CLAUDE.md numeric rule 5 says divide last so truncation happens once), then narrowed
`checked` to `int` for `WeightedOption<T>` exactly as `EventDraw.PickEvent` narrows today. With the shipped tuning
(`specificityStepMilli` 1000; climate `matchMilli` 1000, `gk-core/data/tuning/dungeon.v3.json:316-320`) the bound is
`1000 × 17,000 × 1000 / 1,000,000 = 17,000`; a tuning publish that raises either input past `int` throws at the
narrowing rather than wrapping, and the weight-bound test computes its expectation from the loaded tuning, never a
literal. Specificity counts each leaf by compiling it alone at load (one compiled
predicate per leaf; the tree has at most 16) — "most specific wins, tempered by the draw" (ideal §6.2 item 2).

The pick is `WeightedChoice.Pick(options, rollSeed, streamName)` on `host.StreamRoot(slotKey) + ":pick"`, the
engine's stream (`spec-storylet-reseam.md` §2). Options enumerate in ordinal id order.

### 6. Fire chance with pity, with no stored counter

```text
n      = pulses at this site since the last Chosen result there   # HostClock − LastFiredAtSite().HostClock, or since the site existed
p      = min(1000, firing[hostKind].baseMilli + n × firing[hostKind].stepMilli)   # per-mille
roll   = SeededRng.DeriveStream(seed, host.StreamRoot(slotKey) + ":fire:" + HostClock).NextULong() % 1000
fires  = roll < p
```

`n` is **derived from the ledger** (the last `storylet.seen` fact at this site), so there is no pity counter to store
or to go stale. The `min(1000, …)` is a probability bound — a bounded ratio — and the code says so in a comment
(map principle 7, `:94-96`). A Delve room or a sanctum return with `baseMilli = 1000` always fires. The modulo draw
has a bias below 10⁻¹⁵ for a 64-bit source; it is documented, not corrected.

### 7. Empty pools

- **Dense hosts** (`delve.room` clock): the room kind has already decided the room holds an event, and a blank room
  is a refusal (`party-dungeon/spec-event-deck.md` §9, `:266-270`). An empty pool throws `EventDeckRefusal` naming
  the site and the filter that emptied it. If only the fairness filter emptied it, fairness **yields** for that
  pulse (the rule is a preference; a blank room is a defect) and the yield is recorded in the ledger's
  `storylet.seen` attributes (`fairnessYielded: true`) for `narrative-readings`.
- **Sparse hosts** (every other clock): an empty pool is `Quiet("empty-pool")`. Most world pulses are meant to be
  quiet (ideal §7, `npc-story-events-ideal.md:597`).

### 8. What a Chosen result writes

The host, in its own transaction, appends `storylet.seen` (subject `storylet:{id}`, `storylet_revision`, host kind,
host clock, attrs `{slotKey, repeatScope, tier, negative}`) at the **draw**, and `arc.started` plus pins when the
storylet is an arc's first link. Selection itself is pure and writes nothing. (`mechanic.first-seen` is written at the
answer, §4, not at the draw — Owner ruling 2026-09-20.)

## Data shapes

- No table: pity, cooldown and fairness history are derived from `storylet.seen` facts.
- Tuning: `selection.*`, `firing.*`, `cooldown.*`, `fairness.*` (`spec-narrative-vocabulary.md` §4).

## Numeric types

| Quantity | Type | Why |
|---|---|---|
| `HostClock`, `n`, cooldown lengths | `long` | unbounded clocks (R3) |
| `p`, `baseMilli`, `stepMilli` | `long` per-mille, `checked` | `n × step` grows with a long drought; `min(1000, …)` is applied after the checked sum |
| weight | `long` intermediate, narrowed `checked` to `int` | `WeightedOption<T>.Weight` is `int` (`WeightedChoice.cs:6`); the bound is 17,000 |
| specificity | `int` | 0..16 |
| roll | `int` from `ulong % 1000` | a per-mille die |

## SOLID notes

- **S:** one selection procedure; hosts only supply site, clock and facts.
- **O:** a new host is an `IStoryletHost` and a `firing`/`cooldown` tuning row; the procedure is unchanged.
- **L:** the Delve keeps its own seen sets and recent-cells cooldown; when `delve-host` routes the Delve through this
  procedure, legacy rows (no eligibility, one frequency band) weigh exactly as their climate affinity today, up to a
  common factor.
- **D:** depends on `IStoryletHost`, `NarrativeFactView`, `CastResolver` and the catalog, never on a store.

## Commands

```powershell
.\scripts\verify-change.ps1 -Paths @('src/FusionRpg.Core/Narrative/Selection/StoryletSelector.cs','tests/FusionRpg.Core.Tests/Narrative/Selection/StoryletSelectorTests.cs') -Session <session-id>
dotnet test tests\FusionRpg.Core.Tests --filter "FullyQualifiedName~Narrative.Selection|FullyQualifiedName~Narrative.Storylets"
python scripts\audit-magic-numbers.py --domain narrative ; python scripts\audit-overflow.py
```

## Structure

```
src/FusionRpg.Core/Narrative/Selection/StoryletSelector.cs     (new: the procedure)
src/FusionRpg.Core/Narrative/Selection/SelectionFilters.cs     (new: the five set filters)
src/FusionRpg.Core/Narrative/Selection/FireChance.cs           (new)
src/FusionRpg.Core/Narrative/Selection/SelectionTypes.cs       (new: request, result, tier, spine candidate)
tests/FusionRpg.Core.Tests/Narrative/Selection/StoryletSelectorTests.cs   (new)
tests/fixtures/narrative/selection/                              (new: fixture corpus and ledgers)
```

## Testing strategy

All tests run against a fixture corpus and in-memory fact lists; none reads the committed corpus.

- **Determinism:** the same request selects the same storylet on two runs; changing only `HostClock` or `Seed`
  changes the stream name or root and is allowed to change the pick.
- **Tier order:** a fixture spine beat pre-empts an eligible priority storylet, which pre-empts the pool; two
  spine beats yield exactly one per pulse.
- **Arc and chain:** link 2 is priority only after link 1's `storylet.seen`; a legacy `chainRef` successor becomes
  priority after its predecessor is seen.
- **Consequence:** a storylet requiring a flag is priority once the flag exists; one with the flag under an `Or` is not.
- **Filters commute:** every permutation of the five filters leaves the same survivors (property over fixtures).
- **Unplayed first and reset:** with one unplayed candidate it is always chosen; when all are played the pool resets,
  and a storylet still in cooldown stays excluded.
- **Cooldown on the host clock:** a storylet seen at turn 10 with a 10-turn cooldown is absent at turn 19 and
  present at turn 20; wall-clock time has no input.
- **Pity:** with `base 50, step 5`, the derived `n` rises one per quiet pulse and resets after a Chosen result; the
  probability reaches 1000 at `n = 190` and the `min` holds it there; a Delve room (1000/0) always fires.
- **Fairness:** after a negative storylet, a sparse host never chooses another negative next; a dense host whose pool
  holds only negatives yields and records `fairnessYielded`.
- **Empty pools:** dense → `EventDeckRefusal` naming the filter; sparse → `Quiet("empty-pool")`.
- **Weight bound:** the maximum weight (16 matched leaves, `staple`, `match`) equals the value computed from the
  fixture tuning (17,000 with the shipped values) and fits `int`; an oversized fixture tuning throws at the checked
  narrowing.
- **World lifecycle (Owner ruling 2026-09-19 (round 4)):** a world host request for a `Dormant` or `Frozen` world
  returns `Quiet` and derives no stream; the same request is selectable again after the world returns to `Live`.
- **Stream isolation:** every stream the selector derives starts with the host's stream root; none is a combat stream.

## Success criteria

1. One procedure selects for every host kind. 2. Tiers, pool pick, pity, cooldowns and fairness each have named
tests. 3. No stored selection state; everything derives from the ledger. 4. Deterministic for the same seed, ledger
and revision. 5. The Delve's behaviour is unchanged until `delve-host` routes it here.

## Boundaries

- **Always:** filters as pure sets; draw on the host's named stream; derive pity from facts; write seen at draw.
- **Ask first:** a second spine beat per pulse; letting fairness blank a dense host; a fourth tier.
- **Never:** a real-time cooldown; a stored pity counter; a per-host selection variant; a model call.

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| `StoryletSelector.Select(SelectionRequest)` → `SelectionResult` | every host (wave 4), `choice-resolution` |
| `SpineBeatCandidate` | `spine-progress` (provider) |
| `storylet.seen` attribute set (`slotKey`, `tier`, `negative`, `fairnessYielded`) | `narrative-readings`, `quest-log-contract` |

## Contradictions found (report; not fixed here)

1. **Repeat scopes outside the Delve.** The three `repeatScope` members are Delve-shaped (`EventFilters.cs:68-91`);
   neither ideal nor seed contract says what `per-delve` means on a world host. §3 defines it per clock. If
   narrative-seed would rather add host-neutral members, that is a `storylet-vocab` change and this table follows it.

## Open questions

None for the owner.

## Design-gate checklist

```
[x] Subsystems: storylet engine, narrative ledger (reader), roll SDK, tunables.
[x] Session boundary recorded (narrative-programs-spec2-20260919).
[x] Read this session: ideal §4.1 (selection prior art), §6.2, §7; spec-event-deck.md §2, §3, §8, §9;
    EventFilters, EventDraw, EventDeck, WeightedChoice, SeededRng; RpgStore.Delve.cs draw-time seen rule.
[x] Every claim cites file:line.
[x] Order independence stated for the filters and tested over permutations.
[x] No cache; the fact view is a per-pulse value. No population pinned. No actor number.
[x] Caps: the fire-chance min is a bounded ratio and commented; no magnitude capped.
[x] No parallel path: one selector for every host.
[ ] Registry row: none proposed. (Audit 2026-09-19: row proposed below.)
```

## Standards audit (2026-09-19)

| # | Severity | Finding | Status |
|---|---|---|---|
| 1 | high | Round-4 owner ruling: selection had no world-lifecycle gate, so a hibernating or fallen world's hosts could still draw | **Fixed:** `Quiet` for `Dormant`/`Frozen`; coarse-step facts are world-continuity's record |
| 2 | medium | The weight divided by 1000 twice (two truncations), against CLAUDE.md numeric rule 5 | **Fixed:** one division |
| 3 | low | The weight-bound test pinned 17,000, a value derived from tuning, not a closed vocabulary | **Fixed:** computed from the loaded tuning |

Checked and clean: filters are pure commutative sets with a permutation test; pity derived from the ledger (no stored
counter, so no §2.16 trigger set); the fire-chance `min(1000, …)` commented as a bounded ratio (no magnitude cap);
cooldowns on host clocks, no wall clock; `long` for clocks and per-mille; named streams; draw-time seen writes;
no population pin. Verified: `EventDraw.WeightMilliFor` (`gk-core/src/FusionRpg.Core/Delve/Events/EventDraw.cs:30-35`) and
the shipped climate milli values.

**Proposed enforcement-registry row:** `ns-no-per-host-selection` — one selection procedure for every host; guard:
`StoryletEngineSingleSourceTests` (`spec-storylet-reseam.md` §6) extended to `*Selector` types referencing
`EventRow` outside `FusionRpg.Core.Narrative.Selection`.

## Cross-lane alignment (2026-09-20)

- Owner ruling 2026-09-20 (story is also the tutorial): §4 gains a third priority rule — an eligible storylet that
  teaches a mechanic the save has no `mechanic.first-seen` fact for is priority; the fact is appended when a teaching
  storylet is answered or a teaching scene acknowledged, once per save. The boundary with the first-session sequence
  (`docs/architecture/standalone/spec-first-session-progression.md`: it owns the checkpoints, the story supplies the
  scenes that teach) is stated there and in `narrative-seed/spec-storylet-vocab.md` §3.8.
- Alignment 2026-09-20: the consequence rule reads the leaves a widened `eligibility` list can compile to
  (`StoryFlagSet`, `DoctrineStudying`).
