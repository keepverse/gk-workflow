# Empire progression — the ideal

**Status:** idea phase, 2026-09-17. **Not a spec. No build authorized.**
**Status: graduated to map 2026-09-18** — [empire-progression-map.md](empire-progression-map.md) (module specs in [empire-progression/](empire-progression/)).

> **Superseded in part, 2026-09-18 — the map and [spec-rulings-2026-09-18.md](spec-rulings-2026-09-18.md)
> win where this reasoning trail disagrees.** Read these before quoting this document:
> - **R-Q3's free respec counter (`respecFreeCount`, default 25) is superseded by ruling R18.** Free
>   respecs are **earned**, one grant per **empire level** (ruling R19, `empire-level`), they pay only the
>   **empire (species) respec**, and the player chooses each time to spend one or pay souls
>   (`respec-free-counter`). A unique creature, **commander included**, always pays to respec
>   (`specimen-respec-price`). `respecFreeCount` is never published.
> - **Open question 2 (zombie species XP) is answered by ruling R1**: Zomboss's empire, on both XP paths,
>   keyed per save by ruling R3 (`save-identity`); Zomboss stops being a global player row.
> - **Q7a (does a high threat rung sharpen the build?) is answered by ruling R6**: yes; the signal ships at
>   weight 0 and a tuning publish turns it on (`per-species-lean`).
> - **Whose commander allocation lifts the side when a creature leads** (the map's question 2) **is answered
>   by ruling R4**: the empire's commander allocation still applies side-wide; the creature adds only its aura.
> - The `creature-system-map.md` Axis 2 amendment this document says is owed **is done**
>   (`creature-system-map.md:69-141`).
>
> Superseded passages below carry an inline *Superseded* note and are otherwise left as written.

> **Updated 2026-09-17.** Adopted the **commander identity defect** as a task (SOLID). **10 owner rulings** landed: auto-assign default + free respec counter, one-sided lead cap, per-species lean, multiplicative scorer, and R-C1–R-C6 — a commander is a `UniqueActor` carrying a role, fighting everywhere except the lawn run. **Q1 closed** by `species-progression` R-S1.

This is the **assignment layer**: who decides where a progression point goes, for a human and for an AI
empire. It is deliberately *not* a second progression system.
[`species-progression-ideal.md`](species-progression-ideal.md) owns **what a level grants**; this
document owns **who fills the shares**. If those two ever disagree, the other one wins on grants and
this one wins on assignment — and a reader who needs both should read both.

---

## Step 0 — the principles, in my own words, before anything else

Restated inline rather than linked, because a downstream session reads this page and not its links.

1. **Every RPG feature lives in the RPG layer, and is never built by changing what PvZ is.** Nothing
   here touches a `Plant` field. Aptitude shares, build presets and AI weights are RPG-layer concepts
   PvZ has never heard of. "Can the lawn express this" is the wrong question and has sent a session down
   a wrong path before.
2. **The PvZ write surface constrains persistent vanilla stat changes only.** It says nothing about what
   a progression feature may do.
3. **Two async systems; deltas, never absolutes; record-then-drain.** Delay is the designed degradation
   mode, not a problem to engineer around.
4. **One power ladder.** Contests read `Θ` (linear, difference-based); magnitudes read `P(Θ)`.
   `ssot-power-scale.md` §10 is a **closed inventory** — a power-shaped number not in that table has no
   permission to exist. Writing a fresh `f(level)` for "species level" is the exact defect that let three
   incompatible curves ship at once.
5. **The balance surface is data.** Every weight, favour multiplier and preset number belongs in
   `gk-core/data/tuning/<domain>.v{n}.json`. A weight written as a `const` is a tax paid at every rebalance, and
   it makes a tuning change indistinguishable from a code regression when a golden moves.
6. **No hard progression ceilings.** A cap on a magnitude is a soft, configurable cap; an absolute bound
   is derived and **throws**, never clamps silently. Structural limits and bounded ratios are exempt and
   must say so in a comment.
7. **One ActorHub compose.** Anything that changes an actor's numbers contributes `DerivedModifier`s
   into the one fold, or consumes Hub output. Never a private fold, never a second composer.
8. **Gameless-first is a capability.** Whatever this becomes must stay playable with Fusion closed once
   unlocked.

And the constraint that binds this feature hardest, straight from the product vision
([`guide/the-game.md`](../guide/the-game.md) "What you are not"):

> **"You are not a class. Character building is free — points go where you want."**

So auto-assign is an **assist with a default**, never a lock, never a class, and never the only path.
A design that makes the recommended build mandatory has failed this line regardless of how good the
recommendation is.

---

## Which loop this extends

Named explicitly, because `the-loops.md` requires it and forbids inventing a parallel pitch:

- **Spine A — Level up and power.** *"Aptitude points go where you want — you have no class."* This
  feature is the assist over that freedom, and the AI's equivalent of it.
- **Spine C — Item collection and progression**, whose Vision row already names this by name:
  **"Build presets"** ([`the-loops.md:164`](../guide/the-loops.md)), hanging on *"Item collection ·
  level up and power"*.

It also touches **Places 3 and 5** (farm/hunt/defend, world stage) on the AI side, because an AI empire
that levels species is an empire that develops. It introduces **no new loop**, **no new currency**, **no
player class**, and **no stamina gate**.

---

## What this is

Three questions, one system:

1. **A human with points to spend** wants a sensible default without an hour of research, and the
   freedom to ignore it.
2. **A general creature** — an engine-spawned lawn plant or zombie, troop-stack shaped, no persistent
   instance — has no one to click for it. Its build has to come from its species and its empire.
3. **An AI empire** — Zomboss — needs the same, at the scale of a whole species roster, without a model
   call at runtime.

These are the same problem viewed from three distances, which is why it is one module and not three.
The vocabulary already says so: `creature-system-map.md:51` gives general creatures *"Empire-wide,
per-player, per-species progression fallback (primary stats, the general passive tree)"* and unique
creatures *"own specimen progression and `UniqueCreature` allocation"* — one system, two scopes.

---

## What already exists

Sorted into **built** / **wiring gap** / **real gap**, with `file:line`. A default-off toggle, a null
delegate, a debug-only entry point or a missing argument at every call site is a **wiring gap** — never
an architectural limit.

### Built

| What | Where | What proves it |
|---|---|---|
| Six auto-assign rules, closed set | `AptitudeAutoAssign.cs:6-11` (`even`, `posture-force/finesse/bastion`, `active-preset`, `species-favour`) | 9 tests, `AptitudeAutoAssignTests.cs`; every refusal named, none silent |
| Correct integer per-mille math | `AptitudePresetMaterialize.cs:101` — `checked { raw = budget * row.TargetPermille / 1000L; }` | `long` throughout, widen before multiply, ÷1000 last; overflow test at `AptitudeAutoAssignTests.cs:104` |
| Species favour **content** | `gk-data/packs/fusion/data/generated/creatures/_species-build-plan.json`, 120,183 bytes | **904 species, every row sums to exactly 1000‰**, measured; genuinely differentiated (`acientsunnut` → Bulwark 502, `armedgargantuar` → Might 596) |
| The generator, LLM-out-of-the-loop | `gk-forge/tools/CreatureBuildPlanGen/Program.cs`; math in `SpeciesBuildPlanner.cs:13` — *"no file IO, no `RpgStore`, no model call ever"* | `--check` byte-compare in CI (`gk-core/.github/workflows/ci.yml:129`); 10 tests incl. byte-identical reruns and input-order independence |
| The projector that consumes it | `SpeciesAllocation.Baseline(planSharePermille, speciesLevel, tuning)` `:59`; budget `PointBudget.CreatureTypeSourceFromLevel = max(0, level-1)` `:40` | Live callers `RpgStore.Aptitudes.cs:249,271`; reaches ActorHub via `SpeciesAllocationSource` |
| Preset storage + full API | 3 tables `RpgStore.AptitudePresets.cs:58,69,80`; 9 routes `AptitudePresetEndpoints.cs:22-172` | 7 endpoint tests incl. transactional activate with rollback on insufficient souls |
| An offline weight corpus at species scale | `gk-data/packs/fusion/data/seed/actions/type-weights.json` — **1131 entries (904 species + 227 families), 100% `basis: "derived"`** | Every `categoryMilli` sums to exactly 1000; largest-remainder apportionment in `distribution_planner/derive.py` |
| A live six-axis weighted sum for AI | `ValueMap.cs:98-108` — yield/strategic/defensibility/cost/risk/curiosity, per-mille, weights from `ai.v2.json` | Zomboss runs `frontier-rules` in shipped worlds (`WorldTemplateCatalog.cs:83`) |
| A nine-rule AI ladder, fully deterministic | `FrontierRulesPolicy.cs:62-70` | It never consumes its seed at all — a pure function of fogged belief |
| Additive combat AI scoring | `Actions/Ai/CandidateScorer.cs:97-110` (moved from SiegeAi.cs by combat-ai CAI1.1), XCOM's shipped weights now in `combat-ai.v1.json` (moved from `siege.v1.json` by CAI1.8) | `checked` throughout; tier-first with signed aggression |
| A deterministic weight family in seedsmith | type-weights, innate-picker (`gk-forge/tools/seedsmith/seedsmith/adapters/creatures/anchor/derive.py:249`, *"Model calls: none — permanently, not provisionally"*), usage-direction, threat-band, distribution-planner, numerics, tree quota | An explicit numeric-smuggling audit blocks magnitudes from model answers (`gk-forge/tools/seedsmith/seedsmith/adapters/creatures/anchor/schema.py`) |
| The LLM/deterministic boundary, already written down | `gk-forge/tools/seedsmith/seedsmith/adapters/creatures/anchor/schema.py:93` — *"computed by code (never let the model author posture/pure/basis — boundaries)"* | `aptitudePrimary`/`aptitudeSecondary` are LLM-classified and 3-way voted; `posture` is derived |

### Wiring gap

<!-- citations-historical: CommanderId.cs was deleted (commander-identity SE4.2/SE4.3); the faction is EmpireId, the unit is CommanderRef, and every display name/scope key/empire/default comes from data through ICommanderDirectory -->


- **W1 — `AptitudeAutoAssign` has zero production callers.** `AptitudeAutoAssign.cs:110` `Fill(...)` is
  reachable only from tests. The FE keeps its own TypeScript mirror; the C# is never consumed by the
  server.
- **W2 — nothing emits `aptitude.autoAssign`.** Two handlers subscribe (`AptitudesTab.tsx:261`,
  `SpeciesBuildPanel.tsx:116`); no button, no rule picker, no producer anywhere in `web/`. The handler's
  `const rule = (p as { rule?: string })?.rule ?? "even";` has no caller that can set `rule`.
- **W3 — `species-favour` refuses 100% of real species.** `AptitudeAutoAssign.cs:89-90` returns
  `autoAssign.favour.incomplete` when any of the 12 aptitudes is missing, and **every one of the 904
  plan rows carries exactly 5** (`species-build.v1.json` sets `maxAptitudesPerSpecies: 5` deliberately).
  The spec does **not** mandate this: `spec-aptitude-auto-assign.md:62` refuses only when favour is
  `{}` **or the species is missing**, and its acceptance line reads *"Empty favour refused"*. The
  sibling seed path zero-fills correctly (`evenPermille.ts:13-18`). This is the implementation being
  stricter than its own spec. **Every auto-assign test builds a synthetic 12-key map, so the real 5-key
  shape is never exercised — the coverage gap is the defect's cover.**
- **W4 — preset `kind = "systemCopy"` is validated and never produced.** `RpgStore.AptitudePresets.cs:53`
  and `:193` are the only two references repo-wide. This is the natural carrier for a
  system-authored default build and it is sitting empty.
- **W5 — the utility-AI scorer is inert.** `Consideration.cs:23`: *"Nothing calls this yet.
  `frontier-rules` is a rule list because scoring wants an economy to score against and there is not one
  until `sector-development`."* Six response-curve shapes exist at `ResponseCurves.cs:47-53`;
  nothing in production evaluates them.
- **W6 — `INeedVector` is a neutral stub.** `UniformNeeds` returns **1000 for every slot kind and every
  element** (`INeedVector.cs:31-41`), and `ValueMap.For` defaults to it (`:67`). So "a fire vein is
  worth more to an empire short of fire" never happens.
- **W7 — `"zomboss:{playerId}"` allocation keys exist with zero readers or writers**
  (`CommanderId.cs:71`); every non-test caller passes `CommanderId.Dave`. District assault hardcodes the
  AI commander to `Empty` (`RpgStore.WorldTurns.cs:573-576`).
- **W8 — `ai.aggression` is wired end to end with no content.** `DerivedStatChannels.cs:547`:
  *"Defaults to 0 (neutral) for every actor today — no content targets this channel yet."*
- **W9 — the siege AI scorer is opt-in with one opt-in.** `BattleRunState.cs:621` builds it only when
  `aiTuning != null`; the sole production site is `DistrictAssaultResolver.cs:185`. Every expedition,
  delve and lawn battle gets `StubIntentSource`, *"deliberately stupid"* (`StubIntentSource.cs:7-9`).
- **W10 — tree respec is fully built with no caller** (`RpgStore.PassiveTree.cs:292`); the only tree
  auto-allocation is debug-only (`DerivedAuditActor.cs:198-204`); the FE tree "Plan" round-trips through
  a **URL param** and is never saved (`passivesPlan.ts:22`, `PassivesTab.tsx:104`).

### Real gap

- **R1 — the AI empire owns no progression at all.** Measured against the live DB
  (`dist/FusionRpg.Server/data/rpg-hot.sqlite`, read-only): the `Zomboss` player row has **0
  `rpg_actor_progression` rows of any kind**, while `normalzombie` sits at **level 62**, `conezombie` 20
  and `flagzombie` 7 — all banked on the **human** player. The code says so too, in its own
  words rather than the paraphrase this line carried until 2026-09-18 (an audit found the quoted
  sentence appears nowhere in the tree — it was my summary set in quotation marks, which is worse than
  no citation because it cannot be grepped): `RpgStore.Aptitudes.cs:229-231` — *"the species LEVEL row
  is per-player, and no Zomboss species level exists anywhere, so a non-Dave ask resolves Empty rather
  than the human player's progression."* Both `EffectiveSpeciesAllocationUnlocked` and `SpeciesBaselineAllocation` return
  `Empty` for `empire != Dave`. So the ruling that *a lawn zombie reads Zomboss's allocation* resolves
  to nothing, permanently, and the human accrues progression for species they never field.
  **This is the same empire-attribution family as `SR-18`** (`creditEmpire` resolved and never spent).
- **R2 — species level cannot change what a species composes.** `AptitudeResolver` reads
  `allocation.Share(edge.Source)` — a **share**, not a point count — and magnitude comes from
  `pTheta = ladder.Value(theta)` where theta is the **member's** level. Ten points and two hundred points
  in one share are both share 1.0. So a level-4 species composes **exactly** as a level-1 one
  (`actor-layer-compose-ideal.md` **R3**; the same defect the `solid-remediation` audit carries as
  **S7**). Until a species level reaches **theta or a channel**, every build plan in this document is
  cosmetic. *This is the one blocker that makes the rest moot, and it is the question
  `species-progression-ideal.md` owns.*
- **R3 — the passive-tree favour corpus is a 1-of-904 pilot.** `gk-data/packs/fusion/data/seed/passive-tree/species/` holds
  exactly one file, `AshThreePeater.json`, whose `mechanicalFavour` is
  `{"aptitude": "Composure", "element": "earth", "status": "charm_pulse"}` — a compact identity triple,
  exactly the right shape, at 0.1% coverage. Aptitude favour is 904/904; tree favour is 1/904.
- **R4 — no "closed" vs "half-open" preset notion exists**, verified across `docs/`, `src/`, `tools/`,
  `tests/`, `web/`. `halfopen`/`half_open`/`HalfOpen` return **zero matches repo-wide**. Every "closed"
  hit is an unrelated sense (closed vocabulary, closed event bus, closed-form algorithm, math interval).
  The only preset completeness vocabulary is `kind ∈ {player, systemCopy}`.
- **R5 — seedsmith emits no decision weights.** It has a large deterministic weight family, but greps
  for `decision tree`, `behaviour tree`, `aiProfile`, `targetPriority`, `utility ai` and `aggression`
  return **zero hits** in the package. Every existing weight is *content* distribution, never *behaviour*.
- **R6 — no unified synergy loadout.** `guide/mechanisms/build-presets.md:3` — `**Status:** Vision`;
  `:66` — *"Can I save presets now? No — Vision."* Nothing combines patron + relics + aptitudes + field
  list. (That page is also stale: it tells the player preset UI is Vision while the aptitude preset
  console ships end to end.)
- **R7 — enemy counter-development does not exist.** The nearest thing is
  `ZombossPatternSelector`'s counter-bias, a single-encounter posture counter, not a developing war.

### Measured: build favour is converged on identity, while its own gate reads green

The owner's judgement — *"current build favor is not good"* — is measurable against the committed
corpus. The important part of the measurement is that **the corpus passes every check the generator
makes of it, and is still converged**, because the thing that converged is not the thing the generator
gates. Counted directly from `gk-data/packs/fusion/data/generated/creatures/_species-build-plan.json` (904 rows):

**Which aptitude leads a species:**

| Top-share aptitude | Species | Share of corpus |
|---|---|---|
| Onslaught | **378** | **41.8%** |
| Bulwark | 141 | 15.6% |
| Retribution | 114 | 12.6% |
| Focus | 90 | 10.0% |
| Fortitude | 55 | 6.1% |
| Precision | 53 | 5.9% |
| Pierce | 29 | 3.2% |
| Agility | 23 | 2.5% |
| Might · Vigor | 7 · 7 | 0.8% each |
| Composure | 5 | 0.6% |
| **Ferocity** | **2** | **0.2%** |

One aptitude leads **42%** of all species; the top three lead **70%**; the bottom four lead **2.4%
between them**, with Ferocity leading **two species in the entire game**.

**The shape is even more converged than the lead:** across 904 species there are only **21 distinct
share *shapes*** (the sorted value profile, ignoring which aptitude holds which slot). A single shape,
`(350, 163, 163, 162, 162)`, covers **292 species — 32% of the corpus**; the top two cover **45%**.

**And the mechanism is exact, not approximate — read `SpeciesBuildPlanner.cs` before designing a fix.**
The lean is a pure function of *which aptitude is primary*, never of the species:

```csharp
// Phase 1 — one lean per PRIMARY, from that primary's own corpus-wide crowding. Every species
// sharing a primary shares its lean by construction (spec §"Phase 1").
crowdingPermille = count * 1000 / speciesCount;
contribution     = tuning.CrowdingFactor * crowdingPermille / 1000;   // crowdingFactor 633
lean = Math.Clamp(tuning.LeanMaxPermille - contribution, LeanMin, LeanMax);  // [350, 600]
```

So the whole corpus carries **exactly twelve lean values**, one per aptitude — measured, every species
leading an aptitude has that aptitude's single lean and no other:

| Lead aptitude | Species | Lean | Corpus share of points |
|---|---|---|---|
| Onslaught | 378 | **350‰** | 150‰ |
| Bulwark | 141 | 502‰ | 83‰ |
| Retribution | 114 | 521‰ | 76‰ |
| Focus | 90 | 538‰ | 77‰ |
| Fortitude | 55 | 563‰ | 77‰ |
| Precision | 53 | 564‰ | 76‰ |
| Pierce | 29 | 580‰ | 76‰ |
| Agility | 23 | 585‰ | 76‰ |
| Might · Vigor | 7 · 7 | 596‰ | 76‰ |
| Composure | 5 | 597‰ | 76‰ |
| Ferocity | 2 | **599‰** | 76‰ |

Two things fall straight out of that table, and they are the actual finding of this section.

**First: point parity is already solved, and solved well.** Every aptitude's corpus share sits between
76‰ and 150‰, comfortably inside the planner's own `[parityFloorPermille 50, parityCeilingPermille 200]`
band — and Phase 3 *refuses to emit a plan at all* if it ever leaves that band
(`SpeciesBuildRefusal`). **Do not design a fix that redistributes points.** That job is done, it is
gated, and breaking the gate is how this gets worse.

**Second: the crowding response is backwards for identity, by construction.** Because a crowded primary
*lowers* its own lean, the 378 species sharing the most common archetype get the corpus' **blandest**
build (350‰, clamped at the floor), while Ferocity's two species get its sharpest (599‰). The more
typical a creature is, the less its build says about it. That is the exact opposite of what makes a
roster feel varied, and it is not a bug in the planner — it is the planner correctly serving *point
parity*, which is the goal it was actually given (`spec-redistribution-plan.md`).

> ⚠️ **The obvious diversity metric would pass this corpus forever.** Distinct *exact* share vectors
> reads **769 of 904 — 85% unique** — because largest-remainder filler differs by ±1‰ between species.
> A CI check written against vector-uniqueness would report a healthy corpus while one aptitude leads
> 42% of it. **Any diversity assertion this program ships must measure the shape and the lead
> distribution, never vector distinctness.** This is the single most important thing measured on this
> page.

### The species power ladder already exists, spreads well, and is half-covered

`threat-band` (`gk-forge/tools/seedsmith/seedsmith/adapters/creatures/power/bands.py`) turns a power score into
**ten threat-noun rungs**, each carrying a `thetaOffset` — `nuisance 0`, `pest 4`, `marauder 9`,
`raider 13`, `warden 18`, `scourge 22`, `tyrant 27`, `harbinger 31`, `cataclysm 36`, `calamity 40`
(`gk-core/data/tuning/creature-threat.v1.json`).

**Its own design note is the lesson this program most needs:**

> *"the ladder is a table because the captured stat distribution is lumpy, not smooth: **a fitted curve
> puts most of the roster in two rungs**."*

They already met this exact convergence problem on the power axis and solved it by abandoning the curve
for a table. The build-favour axis has not had that correction yet — it is still a formula
(`lean band + equal filler`) producing 21 shapes.

It also already ships a diversity guard worth copying by name: `UnoccupiedRung` —
*"A histogram request found a rung with zero occupants — reported, not hidden."*

**Measured against the live corpus (904 files in `gk-data/packs/fusion/data/generated/creatures/`, 2026-09-17), the rungs
occupy — with one clump.** Every rung has occupants, so `UnoccupiedRung` has nothing to report:

| `theta` | 0 | 4 | 9 | 13 | 18 | 22 | 27 | 31 | 36 | 40 |
|---|---|---|---|---|---|---|---|---|---|---|
| species | **224** | 60 | 74 | 81 | 87 | 70 | **101** | 77 | 55 | 75 |

Nine rungs sit in a 55–101 band, which is the healthy shape the table was chosen to produce. The
exception is `theta 0` (`nuisance`) at **224 — 24.8% of the roster**, a quarter of all species pinned
to the bottom rung. That is a real clump and worth naming, but it is a *different* problem from a
fitted curve collapsing the roster into two rungs, and it is far milder.

**`actor-layer-compose-ideal.md` R4 is now half stale — corrected here, because a downstream session
would otherwise design against a problem that has partly been fixed.** Re-measured directly from the
same corpus:

| R4 as written | Measured 2026-09-17 |
|---|---|
| *"730 share `theta 13`"* | **Stale.** `theta 13` holds **81**; ten rungs are occupied, largest is `theta 0` at 224 |
| *"450 share `resource.max.hp 2712`"* | **Stale.** `2712` holds **44**; **88 distinct** hp values, most common is 480 at 159 |
| *"only 457 (50%) carry `combat.power.omni`"* | **Still exactly true — 457 of 904** |
| *"Peashooter and GatlingPea bake identically in both"* | **Still true** — byte-identical `magnitudes` and `pTheta 452`, differing only in `attackIntervalMs` and `elementSecondary` |

R4's **thesis** survives, weakened: the bake is no longer near-constant (**189 distinct magnitude
vectors** across 904 species, largest shared by 70) but it still does not separate two plants that
should obviously differ. What has changed is the scale of the defect, and that matters here — a pass
designed to break up "730 identical species" is a different pass from one designed to break up a
224-species bottom rung.

So the half-built part of the species power ladder is not the rungs; it is that **447 of 904 species
(49%) carry no `combat.power.omni` magnitude at all** — the half a build-favour pass would need to
read if favour is ever to follow power.

### The item tier ladder is the structural precedent to copy

`IlvlTierLadder.cs` is a small, closed, already-shipped answer to "how does a ladder stay bounded without
becoming a ceiling", and three of its properties transfer directly:

1. **Five tiers, `MinIlvlByTier = 1 / 1 / 8 / 18 / 32`, and growth past the top tier is carried by
   `contentScale` — not by adding a sixth tier.** A bounded rung count that does not become a
   progression ceiling, because the magnitude keeps climbing on the one power ladder. This is how a
   species build ladder can be small and still endless.
2. **A collapsing envelope that never excludes the bottom** (`Envelope`, the I12 ruled-window rule,
   explicitly *not* I8's rejected sliding window which dropped t1 out at ilvl 40+). As a species
   advances, the window of legal build shapes may narrow toward its band — but the base never becomes
   illegal.
3. **Never reject; narrow and record.** `EnvelopeNarrowing.Apply` — *"if the narrowed envelope leaves
   fewer drawable groups than the roll count asks for, narrow the COUNT and record it — never reject a
   legal drop from legal content."* The build-favour equivalent: if a species' narrowed envelope cannot
   supply `maxAptitudesPerSpecies` distinct leans, emit fewer and record why, never fail the species.

### The pattern worth naming: three neutral stubs

`action-role-lean.v1.json` ships **165 of 165 multipliers flat at 1000**, and its own `_meta` says
*"These weights are untuned."* `INeedVector` returns 1000 for everything. `ai.aggression` defaults to 0
for every actor. Three independent systems have a complete, correct, tested *mechanism* whose
*differentiating content* is a constant. That is this repo's characteristic failure mode for this class
of feature, and it is the thing this program most needs to avoid becoming a fourth instance of.

---

## Prior art, with numbers

### Nobody ships a runtime optimizer

Every shipped auto-allocator is one of exactly three cheap rules:

| Shape | Examples | The actual rule |
|---|---|---|
| **Fixed per-class table** | Diablo III | Attributes removed from player control; per-class bias — lv60 base Str **187 Barbarian / 67 others**, Vitality **128 all**, ~1–2 points per attribute per level |
| **Ordered priority list, take first legal** | Neverwinter Nights "Recommended"; Mass Effect auto-spend (**80 points over levels 1–60**); FFXII gambits (*"the first gambit that has a met, actionable condition will be executed"*) | A list, walked top-down |
| **Hand-authored preset blob** | WoW "Starter Build" (*"a preset talent build … suitable for most content"*, revised per patch); Pathfinder auto-level; DA:O tactics presets (slots **2 at lv1, +1 at 3, 6, 10, 15, 20, 25, 30**) | A designer wrote it |

Only FFXIV computes anything — *"automatically select the gear with the **highest attributes**"* — and
only because "best per slot" is trivially separable. **Path of Exile ships no auto-allocation at all**
for **1,325** passive nodes and **~122** points, offloading entirely to community planners.

⚠️ **A common premise is false and worth killing here:** *Diablo II never shipped stat auto-assign.*
1.13/D2R added an unspent-point **reminder** and a limited respec token. Auto-assign exists only as a
third-party mod.

**Preset brittleness is the documented cost.** Pathfinder's auto-level is all-or-nothing — *"if you go
and manually change anything, the auto will no longer work"*. NWN's Recommended *"never works if you
intend to multi-class"*. **A preset that cannot re-plan around a deviation is a cliff, not a gradient** —
which matters enormously for a game whose vision sentence is "points go where you want".

### Utility AI: the canonical shapes

Response curves, quoted from Mark & Dill, GDC 2010:

```
Linear:       Anxiety = (100 − distance) / 100
Exponential:  Anxiety = (100 − distance^k) / (100^k)        [k = 2, 3, 4, 6]
Logistic:     Anxiety = 1 / (1 + (2.718 × 0.45)^(distance+40))
```

Selection: *"Highest scoring / Weighted random from all choices / Weighted random from top n choices."*

Two combination schools, and the repo should pick one knowingly:

- **Additive** (Mark & Dill 2010; Game AI Pro Ch. 9): `EU = Σ(D_i · P_i)`, with veto or final-multiplier
  gates. This is what `ValueMap.cs:98-108` and `Actions/Ai/CandidateScorer.cs:97-110` (moved from
  SiegeAi.cs by combat-ai CAI1.1) already do.
- **Multiplicative** (Guild Wars 2 IAUS, Game AI Pro 3 Ch. 13): *"These scores are multiplied together"*,
  with **zero as a hard veto and an early-out**, considerations **ordered cheapest-first** — *"a large
  part of what made the Heart of Thorns AI sufficiently performant."*

Multiplication has a known defect — more considerations drive scores toward zero, so richer decisions
systematically lose. Two published fixes: Dave Mark's compensation factor
`final = score + ((1 − score) × (1 − 1/n) × score)`, or Rez Graham's **geometric mean** `(Π c_i)^(1/n)`,
which removes the bias exactly.

**Real shipped weight magnitudes** (Zoo Tycoon 2, via Dill's dual-utility chapter) — the most concrete
"what do weights look like" datapoint found: ordinary needs **rank 0**; situational lock-in **~5**;
scripted sequence **98–102**; death **1,000,000**. Ranks are a coarse priority class, not a fine dial.

**Cardinality reality check:** Civilization II shipped **three** aggression levels total, a third of all
leaders sharing the lowest. (The "Nuclear Gandhi underflow" story is **false** — Sid Meier debunks it in
his 2020 memoir. The real lesson is that a myth about a weight bug outlived every actual weight in the
game.)

**The tuning surface explodes, and that is the thing to design against.** Halo 2:
*"three parameters, times 115 or so behaviors, times 30 or so character types … about **10,350 different
numbers we need to maintain**"* — solved by hierarchical character inheritance where variants override
only what differs. Zubek names the same wall: *"some of the tunable parameters have global effect, and
are therefore very difficult to tune after the game has grown past a certain size"*, fixed by
**partitioned tuning with global defaults plus per-partition overrides**.

**Three independent shipped-title authors converge on one conclusion about curve authoring:** Zubek —
analytic functions *"are not easy for designers to tweak or reason about"*, use piecewise-linear point
pairs from a spreadsheet; Lewis — GW2 shipped *"a small palette of preset curves"* with arbitrary curves
behind an advanced mode; Merrill — make the formulas *"reloadable data"*.

### Precomputed policy: what baking actually buys, and what it costs

| System | Offline | Ships | Runtime |
|---|---|---|---|
| Libratus | ~15M core-hours | bucketed blueprint (turn 55M hands → 2.5M buckets) | 1,400 cores |
| Pluribus | 12,400 core-hours / 8 days | blueprint for **round 1 only** | 28 cores |
| Modicum | **700** core-hours | **5 GB** | 4 cores — and it **beat** the 2M-core-hour table-only bot |

**The single most transferable finding:** Libratus *"never plays according to the abstraction solution
in the final two rounds. Rather, it uses the abstract blueprint strategy in those rounds only to
**estimate what reward a player should expect**."* The baked artifact is a **value estimate feeding a
cheap runtime decision**, never the decision itself. Libratus → Pluribus shrank the table **~1,200×**
while getting *better*.

Storage shape matters more than coverage: Syzygy stores **the decision, not the analysis** and beats
Nalimov's distance-to-mate ~8× on size for the same 6-piece coverage (150 GB vs ~1.2 TB).

**Documented failure modes of baked tables**, all sourced:

1. **Meta drift is quantified.** OpenAI Five needed *"over twenty surgeries … over the ten-month
   lifetime"* to track Dota patches; patch-tracking cost **~5×** the artifact's own regeneration cost.
   Riot patches every two weeks — any baked comp table has a **~14-day half-life by construction**.
2. **A frozen policy loses to adapting opponents.** *"The bots are locked. They are not learning, but we
   humans are."* OpenAI Five Arena: 99.4% win rate, but **42 losses across 29 teams** — the holes were
   findable and reproducible.
3. **Off-distribution exploitation, the strongest case.** Adversarial policies beat superhuman KataGo
   **>97%**, and more runtime search mitigates but does not fix it (95.7% @ 4,096 visits → 72% @ 10⁷).
   A human amateur then learned the attack and beat KataGo **14 of 15** unaided.
4. **Bigger table ≠ better play.** Refining an abstraction can make full-game strategy *worse*
   (Waugh et al., AAMAS 2009). Claudico was beaten by humans betting **between** its known bet sizes.
5. **The coupling is invisible until it breaks.** GTO Wizard's library is solved for one specific rake
   (*"5% with a cap of 0.6BB"*) — change the assumption and the whole library is silently wrong.

**Commercial games do ship static build tables**, and it is unglamorous: League's recommended items are
static per-champion `RecommendedDto` blocks in Data Dragon, versioned with the patch; Valve's Dota bots
use per-hero Lua build files. The counterexample is deliberate — Hearthstone Battlegrounds runs
**~10,000 Monte Carlo combats at runtime** because board state is combinatorially open.

### Convergence detection: the actual deliverable

If you ship *N* role templates they inherit whatever convergence the underlying math has. What shipped
studios build is the **detector**, not the "best build":

- **Riot's Champion Balance Framework** — OP at **54.5% WR** for average players (sliding to 52.5% at 5×
  average ban rate), **45% ban rate** at Elite, **90% presence on a patch** at Pro; UP at **49% WR** or
  **5% presence**. Balanced if balanced for *any* audience.
- **Blizzard D3** — benchmark GR130 solo at 5,000 Paragon; **±1–2 GR fine, ±3–4 warning, ±5+ warrants
  significant change**. Measured 2.6.7 spread: Crusader 138 → Necromancer 123.

### LLM at build time, not runtime — the strongest argument is not cost

- **Ubisoft Ghostwriter** is the canonical build-time case: drafts NPC barks inside an authoring tool,
  **two candidates per generation**, writer picks/edits/discards, *"after thousands of selections made by
  humans, it becomes more effective"*. The shipped artifact is static data. Acceptance varies sharply by
  category — confident/excited barks frequently accepted, **curious barks "almost always rejected."**
- **The determinism argument beats the cost argument.** LLM inference is **not reproducible even at
  temperature 0**: 1,000 samples on Qwen3-235B produced **80 unique completions**, divergence first
  appearing at the **103rd token**. Root cause is not sampling — *"the primary reason nearly all LLM
  inference endpoints are nondeterministic is that the load (and thus batch-size) nondeterministically
  varies"*. A runtime model call therefore **cannot live inside a deterministic sim, a replay, a
  lockstep path, or a seeded save** — the same request under the same seed can answer differently
  because of *server batch load*, which is outside the game's control. This repo's world turns are
  seeded and replayable; that alone settles it, independent of price.
- **Cost, where it is real:** offline generation is asynchronous and so qualifies for the **50% Batch API
  discount** a runtime loop structurally cannot use; prompt-cache hits are **0.1×** base input price.
  The only published game-scale volume figure is Death by AI's **1.2 billion tokens in month one**, with
  the note that *"there is no opportunity for caching to save on costs"* — per-user cost undisclosed.
- **Validation is the part that earns its keep.** MarioGPT: **88.4%** of generated levels completable →
  **11.6% rejected by an A\* validator**; prompt adherence by feature 92% blocks / 81% pipes / 76%
  elevation / **68% enemies**. And schema-valid ≠ correct: across 21 models, median JSON pass rate
  **97.5%** but best **value accuracy 0.830** — *"17–31% of leaf values are wrong despite the JSON being
  schema-valid."* **A JSON-schema gate buys ~2.5%; the domain validator — does this channel id exist,
  does the atom resolve, do the shares sum to 1000 — is the one that matters.**
- **Homogenization is measured, and a per-item gate cannot see it.** Doshi & Hauser, *Science Advances*
  2024 (300 writers, 600 evaluators): one generative-AI idea raised individual novelty **+10.7%** and
  usefulness **+11.5%**, **and raised inter-writer similarity by 10.7%**. Every item individually better,
  the corpus collectively flatter — precisely the risk for a 904-species LLM-authored favour corpus.
- **Two cautionary postmortems.** Keywords "Project Ava": six months, 400+ AI tools, seven studios, game
  never released — *"the tooling was unable to replace talent."* AI Dungeon 2021: runtime generation
  produced content that a build-time review pipeline would have caught and a runtime one shipped.

---

## The question this reduces to

Not *"can we build the weights"* — this repo has built a 1131-entry deterministic weight table at
species scale, and a 904-row per-mille build plan, already. The engine is proven. Three real questions
remain, in dependency order:

**Q1 — Does a species level change anything?** (R2) Shares are scale-free, so more points into the same
shares compose identically. Until species level reaches **theta or a channel**, every build plan is
cosmetic and both human and AI assignment are decoration. **This is a prerequisite, not a parallel
track**, and it belongs to `species-progression-ideal.md`.

**Q2 — Who owns the AI empire's progression?** (R1) Zomboss owns zero rows while zombie species level on
the human's. Assignment for an empire that owns nothing is a no-op. **This is an attribution fix, not an
AI feature**, and it is the same shape as `SR-18`.

**Q3 — What authors the favour signal, at what coverage, and how is it kept honest?** Aptitude favour is
904/904; tree favour is 1/904; three separate systems ship neutral-constant weights. The mechanism is
never the bottleneck here — **the differentiating content is**. And 904/904 is *coverage*, not
diversity: measured below, that fully-covered corpus still has one aptitude leading 42% of species and
carries only twelve distinct lean values, which is what the **build favour pipeline** (§4a) exists to
address.

Only after those does "AI decision weights" become the interesting question — and by then most of the
machinery (`ValueMap`, `Considerations`, `ResponseCurves`, the seedsmith derivation family) is already
sitting built and inert, waiting for exactly the economy `Consideration.cs:23` says it is waiting for.

---

## The shape

Proposed, not decided. It is deliberately the shape the repo already proved twice, because inventing a
third would be the defect.

### 1. Keep the existing division of labour, verbatim

```
LLM (seedsmith, offline)         →  closed-enum IDENTITY labels only
        ↓                           aptitudePrimary, mechanicalFavour {aptitude, element, status}
Deterministic derive (seedsmith) →  per-mille WEIGHTS, largest-remainder, sums to exactly 1000
        ↓                           byte-identical across runs, --check in CI
Committed artifact               →  gk-data/packs/fusion/data/seed/**, gk-data/packs/fusion/data/generated/**
        ↓
Runtime (C#)                     →  cheap arithmetic only: share × budget, weighted sum
```

This already exists as `gk-forge/tools/seedsmith/seedsmith/adapters/creatures/anchor/schema.py:93`'s *"never let the model author posture/pure/basis"* and
`innate_picker/derive.py:7-9`'s *"Model calls: none — permanently, not provisionally"*. **The model
names a lean; code turns the lean into a number.**

### 2. Resolve the runtime-vs-precompute tension explicitly

There is a real conflict in the prior art and it should be settled on the page rather than discovered
later. Kevin Dill: *"One point that cannot be overemphasized is the importance of calculating each
option's utility **in game, at run time**. It is not enough to assign fixed weights to the options a
priori."* Against the owner's constraint: a model call at runtime is unaffordable *and*
non-deterministic.

**Both are satisfied, and the repo already does it:** precompute the **weights** (data), evaluate the
**decision** at runtime (arithmetic). `ValueMap.cs:98-108` is exactly this — six weights loaded from
`ai.v2.json`, the weighted sum computed live against current fogged belief. Nothing is precomputed that
depends on game state; nothing state-dependent is baked. Libratus's lesson is the same one: the baked
artifact is a *value estimate feeding a cheap live decision*, never the decision.

### 3. Assignment ladder, cheapest rule that works

Following the prior art rather than inventing: **ordered priority list, take the first legal** — the
NWN/Mass Effect/gambit shape, which is also `FrontierRulesPolicy`'s existing shape. Proposed order for
filling a point budget:

1. **Active preset**, if the player set one (`active-preset`, already built)
2. **Species favour**, zero-filled to 12 (fixes W3), if a plan row exists
3. **Posture lean**, if the actor has a dominant posture
4. **Even split**, which always succeeds

Each rung already exists as a rule id. The work is the ladder, the emitter (W2) and the zero-fill (W3) —
not new math.

### 4. Empire scope reuses the layer that already exists

No new layer. Layer **2b empire species progression** is already ruled, already scoped per
`(empire, species)`, already mutually exclusive with 2a, and already has an override key carrying an
empire dimension (`SpeciesAllocation.ScopeKey(playerId, empire, speciesId)`). What is missing is a
**writer for a non-Dave empire** — `RpgStore.SpeciesRespec.cs:155-159` says *"A non-player empire has no
respec surface — Zomboss does not spend points at a workbench"*, which is true and is exactly why the AI
needs an assigner instead of a workbench.

### 4a. The build favour pipeline — a second pass that re-leads, and an LLM that reads the first run

**Owner's proposal, named:** *"current build favor is not good, we need deterministic engine to second
run (new pipeline) and llm engine to solve diversity base on the original run, should named it is build
favour pipeline."*

The measurement above says exactly what this pipeline must and must not do, and it is narrower than it
first looks.

**What is already built and must not be rebuilt.** `SpeciesBuildPlanner` is *already* a corpus-level
deterministic pass. It already reads corpus-wide crowding (Phase 1), already redistributes filler
against a running corpus deficit (Phase 2), and already refuses to emit a plan whose per-aptitude
corpus share leaves `[50, 200]‰` (Phase 3). Point parity is met at 76–150‰. A second pass that
re-balances points would re-solve a solved problem and risk the gate that keeps it solved.

**What is not built, and is the whole job.** The planner **cannot change which aptitude a species
leads.** The lead is `AnchorRow.AptitudePrimary`, authored by the LLM one creature at a time, and the
deterministic pass only *sizes* it. So 378 species lead Onslaught not because the maths converged, but
because the identity step converged and nothing downstream is permitted to disagree. **The gap is
re-leading, not re-sharing** — and that is precisely the split the owner's two-pass proposal draws.

```
PASS 1 — today, unchanged                          gk-forge/tools/CreatureBuildPlanGen
  LLM  : aptitudePrimary / aptitudeSecondary          identity label, per species, no corpus view
  code : SpeciesBuildPlanner                          crowding lean + deficit filler + parity refusal
  out  : _species-build-plan.json                     904 rows · 12 lean values · 21 shapes
                     │                                 parity MET (76–150‰) · lead NOT diverse (42%)
                     ▼
PASS 2 — NEW: the build favour pipeline               corpus in, corpus out
  measure : lead histogram, shape histogram, lean-vs-crowding inversion   deterministic
  LLM     : given this species' identity AND the measured crowding of
            its current lead, which aptitude should it lead instead?      identity label, corpus-aware
  code    : re-run SpeciesBuildPlanner on the re-led anchors              unchanged, still refuses
  out     : the build favour artifact, byte-identical, --check in CI
```

The shape has a property worth stating plainly: **pass 2 reuses pass 1's planner rather than replacing
it.** Re-leading changes the planner's *input*, so Phases 1–3 re-run untouched and the parity gate still
guards the result. A re-lead that would break parity is refused by code that already exists.

**What each half is allowed to author, and it is the repo's existing rule, unchanged.** The LLM authors
a **label** — which aptitude this creature leads — never a magnitude. `gk-forge/tools/seedsmith/seedsmith/adapters/creatures/anchor/schema.py:93` already
forbids the other thing in as many words, and `innate_picker/derive.py:7-9` already states *"Model
calls: none — permanently, not provisionally"* for the numeric half. Pass 2 changes **what the model is
shown** (its own species *plus* the corpus-level crowding of its current lead), never **what it may
emit**. The lean, the filler, the largest-remainder split and the parity refusal stay in code.

**The homogenization warning applies to pass 2 specifically, and it cuts both ways.** Doshi & Hauser
measured that generative assistance raised individual quality (**novelty +10.7%, usefulness +11.5%**)
**while raising inter-item similarity by 10.7%**. A pass that asks a model "make this one different" 904
times, one creature at a time, can converge on a *new* dominant answer — trading Onslaught 42% for
Ferocity 42%, which would be no better. **The crowding figure must be computed by code and handed to the
model as a constraint, not left to the model to intuit** — which is also why pass 2 is a pipeline over
the first run's output rather than a better prompt in pass 1.

**One design question pass 2 forces, and it belongs in the open questions below.** If the lead
distribution flattens, the crowding term flattens with it, and every species converges toward the same
mid-band lean — the shape histogram could get *worse* while the lead histogram gets better. Whether
`crowdingFactor 633` survives a re-leading pass, or is replaced by something keyed to the species rather
than to its archetype's population, is a balance decision on `gk-core/data/tuning/species-build.v1.json`, not a
code decision.

**Non-negotiables inherited, not re-decided:** no model call at runtime (determinism, §"What a
downstream session must not do"); output byte-identical across runs with `--check` in CI, as
`CreatureBuildPlanGen` already is; every vector sums to exactly 1000‰ via largest remainder; the parity
band stays gated by `SpeciesBuildRefusal`; and the generated corpus is never hand-edited — a fix belongs
in the generator or in `gk-core/data/tuning/species-build.v1.json`.

### 5. Ship the detector, not the "best build"

Per Riot and Blizzard: the deliverable that survives content growth is a **variance band asserted in
CI**, not a build asserted once. Candidates, all measurable offline against the committed corpus:

- No aptitude appears as the top share for more than *X*% of species (anti-convergence)
- Every plan row sums to exactly 1000 (**already asserted**, `SpeciesBuildPlannerTests.cs:93`)
- Corpus-level diversity: distinct top-share distribution stays above a floor (catches the
  Doshi & Hauser homogenization a per-item validator structurally cannot see)

### 6. Naming: `systemCopy` is the carrier for a default build

W4's orphan constant is the right home for "the build the game suggests", distinct from `player` presets.
It is already validated and needs a producer, not a new concept — which also keeps "closed / half-open"
(R4) from becoming a fourth vocabulary nobody else uses.

---

## Tunables

Every number this introduces is config, never a `const` (principle 5). Existing homes, reused:

| Domain | File | Already carries |
|---|---|---|
| Species build shares | `gk-core/data/tuning/species-build.v1.json` | `leanMinPermille 350`, `leanMaxPermille 600`, `crowdingFactor 633`, `secondarySharePermille 300`, `maxAptitudesPerSpecies 5`, `minAptitudesPerSpecies 2`, **`parityFloorPermille 50`, `parityCeilingPermille 200`** (the band `SpeciesBuildRefusal` enforces) |
| Preset limits | `gk-core/data/tuning/aptitude-presets.v1.json` | `softMaxPresets 32`, `defaultRowAbsMax 1000` |
| World AI weights | `gk-core/data/tuning/ai.v2.json` | `valueMap.defaultWeights` {yield, strategic, defensibility, cost, risk, curiosity}, `optimismMilli`, penalties |
| Siege AI weights | `gk-core/data/tuning/siege.v1.json` → `ai` | `weightHitChance 70`, `weightObjective 50`, `weightKill 15`, `weightRisk 120`, … |
| Action lean | `gk-core/data/tuning/action-role-lean.v1.json` | 165 multipliers, **all flat at 1000** — the content gap, not a new file |

New numbers this would need: the assignment ladder's order (data, not code), the anti-convergence
thresholds, and — if `INeedVector` is ever made real — per-empire need multipliers. The
2026-09-17 rulings add exactly two keys, both to `species-build.v1.json`, which already owns every
neighbouring value:

| key | default | ruling | why here |
|---|---|---|---|
| ~~`respecFreeCount`~~ | ~~25~~ | R-Q3, **superseded by ruling R18** | *Superseded 2026-09-18:* never published. Replaced by `freeRespecsPerEmpireLevel` (earned per empire level, `respec-free-counter`) |
| `leadCapPermille` (+ tolerance) | unset | R-Q6 | The one-sided cap on a single aptitude's share of corpus LEADS. Sits beside `parityFloorPermille 50` / `parityCeilingPermille 200`, which gate the different (already-solved) point-parity axis |

Neither is a new domain, and `crowdingFactor` is **changed, never deleted** (R-Q8) so the change stays
revertible. **No new tuning
domain is proposed**, and the build favour pipeline in particular introduces none: its lead-distribution
band belongs beside `parityFloorPermille`/`parityCeilingPermille` in the file that already owns the
parity band, and the `crowdingFactor` question (open question 8) is a change to a value that already
exists there. Note that `species-build.v1.json`'s own `_meta` disclaims its band values — *"Working
values, not a validated balance decision … shipping a guess is fine, calling it balance is not"* — so a
pipeline that leans on those numbers inherits that disclaimer rather than clearing it. Per Zubek's warning about global knobs, any new dial should ship as **global
default + per-partition override**, never one global constant.

---

## What this deliberately does not decide

- **What a species level grants.** That is `species-progression-ideal.md`'s question and the owner has
  it deferred. Q1/R2 is a prerequisite this document depends on and does not attempt to answer.
- **The action system.** The owner has ruled it a redesign and deferred it: *"current action system is
  gacha, that is not good for default build and build favor so we will defer it."* Noted here only
  because `type-weights.json` is this document's best in-repo precedent for offline weight generation —
  borrowing its **shape** implies nothing about its **content**.
- **Any balance number.** Magnitudes, curve shapes, thresholds and per-mille values are a balance pass's
  work against a real corpus, not an idea doc's.
- **Whether `INeedVector` should be made real**, and whether the utility scorer should replace or
  supplement `frontier-rules`. `Consideration.cs:23` ties that to `sector-development` shipping an
  economy to score against.
- **UI.** Where an auto-assign control lives is `gui-lego`'s question and needs `/idea-ui`, not this page.

---

## The commander identity defect — adopted into this program (2026-09-17)

> ### ➡️ The SOLID fix moved to `solid-enforcement` (2026-09-18)
>
> The owner's ruling *"Everything SOLID, one program"* moved the **shape change** to
> [`solid-enforcement`](solid-enforcement-map.md), module
> [`commander-identity`](solid-enforcement/spec-commander-identity.md). That spec found something this
> section did not: `CommanderId` carries **two** meanings, the **empire** (species-allocation key,
> kill attribution, allocation scope) and the **commander** (the unit). It splits the enum into
> `EmpireId` and `CommanderRef` before opening it, so a creature-commander can never re-key species
> progression.
>
> **What stays here:** what a commander *does*, meaning XP by mode, delve participation, and aura
> strength per mode (R-C1..R-C6). That is feature work, and after `commander-identity` lands it arrives
> by **adding directory rows**, not by editing `switch` statements. The reasoning below is kept as the
> trail. For the shape of the fix, read the spec, not this section.

**Owner:** *"ok, it violate the solid so we will make it is a task in this program too."*

This section is idea phase. No build authorized, no spec, no code.

### Which loop this extends

**Spine loop A — "Level up and power"** (`docs/guide/the-loops.md`), which already names this work in
its own forward list: *"Later: trees and **commander presence**."* It also touches **Place 3** (farming,
hunting, defending — sieges), **Place 4/5** (world map and stage — legions), and **Place 6** (the Delve),
because the owner's model puts one commander into all of them. It invents no loop.

### The principles this is constrained by, restated here rather than linked

A downstream session reads this page, not its links.

1. **Every RPG feature lives in the RPG layer, and is never built by changing what PvZ is.** A commander
   never becomes a PvZ entity. It resolves in the RPG stack and contributes signed deltas.
2. **One ActorHub compose, one read.** A commander's numbers contribute `DerivedModifier`s into the one
   fold via a registered `IActorStatSubsystem`, or consume Hub output. Never a private fold.
3. **One power ladder.** A commander's level reads `Θ`; its magnitudes read `P(Θ)`. No private
   `f(level)`.
4. **A guardrail asserts the CONTRACT and closed enums — never a population count.** This is the rule
   the defect broke, and it is the whole section.
5. **The balance surface is data.** Every number here lands in `gk-core/data/tuning/`, not a `const`.
6. **No hard progression ceilings.** A commander roster size limit would be a ceiling unless it is a
   soft, configured one.

### What this is

A commander is **a unique creature that has been given the commander role** — named, levelled, geared,
and individually meaningful, exactly like any other `UniqueActor`. The role is a hat, not a species of
thing. §"The clarification that settles the rest" below states this as a rule and works through what
follows from it; read that section before designing anything here.

The owner's model, in their words: *"it is a unique creature with named and play a role like another
unique actor but it can play commander role in the legion (the inspire of heroes of might and magic) …
the lawn game empire can deploy commander to their side, cannot enter the lawn but outside the lawn with
aura buff and action skill can cast to the lawn … it can play in siege, world assault, delve too."*

### The defect, and which SOLID letters it breaks

```csharp
// gk-core/src/FusionRpg.Core/Commanders/CommanderId.cs:21
public enum CommanderId { Dave, Zomboss }
```

The file's own comment records how it got there:

> *"There are exactly two commanders total (owner decision, 2026-08-30: **"for now only have 2 of them
> for lawn run"**)"*

**A content statement became a type statement.** *"For now"*, *"only have 2"* and *"for lawn run"* are
three qualifiers, and all three were dropped in the translation.

| Letter | How it breaks |
|---|---|
| **O** — open for extension, closed for modification | Shipping a third commander is **content**, and content must never require editing a declaration. Today it requires editing the enum plus every `switch` over it — `ToStableId` and `AllocationScopeKey` both `throw` on an unhandled member, so the compiler and runtime both fight new content |
| **D** — depend on abstractions | Allocation, aura, world-turn and persistence all depend on a **concrete enum** rather than on an actor reference. `RpgStore.PlayerCommander` stores `TEXT` — the right abstraction — then narrows it back through `TryParseStableId` |

And it breaks the repo's own written rule, which both `AGENTS.md` and `CLAUDE.md` carry as a table:

> | | Closed vocabulary (the code owns it) | Derived population (content grows it) |
> | Cardinality | **constant — pin it, say why** | **a reading — never pin it** |

**A commander roster is a population.** It grows when content ships, exactly like a species. "Two today"
is a reading. This is the `len(species) == 904` mistake expressed as a *type* rather than an assertion —
and worse for it, because an assertion fails loudly and gets edited, while an enum makes a third
commander **unspeakable** across 40 files.

Full diagnosis, including why nobody caught it:
[`../research/commander-identity-drift-2026-09-17.md`](../research/commander-identity-drift-2026-09-17.md).
The short version: the concept was **explicitly deferred** by `decisions.md` on 2026-08-29, and the aura
program minted the identity type the next day as a side effect of needing a collision-free key. The
deferral removed the document the enum would have been reviewed against.

### What already exists — built / wiring gap / real gap

<!-- citations-historical: CommanderId.cs was deleted (commander-identity SE4.2/SE4.3); the faction is EmpireId, the unit is CommanderRef, and every display name/scope key/empire/default comes from data through ICommanderDirectory -->


**Built.**

| Thing | Where |
|---|---|
| Unique actors: specimen progression, own allocation, equipment, phase FSM, death into `corpse-cache` | `rpg_unique_actors`; `decisions.md` deployment-hierarchy row |
| `Commander` as one of four summed allocation scopes (commander → creatureType → aspect → uniqueCreature) | `AptitudeAllocation.cs:8` |
| A legion member that **is already a unique actor** — *"Roster specimen (`rpg_unique_actors`); null for non-player forces and guards"* | `WorldState.cs:277` |
| Commander identity on the world map is **already an open string** | `WorldCommand.cs:140` (`public string CommanderId`) |
| Legion founding already stamps the commander onto the entity, and derives its id from it | `RaiseResolver.cs:97,124` — `e-{commanderId}-legion-{turn}-{sector}` |
| Persistence column is **already open** | `RpgStore.PlayerCommander.cs:17` — `default_lawn_commander_id TEXT` |
| Match-start freeze of who led and which aura was live | `MatchCommanderSnapshot.cs`, `MatchCommanderSnapshotHolder.cs:35` |
| Commander resource pools | `CommanderResourcePools.cs` |
| **The vocabulary already says the owner is right** — *"the two passive-aura roles (**both assignable only to a unique creature**)"*, *"**designate one creature**"* | `creature-system-map.md:69-75`, and `DESIGN-GATE.md` §1 points at it as binding |

**Wiring gap** — inert or narrowed, not architectural walls.

| Gap | Where |
|---|---|
| `TryParseStableId` accepts exactly two string literals and rejects everything else | `CommanderId.cs:41-58` |
| `SetDefaultLawnCommanderId` validates the open `TEXT` column back down through that parser | `RpgStore.PlayerCommander.cs:47` |
| `PlayerEmpireCommanders.ForPlayer` returns a hardcoded one-element array instead of reading a roster | `PlayerEmpireCommanders.cs:9` |
| `AllocationScopeKey` hardcodes two key shapes in a `switch` that throws otherwise | `CommanderId.cs:66-72` |

Measured blast radius: **14 enum-typed parameters** and **45 literal** `CommanderId.Dave`/`.Zomboss`
references (37 Dave, 8 Zomboss) across 40 files. **The world/legion layer never adopted the enum** — its
commander identity is already a string — so the closed half is confined to lawn, aura, allocation and
persistence-validation.

**Real gap** — no mechanism exists.

| Gap | Detail |
|---|---|
| The enum itself | `CommanderId.cs:21`. There is no representation of "a commander that is a unique actor" |
| No commander role on a legion member | `WorldEntityMemberRole` is `{ Fighter, Bearer }` (`WorldState.cs:269-273`). The owner's *"play commander role in the legion"* has nowhere to live |
| Nothing binds a unique actor to the commander role | `CommanderId` is the only answer to "who is a commander" |
| Zomboss has an allocation key but no progression row | `zomboss:{playerId}` exists; "a commander levels" is true for Dave only. This is already open question 2 of this program. *(2026-09-18: his progression rows are answered by rulings R1/R3 and `zomboss-commander-clock`; his commander allocation is still unowned, map Q-S1)* |
| Scope is lawn-run only in the docs, and the "never fights" rule is wrong outside it | `creature-system-map.md` scopes Commander to *"the lawn run"* and says the role *"never fights"*. Owner-ruled 2026-09-17: the commander **fights** in delve, siege and world assault, and only the lawn run is non-combat. That text needs amending, not just widening |
| Aura is documented as *continuous, passive* | The owner wants *"aura buff **and action skill can cast to the lawn**"* — an active, cast ability is not in the current commander model at all |

### Prior art — Heroes of Might and Magic III, with numbers

The owner named HoMM3 and `aura-skill-ideal.md` §1 already records it: *"the commander is not a unit on
the board, and their stats reach the fight by lifting everything they command."*

- **Four primary skills** — attack, defence, spell power, knowledge. **One point is granted per level**,
  weighted by class: might classes advance might skills faster, magic classes magic skills, and the
  spread *converges* after level 9 rather than diverging forever.
- **The hero's attack is added to every stack under its command** at combat start. That is the "lifting
  everything they command" shape, and it is exactly a `DerivedModifier` contribution in our terms.
- **Damage is a differential, not a second multiplier.** Each point of attack over the defender's
  defence adds **5% damage**, capped at **+300%** (reached at +60). Each point under subtracts **2.5%**,
  floored at **−70%** (reached at −28).
- **Spell power is duration**: 1 point = 1 extra round on Bless / Curse / Haste / Slow.

**Two cautions that transfer directly.**

1. **The caps are the load-bearing part.** A commander bonus added to every unit is the definition of a
   snowball, and HoMM3's answer is a hard differential ceiling reached at a specific, small number
   (+60 / −28). A commander contribution here needs the same shape — a bounded differential, not an
   unbounded flat add. This matches our own rule that contests read `Θ` (difference-based) and
   magnitudes read `P(Θ)`.
2. **HoMM3 is not a balance model to copy wholesale.** *"Balance was not considered a goal when Heroes
   of Might and Magic 3 was in development"* — copy its **structure** (off-field, differential, capped),
   not its numbers.

Sources: [Primary skill — heroes.thelazy.net](https://heroes.thelazy.net/index.php/Primary_skill) ·
[Damage — heroes.thelazy.net](https://heroes.thelazy.net/index.php/Damage) ·
[Hero specialty — heroes.thelazy.net](https://heroes.thelazy.net/index.php/Hero_specialty) ·
[Imbalance — heroes.thelazy.net](https://heroes.thelazy.net/index.php/Imbalance)

### The shape being proposed

**1. Commander becomes a role reference, not a type.** The identity is whatever already identifies a
unique actor (`instanceId`), and `commander` becomes a **role** a unique actor holds. The `TEXT` column
already stores an opaque id, so **no schema change is required** — the validator changes, not the table.

**2. Do not add a `commander` member to `RpgActorKinds`.** The five kinds are `player`, `plant`,
`zombie`, `species`, `specimen`. `CommanderIds.AllocationScopeKey` gives Dave the key `player:{playerId}`
— byte-identical to the player's own — and the source states why: *"he IS the player's own commander — no
new convention needed, no data migration for existing saves."* A `commander` actor kind would fork Dave's
identity in two and recreate the dual-source defect `decisions.md` overturned for `BattleStatComposer`.

**3. The legion role is where `WorldEntityMemberRole` grows.** `{ Fighter, Bearer }` gains a third
member. That enum **is** a closed vocabulary the code owns — adding to it is a reviewed declaration
change, which is exactly the correct use of an enum, and the contrast with `CommanderId` is the lesson.

**4. Dave stays Dave by seeding, not by typing.** The two existing commanders become **content rows**,
not enum members. `PlayerEmpireCommanders.ForPlayer` reads a roster; the default stays Crazy Dave because
a seeded row says so, not because a type forbids alternatives.

**5. Scope widens to where the owner put it** — lawn, siege, world assault, delve — which the actor-layer
rules already permit, because a commander contributing `DerivedModifier`s through Hub reaches every mode
that composes through Hub. That is one contribution path, not four.

**Rejected alternative:** keeping the enum and adding members as content ships. It compiles, and it is
the status quo that produced this defect — every new commander would be a code change, a
`decisions.md` row, and a migration. That is the definition of the Open/Closed violation, not a fix for
it.

### Tunables this introduces

**No new tuning domain, and — after R-C2 — no commander-specific magnitude at all.** A commander composes
like any other unique actor, so its numbers are already `P(Θ)` reads on the one ladder. There is no
commander stat curve to tune because there is no commander stat path.

**One table, owned elsewhere.** The per-mode aura scale (R-C3, R-C5) is `aura-skill`'s file, not this
program's:

| Mode | Scale | Ruling |
|---|---|---|
| Lawn run | 100‰ of 100‰ — the reference | R-C3 |
| Siege | 100% | R-C5 |
| World assault | 100% | R-C5 |
| Delve | 10–15% | R-C3 |

All four are rows, including the three at the reference: a mode pinned at 100% in code would be a
balance number in a `const`, and *"would a balance pass ever want to change this number?"* is plainly
yes. The three 100% rows are a **starting value**, not an equality claim.

**Explicitly not introduced:** an idle/garrison XP rate (R-C6 — there is no idle faucet to tune) and any
commander-sourced empire-economy modifier (R-C6 — out of scope; `WonderEffectKind.EmpireBuff` already
reserves that shape and is refused by `Validate` today).

### What this deliberately does not decide

- **How many commanders exist, or who they are.** That is content, which is the entire point.
- **What the active cast skill does.** The owner named *"action skill can cast to the lawn"*; whether
  that reuses the existing action system (currently gacha-shaped and deferred by this program) or a
  commander-specific surface is unresolved.
- **Aura magnitude, tick cost and channel mapping.** Owned by `aura-skill`, per its own scope boundary.
- **Whether a commander can be lost.** The deployment-hierarchy row already groups *"unique/commander"*
  for corpse-cache purposes, but nothing says whether a commander may die.
- **Migration ordering.** A spec decides that; an ideal does not.

### The clarification that settles the rest: a commander IS a unique creature

**Owner, 2026-09-17:** *"make the thing clear, a commander literally a unique demon, it only carry more
role."*

Stated as a rule, because every ambiguity below dissolves once it is held:

> **A commander is not a kind of thing. It is a `UniqueActor` — the same `rpg_unique_actors` row, the
> same `instanceId`, the same phase FSM, the same specimen progression, the same equipment — that has
> been given one additional role. Roles are additive and removable. The creature is the noun; commander
> is an adjective.**

Three consequences follow immediately, and they are what make this cheap rather than a new subsystem:

1. **Everything that already works for a unique actor works for a commander, with no new code.** XP,
   levels, gear, aptitude allocation, death, corpse-cache, the deploy FSM. If something does *not* work,
   that is a defect in the role layer, never a missing capability.
2. **Restrictions belong to the PLACE, not the creature and not even the role.** *"Does not fight"* is a
   property of **the lawn run alone** — the lawn's own constraint that a commander is not a board tile.
   The same specimen with the same role fights normally in a delve, a siege and a world assault
   (owner-ruled; see §"Where a commander plays"). A rule written on the creature, or on the role, would
   make three of the four places impossible.
3. **`RpgActorKinds` gains nothing.** `player`/`plant`/`zombie`/`species`/`specimen` already contains the
   noun (`specimen`). A `commander` kind would be an adjective pretending to be a noun, and would fork
   Dave's identity in two (§"The commander identity defect").

**The codebase already tried to say this twice, and both times had to stop at the enum.** These are not
my observations; they are comments already in the tree:

> `RpgStore.UniqueActors.cs:177-185` — *"Commander is deliberately NOT checked here, and that is not an
> oversight: `CommanderId` … is a fixed two-value enum … with **NO creature-instance binding anywhere**
> … **There is currently no state anywhere in this codebase that means "this specific creature specimen
> IS the Commander,"** so there is nothing yet to refuse against … when that lands, this refusal needs a
> second branch here, symmetric with the Patron one above."*

> `CreatureLawnDeployCommanderRefusalTests.cs:9-14` — *"Commander is NOT tested here — `CommanderId` … is
> a fixed Dave/Zomboss enum with no creature-instance binding at all today, so there is no state yet that
> means 'this specimen is the Commander' to refuse against."*

Two independent authors, at a call site and at a test, each wrote down the missing binding and each
named where the fix goes. **Those comments are canaries that go red when this lands** — the refusal
branch and its test are already specified by them.

---

### XP for a commander that never enters combat — already built, and that is the headline

**Owner:** *"the commander deploy to run the lawn that not enter the combat will earn xp. same for legion
siege and world assault."*

**This needs no new XP source.** The mechanism already ships, is idempotent, and awards a specimen XP for
**time deployed rather than kills**:

```
RpgXpReasons.SpecimenLawnDuration = "specimen_lawn_duration"     RpgProgression.cs:46
rpg_unique_lawn_xp_receipts(instance_id, match_key, occurrence_id='duration', reason, xp, created_utc)
                                                                  RpgStore.UniqueActors.cs:976-1000
```

The receipt is written `INSERT OR IGNORE` and re-read on conflict to assert the same delta
(*"unique lawn XP duration receipt collision"*), so a replayed match cannot double-pay. A second
non-combat term already exists beside it — `RpgXpReasons.SpeciesRunComplete`, *"fired once per resolved
match a species was fielded in"* (`RpgProgression.cs:36-39`), an **outcome** award rather than a kill
award.

So the owner's mechanic is not a new faucet. It is **the faucet a deployed specimen already drinks
from**, and the only reason a commander cannot is that no specimen can currently *be* a commander. That
makes this the single strongest argument for the fix: **the feature is already built and the enum is the
only thing standing between it and the player.**

Sorted honestly:

- **Built.** Duration-based, kill-free, idempotent specimen XP on the lawn (`RpgStore.UniqueActors.cs:976`).
  Outcome-based species XP (`RpgStore.Progression.cs:118`). One deploy FSM — `Roster → Deploying →
  ActiveBound → Recovering → Retired` (`UniqueActorDtos.cs:6-13`) — which `decisions.md`'s
  deployment-hierarchy row already applies to *"lawn Bound, delve party slot, siege combatant, expedition
  seat"*, i.e. every place the owner named.
- **Wiring gap.** A commander cannot reach any of it, because nothing binds a specimen to the role.
- **Real gap — narrower than it first appeared.** The duration receipt is keyed on `match_key`, a **lawn
  match** concept, and an earlier draft called the lack of a turn-clock equivalent a real gap for siege
  and world assault. **Owner-ruled 2026-09-17: it is not needed.** A commander *fights* in siege and
  world assault, so it earns there through the ordinary combat path like any other unique actor. Only
  the lawn run is non-combat, and the lawn run is exactly where the receipt already works. What remains
  is a much smaller question — whether a commander garrisoned and idle earns anything — listed in the
  open questions rather than assumed to be a gap.

---

### Where a commander plays, and what changes per place — owner-ruled 2026-09-17

> ⚠️ **An earlier version of this table said a commander never fights in siege or world assault. That
> was wrong, and the owner corrected it:** *"in the delve, commander is a part of party, it basically a
> unique unit, only have commander aura. **this is the mode commander go to the fight, it can go to the
> fight in siege and world assault too. so only outside the combat in lawn run.**"* The mistake was
> generalising the lawn's "cannot enter the lawn" into a property of the role. It is a property of **one
> place**.

**The commander fights everywhere except the lawn run.** The lawn is the exception, not the rule, and
the reason is the lawn's own constraint — the commander is not a lawn tile — never a statement about
what a commander is.

| Place | Fights? | Aura | XP |
|---|---|---|---|
| **Lawn run** | **No** — stands outside the board, casts in | Full strength (the reference value) | **Duration only**, no kill XP |
| **Delve** | **Yes** — a party member like any other unique | **Weakened: 10–15% of the lawn-run value** | Normal combat XP, as any party member |
| **Siege** | **Yes** | Per-mode tuned | Normal combat XP |
| **World assault** | **Yes** | Per-mode tuned | Normal combat XP |

So exactly **one** row needs the non-combat XP mechanism, and it is the row where the mechanism already
exists (`specimen_lawn_duration`, `RpgStore.UniqueActors.cs:976`). The other three rows need **nothing
new at all** — a commander that fights earns XP the way every fighting unique actor already does.

This also simplifies the sibling question the earlier draft raised. The siege and world-assault
"duration receipt on a turn clock" it called a **real gap** is **not needed**: those modes are combat,
so they use the combat path. The only turn-clock question left is whether a commander sitting idle in a
sector earns anything, which is a different (and much smaller) question than the one that was posed.

---

### R-C1 — exclusivity is already solved by the deployment hierarchy; no new rule

**Ruled:** *"no, we already have deployment scope. so the commander or any unique demon must is some
where on the map or on the sector. to enter the lawn run, the commander must on any base."*

Verified — `deployment-hierarchy-ideal.md` §"The tree" already models exactly this, and the column
headings are the answer:

```text
parent (where a force LIVES)                child (where it DEPLOYS)
roster / home                                ├─ lawn Bound (1 specimen)
legion in sector (troops + attached uniques) ├─ lawn Bound (attached unique)
                                             ├─ siege combatant (troop slice + attached uniques)
                                             ├─ delve party slot (bound unique)
                                             └─ expedition seat (bound unique)
garrison (sector defense)                    └─ siege combatant (defense)
```

**A specimen has exactly one parent, so it is in exactly one place.** Exclusivity is not a commander
rule to invent — it is a consequence of a model that already ships for every unique actor. The
commander inherits it by being a unique actor, which is the clarification doing its job.

*"To enter the lawn run, the commander must be on any base"* maps onto the parent column directly: the
lawn-Bound child is reachable from **roster/home** or from a **legion in sector**, and from nowhere
else. A commander parked on a lane, mid-march, is not at a base and therefore cannot be the lawn's
commander that run.

**One wiring gap this depends on, already named by that document:** *"**Attached uniques** (later): a
legion member row may carry `InstanceId` (the column exists, `WorldState.cs:278`, **all writers omit it
today**)."* So a commander riding with a legion is inert, not impossible — the column exists and nothing
writes it.

**What this retires:** the double-XP-faucet worry the earlier draft raised. Two faucets required one
specimen to be in two places, which the parent model already forbids.

### R-C2 — no commander-specific aura mechanic; it is a unique unit with one feature

**Ruled:** *"no special for commander, it basically a unique unit, no more special, only thing it have
special is commander aura feature that buff other unit in lawn/delve/siege/world assault."*

This rejects the earlier draft's framing, and correctly. The draft asked whether the commander's aura
should be a HoMM3-style capped differential — as though commanders needed their own contribution math.
They do not. **A commander composes exactly like every other unique actor**, through ActorHub, with no
commander-shaped exception anywhere in the stat path.

The single addition is the **commander aura feature**: one effect that buffs other units, present in all
four modes. Its magnitude, tick cost and channel mapping are owned by `aura-skill`, not here, and this
program must not invent a second aura path.

The HoMM3 prior art above is **not** retired by this ruling — it still explains *why* an effect that
reaches every unit on a side needs a bound, which is a live concern for whoever tunes the aura. It is
simply not a *commander* design question; it is an aura one.

### R-C3 — the aura is tuned per game mode; delve is 10–15% of the lawn-run value

**Ruled:** *"each game mode have aura tuning table, commander have aura in delve but weaker version,
10% to 15% of lawn run."*

So the aura is live in all four modes and **scaled per mode**, with the lawn run as the reference (100%)
and the delve at **10–15%**. Siege and world assault were unset at the time of this ruling and were set
to **100%** shortly after — see R-C5.

**Why a per-mode table rather than a flat aura, stated so it is not "simplified" later:** the modes are
not comparable. A lawn run fields a whole side of plants for several minutes; a delve party is four
members in a room. The same absolute buff is background noise in one and decisive in the other. The
10–15% figure is the owner pricing that difference, and a single global aura value would be wrong in at
least three of the four modes.

**It also resolves the Patron tension the earlier draft raised.** The draft argued the delve aura should
go *dormant*, citing `CreatureLawnDeployCommanderRefusalTests` and `RpgStore.Fusion.cs:504` (`return "sacrifice.is-patron";` — this cited `:354` until 2026-09-18, which is a `db.CreateCommand()` inside an unrelated atom-insert loop), which refuse
*"free lawn combat value on top of its aura"* for the Patron. The owner's answer is better than dormancy:
the aura is not free in a delve because it is **cut to a tenth**. A fighting commander is paying for its
own combat presence with a weakened aura, which is the same balance the Patron rule wants and keeps the
fantasy the dormant option threw away.

**Tunables this lands in:** a per-mode aura scale table. It is `aura-skill`'s file to own, not this
program's — this ruling records the shape (`lawn = reference`, `delve = 100–150‰ of it`); R-C5 fills in
the remaining two rows.

### R-C4 — duration XP applies to the lawn run only

**Ruled by the Q4 correction:** the commander fights in delve, siege and world assault, so it earns XP
there the way any fighting unique actor does. **Only the lawn run is non-combat**, and only there does
the commander draw the existing `specimen_lawn_duration` receipt without a matching
`specimen_lawn_kill`.

This needs **no new tunable and no new faucet**. A commander in a lawn run earns strictly less than a
creature that fought in the same run, automatically, because it draws one of the two terms instead of
both. The ratio is emergent from machinery that already ships, rather than a number somebody has to
guess — which also answers the prior-art tension: it is neither Persona 3/4's zero (the commander does
level) nor parity (it earns less than fighting), without a balance pass to set it.

---

### Prior art — what happens when a benched character earns nothing, and when it earns too much

The owner's mechanic sits between two well-documented poles.

- **No XP for the non-fighting member (Fire Emblem, Persona 3/4).** Fire Emblem treats experience as
  *"one of many resources the player is meant to manage"*, and sharing it *"would throw out a major
  aspect of the long term planning."* The documented cost is severe in Persona 3/4, which lack a share:
  *"you're basically forced to commit to a team whenever a new member joins … anyone you don't add to
  your squad by the end of the current dungeon/moon phase **may as well be dead for the rest of the
  game**."*
- **Full or near-full share (Persona 5, modern JRPGs).** Persona 5 added Exp Share precisely so players
  *"can swap out party members as needed for specific tough fights to have the right resistances or
  moves"* — rotation becomes possible.

**Both failure modes apply directly here, in opposite directions:**

1. **Zero commander XP recreates the Persona 3/4 trap.** A commander that earns nothing while commanding
   falls behind every creature that fights, so the player picks one commander forever and never rotates.
   The owner's ruling avoids this, and that is the reason to state, not merely the mechanic.
2. **Commander XP equal to combat XP inverts the game.** If standing outside the lawn pays what fighting
   pays, commanding becomes the optimal way to level *everything*, and the lawn — the first core loop —
   becomes a place you send creatures to avoid. A duration term that is not clearly *less* than the
   fighting term is a faucet that competes with the spine loop.

This is a ratio decision, not a yes/no one, which is why it is an open question below rather than a
recommendation.

Sources: [How Exp Share Has Evolved In Modern RPGs — GameSpot](https://www.gamespot.com/articles/how-exp-share-has-evolved-in-modern-rpgs/1100-6513761/) ·
[Experience — Fire Emblem Wiki](https://fireemblemwiki.org/wiki/Experience) ·
[RPG party EXP discussion — ResetEra](https://www.resetera.com/threads/thoughts-on-how-exp-xp-should-be-shared-among-rpg-parties-in-games.1395163/)

---

### What this adds to the shape

Extends §"The shape being proposed" rather than replacing it:

**6. The role is a binding, and the binding is what everything else keys on.** Something must mean "this
specimen holds the commander role, in this place, right now." Once that exists, the two canary comments
get their refusal branch, the duration receipt has a subject, and `PlayerEmpireCommanders.ForPlayer`
has a roster to read.

**7. Restrictions are role-scoped and place-scoped, never creature-scoped.** *"Never fights"* is enforced
where the role is held (lawn, siege, world assault) and absent where it is not (delve). A rule written on
the creature would make the delve case impossible, which is how this gets built wrong.

**8. The non-lawn XP receipt needs its own occurrence key.** `match_key` is a lawn concept. Siege and
world assault settle on the virtual-turn clock, so their idempotency key is turn-shaped. Reuse the
receipt *pattern* (`INSERT OR IGNORE` + re-read + assert same delta), never a second XP path — the
existing one already proves replay-safety and a parallel faucet would be the defect this program keeps
naming.

---

### R-C5 — siege and world assault run the aura at full lawn strength, tunable

**Ruled:** *"just make 100% life the lawn, tunable."*

The per-mode aura table is now fully specified:

| Mode | Aura scale | Set by |
|---|---|---|
| **Lawn run** | **100%** — the reference | R-C3 |
| **Siege** | **100%** | R-C5 |
| **World assault** | **100%** | R-C5 |
| **Delve** | **10–15%** | R-C3 |

**The delve is the outlier, and that is the point.** Three of the four modes are side-scale fights — a
lawn side, a siege force, an assaulting army — where a side-wide aura is one contribution among many. A
delve party is four members in a room, so the same buff is decisive rather than contributory. The table
prices that, and the shape to carry forward is *"delve is the exception; everything else is the lawn
value"*, not *"every mode gets its own hand-tuned number."*

**Tunable, not constant.** Every one of the four is a row in `aura-skill`'s per-mode table, including
the three at 100%. A mode pinned at the reference in code would be a balance number in a `const`, which
the repo bans outright (*"would a balance pass ever want to change this number?"* — yes, obviously). The
three 100% rows are a **starting value**, not an assertion that they are equal forever.

### R-C6 — a garrisoned idle commander earns nothing, and empire economy is not this program

**Ruled:** *"earn nothing, some commander have special equipment or passive tree to buff economic but we
just mention, that is empire building feature need to design, not this program cover."*

**A commander that is neither in a lawn run nor in a fight earns no XP.** No idle faucet, no
garrison stipend, no turn-clock trickle. This closes the last open question from R-C4 and it closes it
in the direction that adds nothing: XP comes from the lawn duration receipt or from fighting, and a
commander parked in a sector is doing neither.

Stated as the rule a downstream session needs: **there is no third XP source.** If a future feature
wants idle progression, that is a new faucet and needs its own justification — it does not get to arrive
as an unexamined side effect of garrisoning.

**Noted and explicitly out of scope: commanders that buff the empire's economy.** The owner named the
shape — *"some commander have special equipment or passive tree to buff economic"* — and immediately
scoped it out: it is **empire-building's** feature to design, not this program's.

Recorded here only so a later session knows the idea exists and does not re-derive it, and so nobody
mistakes R-C6's "earns nothing" for "a garrisoned commander does nothing." Those are different claims: a
garrisoned commander may well *contribute* to the empire; it just does not *level* from sitting there.

**What already exists for whoever picks that up, so it is not built twice:** `WonderEffectKind` already
reserves the exact shape — `EmpireBuff`, *"a buff reaching every sector/legion the faction owns.
`WorldFaction.ScopeModifierMilli` is the storage; each consumer is its own wiring task. **Refused by
`Validate` today**"* (`WonderCatalog.cs:60-62`). So the storage and the vocabulary entry exist and are
deliberately inert. A commander-sourced economy buff should contribute through that reserved kind rather
than inventing a parallel empire-modifier path — the same "do not ship a fourth neutral-constant weight
table" discipline this document applies elsewhere.

**This program's boundary, stated plainly:** `empire-progression` covers the commander's **identity**
(it is a unique actor carrying a role) and its **progression** (how it levels, where it deploys, what
its aura scale is per mode). It does **not** cover what a commander does to an empire's economy. That
line is drawn here so the next enrichment does not quietly cross it.

---

### Open questions — none remain for this section

All **six** were closed on 2026-09-17 (this said "five" while listing six until 2026-09-18): **R-C1** (exclusivity is the deployment hierarchy's, not a new
rule), **R-C2** (no commander-specific aura mechanic), **R-C3** (per-mode aura, delve 10–15%),
**R-C4** (fights everywhere but the lawn run; duration XP there only), **R-C5** (siege and world assault
at 100%, tunable) and **R-C6** (idle earns nothing; empire economy is out of scope).

**Answered by code, not by ruling — recorded so it is not re-asked.** *Does the commander role have its
own progression, or read the specimen's?* Both, and they already sum. `AllocationScope` is
`{ Commander, CreatureType, Aspect, UniqueCreature }` (`AptitudeAllocation.cs:8`) and an actor's
allocation is the **sum of all four scopes**, with `share` taken on the sum rather than per scope
(`decisions.md` Class system row: *"commander smallest, unique largest"*). A commander that is a unique
actor therefore carries its `UniqueCreature` pool **and** its `Commander` pool, and the existing fold
adds them. There is no second level on one creature — there are two allocation scopes on one creature,
which is the design that already ships.

**One amendment this section owes another document** (*done:* `creature-system-map.md:69-141` carries it). `creature-system-map.md`'s Axis 2 said the
Commander role *"never fights"* and scopes it to *"the lawn run"*. Both are now wrong: a commander
fights in delve, siege and world assault, and only the lawn run is non-combat. That text needs amending
when this graduates — it is a binding vocabulary the DESIGN-GATE points at, so leaving it stale would
mislead the next reader exactly as it would have misled this one.

---

## Owner rulings — 2026-09-17

Four of the eight open questions were ruled on 2026-09-17; one was closed by measurement; three remain
owned by other programs. Each ruling keeps the question it answered, because a ruling read without its
question is how a decision gets re-litigated.

### R-Q3 — auto-assign is a silent default the player can overwrite, with a free respec counter

> *Superseded in part by ruling R18 (2026-09-18):* the silent default stands (map D1). The **fixed free
> counter of 25** below does not: free respecs are earned per empire level, pay only the empire respec,
> and the player chooses each time; unique creatures and commanders always pay. See
> [spec-respec-free-counter.md](empire-progression/spec-respec-free-counter.md) and
> [spec-specimen-respec-price.md](empire-progression/spec-specimen-respec-price.md).

**Ruled:** default auto-assign, player may overwrite, and respec is **free for a tunable number of
times** before it starts costing souls. Free counter default **25**.

*The question was:* is the ladder a default the player can overwrite, or only an explicit button?

Both halves of the original tension are satisfied. General creatures are engine-spawned troop stacks
with nobody to click for them, so a never-silent default is the only thing that allocates them at all;
a unique actor's player can always disagree. The free counter is what keeps that disagreement cheap
early and priced later, so a default that turns out wrong is not a punishment.

**The pricing machinery already exists and must be reused, not rebuilt.**
`gk-core/data/tuning/species-build.v1.json` already ships `respecBasePrice 50`, `respecEscalationPermille 500`
and `respecDecayDays 3`, and `spec-species-respec.md` decision 15 already fixes the shape:
`price(count) = base + base * count * escalationPermille / 1000` — **linear, churn-priced, never
level-scaled**, because a geometric price against a flat soul faucet is how a price becomes a ceiling
(`AGENTS.md`: no hard progression ceilings). The free counter is one new key in that same file
(`respecFreeCount`, default 25), consumed before the first priced respec, and decaying on the same
`respecDecayDays` clock as the rest.

**A correction the counter depends on, verified in code rather than recalled.** The owner flagged
uncertainty about whether a player or commander level exists.

> ⚠️ **An earlier version of this section said "there is no commander kind and no commander level
> anywhere." That was wrong, and the owner caught it** — *"this really weird when we don't have
> commander, how legion work without commander?"* Commanders are a real, shipped subsystem
> (`gk-core/src/FusionRpg.Core/Commanders/`). The narrow true fact was about `RpgActorKinds` only, and stating it
> as "anywhere" would have sent a downstream session looking for a system that is already built. Corrected
> below.

**Commanders exist, and there are exactly two.** `CommanderId` is a closed enum — `Dave`, `Zomboss` —
fixed by owner decision 2026-08-30 (*"for now only have 2 of them for lawn run"*). They carry a stable
`commander:dave` / `commander:zomboss` id whose prefix is load-bearing: it is what keeps them from
colliding with `WorldFaction.FactionId` (bare `"dave"`/`"zomboss"`) and `BattleActorSetup.Key`
(`"squad:N"`), which share the same words in different id spaces.

**Legions work through them, and the link is the faction id.** A legion is a `WorldEntity` of
`WorldEntityKind.Legion` carrying an `OwnerFactionId`; `RaiseResolver.FoundLegion` stamps the raising
command's `CommanderId` into exactly that field, and even derives the entity id from it
(`e-{commanderId}-legion-{turn}-{sector}`). Its `Members` each carry their own `SpeciesId` / `Level` /
`Role`. So a legion is never commander-less — it is owned by a commander from the moment it is founded.

**The answer to the original uncertainty, and it is the interesting part:**

| claim | code |
|---|---|
| No player level *column* | **True.** `players` is `(id, name, created_utc, world_seed)` (`RpgStore.cs:198`), and `CharmPouchGate.PlayerLevelUnavailable` exists to document exactly that absence. |
| A player level exists anyway | **Yes** — a `kind="player"` row in `rpg_actor_progression`. `OnboardingEndpoints.cs:101` reads `player?.Level`; `OnboardingCheckpointEvaluator` gates rewards on `PlayerLevel >= 3` / `>= 4`. |
| A *separate* commander level | **No — and deliberately so.** `AllocationScope` includes `Commander`, and `CommanderIds.AllocationScopeKey` gives Dave the key **`player:{playerId}`** — byte-identical to the player's own scope key. The source says why in as many words: *"he IS the player's own commander — no new convention needed, no data migration for existing saves."* |

So the owner's memory was exactly right, and for a better reason than "the level was removed":
**commander Dave and the player are one identity by construction**, sharing one allocation scope key and
one `kind="player"` progression row. There is no second level because there is no second thing to level.

`RpgActorKinds` (`player`, `plant`, `zombie`, `species`, `specimen`) therefore has no `commander` member
and correctly should not gain one — adding one would fork Dave's identity in two. A free-respec counter
keyed to "first commander level" reads the `player`-kind row, and that is the same number either way.
*(Superseded by rulings R18/R19: free respecs are granted per **empire** level, a new `kind = 'empire'`
row, not read from the commander or player level.)*

**Zomboss is the asymmetry, and it is already open question 2** *(answered by rulings R1 and R3,
2026-09-18: his species levels live on his own empire of each save; his commander allocation is still
unowned, see the map's strengthen-pass gap and Q-S1)*. He gets a sibling allocation key
(`zomboss:{playerId}`) under the same scope and the same `LoadAllocation`/`SaveAllocation` mechanism, but
no progression row of his own — which is precisely the R1/Q2 attribution gap still listed as open below.
`PlayerEmpireCommanders.ForPlayer` returns Dave only; Zomboss is world/AI and is never listed as a
player-empire commander.

### R-Q6 — cap with tolerance, no floor

**Ruled:** assert a **maximum** share per lead, with tolerance. **No floor.**

*The question was:* what target LEAD distribution should the gate assert, given Onslaught at 42% and
four aptitudes under 1%?

**The owner's reason is the load-bearing part and must not be lost:** *"the problem is the pvz design,
if we have more strictly that become really weird when we force a lot of attacker become tanker or
support."*

That is correct, and it overrides the tidier symmetric band. PvZ's roster is genuinely attack-heavy —
the game ships hundreds of shooters and a handful of nuts. A floor would force the re-leading pass to
relabel shooters as tanks to satisfy a number, producing a corpus that is statistically balanced and
fictionally absurd. **A diversity metric that fights its source material is worse than no metric.**

So the gate is one-sided: nothing may dominate, but nothing is required to be common. Onslaught at 42%
fails; Ferocity at 0.2% does not. This deliberately rejects the Riot-style OP/UP band **for this axis
only** — the reasoning that a two-sided band catches homogenization in both directions still holds in
general, which is why the cap must be paired with the **shape histogram** (§"Measured"). The shape
histogram is what actually catches a pass that merely trades one dominant lead for another.

Left as a task rather than a question: the exact cap value and tolerance width. Both belong in
`gk-core/data/tuning/species-build.v1.json` beside `parityFloorPermille` / `parityCeilingPermille`, and that
file's own `_meta` already disclaims its band values as *"working values, not a validated balance
decision"* — so shipping a first guess is sanctioned; calling it balance is not.

### R-Q8 — key the lean per-species, not per-archetype

**Ruled:** replace population-crowding with a per-species signal.

*The question was:* does `crowdingFactor` 633 survive a re-leading pass?

Not in its current form. Today the lean is a pure function of *which aptitude is primary*, so the whole
904-species corpus carries exactly twelve lean values, and the crowding term runs backwards for
identity: the 378 species on the most crowded lead get the corpus' **flattest** build (350‰) while
Ferocity's two get its **sharpest** (599‰). The more typical a creature is, the less its build says
about it.

Keying the lean to the species itself fixes the inversion at its root, and is also what finally makes
the lean *vary* — twelve values across 904 species is the direct cause of the 21-shape convergence.
Candidate per-species signals, in order of how ready they are:

1. **The real base stats**, now that they exist. `type_base_stats` holds 911 rows of the game's own
   `maxHealth` / `attackDamage` / `cost` / `armor` / `summonLevel`. A creature with `attackBase 0` and
   `hpBase 4000` (WallNut) is not the same build object as one with `attackBase 20` (Peashooter), and
   nothing in the current pipeline can tell them apart.
2. **The threat rung**, which already spreads across all ten rungs.
3. **`Pure`**, which the anchor already authors and `SpeciesBuildPlanner` already reads.

All three are a tuning publish plus a planner change, not a rewrite. `crowdingFactor` stays in the file
as a value that may fall to 0 rather than being deleted, so the change stays revertible.

### R-Q5 — multiplicative with a zero-veto and a compensation factor, in the new scorer only

**Ruled by recommendation** (owner: *"what is best for smart AI? i don't good as this domain so you
suggest"*), so the reasoning is written out in full rather than asserted.

**Multiplicative is genuinely better for making an AI look smart, and the reason is specific.** An
additive scorer cannot express a hard disqualifier. You approximate one with a large negative weight,
and then enough small positives out-vote it — which is the mechanism behind most visibly stupid game
AI: six mild positives beating one "cannot actually reach the target" penalty. A multiplicative scorer
with a zero-veto cannot make that mistake, because any consideration returning 0 kills the option
outright; it also short-circuits, so it is cheaper.

**Its known failure mode is real and must be handled up front, not discovered later.** Multiplying N
values in [0,1] drives every score toward 0 as N grows, and biases against exactly the options with the
most considerations attached — the well-modelled ones. The standard fix is Dave Mark's **compensation
factor**: `modification = (1 - 1/N) * (1 - score); final = score + (modification * score)`, or
equivalently the geometric mean `score^(1/N)`. Choosing multiplicative without this is the trap;
choosing it with this is fine.

**Scope, and why this is not a SOLID violation.** The repo is additive twice already (`ValueMap`,
`SiegeAi`), and `CLAUDE.md` forbids forking a parallel path for the same numbers. This does not fork
one: `ValueMap` scores *strategic locations*, `SiegeAi` scores *siege targets*, and a build scorer would
score *stat allocations*. Three different questions, so three scorers is not the ActorHub dual-compose
defect — that defect was two engines answering the **same** question. **Migrate nothing.** The existing
additive scorers stay additive; only the new build scorer is multiplicative, and if it is never built
this ruling costs nothing.

The deferral option was rejected deliberately. `Consideration.cs:23` says the scorer waits on an
economy, but the compensation-factor problem is exactly the kind of thing discovered after a scorer
ships and then never fixed properly.

---

## Still open — and who owns each

1. ~~**Does a species level feed `Θ`, or a channel, or neither?**~~ (Q1/R2.) **✅ CLOSED 2026-09-17 by
   `species-progression-ideal.md` R-S1: it grants ALLOCATION**, the same aptitude-shaped points over the
   same share weights a specimen gets, through `SpeciesAllocationSource`. Neither a raw `Θ` feed nor a
   private channel — allocation, which the existing fold already reads.

   **This unblocks the rest of this document.** The whole assignment layer was downstream of this, because
   until a species level changed *something*, shares were scale-free and both human and AI assignment were
   cosmetic. They are not any more.

   The ruling also retired the objection this question carried. It was written fearing that specimen-shaped
   species progression *"weakens the 2a/2b distinction"*; the owner's answer is that **2a and 2b differ in
   SCOPE, never in KIND** — same points, same weights, different owning row. What separates a unique
   creature from a general one is **equipment, then title, then later layers**, in that order:
   *"if unique unit have no equipment, is literally a general unit with same level and same stats/passive
   skill distribution."* That is the test for any proposed fourth difference — if it is not a layer above
   the shared progression, it does not belong.
2. ~~**Should zombie species XP credit Zomboss instead of the human?**~~ **✅ ANSWERED 2026-09-18 by ruling
   R1: yes, Zomboss's empire** (keyed per save, ruling R3; built by `ai-empire-species`). Original text: (Q2/R1.) **An economy decision**,
   the same shape as the `SR-18` ruling already given. Today `normalzombie` levels to 62 on the player's
   row while the empire that should own it has zero rows.
3. **What coverage does the tree favour corpus need before tree auto-assign is worth building?** (Q4.)
   1/904 today against aptitude's 904/904. **A scope decision for the tree generator**, not this
   program's.
4. ~~**Should a high threat rung change a species' build SHAPE, or only its `Θ`?**~~ **✅ ANSWERED 2026-09-18 by
   ruling R6: yes, it sharpens the build** (`per-species-lean`, weight 0 until a publish). Original text: (Q7a.) Still open, and
   it pairs with R-Q8 — answer them together. The item ladder's collapsing envelope
   (`IlvlTierLadder.Envelope`) is the precedent: a rung may narrow the legal window without ever
   excluding the bottom, which would let a `calamity` specialise while a `nuisance` stays generalist.

### Closed by measurement, not by ruling

**Q7(b) — "447 of 904 species carry no `combat.power.omni`."** That gap existed because the bake had
nothing real to derive power from: the only stat capture path read fields off a live spawned entity, so
64 of 677 plants and 18 of 227 zombies had observed stats, and plant armour had been captured zero
times. As of 2026-09-17 `type_base_stats` holds **911 rows** of the game's own static tables, swept by
`GameHooks.EnqueueBaseStats`. The input now exists, so this is no longer a question — it is a
regeneration task owned by `species-flavour-lawn`.

It also moved the target. Measured plant `hpBase` spans **300 to 640,000** against the shipped bake's
480 to 46,080, so the current ladder is roughly **22× too compressed** — a larger problem than the
coverage gap it replaces.

---

## What a downstream session must not do

- **Do not build a second progression system.** The layer stack is a closed vocabulary — open to
  extension by reviewed registry entry, closed to invention. 2a and 2b already exist and are already
  mutually exclusive per actor.
- **Do not call a model at runtime.** Not for cost, and more importantly not for determinism: world
  turns are seeded and replayable, and LLM inference is non-reproducible even at temperature 0 because
  batch size varies with server load.
- **Do not write a new `f(level)`.** `ssot-power-scale.md` §10 is closed.
- **Do not ship a fourth neutral-constant weight table.** If the content cannot be authored, say so and
  do not ship the mechanism claiming it works — `action-role-lean`, `INeedVector` and `ai.aggression`
  are three existing instances of exactly that.
- **Do not make the recommended build mandatory.** *"You are not a class."*
- **Do not hand-edit a generated corpus.** `_species-build-plan.json` is `CreatureBuildPlanGen`'s output
  and CI byte-compares it; a fix belongs in the generator or its tuning.
- **Do not add a `commander` member to `RpgActorKinds`, and do not encode a roster as an enum.**
  `CommanderIds.AllocationScopeKey` already makes Dave and the player one identity (`player:{playerId}`),
  so a commander actor kind forks that identity in two. And a roster is a **population**, not a closed
  vocabulary — pinning its cardinality in a type is the exact defect this program adopted
  (§"The commander identity defect"). `WorldEntityMemberRole` growing a third member is the opposite
  case and is correct: that enum is a vocabulary the code owns.

---

## Hand-off

Written to `docs/architecture/empire-progression-ideal.md`. This is the idea phase and it stops here —
no spec, no plan, no code.

**Adopted 2026-09-17:** the commander identity defect is now a task in this program
(§"The commander identity defect"), on the owner's ruling that it violates SOLID. Its diagnosis lives in
[`../research/commander-identity-drift-2026-09-17.md`](../research/commander-identity-drift-2026-09-17.md)
and is not repeated in a spec.

**Next step:** `/spec` for a capability map plus module specs, **once open questions 1 and 2 are
answered**, because everything else in this document is downstream of them. Q1 in particular is a hard
prerequisite: assignment cannot matter while a level-4 species composes identically to a level-1 one.

Three findings in here are actionable immediately and independently of any of that, and are the
cheapest real wins available:

- **W3** — `species-favour` refuses all 904 species by demanding 12 keys the corpus intentionally never
  carries; the spec only mandates refusing *empty*. Zero-fill, matching the sibling path.
- **W2** — nothing emits `aptitude.autoAssign`; the whole FE feature is unreachable.
- **R1** — the AI empire owns no progression at all, while the human accrues it.
