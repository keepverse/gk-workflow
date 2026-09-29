# Elemental Impact VFX

**Status:** idea phase, 2026-09-18. Not a spec. No build is authorized by this document.

## Problem statement

How might we let a player recognise a plant or zombie's elemental hit at a glance on the Lawn,
without adding gameplay state, making a crowded board expensive to render, or turning a hit into a
wall of unrelated particles?

This extends the **Lawn** first-core loop and its shared combat-depth language; it does not add a
new loop ([the-game.md](../guide/the-game.md), [the-loops.md](../guide/the-loops.md)).

## Observed foundation

The shipped VFX system already receives the semantic `combat.hit` cue with its element payload,
uses a single injector-side director, and has a player-controlled master VFX switch plus an
element-VFX switch. Its existing element treatment is colour-first: a burst, floater, and brief
flash use the element palette; hybrid particles already mix payload colours. The architecture is
explicitly presentation-only and keeps a failed VFX from affecting the hit.

That makes an impact silhouette the missing player-facing signal. It is a visual refinement of the
existing cue and pool, not a damage system, status system, or new event vocabulary.

## Directions considered

| Direction | Value | Cost / reason not selected |
|---|---|---|
| More coloured particles only | Very safe | Does not give each element a memorable shape at a glance. |
| Bespoke multi-frame animations per hit | Impressive in isolation | Too much asset and pooling complexity for crowded Lawn hits. |
| Custom per-element ShaderLab effects | Potentially dramatic | Unsafe for the IL2CPP host and contrary to the current no per-hit material/shader-work rule. |
| **Pooled alpha-mask impact stamp plus the existing burst and flash** | **A distinct silhouette with bounded cost and a graceful fallback** | **Chosen.** |

## Recommended direction

Each elemental `combat.hit` gains one short-lived **impact stamp**: a transparent, monochrome
alpha-mask texture placed on the struck actor, scaling in quickly and dissolving. The already
shipped burst continues to carry colour, and the existing flash continues to make the target feel
hit. Together they give the player a three-part read:

```text
silhouette = what element struck
colour and particles = which elemental payload was involved
flash + floater = that real damage landed
```

The stamp is tinted using the existing catalog-derived element colour. It must use the same
already-probed alpha-blended sprite/particle material path, not a new custom shader. ShaderLab
cannot safely be compiled into the target IL2CPP player, and per-hit material work violates the VFX
performance boundary.

For a hybrid hit, the largest-weight concrete element supplies the one stamp silhouette. The
existing hybrid particle and floater colour treatment still represents every payload component.
That preserves hybrid identity without spawning two large stamps for every hit.

## Asset brief

Generate a separate effect family; do **not** reuse the static Actor HUD crests as hit stamps.
They should share the same visual language but have a more kinetic, outward impact shape.

| Element | Impact-mask silhouette |
|---|---|
| Fire | Exploding flame chevron, ember slashes pointing outward |
| Ice | Crystal fan with snapping shard fragments |
| Air | Slicing double-ribbon vortex |
| Earth | Angular crack burst and small stone chips |
| Light | Vertical prism beam with diamond rays; never a sun or star |
| Dark | Fractured void rift with inward shards; never a moon or crescent |

For each of the six elements, preserve these transparent RGBA deliverables in the repository:

- 512px master alpha mask;
- 256px runtime source;
- 128px low-cost fallback / web presentation source.

Masks are white or neutral-grey in the RGB channels with authored alpha. Runtime tint supplies the
element colour, avoiding a hard-coded renderer palette and allowing the same source to work with
future catalog palette revisions. No text, UI framing, baked glow background, or animation frames
in this first batch.

## MVP scope

- One new pooled `ImpactStamp` presentation primitive inside the existing VFX director.
- One alpha-mask asset selected from the element payload on a `combat.hit`.
- Existing burst, flash, semantic cue, queue, admission rules, and VFX toggles stay unchanged.
- Lifetime, scale, fade, and pool budget are versioned VFX tuning—not constants in the primitive.
- A live proof covers all six single elements, a hybrid, disabled element VFX, missing asset/shader
  fallback, and a crowded Lawn observation.

## Next effect categories

These are distinct presentation moments, not additions to the impact-stamp MVP. They use the same
element visual family so a player learns one combat language rather than three unrelated effects.

| Category | Player moment | Visual grammar | Asset need |
|---|---|---|---|
| **Cast / Charge** | An actor is about to release a deliberate elemental skill or charged attack | A compact rune/crest gathers at the actor's body or crown, with a short inward pull and an intensity ramp before release | Six transparent **charge crests** (512, 256, 128); each is a calmer inward-facing counterpart to its impact mask |
| **Projectile / Travel** | An elemental attack visibly travels from source to target | A thin directional ribbon, shard, or ember streak that follows an already-known projectile or ray | Six narrow **travel streak masks** (512×128 master, plus 256×64 and 128×32); never replace the host game's projectile sprite |
| **Critical / Overload** | A crit or high-impact elemental hit lands | The normal impact stamp gains one fast secondary echo and a universal angular shock ring; the floater remains the authoritative damage read | One neutral **overload ring** alpha mask; reuse the six impact masks rather than creating a second full elemental set |

### Category boundaries

- **Cast / Charge** is the first follow-on after impact. It is only for explicitly telegraphed skills
  or a true charge state—never every basic Peashooter shot.
- **Projectile / Travel** waits for a verified source-to-projectile-to-target binding. A guessed
  trajectory, a scene scan, or a replacement of vanilla bullets is out of bounds.
- **Critical / Overload** is a presentation branch of the existing `combat.hit` classification, not
  a new damage event. It must remain readable even when element VFX is disabled.
- All three stay behind the existing master VFX and element-VFX controls and share the same pooled,
  bounded presentation lifecycle as the impact stamp.

## Reusable action VFX grammar

The five gameplay action categories are already closed: **Attack, Defense, Support, Movement, and
Status**. Their tags and target modes are also established vocabularies. This idea does **not** add
per-category subclasses such as `fireAttack`, `healingSupport`, or `iceStatus`; that would create a
second action taxonomy with no gameplay value.

Instead, VFX composes four facts already available when an action happens:

```text
existing ActionCategory + existing ActionTags + existing ActionTargetSpec + element payload
    → VFX topology + semantic moment + recipe modifiers
```

### 1. VFX topology — reusable spatial shape

Topology is a VFX-owned presentation profile, never an action rule, AI selector, cost rule, or
stat channel. One profile can serve many action categories.

| Topology | Presentation shape | Reused by |
|---|---|---|
| **Strike** | source acknowledgement → target impact | direct attacks, debuffs, counter-hits, targeted heals |
| **Bolt** | source acknowledgement → visible travel → target impact | ranged attacks, targeted support, curse shots |
| **Field** | cell/area charge → area resolve → optional bounded residue | area attacks, heals, buffs, debuffs |
| **Ward** | self/ally raise → sustained readable marker/aura → end | guard, shields, buffs, channeled support, persistent status |
| **Shift** | source cue → actor-body travel → arrival cue | dash, leap, blink, forced reposition |
| **Manifest** | chosen-cell charge → arrival/build/summon resolve | summon and construct-tagged support actions |

### 2. Semantic moments — when presentation is allowed

These are discrete semantic cues emitted by action lifecycle facts. They are **not** a timeline or
keyframe DSL: VFX never schedules gameplay and never infers a moment that gameplay has not produced.

| Moment | Meaning | Typical visual |
|---|---|---|
| **Prepare** | a real charge/cast state begins | Cast/Charge crest gathers at the source |
| **Release** | action commits/releases | short source flare or recoil |
| **Travel** | a real source-to-destination path exists | travel streak/ribbon or body movement accent |
| **Resolve** | effect definitively lands | impact stamp, burst, flash, floater, heal, or field pulse |
| **Sustain** | a duration-bound effect is active | existing bounded aura, tint, or marker |
| **End** | sustain expires, is interrupted, or is withdrawn | short dissolve / collapse, never a second damage hit |

`Resolve` must reuse the current semantic result paths where they already exist (`combat.hit`,
`combat.heal`, and status apply/expire). A future action does not earn a VFX merely because it was
requested: it emits a moment only when the runtime knows that moment is real.

### 3. Category-to-topology defaults

This table is a presentation default, not a new action subcategory. An authored action may use a
compatible topology only when its actual target/lifecycle facts support it.

| Existing action category | Default topology choices | Common moments |
|---|---|---|
| Attack | Strike, Bolt, Field | Release → optional Travel → Resolve; optional Prepare for charged skills |
| Defense | Ward, Strike | Prepare → Sustain → End; Resolve for a counter or block outcome |
| Support | Strike, Bolt, Field, Ward, Manifest | Prepare/Release → Resolve; Sustain for buffs; Manifest for summon/construct tags |
| Movement | Shift | Release → Travel → Resolve at arrival |
| Status | Strike, Field, Ward | Resolve on successful apply → Sustain → End |

### 4. Recipe modifiers — detail without multiplying topologies

Existing action tags and outcome data add visual detail rather than selecting a new category:

- `heal` changes Resolve from an impact burst to rising restorative motes.
- `buff` and `defensive` prefer Ward's readable persistent marker/aura.
- `debuff` prefers Strike or Field plus the existing status identity visual after success.
- `summon` and `construct` select Manifest only when the chosen cell is real.
- crit, amount tier, and element payload modify the existing Resolve recipe; they do not create new
  action or VFX topologies.

### Reusable asset families

Generate by topology, not per action row. The first asset library stays intentionally small:

| Asset family | Element-specific? | Used by |
|---|---:|---|
| Impact masks | yes, six | Strike, Bolt, Field Resolve |
| Charge crests | yes, six | Prepare across every topology |
| Travel streaks | yes, six | Bolt and Shift Travel |
| Field ring / ward frame | no, tinted at runtime | Field and Ward |
| Manifest glyph | no, tinted at runtime | Summon and Construct support |
| Overload ring | no, tinted at runtime | Crit/high-impact Resolve across all topologies |

This means six elements do not multiply into five category-specific asset packs. The element family
supplies identity; topology supplies motion and placement; existing action data supplies meaning.

### Catalog decision — later

**Approved direction:** this grammar is the current design to preserve. A dedicated, versioned
**Action VFX Presentation Catalog** will be added in a later implementation/spec phase. It will own
the presentation-only mapping from an action's existing category, tags, target geometry, and actual
lifecycle moments to a topology and recipes.

It must not extend `ActionCategory`, `ActionTag`, `ActionKind`, targeting, or combat data, and it
must not become an alternative action catalog. The existing action row remains authoritative for
what an action is and does; the future VFX catalog answers only what an already-real action moment
looks like. Until that catalog is specified and built, this idea is the approved reference direction
and no renderer code or temporary action-specific switch is authorized.

## Guardrails for a later spec

- VFX profiles must not become a fourth action vocabulary or affect action validation, targeting,
  AI, timing, cost, or combat resolution.
- A `Travel` cue requires a verified path/anchor supplied by gameplay; no scene scan or guessed arc.
- One action may emit only the moments its runtime actually reaches. Interrupted casts must never
  show Resolve.
- All topology choices, rates, lifetimes, scale, and pool limits belong to versioned VFX tuning or
  recipe data, never hidden renderer constants.
- A missing profile, asset, anchor, or shader must skip presentation and leave the action outcome
  untouched.

## Not doing

- **No new damage cue ids** — `combat.hit` already represents the semantic moment.
- **No custom ShaderLab, per-hit material instance, or screen-space distortion** — unsafe or costly
  in this host and unnecessary for the first readable version.
- **No new gameplay effect, combat branch, RNG, status, or Unity stat write** — VFX remains a
  lossy presentation consumer.
- **No multi-frame element animations or trails in the first slice** — Cast/Charge,
  Projectile/Travel, and Critical/Overload are named follow-on categories, not permission to add
  animation and atlas complexity to the impact MVP.
- **No second stamp for dual-element hits** — the current hybrid colour mix retains both elements
  while the dominant weight chooses one readable silhouette.

## Assumptions to validate

- [ ] A pooled textured sprite can use the existing approved material path without a new per-hit
  allocation or material instance.
- [ ] The masks still read on live PVZ art at their intended on-screen scale, not merely on a dark
  asset preview.
- [ ] The dominant-weight stamp plus hybrid colour mix communicates a dual payload clearly enough.
- [ ] The stamp pool stays within the actual VFX frame budget on a reachable crowded board.
- [ ] A missing texture or stripped shader degrades to the already-shipped burst/floater path and
  emits the normal skipped diagnostic without touching gameplay.

## What must happen before implementation

1. Generate and approve the six monochrome impact masks at native scale.
2. Write a dedicated VFX extension spec that names the primitive, asset lifecycle, tuning schema,
   pool ownership, and LIVE proof rows.
3. Set a reachable VFX budget before treating the new primitive as ready; the prior `vfx.tick`
   criterion referenced an unreachable board size and must not be copied forward.
4. Build only after that spec and its verification boundary are approved.

## Design-gate evidence

- Product fit: the Lawn first-core loop and combat depth in
  [the-loops.md](../guide/the-loops.md).
- VFX authority and constraints: [vfx-ssot.md](../architecture/vfx-ssot.md) §§2–3, §10, §14, and
  §16 — semantic cues, a single director, shader/material constraints, element payload presentation,
  and the existing element-VFX toggle.
- Action vocabulary: [action-ideal.md](../architecture/action-ideal.md) §§0–2 and
  `gk-core/src/FusionRpg.Core/Actions/ActionEnums.cs` — three action kinds, five closed action categories,
  closed tags, and the ban on a third action vocabulary.
- Existing enhancement and performance finding: [vfx-v2-spec.md](../architecture/vfx-v2-spec.md)
  §§2a and 3 — do not build against its unreachable `300z` criterion.
- No tests run: this is an idea artifact only; it changes no runtime code or asset.
