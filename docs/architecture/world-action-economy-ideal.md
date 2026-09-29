# World action economy — the ideal

> ### ⚠️ Status line vs. what shipped (checked 2026-09-18)
>
> **This document's status line is not current, and it is the kind of wrong that costs a whole
> session.** Measured today: **map APPROVED 2026-09-15 (owner: "Approve all")**, **4 module specs** under `docs/architecture/world-action-economy/`, and a task list at **all 4 module specs written against the approved map**.
>
> A status line reading *"no build authorized"* over a program that has already shipped invites
> the next session to re-derive work that exists — and its inventory of gaps is stale in the same
> direction, because a gap named before the build is usually closed by it. **Read this document
> for its reasoning and its decisions; never for its status, its gap list, or its counts.**
> Verify anything load-bearing against the capability map, the task list, and the code.

**Status:** idea phase, 2026-09-15. Not a spec. No build authorized.

**Program id:** `world-action-economy` (new). No existing program owns per-action costs on the
world map: `world-map-program.md` is the engine foundation (phases, clock, determinism — not an
economy design), and `empire-development-map.md` is the inventory/wonder umbrella (carry/deposit
verbs are only a subset of the verbs a cost rule would touch — cache-claim, clear, sustain, build,
dowse are outside it). A cost rule spanning all of them gets its own id and its own future map;
the relation to the umbrella (`scoped-inventory` verbs as first consumers) is registered at spec
time, not here.

**Owner order (verbatim):** "cost action point, need new idea for this, inspire of heroes of might
and magic 3". **Motivation:** claiming a cache (`ClaimCorpseCacheIntoCargo`) currently costs
nothing; cache-claim — and by extension deposit/withdraw/build-adjacent verbs — should cost action
points.

---

## Step 0 — principles, in this doc's own words (read first, per idea-phase §0)

1. **Genre and loops first.** This is the RPG-plus-empire-building game (`the-game.md:11` — "Rise
   of Summoner is an RPG plus empire-building game"). No new loop is proposed; see below.
2. **Every RPG feature lives in the RPG layer, never by changing what PvZ is.** This economy is
   pure world-map state — a budget field, command kinds, Data verbs. It never reads PvZ state,
   never touches the injector, never needs a Unity field. "Does the lawn support action points"
   is the wrong question; the right one is "does the world-map layer already have a budget" —
   yes, see §What already exists.
3. **Two async systems; delay is the designed degradation, not a bug.** Orders seal at commit and
   reveal together (`TurnEngine.cs:188-233`); a cost paid this turn that bites next turn is the
   normal shape of this engine, not a problem to engineer around.
4. **One power ladder.** Contests read `Θ`, magnitudes read `P(Θ)`, and the §10 inventory is
   closed. Action costs in this doc are **flat per-mille spends from a turn budget** — no
   level-derived number exists here. If any cost ever scales with Dave's level, it must read the
   ladder; a private `f(level)` cost curve is the defect the ladder exists to stop.
5. **The balance surface is data.** Every per-verb cost this idea introduces belongs in
   `data/tuning/world.v{n}.json` beside `movement.dowseBudgetMilli` — never a `const`. The dowse
   precedent (`LaneCost.cs:51-56` comment: "Never a const here … exactly the kind of number a
   balance pass wants to move") is the working example.
6. **No hard progression ceilings; absolute bounds throw, structural limits say so.**
   Pack/vault/cargo limits upstream are structural (fixture-bound, refuse-with-reason). A zero
   budget refusing an act with a named reason (`entity.spent`-shaped, cf. `entity.held`,
   `entity.routed`) is a structural turn boundary in the same class — it must refuse loudly in
   the turn report, never silently clamp or swallow the order.
7. **Gameless-first is capability.** The world map already resolves server-side with Fusion
   closed. Costs keep that property: no injector read, no live-match gate, no lawn-only step.

**DESIGN-GATE §1 rows read this session:** Product vision (`guide/the-game.md`,
`guide/the-loops.md`); World map (`world-map-program.md`); Tunables (`tunables-ssot.md`).
**Honest gaps:** the Economy row (`empire-economy-ssot.md`) was **not** re-opened — the
faucet/sink framing below ("every cost names its budget in the same change") is borrowed from
the gate's summary line, not verified against the SSOT; `power/ssot-power-scale.md` §11 was not
re-opened (no cap is proposed, so the row is cited, not applied); the `world-map-runtime` spec
set was not re-opened (engine facts below are verified against `src/`, not against those
specs); `decisions.md` was grepped for phase-order/RulesetVersion locks (confirmed) but not read
in full. **No suite was run** — idea phase; no "moves goldens" claim is made beyond naming the
bump as a consequence (see §What this deliberately does not decide).

---

## Which loop this extends

**Place 4 — World map, adventure** (`the-loops.md:103-111`: "The graph where you go: fog, march,
claim, cede, dowse… Time here is virtual turns — End Turn commits everyone's orders") and
**Place 3 — Farming, hunting, and defending the empire** (`the-loops.md:83-99`: farm = hold
ground and take yield; hunt = the aftermath that includes picking things up).

- Cache-claim hangs on Place 4's march-and-claim verbs and Place 3's hunt aftermath (a fallen
  cache is ground reached, then picked up — the inventory-surfaces ideal §1 already places it
  there, `empire-inventory-surfaces-ideal.md:43-46`).
- Deposit/withdraw hang on Place 5 — World stage, empire building (`the-loops.md:115-121`:
  "Inside a held sector: slots, buildings, recruitment, upkeep") insofar as the vault lives
  there; the *act* of moving goods is Place 4 (the band stands somewhere and does something).
- No new loop, no fourth stock, no stamina gate, no diary clock. What is priced is **acts inside
  the existing virtual-turn clock**, not a new clock and not a wallet. (`the-game.md:73`:
  "There is no stamina gate and no fourth wallet" — the fork in §The shape is where this
  constraint bites, and it bites Fork B hardest.)

---

## What this is (player language)

*My war bands can march, and marching costs them distance. Now everything else they do out there
costs them too — prying open a fallen cache, loading and unloading packs, putting goods into a
settlement's vault or taking them out. A band that sprinted all day can't also strip a
battlefield bare; a band I hold in reserve still has its hands free. I spend the day, not just
the road.*

One sentence of mechanics: **every world-map act a legion performs spends from the same daily
budget its march spends from** — that is the HOMM3 shape (see §Prior art), and the fork in
§The shape is only about whether "the same budget" is literally true or merely the model.

---

## What already exists — built / wiring gap / real gap, with file:line

Every citation below was opened this session in the worktree. (Line note: the overlap audit
recorded the Snapshot refill as `TurnEngine.cs:372-376`; the code has drifted — the refill now
lives at `TurnEngine.cs:405-423`. Cited fresh below.)

### Built (the budget, the pricing, the refill, the discipline — all working end to end)

| Finding | Evidence |
|---|---|
| A per-legion turn budget EXISTS: `WorldEntity.MovementRemaining`, refilled every turn | `gk-core/src/FusionRpg.Core/World/WorldState.cs:311`; refill `gk-core/src/FusionRpg.Core/World/Turn/TurnEngine.cs:413-423` |
| The refill reads the NEW posture: stance orders land in Snapshot, then every legion's budget becomes `BudgetFor(newStance)` — "a legion keeps the budget it started the turn with and only pays for its new posture from the next turn" | `TurnEngine.cs:405-423` (comment `:405-407`, refill `:420`) |
| `BudgetFor` EXISTS: march 1000 (`PointsPerTurn`), scout 500 (`ScoutPointsPerTurn`), hold 0, dowse tunable | `gk-core/src/FusionRpg.Core/World/Movement/LaneCost.cs:32,35,47-57` |
| Dowse is the tunable-cost precedent: `WorldTuningHub.Tuning.Movement.DowseBudgetMilli`, currently 250 ("a quarter turn… the number a balance pass moves first") | `LaneCost.cs:55`; `gk-core/src/FusionRpg.Core/World/WorldTuning.cs:19,127`; `gk-core/data/tuning/world.v5.json:43` (note `:8`) |
| March pricing EXISTS: `LaneCost.For` = length × type × hazard, ley discount 800‰ on banner-climate match at either end; march spends `entity.MovementRemaining` per-mille along the path | `LaneCost.cs:105,131-144`; spend `gk-core/src/FusionRpg.Core/World/Movement/MarchResolver.cs:70-74` + `MovementPhase.cs:301-310` |
| Admit+Reveal discipline EXISTS: orders admitted (`WorldCommandAdmission.Admit`), then revealed in stable (commander, command) order; stale/illegal orders drop with a named reason, never abort the turn | `TurnEngine.cs:188-233`; admission `gk-core/src/FusionRpg.Core/World/Turn/WorldCommandAdmission.cs:17-134` |
| Per-legion limits EXIST: one-move-last-wins (two marches → later order), routed-drops (`entity.routed`), held-blocks (`entity.held`) | `MovementPhase.cs:36-41`; `TurnEngine.cs:209-226`; `ClaimResolver.cs:58-62` |
| Command vocabulary is closed and owned: 12 kinds (`stand-fast`, `move`, `clear`, `claim`, `stance`, `sustain`, `build`, `cede`, `bind-warden`, `raise`, `develop`, `assault`) | `gk-core/src/FusionRpg.Core/World/Turn/WorldCommand.cs:7-88` |
| Claims settle in Snapshot AFTER movement/sieges, because everything they depend on is only decided by then | `TurnEngine.cs:380-385`; `ClaimResolver.cs:12-15` |
| Engine change rule: world turn engine carries `RulesetVersion` (live value **10**); the locked phase order is Reveal → Movement → Sieges(/Assaults) → Production → Growth → Pressure → Events → Snapshot → Intel | `TurnEngine.cs:94,98-120`; order executed `:160-177` |
| Claim-into-cargo EXISTS with per-row fit, skip-not-refuse, replay safety — and NO cost parameter anywhere in its body | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.CacheFieldAccess.cs:280-366` (reachability-only admission `:302-304`, per-row gates `:327-337`, replay `:296-300`), public entry `:372-387` |
| Deposit/Withdraw EXIST with presence/faction/capacity gates only — signatures take `(worldId, entityId, sectorId, seq)`, no budget/cost parameter | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.CargoTransfer.cs:62-96` (refusals `cargo.not-present`/`wrong-faction`/`sector-full`) |
| Load/Unload EXIST, same shape (ownership + slot/weight gates, no cost) | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.LegionCargo.cs:253-304,395-402` (per the inventory-surfaces ideal §4, verified that session) |
| World-map stamina/AP is NOT-FOUND as a turn pool: the only `ActionPoints`-shaped economy in the repo is battle-side (`hybrid-atb` `ActionPointsEconomy(maxPoints: 2)`, per `decisions.md` battle row) — no second world pool exists to collide with. BOUNDARY NAMED (correction 2026-09-15): a tactical-scope `stamina` vocabulary DOES exist under Core/World for siege entry costs (`Siege/Obstacles.cs:26,82-83` `WireStamina`, `StructureCatalog.cs:179,183` `EntryStaminaMultiplierMilli`) — cell-entry pricing, not a turn pool; the cost design must steer around (never debit, never rename into) that vocabulary | Verified by grep this session (turn-pool scope; siege-tactical hits acknowledged as the collision surface) |

### Wiring gap (machinery exists and is inert — not a wall)

| Finding | Evidence / notes |
|---|---|
| The budget is spent ONLY by marching. No act — claim-cache, deposit, withdraw, load, unload, clear, sustain, build — reads or writes `MovementRemaining` | Proven by absence across the verb bodies above; the refusal vocabularies (`cargo.*`, `cache.unreachable`, `correlation.missing`, `claim.*`, `entity.routed/held`) contain no `*.spent`/`*.exhausted` member |
| `ClaimCorpseCacheIntoCargo` runs OUTSIDE the turn engine: it is an immediate Data verb (lock + transaction + commit), not a `WorldCommandKinds` command — so even though a budget exists, there is no pipe between the act and the budget | `RpgStore.CacheFieldAccess.cs:372-387` vs `WorldCommand.cs:83-84` (no cache-claim kind) |
| Same for deposit/withdraw/load/unload: immediate Data verbs, no command kind, no Reveal admission, no report entry | `RpgStore.CargoTransfer.cs:62-73,136-147`; `RpgStore.LegionCargo.cs:253-266,395-402` |

### Real gap (no mechanism exists anywhere)

| Gap | Notes |
|---|---|
| A per-act price list: which verbs cost, how much (per-mille), priced where | No `*CostMilli` key besides lane/ley/dowse exists in `gk-core/data/tuning/world.v5.json`; no cost table in code |
| The debit seam for immediate Data verbs: how an out-of-turn verb spends a turn-engine budget (or whether it must become a command first) | The three audit-named options — promote-to-command vs in-verb debit vs Pressure-side drain — are all unbuilt; §The shape |
| Ordering semantics: claims settle in Snapshot AFTER Movement already spent the budget — a "spend from remaining" rule needs to say which remaining (at Reveal? at act time? reserved?) | `TurnEngine.cs:160-175` order vs `ClaimResolver` Snapshot settle; no reservation mechanism exists |
| Hold-stance interaction: hold budgets 0 (`LaneCost.cs:49`) — under a literal same-pool rule a garrison could never act; whether garrison acts are free, gated, or impossible is undecided | Open question Q2 |
| Build-adjacent verbs already HAVE a cost (loam/materials: `BuildResolver` spends `CarriedLoam`/rubble/ironwork; Wonder flow spends relics) — whether AP stacks on top or build is exempt is undecided | `BuildResolver.cs`, `spec-wonder-build-flow.md`; see Q3 |

---

## Prior art — genre research, with numbers and sources

### HOMM3 (the owner's named inspiration): one pool for moving AND doing

Researched genuinely this session ( Heroes III wiki `Movement`, `Dimension Door`; thelazy.net
mirror; staroceans.org movement table).

- **One daily pool.** Every hero gets a base of **1900 movement points per day**, set by the
  SLOWEST creature in the army (1300 at speed 0 … 2000 at speed 11+). Moving costs **100 MP per
  orthogonal tile, 141 diagonal**, multiplied by terrain (rough ×125%, sand/snow ×150%, swamp
  ×175%; roads discount down to 50%). Sources: [Movement — Heroes III Wiki](https://homm.fandom.com/wiki/Movement),
  [staroceans movement table](http://staroceans.org/hero3/Movement).
- **Non-move acts debit the SAME pool — the exact shape the owner asked for.** `Dimension Door`
  (teleport, the game's strongest map act) **spends 300 MP per cast (200 at Expert Air Magic)**,
  is capped at **2/3/4 casts per day** by skill level, and **may not be cast if it would reduce
  movement to zero or below**. Pickups cost movement implicitly: the hero must spend tile-entry
  MP to stand on the resource/artifact/object. Source: [Dimension Door — Heroes III Wiki](https://homm.fandom.com/wiki/Dimension_Door).
- **End-of-day acts exist too.** Swan Pond and Watering Place **consume ALL remaining movement**
  (ending the hero's day) in exchange for their benefit; Stables (+300/400), Fountain of Youth
  (+400), Oasis (+800) grant bonus MP mid-day. Source: [Movement — Heroes 3 wiki](https://heroes.thelazy.net/index.php/Movement).
- **Documented failure modes to steal honestly:**
  1. *Teleport chains broke map balance.* Unlimited DD/Town Portal let one hero cover a map;
     competitive play caps DD at 1–2/day (tournament rules) — i.e. **a per-day act COUNT cap rode
     alongside the pool cost**, the hybrid shape (§The shape, Fork C).
  2. *The slowest-unit rule punishes mixed armies* — our analogue: if costs ever scale per member
     or per weight, mixed legions pay more; keep costs per-legion-per-act unless the owner says
     otherwise (open Q5 touches this).
  3. *Native-terrain + mono-army rewards* (no penalty when all troops match the terrain) — our
     analogue already exists as the ley/banner discount (`LaneCost.cs:139-141`); act costs should
     reuse it or explicitly not, never re-mint it.

### Age of Wonders 4: move points with a priced refresh, plus a split combat pool

- **World map:** armies move at the slowest unit's speed; **40 MP default (48 for scouts), 6 MP
  per normal hex**. **Forced March restores move points mid-turn at a price: 30% of current HP +
  mana per unit + 2 turns of Exhausted** — the precedent for "refresh the pool, but pay for it,"
  relevant if the owner ever wants a rally/forced-action verb. Scouts are simply faster (48),
  the same half-vs-full shape as our scout-500/march-1000. Source: [Unit — AoW4 Wiki](https://aow4.paradoxwikis.com/Unit).
- **Tactical combat:** 3 AP per turn, **max 2 spendable on movement** — a hard move/act SPLIT
  inside one turn. This is the anti-precedent for Fork B done right: where AoW4 wanted acts
  protected from movement, it split explicitly and visibly. Our audit verdict forbids a second
  world pool, so this pattern is cited as **rejected for the world map** (it would be the second
  pool), but it is the shape to copy if playtesting ever proves acts starve. Source:
  [Combat — AoW4 Wiki](https://aow4.paradoxwikis.com/Combat).

### Civilization VI: acts cost movement from the same pool, with named exceptions

- **Pillage costs movement** — a unit needs MP remaining to pillage (e.g. ~2 for a coastal
  raid); no MP, no raid until next turn. **Denmark's melee units pay NO movement to pillage** —
  a faction-shaped exception to a universal cost, the precedent for "one verb is free for one
  faction/stance" if the owner wants garrisons or dowsers exempted. Sources:
  [Pillage — Civ Wiki](https://civilization.fandom.com/wiki/Pillage),
  [Coastal Raid thread](https://steamcommunity.com/app/289070/discussions/0/312265782622627934).
- **Builder charges are a SECOND, discrete pool** (build/improve consumes charges, not MP) —
  again the hybrid precedent, and again **rejected here by the audit boundary** (no second pool;
  `the-game.md:73` no-stamina-gate). Cited so the rejection is on record, not overlooked.

**What transfers, in one line:** HOMM3 says price acts from the movement pool (DD: 300/200 MP +
daily count cap); AoW4 says a priced refresh (Forced March) and an explicit split are both
shipped patterns with known costs; Civ6 says acts-from-movement with named exceptions is the
genre default, and a second charge-pool is the thing you add only when the single pool proves
insufficient. All three point at Fork A first.

---

## The shape — the fork, presented honestly (nothing pre-decided)

### Fork A — extend `MovementRemaining` (the audit's boundary, HOMM3's shape)

Every priced act debits per-mille from the same budget marching spends. `BudgetFor` and the
Snapshot refill do not change shape; a new cost table says what each verb costs; the verbs check
(and spend) before they do their current gates. March-vs-act tradeoff IS the strategy: a band
that marched 1000 can't also strip a cache; scouting half the distance leaves 500 for two
250-cost acts.

- Fits: one pool (audit verdict); `the-loops.md` no-stamina-gate; HOMM3 DD precedent; dowse-250
  already prices "act instead of march" in exactly these units.
- Costs: needs the §Real-gap debit seam (immediate Data verbs can't see turn budget without
  one); needs ordering semantics (Reveal-time check vs Snapshot-time spend — claims settle
  after movement, so "remaining" must be defined, not assumed); hold-0 makes garrisons
  act-less by default (Q2).

### Fork B — a new AP field (e.g. `ActionsRemaining` per legion per turn)

Acts cost discrete points from their own pool; movement untouched. Civ-builder-charge precedent.

- Fits: discrete acts priced discretely; no march/claim ordering tangle; garrisons act freely.
- Collides with: the audit verdict ("never a second pool" — the one hard boundary this idea
  was given); `the-game.md:73` / `the-loops.md:173` no-stamina-gate (a second pool that gates
  acts IS a stamina gate until proven otherwise); SOLID one-SSOT (two refills, two admits, two
  goldens surfaces); the genre evidence above (every reference prices acts from movement first
  and adds a second pool only after). **Choosing B requires overturning the audit boundary
  explicitly and owning the stamina-gate conversation with the owner.** Listed so the cost of B
  is visible, not so B is forbidden knowledge.

### Fork C — hybrid (A + count caps, no second pool)

Fork A's single pool, plus per-turn per-legion COUNT caps on named verbs (HOMM3's DD 2/3/4-per-day
riding alongside its 300 MP) — only if spam play (claim-every-stand loops) proves real. Note
what already exists: the cache-claim log is already idempotent per `(cacheId, worldId, entityId,
correlationId)` (`RpgStore.CacheFieldAccess.cs:296-300`) — replay is solved; a count cap would
be anti-SPAM, not anti-double-spend, and must justify itself with observed play, not theory.

**Where this doc leans, without deciding:** A fits every written constraint; B contradicts two
(the audit boundary and the no-stamina-gate loop rule) and would need both overturned in the
open; C is A with an optional, evidence-gated extra. The real question is §The real question.

### The debit seam (needed by A; the audit's three options, still open)

1. **Promote the act to a command kind (Admit+Reveal).** Cache-claim/deposit/withdraw become
   `WorldCommandKinds` members, admitted at Reveal (budget check), resolved in Snapshot (spend +
   effect), reported like every other order. Purest w.r.t. the engine (one pipeline, replayable,
   golden-covered); heaviest (REST + command plumbing for verbs that work today; acts stop being
   immediate — a UX latency the surfaces ideal never assumed).
2. **In-verb/resolver debit.** The Data verb reads the legion's live `MovementRemaining` and
   decrements it in the same transaction (move-never-copy discipline, same as the cargo move).
   Cheapest; but it spends turn-budget OUTSIDE the turn (phase discipline breaks — an act
   between turns spends next turn's budget or last turn's leftover? both answers are defensible
   and both need a rule), and replay/idempotency must be re-proven per verb.
3. **Pressure-side drain.** Acts stay free at act time; the engine drains the cost from the
   legion's NEXT refill (or logs a deficit) during a turn phase. Eventual-consistency shaped;
   weakest guarantee (a disbanded/dead legion never pays), most surprising to players.

### Rejected (this phase)

| Rejected | Why |
|---|---|
| Re-mint `LaneCost` or the ley/banner discount for acts | Pricing exists and is verified; acts reuse the pool and its prices, never a parallel price engine |
| Re-mint Admit-Reveal-report discipline (a second acceptance path for acts) | `WorldCommandAdmission` + Reveal + `TurnReportKinds` already accept, drop-with-reason, and report; a second vocabulary is a SOLID fork |
| A second budget pool alongside `MovementRemaining` without overturning the audit boundary | The one hard "never" this idea was given; Fork B names its price above instead of sneaking it |
| Level-scaled act costs on a private curve | One power ladder; flat per-mille costs need no ladder read at all |
| `const` costs in code | Balance surface is data (`world.v{n}.json` movement section); the dowse comment already says why |
| Silent failure (act quietly does less when the budget is short) | Refuse with a named reason in the report/surface (GG-16 silence-is-not-an-outcome, per the surfaces ideal §3); partial-claim skip precedent (`skipped` rows stay) suggests skip-with-reason over whole-act refusal — but that is spec detail, not decided here |

---

## Module breakdown (for `/spec`) + reuse map

| # | Module | Owns | Reuses (never rebuilds) |
|---|---|---|---|
| 1 | `act-price-table` | Per-verb `*CostMilli` rows in `world.v{n}.json` `movement` + hold-allowance number (§Tunables) | `WorldTuningHub`/`MovementTuning` load path; `dowseBudgetMilli` units precedent |
| 2 | `claim-kind` (+ deposit/withdraw kinds) | New `WorldCommandKind`s, payload fields, admission arms, report entries | `WorldCommand`/`Admit`→`Reveal`→report discipline; `CommandId` idempotency shape |
| 3 | `budget-debit` | Debit site honoring the locked constraints below (debit-after-refill or refill-minus-spent) | `MovementPhase` leftover semantics; `Snapshot` refill frame |
| 4 | `hold-allowance` | Garrison allowance rule + number; ReachMap/admission/AI/fixture updates the allowance forces | `ReachMap.For`, `entity.held` gate, `FrontierRulesPolicy` order slot |

Reuse map: pricing units ← `LaneCost`; budget frame ← `BudgetFor`/`Snapshot`; command discipline ← `WorldCommand`; refusal sentences ← inventory-surfaces fold/bus (surface copy owned there, not here).

## Locked constraints for `/spec` (do not relitigate — strengthen-pass findings, code-evidenced)

1. **Debit-vs-refill order is undefined until the spec fixes it.** `Snapshot` overwrites
   `MovementRemaining = BudgetFor(stance)` after resolvers run — a priced act debited before the
   refill is wiped (free acts); after, it eats next turn's march. The spec MUST implement
   debit-after-refill or refill-minus-spent, or the locked resolutions are unimplementable.
2. **Hold allowance fans out beyond the budget field.** Allowance N>0 changes `ReachMap.For`
   emptiness, the `entity.held` admission drop, the AI's single-order slot (wasted `Move`s,
   yanked `Recover`-to-`Hold` healers), the `MovementPolicy.Hold=>0` comment, and the ash-waste
   hold fixture — the spec updates ALL of them or holds the allowance at spec time.
3. **Deposit is priced with no pipe.** Only claim converges with plan Task 4A.1's kind today —
   deposit/withdraw/load/unload need their own kinds (or Q3 re-scoped to claim-only) plus the
   wire fields the submit DTO lacks; an in-verb debit would read stale committed budget, not the
   in-turn leftover.
4. **Claim-vs-decay precedence + idempotency mapping are unnamed.** Claim-then-decay order per
   left-behind row (pay-for-nothing vs free retry) and the Data replay key ↔ `CommandId`
   mapping must be decided at spec — priced revisits make both load-bearing.

## Tunables — every number this introduces, and which file owns it

None decided — shaped so a future spec knows where each lands:

| Tunable | Home |
|---|---|
| Per-verb act costs (cache-claim, deposit, withdraw, load, unload, + any of clear/sustain/dowse if priced): `*CostMilli` in per-mille, same units as `LaneCost` and `dowseBudgetMilli` | `data/tuning/world.v{n}.json` `movement` section (sibling of `dowseBudgetMilli: 250`, `world.v5.json:83-85`); loaded through `WorldTuningHub` like `MovementTuning` (`WorldTuning.cs:19,127`); Core never reads the file (tunables-ssot §7.2) |
| Daily count caps, IF Fork C is ever evidenced (per-verb, per-legion, per-turn) | Same file, same section; structural-looking but balance-owned (grey-zone tiebreaker: tunable, per tunables-ssot §1) |
| Forced-refresh price, IF a rally/forced-march verb is ever proposed (AoW4 precedent) | Same file; named here only so nobody invents a second file for it |
| Hold-garrison act allowance (a number, tuned — "Small allowance" locked, number open) | Same file, same section |
| Refill amounts (`PointsPerTurn` 1000, scout 500, hold 0) | NOT retuned by this program — cited as the fixed frame costs are measured against; moving them is a separate balance change (T7: never land re-tune with the cost introduction) |

---

## What this deliberately does not decide

- Fork A vs B vs C (RESOLVED: A, extend `MovementRemaining` — Owner resolutions Q1).
- The debit seam (RESOLVED: command-kind — Owner resolutions Q4; immediacy loss accepted).
- Which verbs cost (RESOLVED: claim + deposit/withdraw; build stacks nothing — Owner
  resolutions Q3).
- Exact numbers for any cost — shapes only; values are balance passes over `world.v{n+1}`.
- Whether the engine bump (`RulesetVersion` 10 → 11 + golden re-bless) rides with the first cost or waits for the first PROVEN-behavioral change — engine-shape change says bump; the standing rule says a bump is earned by a moved golden (`decisions.md` RulesetVersion-history precedent). Named, not settled.
- Fog interaction of priced acts (does a claim attempt on unobserved ground cost before reachability is checked? the claim verb checks reachability first today — `:302-304` — cost-after-admit preserves that for free under seam 1, needs a rule under seams 2/3).
- Zomboss/AI use of the budget (AI commanders file through the same `WorldCommand` shape, so seam 1 covers them for free; seams 2/3 need an AI-spend policy).
- Surface copy for refusals (`entity.spent`-shaped sentences, meter states) — owned by the inventory-surfaces program's fold/bus, not here.
- Umbrella registration (whether `world-action-economy` becomes a third sub-program under `empire-development-map.md` or stays standalone) — spec-time paperwork.

---

## Open questions — owner decisions only (ALL ANSWERED — see Owner resolutions; kept as record)

1. ~~**Shape**~~ ANSWERED: extend `MovementRemaining` ("Extend budget").
2. ~~**Holding garrison**~~ ANSWERED: small allowance ("Small allowance") — number is spec-time content.
3. ~~**Which verbs cost**~~ ANSWERED: claim + deposit/withdraw ("Claim+deposit"); build stacks nothing.
4. ~~**Debit seam**~~ ANSWERED: command kind ("Command kind") — immediacy loss accepted.
5. ~~**Flat or scaled**~~ ANSWERED: flat per-act-per-legion ("Flat" half).
6. ~~**Spending order**~~ ANSWERED: march-then-act, no reservation ("march-free" half).

---

## The real question

**Shape, not feasibility — and the shape question is A-vs-B, not can-we-build-it.** The budget
exists, the pricing units exist, the tunable home exists, the refusal vocabulary pattern exists,
and the genre (HOMM3 first) prices acts from the movement pool as the default. Q1–Q6 are all
answered (see Owner resolutions) — what `/spec` inherits is the module cut above plus the four
locked constraints: debit order, hold fan-out, deposit pipe, claim-vs-decay precedence. Answer
those four in the capability map
(`docs/architecture/world-action-economy-map.md`), module specs, and the plan/task pair
(`tasks/world-action-economy-plan.md`, `tasks/world-action-economy-todo.md`) — reusing the
budget, the refill, the command discipline, and the tuning file without re-deciding any of them.

---

## Hand-off

- Stop at this ideal. **No specs, plans, or code from this phase.**
- Next step after owner answers §Open questions (Q1+Q2 first): `/spec` → capability map +
  per-module specs as above.
- Cross-refs (read, not touched): `docs/architecture/empire-inventory-surfaces-ideal.md` (§10
  Q6 pickup-cost + §8 deposit/withdraw cost row — this idea is its mechanics answer);
  `docs/architecture/empire-development-map.md` (umbrella — registration at spec time);
  `docs/architecture/world-map-program.md` (engine foundation — unchanged by this idea);
  `docs/architecture/decisions.md` (phase-order + RulesetVersion rows — bump consequence named
  in §What this deliberately does not decide).
- Queue: none (no surface work proposed).

## DESIGN-GATE §5 checklist (this document)

```
[x] Subsystems identified: world-map turn engine + movement budget (Core), cargo/cache Data
    verbs, world tuning. No Status/ActorHub/Combat/Injector subsystem touched.
[x] Session boundary: worktree empire-development-20260915-b7e2 only; main checkout untouched.
    (One new file under docs/architecture/ — the skill-mandated ideal path.)
[x] Read every doc in the §1 rows for those subsystems, this session — with stated gaps:
    Product vision + World map (program) + Tunables read; Economy SSOT / power-scale §11 /
    world-map-runtime specs NOT re-opened (named above as honest gaps).
[x] Checked decisions.md for a lock covering this: phase-order + RulesetVersion-history rows
    (bump-by-moved-golden rule reused); no "action economy" lock exists — greenfield confirmed.
[x] Every factual claim cites file:line (see §What already exists tables).
[x] Verified claims against CODE, not comments (all Core/Data/tuning citations opened in-session
    in the worktree; audit's TurnEngine line corrected 372-376 → 405-423 against live code).
[x] Read the surrounding section of every rule quoted (loop/stance/stamina rules cited with
    their the-loops/the-game context, not as slogans).
[x] Tested (not assumed) constraints: world-AP NOT-FOUND proven by grep over Core/World; zero
    cost params proven by reading the verb bodies/signatures; no golden/test movement claimed —
    idea phase runs no suite (bump named as consequence, not as measured).
[x] Nothing contradicts a §2 invariant (SQL stays in FusionRpg.Data; no magnitude cap as
    progression ceiling — costs are spends with named refusals; no f(level); no second ownership
    root; SOLID: no parallel price engine, no parallel admit path proposed as decided).
[x] No assertion pins a derived-population count, item total, generated name/description text,
    or per-cycle outcome. (Counts named: 1900/1300-2000/100/141/300/200/40/48/6 MP figures are
    cited prior-art readings with sources, not guardrails; 1000/500/0/250 are live code values
    cited as the frame, not proposed constants.)
[x] No event-refreshed cache introduced. (Claim-log idempotency cited as built behavior, not
    proposed.)
[x] No acceptance criterion fixes an ordering. (N/A — idea phase; ordering flagged as an open
    design point, Q6, with both orders named.)
[x] No actor combat/derived magnitude produced or consumed — no Hub-adjacent subsystem touched.
[x] No SOLID-violating parallel path decided: Fork B (the parallel pool) is presented with its
    overturn price attached, not smuggled; rejections table names the forks not taken.
```

## Owner resolutions (2026-09-15 — owner's answers, quoted verbatim)

- Q1 shape: "Extend budget".
- Q2 hold garrison: "Small allowance".
- Q3 verbs: "Claim+deposit".
- Q4 seam: "Command kind".
- Q5/Q6: "Flat, march-free".

Author notes (not owner words): Q1 keeps the no-second-pool boundary; Q3's picked option reads
"Claim+deposit" with description "Inventory verbs cost; build stays priced" — DESCRIPTION GOVERNS:
all five inventory verbs priced (claim/deposit/withdraw/load/unload, transfer 0), build stacks
nothing (locked 2026-09-15 strengthen pass; the label abbreviates the description it came with).
Q4 accepts immediacy loss and converges with plan Task 4A.1's `claim-cache` kind; Q5 is flat
per-act-per-legion; Q6 keeps marching unchanged with no Reveal reservation.
