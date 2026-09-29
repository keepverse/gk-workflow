# Gear climb — the ideal

**Status:** idea phase, 2026-09-13 — **but the subject shipped, and this header did not notice.**

> ⚠️ **Corrected 2026-09-18.** This line read *"Not a spec. No build authorized."* through two
> enrichment passes (2026-09-17 and 2026-09-18) while the feature was already built:
> `docs/architecture/species-gear-chain/spec-craft-risk-ladder.md` is the spec, and
> `gk-core/src/FusionRpg.Core/Items/Materials/CraftRiskPolicy.cs`, `HeadDerivationTables.cs` and
> `RpgStore.Items.cs:843` shipped in `f67930ace` on 2026-09-16. **R-G1 was therefore recorded against
> a document whose subject had already been built** — which is how three of its claims below ended up
> describing a design instead of the code. Read this document for its reasoning, never for its status
> or its inventory.

> **Updated 2026-09-17.** **R-G1 landed 2026-09-17**: one durability pool, one unit, **two** damage formulas — plus a boss-farmed consumable layer giving a route to 100% craft success.
>
> **Updated 2026-09-18 — R10:** the consumable *protect* never covers a repair's destroy chance; that chance
> stands as the durability sink (§ R-G1, end). The consumable layer is specced as `craft-assurance`.

**Program:** `gear-climb`. Map (when approved) → `docs/architecture/gear-climb-map.md`. **This does not
create a new program in the sense `gameplay-tiers-ideal.md:156` closed** — both verbs below are already
owned by the **item** program (module 15 `enhance-reroll` owns promotion; module 14 `salvage-craft` owns the
cost vocabulary). This doc is the reasoning trail for two verbs the item program declared and never
specified; it graduates as an amendment to those modules, not as a rival to them.

**Origin:** `tier-system-ideal.md` § DISPOSITION deferred these as E5/E6. The owner challenged the
deferral — *"i don't see any reason to defer them if they don't need a larger program"* — and re-sizing
against code proved the challenge right. Neither needs a larger program. One of them is nearly built.

---

## Which loop this extends

**Spine C — item collection and progression** (`the-loops.md`): *"find, vault, equip, compare, craft,
socket, salvage."* This is the **craft** verb, and specifically the half that has never worked: an item you
already own getting better. No new loop, no fourth stock, no new named clock.

---

## Load-bearing principles, restated inline

A downstream session reads this doc, not its links.

- **Every RPG feature lives in the RPG layer — never by changing what PvZ is.** Promotion and upgrade
  resolve entirely in `FusionRpg.Core` / `FusionRpg.Data`. No PvZ field, spawn or board is touched.
- **Rarity never touches a magnitude** (`ssot-rarity.md` §3.6). A rung sets a **count band and a tier
  window** — nothing else. `CurveInput.Rarity` is banned on item containers, and a promotion that made
  rarity multiplicative would destroy the measured overlap the ladder is built on.
- **One power ladder.** A promotion **cost curve** is power-shaped, so it owes a `ssot-power-scale.md` §10
  row (rows 6, 26, 27, 31, 33 are the precedent for cost ladders). It is never a private `f(rung)`.
- **The balance surface is data.** Every cost and chance lives in `gk-core/data/tuning/`, carries its unit, and a
  missing value is a load rejection naming it — never a silent default.
- **No hard progression ceilings.** A promotion cost curve is a configurable soft cap. The owner already
  lifted the old drop-only ceiling: *"promotion reaches ordinal 100, no drop-only band exists on any
  axis"* (`spec-enhance-reroll.md:110-112`).
- **Gameless-first.** Both verbs work with Fusion closed; neither is enriched or gated by the injector.
- **Determinism.** An instance's state is `origin seed + catalog_revision + an ordered, recorded list of
  operations`. Every climb step appends one entry to that transcript; nothing is re-simulated.

---

## What this is

In the player's language: **the gear you already like should be able to get better, in two different ways.**
The first is a *promotion* — you push a piece one rung up the rarity ladder, and it gains an affix without
disturbing the ones it already has. The second is an *upgrade* — you take a piece to the bench and it
becomes the next thing in its line, a heavier chassis of the same kind.

They are deliberately different promises. A promotion says *"this exact object, improved."* An upgrade says
*"this object, replaced by its successor."* Today the game offers neither, and a player who finds something
they love has no way to invest in it at all.

---

## What already exists

Verified against code 2026-09-13. **Counts are readings of today's corpus, not constants.**

### Built

**The promotion operation is specified in full, and the spec is old.** `ssot-rarity.md` §3.7 carries seven
legality rules: upward only (`RarityDemotion` otherwise); **one rung per operation**; **existing affixes are
never re-rolled and never re-tiered — promotion only adds**; new affixes roll in the new rung's window ∩ the
item's **recorded** `tier_ceiling` (*"an item does not get stronger because the player got stronger"*); the
count target is the new rung's **band floor**; a promoted item is **marked** (`promoted_from_ordinal`); and
the old drop-only ceiling has since been lifted to all ten rungs.

**It is priced and its content is authored.** `CraftOperation.Elevate` exists
(`CostClassMatrix.cs:33-34`, *"Promote an item's rarity rung. Owned by module 15"*); `materials.v1.json`
prices all ten verbs including elevate (souls `60 × rung`, substrate, shard, `catalyst.temper`); and the
shipped recipe corpus carries **10 authored `elevate` rows**, all `outputKind: "mutation"` with no
`outputRef` — correctly modelled as an in-place mutation.

**Its consumer is already registered.** `RarityBudgetKeys.cs:32` names `"enhance-reroll (15)"` as the
consumer of the `promote_from` budget key, and `RpgStore.Items.cs:946` already writes that key for every
rung via `RarityLadder.PromoteFrom` (`:24`, a stub returning a constant `1` — *"no rung is drop-only. All
ten promote from a lower rung"*).

**Its measured balance already exists.** `ssot-rarity.md` §7.2 simulated it: a Cultivated promoted to Fused
averages **59% of a naturally-found Fused**, and `P(promoted beats natural) = 19.8%`. Promotion is worth
doing (+21% on the item, and it moves the label) without replacing the hunt — *found beats crafted*, with a
number behind it. The `promoted_from_ordinal` mark is what explains the gap to the player instead of hiding
it.

**The mutation substrate is real.** `MutationOpKind` is a closed 10-member namespace with an ordered
`op_seq` transcript and replay-as-transcript semantics (`ssot-enhancement.md` §3.2). `ItemWorkbench`
dispatches five craft verbs through `TryRecipe` with a uniform shape, and `WorkbenchEndpoints` maps six
POSTs — so both the executor and the route have a working pattern to copy, not invent.

### Wiring gap

*Machinery exists and is inert. Each names its line.*

- **`Elevate` has no `op_kind`, so it cannot be persisted at all.** `MutationOpKind` (`MutationOp.cs:13-48`)
  has ten members and none is a rarity promotion; `RpgStore.AppendInstanceOp` takes a `MutationOpKind`.
  This is the single blocking line.
- **`ssot-enhancement.md` §5.3's reserved `op_kind` table has no elevate row.** Its seven reserved entries
  cover enhance / transfer / restore / reroll / socket. *"Adding a value is a reviewed change against this
  document"* — so E6 owes a reviewed amendment. **A conversation, not a program.**
- **No executor and no route.** `ItemWorkbench` has no `Elevate` arm; `WorkbenchEndpoints` maps no elevate
  POST. The 10 authored recipes are therefore unreachable — a POST against one refuses
  `material.operation-mismatch`.
- **It is absent from the UI entirely.** The web `UNAVAILABLE_VERBS` list names Forge, Reroll and Transfer;
  **Elevate is not even listed as unavailable.**
- ⚠ **Contention:** `Repair` is already queued for the same closed-at-ten enum by
  `deployment-hierarchy/spec-item-durability-repair.md:107`, **and that program filed it against the item
  program**. Two verbs want the eleventh and twelfth slots. Both can land; the filing order should be
  honoured.

### Real gap

*No mechanism exists anywhere.*

- **An item cannot be an input to making an item.** A recipe's only inputs are
  `AuthoredCostLine(MaterialId, CostBand)`, and `CostClassMatrix.Allows` is a switch over the five material
  classes that **throws on anything else**. An item id in a cost line is refused at import.
- **There is no consume-and-replace `output_kind`.** All 67 shipped recipes are
  `outputKind ∈ {container, material, mutation}`.
- **No successor edge exists in the corpus.** All 1,042 item seed files were parsed and all 3,363 distinct
  keys collected: **zero** `upgradeTo` / `evolvesTo` / `successor` / `nextTier` / `consumes`.
- **The closest thing to an item chain is ordering only.** The class ladder (`classes.v3.json`) declares
  armour `cloth→leather→scale→plate` and `fibre→husk→bark→heartwood` — **4 rungs for armour only** (weapon
  3, offhand 2, jewel 3, standard 2) — but no field, recipe or code links `cloth` to `leather`, and the
  registry's `rung` integers are read by no C# item code.
- **The creature side already ships the shape the item side lacks:**
  `CreatureRecipeDef(RecipeId, OutputSpeciesId, InputSpeciesIdA, InputSpeciesIdB)`. The item program has no
  analogue of `InputSpeciesIdA`.

---

## Prior art

Numbers and documented failure modes, with sources. Several pages hard-block automated fetch
(`poewiki.net`, `pathofexile.fandom.com`, `icy-veins.com`, `wowhead.com`); anything unverified says so.

### Promotion — PoE's Regal Orb is a near-exact analogue

GGG's own item text, quoted in an [official forum thread](https://www.pathofexile.com/forum/view-thread/3756304):
> *"Upgrades a Magic item to a Rare item, adding 1 modifier. **Current modifiers are retained and a new one
> is added**."*

That is `ssot-rarity.md` §3.7's rules 3 and 5 already shipped by someone else. The wider currency chain
([Craft of Exile](https://www.craftofexile.com/basics)) separates the two behaviours cleanly: **Regal**,
**Augmentation** and **Exalted** *keep* existing mods and add one; **Alteration** and **Chaos** destroy all
of them; **Divine** rerolls numeric values only and **does not change mod tier**. Rarity-destroying and
rarity-preserving are different verbs with different names — a discipline worth copying.

⚠ **The documented failure mode is legibility, and it is exactly our risk.** The same thread records a
player filing a *bug report* because a 1-affix Magic item regaled into a 2-affix "Rare". The resolution:
**rarity is a maximum affix capacity, not a minimum** — community-corrected, with no GGG staff reply. On a
**ten-rung** ladder this confusion is ten times more available than on PoE's four, which is what
`promoted_from_ordinal` exists to answer.

⚠ **Our 59% figure has no prior-art analogue.** No first-party "an upgraded item is worse than a found one"
statement was found. The adjacent documented reasoning is about *mod-pool dilution* at high ilvl
([Steam, player-reported](https://steamcommunity.com/app/238960/discussions/0/1642041886376991096)), not
about tier-window lock-in. **Treat §7.2's 59% as our own measurement, not as genre practice.**

### Failure — D4's Tempering is the documented case against bricking

Temper Manuals grant **up to 2** tempered affixes, with **5 rerolls maximum, shared across both slots**; at
zero the item is permanently un-temperable — "bricked"
([Windows Central](https://www.windowscentral.com/gaming/diablo-4-tempering-guide),
[Dexerto](https://www.dexerto.com/diablo/diablo-4-season-8-crafting-change-fixes-the-worst-part-of-upgrading-3161220/)).
**Bricking is not destruction** — the item keeps its affixes and simply can no longer improve.

The stated crux of the rejection (player-reported,
[Blizzard EU](https://eu.forums.blizzard.com/en/d4/t/tempering-durability-feedback/14914),
[Blizzard US](https://us.forums.blizzard.com/en/d4/t/i-really-want-tempering-to-no-longer-brick-items-in-season-4/167825))
is **not the gamble** — it is pairing a **finite, non-refundable attempt budget** with an item players
describe as a *"once-in-a-season event."* **Blizzard never removed bricking**; it shipped mitigations only
(the Scroll of Retempering, and Season 8 recipe memory to cut misclick bricks).

### The alternative — Last Epoch's depleting budget

Forging Potential **rolls from area level + rarity + a random roll**, so it genuinely differs by rarity
(Exalted > Rare > Magic > Common); per-craft cost scales with the affix tier being touched, with a worked
example spanning **1 to 18**, and it is **zero** on a Critical Success
([Maxroll](https://maxroll.gg/last-epoch/resources/beginner-crafting-guide)). At 0 FP *"no more crafting can
be done to the item"* — **the item remains fully usable; no destruction, no stat loss.** LE's own
rarity-jump verb is the **Rune of Ascendance** (consumes a Common/Magic/Rare with ≥1 FP → a unique).
⚠ **UNVERIFIED:** no first-party EHG statement on *why* depletion was chosen over a fail chance.

### Item A → item B — two documented failure modes, both sharp

- **PoE Blessing orbs** do exactly this — the item gains a new name and may change base — **but every mod
  is rerolled, implicits and explicits, even when the new mod is identical.** Quality, sockets and socket
  colours survive; your rolls do not ([vhpg](http://www.vhpg.com/breach-blessing/); the wiki page itself is
  fetch-blocked).
- **D2's Horadric Cube base upgrade** (Normal→Exceptional→Elite, a unique keeping its properties) carries
  the two failure modes worth stealing:
  1. **Requirement creep turns an upgrade into a downgrade.** Level requirement **+5** (Normal→Exc) and
     **+7** (Exc→Elite), with Str/Dex jumping to the new base. The canonical player-reported case is an
     upgraded Peasant Crown whose strength requirement *"becomes far too high, negating its usefulness for
     casters"* ([PureDiablo forums](https://www.purediablo.com/forums/threads/concern-re-strength-requirements-for-some-of-the-elite-unique-items.173173/)).
  2. **Naming confusion, documented so explicitly the wiki must warn about it:** *"Greyform will **not**
     become The Spirit Shroud"* — it becomes a Ghost Armor carrying Greyform's properties
     ([Maxroll](https://maxroll.gg/d2/resources/horadric-cube-recipes)). **Players expect A→B to mean "becomes
     the higher-tier named item."** Ours must decide what the upgraded item is *called* before it ships.

### The pattern nobody should ignore

WoW's item upgrading is the most-iterated version of this mechanic in the genre, and it was **added and
removed four times**: introduced 5.1.0 (Rare 1,500 JP → +8 ilvl), **retired in 5.2.0**, returned 5.3.0 at
half cost, re-currencied in 6.0.2, **removed entirely in 7.0.3**, absent through Legion and BfA, returned
9.0.5, killed again in Dragonflight S2 ([Warcraft Wiki](https://warcraft.wiki.gg/wiki/Item_upgrading)).
**No Blizzard rationale statement surfaced in any source.** The shape is the warning: an upgrade verb that
is *only* a number tends not to survive contact with a rebalance.

---

## The shape

**Two verbs, built in order, sharing nothing but the transcript.**

### 1. Promotion (E6) — build the spec that already exists

This is not a design problem. `ssot-rarity.md` §3.7 is a complete operation spec, its balance is measured
(§7.2), its cost is priced, and ten recipes are authored. The work is:

- **One reviewed amendment** adding an elevate row to `ssot-enhancement.md` §5.3's reserved `op_kind` table,
  filed on the item program alongside `Repair`, whose filing came first.
- **One `MutationOpKind` member**, so the operation can be persisted at all.
- **One executor + one POST**, copying the five-verb `ItemWorkbench` / `WorkbenchEndpoints` pattern.
- **The `promoted_from_ordinal` mark surfaced on the item card** — this is the answer to PoE's documented
  regal-confusion bug report, and on a ten-rung ladder it matters more than it did on four.

### ⭐ Failure shape — DECIDED 2026-09-13: one graduated risk ladder, not a per-verb chance

**Owner:** *"make SSOT promote risk… potential is the default assurance for each item, but if it exhausted
→ cause item durability decay and can break and lost."*

Neither of the two options offered survives alone; the decision **synthesises them into a single ladder
that no craft verb owns privately**:

| Stage | What the player sees | Mechanism |
|---|---|---|
| **1. Assured** | Crafts simply work | Each item carries **crafting potential**. While it remains, a craft spends materials and **always succeeds** — Last Epoch's model, and the answer to D4's documented bricking rejection |
| **2. Strained** | "This piece is wearing out" | Potential exhausted. Crafting is still *allowed*, but each attempt now **decays durability** — a visible, accumulating cost rather than a hidden dice roll |
| **3. Broken** | The item stops working, but is still yours | Durability at zero ⇒ **unusable until repaired, never destroyed by wear** |
| **4. Lost** | The repair failed | The **repair attempt** carries the tunable destruction chance that `spec-item-durability-repair.md` already specifies |

**Why this is the right shape, and why it needed checking against a locked anchor.**
`deployment-hierarchy/spec-item-durability-repair.md` **D1 is a locked anchor**: *"An item at zero
durability is unusable until repaired (**never destroyed by wear alone**)"* — only a **repair attempt** may
destroy. The owner's chain (exhausted potential → decay → break → loss) is therefore **compatible with D1
without amending it**, provided the decay never destroys directly. It doesn't: it drives the item to zero,
and the loss — if it happens at all — occurs at the already-specced repair step, which **already has its
persistence**, the closed four-value `rpg_item.Disposition` vocabulary
(`owned | salvaged | transferred | destroyed`, `RpgStore.ItemUniques.cs:71-73`).

**So this adds no new destruction mechanism.** It adds one new *decay source* beside battle wear, and
routes everything else through paths that already exist.

**What it buys over either option alone:**
- **The player always sees it coming.** D4's rejected mechanic was an RNG brick on a finite, invisible
  attempt budget applied to a *"once-in-a-season"* item. Here the budget is visible, its exhaustion is
  announced by a state change, and the destructive step is a *separate, opt-in* action.
- **Risk becomes a property of the item, not of the verb.** One ladder serves promotion, temper, reroll and
  socket work — so we never answer "does *this* verb brick?" eleven times, and enhancement's three risk
  bands (`spec-enhance-reroll.md` §4) can eventually be reconciled into it rather than sitting parallel.
- **It keeps §3.7 honest.** Promotion stays *additive only* — nothing is re-rolled, so nothing is ruined by
  the craft itself. What degrades is the chassis, which is a different axis.

⚠ **Cross-program consequences, stated rather than discovered:** crafting potential is a **new per-instance
column** alongside durability's `(max, current)`, and its exhaustion is a **new decay source** the
durability module must admit — both are asks against `deployment-hierarchy` module 7, which is
**owner-locked (D1–D6) and written against shipped code**, not idea-phase. Whether potential is derived
(like durability's `max`) or authored is an open question below.

### 2. Upgrade (E5) — the smaller half of a schema change, done honestly

Needs an item-typed cost line, a consume-and-replace `output_kind`, and a successor edge. The class ladder
is the natural spine (`cloth→leather→scale→plate`), and it already exists as ordering. Two rules, both taken
straight from the prior art:

- **Do not reroll on upgrade.** PoE's Blessing orbs reroll everything and that is the documented complaint.
  Ours carries affixes across, exactly as promotion does.
- **Do not claim to be the named successor.** D2 had to put a wiki warning on this. An upgraded `cloth`
  piece becomes a `leather` chassis *carrying its own identity*, and the card must say so.

**And watch requirement creep.** D2's upgrade-becomes-downgrade is a live risk here, because
`requirement-profiles` (item module 23) exists — an upgrade that raises a requirement past what the owner
can meet is a downgrade wearing a better name.

### Alternatives rejected, with reasons

- **A bare failure chance on promotion** (option 2 alone). Rejected on D4's documented evidence — players
  rejected a finite, non-refundable budget on an irreplaceable item, and Blizzard never removed it, only
  papered over it with the Scroll of Retempering.
- **Potential with a hard stop and no consequence** (option 1 / plain Last Epoch). Rejected as *incomplete*
  rather than wrong: at zero FP LE simply ends craftability, which is safe but toothless for a game that
  wants gear to feel mortal. The decided ladder keeps LE's assurance and gives exhaustion a consequence.
- **A per-verb risk setting.** Rejected: eleven verbs each answering "do I brick?" is eleven balance
  surfaces and eleven player explanations. Risk is a property of the **item**, and lives in one ladder.
- **Letting promotion re-roll or re-tier existing affixes.** Rejected by `ssot-rarity.md` §3.7 rule 3 and by
  PoE's own Alteration/Chaos-vs-Regal split. Rerolling is I7's separate verb.
- **Making the upgraded item literally become the named higher item.** Rejected on D2's documented
  confusion.
- **Rarity as a magnitude multiplier** so promotion "feels bigger." Rejected by `ssot-rarity.md` §3.6 —
  it destroys the measured overlap, and `CurveInput.Rarity` is already banned on item containers.

---

## Tunables

Every number this introduces, its unit, and the file that owns it. Nothing here is a `const`.

| Number | Meaning | Owner |
|---|---|---|
| `promoteCostSoulsMilli` per rung + the material legs | The climb's price. **A cost ladder, so it owes a `ssot-power-scale.md` §10 row** (rows 6/26/27/31/33 are precedent; row 18 shows an authored per-rung table still earns one) | `gk-core/data/tuning/materials.v1.json` `operations.elevate` (already priced — confirm rather than re-author) |
| `upgradeCostSoulsMilli` per class rung | E5's price, same shape | Same file, new verb |
| Whether a rung's promotion is enabled at all (`promote_from`) | Already a per-rung registry key with a named consumer; **1 on all ten rungs today** | `rarity_budget` via `RarityBudgetKeys` |
| Class-ladder successor edges | Which chassis upgrades into which | `data/seed/items/_registry/classes.v{n}.json` — **authored content, not a formula** |

**Structural (stays `const`, with a comment):** the one-rung-per-operation rule and the additive-only rule
are §3.7 legality, not balance — they are the contract, and a tunable that could relax them would be a
different feature.

---

## What this deliberately does not decide

- **The cost values themselves** — balance data, owed to a spec and a pass against real play.
- **Whether `Repair` or `Elevate` takes the eleventh `op_kind` slot first** — a filing-order question, and
  `deployment-hierarchy` filed first.
- **What an upgraded item is named** — named as the decision E5 must make before it ships, not made here.
- **Whether E5 rides the class ladder or a new successor field** — the class ladder is the natural spine,
  but it is currently read by no C# code, so adopting it is itself work.
- **Anything about `+X` enhancement, reroll or transfer** — module 15 owns those and they are a different
  promise.
- **Any FE surface beyond the `promoted_from_ordinal` mark** — `item-surfaces` (module 20) owns the card.

---

## Open questions

Owner decisions only. Each is answerable; a recommendation nobody disputes is recorded as a decision.

**Decided 2026-09-13:** the failure shape is the **graduated potential → durability → repair ladder** above
(owner), and **both climbs ship**, with E5 graduating to its own spec.

Still open:

**Decided 2026-09-13 (owner):**

**Potential is DERIVED, with an authored per-base-type override.** The derivation mirrors durability's
`max` — a load-time table over the closed VALIDATED registry fields `class`/`rarity`/`tags`
(`spec-item-durability-repair.md` §2) — so the common case needs no authoring and cannot drift.

> ⚠️ **What shipped reads two fields, not three (verified 2026-09-18).**
> `HeadDerivationTables.cs:37-46,66-75` consults `entry.Class` and `rungId` only — **`tags` is never
> read.** Open question 1 below records this as "DECIDED — the same three"; the build chose the
> subset, and the subset is the truth. An override
exists for chassis a designer wants to treat specially.

⚠ **Two sources of truth is the known hazard here, so the rule is stated rather than assumed:** the
override is **explicit or absent**, never a sentinel. An absent override means *derive*, and a present one
must be a real authored value — a missing-but-expected override is a **load rejection naming the base
type** (`tunables-ssot.md` T5), never a silent fallback. The derivation stays the default path, and the
override is the exception that has to justify itself.

**Enhancement's risk bands fold into the ladder — one risk vocabulary, not two.**
`spec-enhance-reroll.md` §4's Safe/Risk bands (+1..+8 at 1000‰, +9..+14 at 950‰→600‰) predate the
potential→durability decision and were proposed here as **superseded by it**.

> ⚠️ **Overturned — the ask was filed, and answered "no", two days before R-G1 was written
> (found 2026-09-18).** `item-map.md:333`, *"Filed decision 2026-09-15 — ask #4"*: **"The Safe/Risk
> bands stay."** Its reasoning is that the two own exhaustively different things — *"the bands roll an
> attempt's success; the ladder governs refusal and continuation"* — and *"if module 15 later
> supersedes the bands, the ladder needs no change: it never read them."* So there is **one risk
> vocabulary per question**, not one overall: • *did this attempt succeed?* → the bands.
> • *may this craft proceed, and at what cost?* → the ladder. The paragraph below correctly insisted
> the ask *"must be filed, not assumed"*. It was filed. Nobody re-read the answer. A player faces one mechanic, and the repo keeps
one balance surface, for the question *"can this craft hurt my item?"*

⚠ **This is a cross-program ask and must be filed, not assumed.** It reopens a written design inside
**item module 15 `enhance-reroll`**, which owns §4. Per this repo's convention the ask belongs in the
owning program's map (`item-map.md`, the way `deployment-hierarchy-map.md:89` filed its own), not only
here. Note module 15 is already carrying two other queued asks — `Repair`'s `op_kind`, and now `Elevate`'s.

### Still open

1. ✅ **DECIDED 2026-09-13** (stated in this section's own body above: potential is DERIVED from the
   closed `class`/`rarity`/`tags` registry fields, with an explicit-or-absent authored override).
   Original: **What derives potential, exactly?** The durability precedent uses `class`/`rarity`/`tags`; whether
   potential reads the same three or a subset is a table-shape decision for the spec.
2. ~~**How much durability does one craft past exhaustion cost?**~~ **✅ RULED 2026-09-17 — see R-G1.**
   The structural answer is **one pool, one unit, two formulas**: combat and crafting draw the same
   durability in the same per-mille unit, but get separate tuning tables, because *"you cannot calculate
   damage on the item same at a attack hit and a craft time."* This question conflated sharing a *unit*
   with sharing a *formula*; R-G1 separates them. The number itself is still balance data owed to a
   measured pass, and R-G1 adds a consumable layer (boss-farmed repair / protect / success-chance items)
   that must be tuned **together** with the craft-wear table, not after it.
3. ✅ **DECIDED 2026-09-13 — the class ladder**, with the caveat this entry already carries: it is read
   by no C# item code today, so "reuse" is not free. Original:
   **Is the class ladder the successor spine for E5, or a new field?** Recommendation: the class ladder —
   but note it is read by no C# item code today, so "reuse" is not free.
4. *(Answered above — the bands fold in.)*

---

## Owner rulings — 2026-09-17

### R-G1 — one durability pool, two damage formulas, and a consumable path to guaranteed success

**Owner:** *"one durability data but 2 damage level … you cannot calculate damage on the item same at a
attack hit and a craft time. they only share same durability, so we should have 2 formula/tunable tables
for 2 different damage mechanism … i want to use some craft system that craft have cost of break, but
user can use special consumable item that can farm on boss to repair, protect damage or increase success
chance. so basically user can 100% success rate if they have enough item. they have choice gamble with
risk and assurance (damage/durability system) and 100% success with more time effort to farming."*

The owner asked to be corrected if the option they picked did not match what they described. **It did
not, and the description is the better design — so the description is what is ruled.**

**The correction.** The option offered was *escalating per-mille* (each craft past exhaustion costs more
than the last), and it was framed against the recommendation as if the choice were *"share battle wear's
unit"* versus *"have your own curve."* That framing was a false dichotomy. What the owner described is:

| | Ruled |
|---|---|
| **Pool** | **One.** Combat and crafting draw the same durability. The player tracks one number. |
| **Unit** | **One** — per-mille of `max`, matching `spec-item-durability-repair.md` §3, so the two sources stay directly comparable. |
| **Formula** | **Two.** Battle wear and craft wear are different mechanisms with different inputs and get their own tuning tables. |

Sharing a **unit** and sharing a **formula** are different commitments, and the original question
conflated them. The owner's reasoning is correct on the substance: battle wear is driven by hits taken
over a fight, craft wear by how far past exhaustion a player chose to push — *"you cannot calculate
damage on the item same at a attack hit and a craft time."* One formula covering both would have to be
wrong for one of them.

Escalation is therefore **not decided here**. It is a property the craft-wear formula may or may not
have, owned by that table and its balance pass — not a structural choice. The structural ruling is
one pool, one unit, two tables.

### The consumable layer — gamble or grind, and the player picks

The second half of the ruling is a new mechanic, and it is the part that makes the risk tolerable:
**boss-farmed consumables that repair, protect against damage, or raise success chance.** With enough of
them a player reaches **100% success**, so the system offers two honest routes to the same item:

- **Gamble** — craft into the risk, spend fewer materials, accept that the item can break.
- **Assurance** — farm consumables, pay in time, and remove the variance.

**This is Lost Ark's honing model, and the prior art is worth naming because it also documents the
failure.** Lost Ark sells exactly this layer — *Solar Protection*, *Solar Blessing*, *Solar Grace*, plus
Metallurgy/Tailoring books — and pairs it with **Artisan's Energy**, a pity meter where each failure adds
a percentage until the next attempt is guaranteed.

**Two documented failure modes, both of which this design must answer rather than inherit:**

1. **A guarantee that is technically reachable and practically not.** Lost Ark's pity exists, but at high
   item levels *"it takes an eternity and a fortune to reach it"* — so the promise of certainty does not
   actually relieve the frustration it was added for. The owner's *"100% success rate if they have enough
   item"* only works if *enough* is a quantity a normal player genuinely accumulates. **The farming cost
   is the whole design; the mechanic is trivial.**
2. **A guarantee cheap enough to dominate the gamble.** The mirror failure. If assurance costs less than
   the expected cost of gambling, nobody gambles and the risk system is decoration. The two routes have
   to be priced close enough that the choice is real — which means the consumable drop rate and the
   craft-wear formula are **one balance problem, tuned together**, not two.

The player-facing framing that keeps both honest: **variance is a discount.** Gambling is cheaper in
expectation and sometimes ruinous; assurance costs more and never is. Neither is the correct play.

Sources: [Gear Honing System — Maxroll](https://maxroll.gg/lost-ark/resources/gear-honing-system) ·
[Honing — Lost Ark Wiki](https://lostark.fandom.com/wiki/Honing) ·
[High Honing % Constantly Failing — Steam discussion](https://steamcommunity.com/app/1599340/discussions/0/3185737486655373511/)

**Tunables this adds** — ⚠️ **corrected 2026-09-18: this said "all in existing item-tuning files,
none a new domain", and the work that shipped created `gk-core/data/tuning/deployment-hierarchy.v1.json`,
which carries `craftWearPerAttemptMilli`, `potentialCostPerVerb` and the `durability`/`potential`
blocks.** A new domain is not a defect; claiming none was added is, because the next session budgets
for zero new tuning files. The list itself stands: the craft-wear table
(separate from battle wear's), the per-consumable effect magnitudes (repair amount, damage prevented,
success-chance delta), and the consumable drop rates on boss sources. The 1–2 numbers the original
question asked for are still owed to a measured pass — this ruling fixes the **shape**, and the file's
own standing disclaimer applies: shipping a first guess is sanctioned, calling it balance is not.

**Still owed and not decided here:** whether consumables are consumed on failure or only on use, and
whether a protected craft that still fails consumes the protection. Those are spec questions, and both
are the kind of detail that decides whether the assurance route feels honest.
✅ *Answered since* in [spec-craft-assurance.md](species-gear-chain/spec-craft-assurance.md) § Design 4:
**spent on load, whatever the outcome** — the one-transaction spend debits before the outcome persists,
and a price known before the roll is what keeps the assurance route honest.

**R10 (2026-09-18, [spec-rulings-2026-09-18.md](spec-rulings-2026-09-18.md)) — *protect* does not cover
a repair destroying the item.** The repair destroy chance stands as the durability sink; the "Lost" rung
of the ladder above (a failed repair) is unchanged and uninsurable. `spec-craft-assurance.md` § Design 2
refuses `assurance.protect` on a repair attempt by name.

---

## Reading gate (this session, per DESIGN-GATE §1)

**Product vision:** [the-game.md](../guide/the-game.md), [the-loops.md](../guide/the-loops.md) — Spine C
named above; three stocks; no new loop. **Anything at all:**
[software-architecture.md](software-architecture.md), [decisions.md](decisions.md), §2 invariant 15 (SOLID —
both verbs contribute to item modules 14/15, forking nothing), session-boundary policy. **Item rarity /
the ten-rung ladder:** [item/ssot-rarity.md](item/ssot-rarity.md) — §3.2 axis split, §3.6 what rarity is
not, **§3.7 promotion's seven rules**, §4.4 the `rarity_budget` registry, §7.2 the measured 59%.
**Enhancement / the mutation model:** [item/ssot-enhancement.md](item/ssot-enhancement.md) — §3.1 the
mutation model, §3.2 replay-as-transcript, **§5.3 the reserved `op_kind` namespace**, §5.4 content tables.
**Module 15:** [item/spec-enhance-reroll.md](item/spec-enhance-reroll.md) — §4 risk bands (enhancement's,
not promotion's), `:110-112` the lifted drop-only ceiling. **Materials / cost:**
[item/ssot-materials-crafting.md](item/ssot-materials-crafting.md) — the five closed spend classes.
**Caps / power / tunables:** [power/ssot-power-scale.md](power/ssot-power-scale.md) §10 (a cost ladder owes
a row) and §11/PS-8; [tunables-ssot.md](tunables-ssot.md) T1–T8. **Item program:**
[item-map.md](item-map.md) — **21 modules** (not 25; X1–X7 are cross-program *dependencies*, not module
ids). **Origin:** [tier-system-ideal.md](tier-system-ideal.md) § DISPOSITION and § AUDIT.
**Code verified at the `file:line` cites above**, not from comments. Prior art web-searched this session
with sources inline; fetch-blocked domains and unverified figures are flagged as such.

**Boundary honesty:** this session wrote no `tasks/sessions/*.json` record (no `/session-start` tool in this
harness), so **the DESIGN-GATE §5 boundary box cannot be ticked.** `scripts/session-boundary-check.py` was
run earlier this session: 4 active sessions, 13 drift overlaps **between other sessions**, none claiming
`docs/architecture/gear-climb-*` or any path this doc writes.

**§5 checklist:** subsystems identified ✓ · boundary record ⛔ untickable (above) · gate docs read this
session ✓ · `decisions.md` checked ✓ · claims cite `file:line` ✓ · verified against code, not comments ✓ ·
surrounding sections read ✓ (notably: `spec-enhance-reroll.md` §4's risk bands are **enhancement's**, and
are explicitly *not* imported into promotion) · §2 invariants hold ✓ · no population count pinned ✓ (every
corpus size labelled a reading) · **ActorHub — N/A and checked, not assumed**: promotion and upgrade change
an item instance's affix set; the resulting derived magnitudes reach actors through the **existing**
equipment read path, and this feature adds no composer, no private fold and no new Hub contribution ·
no SOLID-violating parallel path ✓ (both verbs land inside item modules 14/15, which already declare them).
