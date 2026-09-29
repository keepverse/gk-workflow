# Combat VFX asset library — brainstorm and production queue

**Status:** Asset exploration, 2026-09-26. Assets are visual candidates until reviewed in-game and
connected through the approved VFX director.

## Art direction from the shipped Earth pilot

Use transparent, isolated VFX cutouts with a dimensional, hand-painted game finish: confident
silhouettes, chipped or sculpted materials, bright inner energy, clean alpha edges, and a few strong
focal details. Preserve each effect's read at small sprite scale. Keep hue and motion direction
specific to its gameplay meaning. No text, UI cards, scenery, character bodies, or baked background
glow. Earth v2's mossy stone and jade energy is a style reference, not a palette mandate for every
effect.

The game is 2D Unity/IL2CPP presentation layered over Fusion. These are source art candidates for
pooled sprites/particles; generation alone does not prove alpha, dimensions, import settings, or
runtime readability. Save source masters and named derivatives in the repository with a manifest
and provenance note. Never overwrite approved V1/V2 files.

## Prioritized families

Generate by reusable visual grammar, not one bespoke effect per action. Existing action categories,
tags, target geometry, elements, statuses, and actual lifecycle moments supply meaning; artwork
supplies a reusable silhouette/material. The future action-timeline ideal is recorded in
[`action-presentation-vfx-ideal.md`](../architecture/action-presentation-vfx-ideal.md).

| Priority | Family | Candidate assets | Shared across |
|---|---|---|---|
| **P0** | Defensive outcomes | elemental shield face/rim; shield impact flare; shield break shards and shield re-form; block brace; parry deflection arc; miss/evade slipstream; absorb inward spiral; pierce/penetrate split | shields, all elements, attacks, counters, defense skills |
| **P1** | Elemental action phases | charge crest, travel ribbon, resolve impact per fire/ice/air/earth/light/dark; neutral overload/critical ring | attack, support, ward, field, projectile and reaction actions |
| **P2** | Status application and sustain | a small set of reusable state motifs, colored/parameterized by the current status catalog; apply pulse and end/cleanse accents | status, buff, debuff, contagion, control |
| **P3** | Protection and support | ward dome/frame, ally link, healing motes, cleanse sweep, rally/buff lift, debuff mark, barrier transfer | support, defense, protect, heal, cleanse actions |
| **P4** | Movement and field actions | dash streak, leap arc, blink fold, arrival and withdrawal cues, ground field boundary, summon/construct manifest glyph | movement, area support/attack, summon, construct |
| **P5** | Consequence punctuation | interrupt snap, stagger burst, combo/reaction seal, defeat dissolve, status expire collapse | interrupts, chained actions, reaction moments, life-state ends |

## First batch: common combat outcomes

Build these as separate transparent assets with a shared material and edge treatment:

1. **Shield impact** — a directional concave ripple and bright contact flare; reusable regardless of
   the shield's element.
2. **Shield break** — a visibly dispersing arc of large shield fragments and a few tiny glints; no
   intact shield silhouette, so it cannot read as a second block.
3. **Block** — a compact forward-facing guard plane catching force, with the motion stopping at the
   plane.
4. **Parry** — a sharp tangential deflection crescent with a concentrated spark at the contact point;
   its direction must differ from the frontal block.
5. **Miss / evade** — a narrow passing slash or displaced after-streak, with a clear gap where the
   target would be; never a target explosion.
6. **Absorb** — a contained inward curl drawing the incoming energy into a central point; direction
   reverses the exploding impact grammar.
7. **Pierce / penetrate** — a thin entry-to-exit line and a small rear-side flare, not a broad blast.
8. **Elemental shield skin** — reuse the neutral faceted barrier from `block` as one shield
   surface/rim that can be tinted or rim-lit by the element payload; do not generate six complete
   shield objects unless runtime evidence proves tinting cannot carry identity.

The first image-generation checkpoint is `shield-impact`. It sets the common outcome family's
visual finish; once it reads well, create `shield-break` and `parry` as the first small batch, then
complete block/miss/absorb/pierce. Keep output to separate assets, not a generated contact sheet.

**Generated in the first batch:** `shield-impact`, `shield-break`, and `parry` are saved as separate
transparent source PNGs under `Assets/combat-action-vfx/reactions/`. Their repository manifest keeps
each prompt, source dimensions, anchor intent, alpha-sampling result, and `candidate` status.

**Generated in the outcome follow-up:** `block`, `miss`, `absorb`, and `pierce` now complete the
common outcome set. The `pierce` source is landscape; preserve its aspect ratio when deriving runtime
sizes. The `miss` source has a 1/255 corner-alpha sample and should remain a candidate until the
transparent edge is normalized and previewed over the actual game background.

**Generated elemental family:** Fire now has separate `charge`, horizontal `travel`, and radial
`impact` candidates under `Assets/combat-action-vfx/elements/fire/`. Its palette uses ember red,
molten orange, gold, and charcoal, keeping the three phases recognizably related while their
silhouettes communicate different moments.

**Generated elemental family:** Ice now has separate `charge`, horizontal `travel`, and `impact`
candidates under `Assets/combat-action-vfx/elements/ice/`. Charge uses an upright crystal assembly;
travel is a narrow shard-led ribbon; impact is a grounded frost fracture. The first charge draft
read too much like an impact burst, so it was regenerated with a deliberately tall, inward-building
silhouette. Keep all three as candidates pending scale/context review.

**Generated elemental family:** Air now has separate `charge`, curved `travel`, and `impact`
candidates under `Assets/combat-action-vfx/elements/air/`. The family uses pale turquoise wind
sheets: a compact inward vortex, a directional ribbon, and crossing slicing blades. The charge and
impact have distinct silhouettes, but their shared curved-flow language should be checked at game
scale before approval.

**Generated elemental family:** Light now has separate `charge`, focused `travel`, and `impact`
candidates under `Assets/combat-action-vfx/elements/light/`. The identity is prism convergence,
refraction, and broken glass planes—no sun, moon, or star emblem. Charge and impact share angular
facets by design, with their motion and silhouette separated; check the bright highlights over
gameplay backgrounds before approving.

**Generated elemental family:** Dark now has separate `charge`, torn-shadow `travel`, and inward
fracture `impact` candidates under `Assets/combat-action-vfx/elements/dark/`. Near-black bodies use
violet edge light to remain visible over varied scenes; verify this contrast in the actual game.
The shapes communicate inward void motion without moon or crescent symbols.

## Elemental phase queue

The six-element action-phase set now has candidate charge, travel, and impact primitives for Earth,
Fire, Ice, Air, Light, and Dark. Earth v2 remains the established pilot; preserve those source files.
All newly generated elemental assets remain candidates until their phase identity and contrast are
reviewed at gameplay scale. Elemental identity comes from each family’s palette, material, motion,
and silhouette—not an icon or emblem.

For each phase, keep charge, travel, and resolve as separate reusable primitives. A given action may
compose one or more only when its real lifecycle provides those moments. A projectile path is never
guessed from two actors' positions.

## Status coverage without an asset explosion

The live status catalog currently feeds apply cues for these IDs (as listed in
`VfxSeedCatalog.StatusFx`): `butter`, `freeze`, `cold`, `poison`, `hypno`, `ember`, `jala`, `kelp`,
`wither`, `bond`, `rally`, `leech`, `expose`, `command`, `shatter`, `charm_pulse`, `blight`, `rot`,
`spark`, `pact_mark`, `spore`, `nerve.unsettled`, `nerve.shaken`, and `nerve.afflicted`. Existing
status sustain already has reusable aura/tint/marker motion for custom statuses in
`VfxSeedCatalog.StatusSustainFx`; vanilla-wrapped statuses retain the engine's own effects. Do not
generate 24 unrelated bespoke animations. Extend with a small, reviewed visual grammar and map IDs
through the status catalog:

| Grammar family | Candidate identities |
|---|---|
| Cold / control | freeze, cold, butter, kelp |
| Toxic / decay | poison, ember, jala, wither, blight, rot |
| Link / drain | bond, leech, pact_mark |
| Rally / command | rally, command |
| Fracture / exposure | expose, shatter |
| Mind / charm | hypno, charm_pulse |
| Contagion / spark | spore, spark |
| Nerve ladder | nerve.unsettled → nerve.shaken → nerve.afflicted; shared grey-violet identity with increasing density |

One base motif can be tinted, scaled, or paired with a marker when those variants remain distinct
in a crowded battle. Add unique art only when live scale tests show the shared grammar cannot identify
the gameplay state. Status visuals represent successful apply, active sustain, and actual end/withdraw
moments; they never invent status state.

## Support, movement, buffs and debuffs

- **Protect / ward:** one reusable ally-facing shield frame, plus an inward/raised start and a soft
  end collapse.
- **Support / healing:** upward restorative motes and a target-centered pulse; no weapon-like impact.
- **Buff:** rising facets or a stable crown/ring; use status identity while active.
- **Debuff:** downward notch/mark, restrained stain, or tether; use the applied status identity while
  active rather than stacking a second aura.
- **Movement:** dash streak, leap arc, blink fold, and landing ripple are individual shapes; only show
  travel when the game supplies actual movement endpoints.
- **Field / summon / construct:** a cell-ground boundary and a distinct arrival/manifest glyph; do
  not draw hidden target cells or predict where a summon will appear.

**Generated support candidates (2026-09-26):** ward frame, healing lift, cleansing sweep, and buff
lift are saved as separate source PNGs under `Assets/combat-action-vfx/support/`. Their silhouettes
are distinct, but their bright ivory/gold bloom is currently strong; keep them as candidates until
we review contrast and small-scale readability against the game scene. Debuff remains a separate
queued asset.

**Generated positive ally-link candidate (2026-09-26):** the selected two-endpoint aqua/ivory tether
has matched nodes and symmetrical pulses, distinct from the rose, one-way `link-drain` status motif.
The first pass nearly touched the canvas edge and is retained as an alternate; the selected revision
has transparent margins. Both remain candidate art; later placement must use real gameplay anchors.

**Generated movement candidates (2026-09-26):** dash streak, diagonal leap path, blink fold, and
low landing ripple are saved separately under `Assets/combat-action-vfx/movement/`. The leap uses an
open diagonal path so it cannot be mistaken for the ward's arch; only render it when actual movement
endpoints are available. These shapes are neutral/tintable candidates, not bound to any action yet.

**Generated status motifs (batch 1, 2026-09-26):** cold/control clasp (`butter`, `freeze`, `cold`,
`kelp`), toxic decay (`poison`, `ember`, `jala`, `wither`, `blight`, `rot`), link/drain (`bond`,
`leech`, `pact_mark`), and contained fracture (`expose`, `shatter`) are saved under
`Assets/combat-action-vfx/statuses/`. These are optional art primitives beside—not replacements
for—the existing 24 status-specific runtime apply cues and the custom sustain catalog. The decay
source has a soft haze; inspect its alpha edge over real lawn colors before treating it as ready.

**Generated status motifs (batch 2, 2026-09-26):** rally/command, mind/charm, contagion/spore,
spark, and all three nerve ladder stages are now represented by separate candidate source assets.
Some generated files have a sampled corner pixel at alpha 1; keep them provisional until their edges
are checked over real gameplay backgrounds. These motifs remain art inputs, not a status-catalog
remap.

**Generated consequence candidates (2026-09-26):** critical/overload, interrupt snap, stagger,
combo/reaction, defeat dissolve, status-expire collapse, and a separate debuff-application mark are
saved as source art. The first interrupt draft read as a flowing combo ribbon and was rejected; the
saved interrupt candidate uses a visibly broken center. Critical and debuff each have one sampled
corner pixel at alpha 1, while stagger/defeat have soft haze that needs lawn-background review. All
remain candidates; their names describe possible semantics, not runtime bindings.

**Generated elemental shield candidates (2026-09-26):** Earth, Fire, Ice, Air, Light, and Dark now
share the block primitive's upright faceted barrier silhouette, with distinct materials and palette
identity. The Air version adds curved edge currents; Light is deliberately bright; Dark has a narrow
violet rim to retain its silhouette. Ice, Light, and Dark have one sampled corner pixel at alpha 1.
All six need contrast and silhouette review at gameplay scale before approval.

**Generated field and summon candidates (2026-09-26):** the field set now has an open boundary, a
ground-hugging pulse, and a quiet fade; summon/construct art has an upward arrival manifestation and
a stone-metal assembly cue. The construct source has one sampled corner pixel at alpha 1. The field
boundary/pulse/fade all preserve open centers and omit target-cell markers; all five remain
unwired candidates pending in-game scale review.

**Generated counter and neutral-phase candidates (2026-09-26):** reflect-return, counter-release,
resist-nullification, neutral cast-focus, and neutral release are saved separately under
`Assets/combat-action-vfx/counter-responses/` and `Assets/combat-action-vfx/neutral-phases/`.
All five have fully transparent sampled corners. The reflect-return has a clear forked return path;
the counter-release is a bright ground-oriented burst and may still read too much like a generic
impact; resist-nullification resembles a closed barrier and needs review against shield/block art.
The neutral cast and release read as distinct prepare/launch shapes. All remain unwired candidates.

## Separate-program handoff: reusable action composition

The reusable action-timeline question belongs to the separate action-presentation program, not this
asset batch. [`action-presentation-vfx-ideal.md`](../architecture/action-presentation-vfx-ideal.md)
already captures the candidate model: an action may select one or more reusable presentation phases
and their event-relative timing. Owner discussion/approval and any later spec remain open; this asset
library does not lock that architecture or implement action wiring.

## Coverage brainstorm and remaining asset queue

This is an art backlog only: each item is an optional sprite primitive, not a new gameplay action,
status id, VFX cue, or runtime mapping. Existing primitives are reused where they already express the
same silhouette; new assets are separate only when they add a distinct gameplay read.

| Wave | Candidate assets to add | Why / intended visual read |
|---|---|---|
| **Now — consequences** | critical/overload, interrupt snap, stagger burst, combo/reaction link, defeat dissolve, status-expire collapse, debuff mark | Make high-signal outcomes legible and complete the explicitly missing debuff/end-state punctuation without cloning status auras. |
| **Generated — shield identity** | shared upright barrier silhouette with Earth, Fire, Ice, Air, Light, and Dark material treatments | Keep the shield silhouette consistent while its material/light communicates element; shield impact and break remain separate outcome effects already in the library. |
| **Generated — shield restoration** | one neutral inward-reassembling barrier cue | The manifest has six intact elemental shield skins and a separate outward shield-break consequence (`manifest.json:183-244,379-388`). One reusable restoration candidate now fills that visual gap without six duplicate repair skins; it remains art only, not a new cue or mechanic. |
| **Generated — field arming** | broken-perimeter arming telegraph, separate from the existing persistent boundary and pulse | Candidate art communicates a real pending area activation only when the game supplies that phase and actual cell/radius. |
| **Generated — summon / construct** | summon arrival and construct assembly; actor-specific manifestation/settle variation remains open | Reusable arrival grammar for spawned actors and erected structures; no bespoke effect per species. |
| **Generated — summon departure** | a controlled upward retract/recall cue distinct from defeat dissolve | The manifest contains arrival and construct-assembly assets but no dismissal visual (`gk-fusion/src/FusionRpg.Injector/Assets/combat-action-vfx/manifest.json:287-310`); defeat-dissolve is a separate downward life-state end (`gk-fusion/src/FusionRpg.Injector/Assets/combat-action-vfx/manifest.json:351-359`). One art candidate now fills the visual gap; it creates no dismissal mechanic or cue and is usable only if a real gameplay event exists. |
| **Generated — counter / reflect** | reflect-return, counter-release, resistance/immune nullification | Candidate art exists; gameplay-scale review must distinguish return, counter, and nullification from parry, impact, block, and absorb. |
| **Generated — neutral cast / launch** | neutral cast-focus and release, reusable with elemental phase families | Candidate art exists for a non-element-specific prepare/launch read; compare it against elemental charge/travel before expanding variants. |
| **Generated — channel / beam** | source flare, stretchable core ribbon, target terminus | Candidate concept-art kit for sustained line attacks; runtime use remains undecided because a beam is a new primitive in [vfx-ssot.md §6.1](../architecture/vfx-ssot.md) and the action-presentation ideal leaves new primitives open ([§What this deliberately does not decide](../architecture/action-presentation-vfx-ideal.md#what-this-deliberately-does-not-decide)). |
| **Generated — melee delivery** | source-anchored multi-cut sweep/afterimage | Candidate adds a readable close-range attack stroke distinct from the existing single contact-centered parry arc. |
| **Generated — lobbed delivery** | curved ballistic trail with a small leading projectile focal | Candidate covers non-straight projectile paths; show it only when the actual projectile trajectory is available. |
| **Generated — forced displacement** | an outward push/knockback pressure wake and a separate inward pull/draw-in ribbon | The manifest now has distinct outward and inward movement candidates. Existing dash/leap/blink cues communicate self-movement, while absorb consumes incoming energy and link-drain travels along a one-way tether; the new silhouettes read as target displacement without inventing gameplay state, action vocabulary, or runtime cues. |
| **Generated — shield stress hit** | one compact, frontal barrier-surface compression with a few bright hairline fractures, while the shield remains whole and no shards break away | `manifest.json` → `reactions.shield-stress`. Existing shield impact is a bright outward burst and shield break is a separated shatter; the new candidate tests a contained hit read without confusing it with a break. Transient impact treatment only: no persistent damage state, threshold, or new shield mechanic is implied. |
| **Generated — defensive outcomes** | a dodge-specific slip/afterimage, distinct from a generic miss; a guard-intercept contact cue, distinct from a persistent ward or reflect-return | [`Dodge` is a semantic outcome in the VFX SSOT](../architecture/vfx-ssot.md#164-color-precedence-locked) (`docs/architecture/vfx-ssot.md:450`), but the [initial art brief groups miss and evade](#first-batch-common-combat-outcomes) (`docs/ideas/combat-vfx-asset-library.md:48`). Protection also needs a momentary “the defender took the hit for an ally” read that does not imply a new shield state. The distinct slip and intercept candidates remain unapproved pending gameplay-scale review; do not infer actors, direction, or timing. |
| **Generated — warm burn-status variant** | paired tapered ember wisps curling around an open actor silhouette, separate from an attack's large fire impact or travel ribbon | The existing catalog includes `ember` and `jala` (`status-ssot.md §9.2`), which currently share the green `decay` art motif. `manifest.json` → `statuses.burn-sustain` is an optional warm-toned art alternative only; it does not change status mappings or add a status id, damage tick, or mechanic. |
| **Generated — positive support link** | symmetric two-endpoint tether with pulses travelling both ways | P3 lists an ally link (`docs/ideas/combat-vfx-asset-library.md:32`), while the existing drain motif explicitly carries motes toward one endpoint (`gk-fusion/src/FusionRpg.Injector/Assets/combat-action-vfx/manifest.json:801`). The selected candidate uses matched aqua/ivory nodes and shared flow; it remains art-only until gameplay provides real endpoints. |
| **Deferred — repeated status damage** | periodic tick punctuation | Reuse the existing impact motif and status identity unless native-scale review proves DoT ticks are not distinguishable; avoid generating one bespoke tick for every status. |

**Generated defensive-outcome candidates (2026-09-26):** dodge-slip and guard-intercept are two
separate momentary reads. Dodge-slip is an empty-center displacement smear rather than a target hit;
guard-intercept is a compact side-caught contact/deflection rather than an enclosing ward or outgoing
reflect trail. They remain candidate art until native-scale gameplay review; placement and any
source/target relationship must come from real action events.

**Generated melee/lobbed candidates (2026-09-26):** the melee source is three separated silver/jade
cuts with sharp tips and no contact flare; the lobbed projectile is a single high curved trail with a
leading crystal focus, visibly distinct from straight elemental travel and the neutral beam ribbon.
Both have transparent sampled corners and remain candidate art pending gameplay-scale/context review.
They add no action vocabulary, new VFX primitive, or timing model; phase selection and event-relative
composition remain with the separate action-presentation program. Use the lobbed path only when an
actual projectile trajectory is available.

**Forced-displacement candidates (2026-09-26):** the outward push/knockback wake and inward pull/draw-in
ribbon are separate art primitives for opposite displacement reads. They remain art-only candidates:
they do not add actions, statuses, cues, or runtime behavior. The push uses a broad opening pressure
arc; the pull uses separated curved streamers converging toward a focal point, not an enclosing shield,
one-way drain tether, or absorb vortex. Verify the distinction at native gameplay scale before use.

**Shield-restoration candidate (2026-09-26):** a neutral pearl-silver barrier re-form cue now complements
the six shield skins, impact, and outward break. Inward-pulling filaments and a reconnecting seam make
the restoration direction distinct from shield-break. It remains art-only and needs gameplay-scale
contrast/readability review; it is not a cue or runtime mechanic.

**Summon-departure candidate (2026-09-26):** orderly pearl-ivory facets and motes fold inward along an
upward path into a narrow fading point, complementing summon arrival and construct assembly. It avoids
the downward ash-like silhouette of defeat-dissolve and remains provisional because its soft glow needs
native-scale contrast review. It adds no gameplay event or runtime mapping.

### Generated batch — area warning and channel concept art

The field-arming candidate uses separated amber/silver ground clusters, and the beam kit now has a
source flare, uniform-thickness silver/turquoise center ribbon, and compact receiving crescent. The
first endpoint draft included an unwanted long ribbon and was discarded; only the regenerated compact
endpoint is retained. All four selected images have transparent sampled corners and remain candidates
pending native gameplay-scale/context review.

These are candidate images only: the batch does not add a cue, action category, beam primitive, or
timing/runtime contract. The target/extent must come from actual gameplay state. Existing VFX
composition and primitive ownership remain governed by the VFX SSOT and the separate action-presentation
program.

**Already represented:** eight common outcome cues (`shield-impact`, `shield-break`, `block`, `parry`,
`miss`, `dodge-slip`, `absorb`, `pierce`); shield restoration; charge/travel/impact for the six elements (Earth pilot plus Fire, Ice,
Air, Light and Dark candidates); six elemental shield skins; all 24 status ids through shared motifs;
ward/heal/cleanse/buff; dash/leap/blink/landing; and field boundary/pulse/fade plus summon arrival /
construct assembly / controlled dismissal; and outward knockback / inward draw-in displacement
candidates. The inventory does not imply these assets are wired or production-approved.

## Delivery order and acceptance

1. P0 universal outcomes, starting with shield impact, shield break, and parry.
2. P1 six-element action phases are represented by Earth, Fire, Ice, Air, Light, and Dark
   charge/travel/impact candidates; assess the set in context before calling it approved.
3. P2 status motifs: reusable art motifs now represent the listed catalog families, including the
   three distinct nerve ladder stages; review them at native scale and against the game before approval.
4. P3/P4 protection, support, movement, field, summon/construct motifs are represented; review all
   candidates in context before adding only the specific field arming or actor-settle variations that
   gameplay demonstrates are needed.
5. P5 consequence and end-state art: the first consequence batch is represented; review at native
   gameplay scale before deciding whether critical, interrupt, stagger, combo, defeat, expiry, and
   debuff reads need revision.
6. Review shield, field/arming/summon, counter/reflect, neutral cast/release, channel, melee-sweep,
   lobbed-trajectory, and forced-displacement candidates at native gameplay scale; revise or add
   variants only where an existing asset does not provide a distinct read in context. Beam art review
   does not approve a new runtime primitive, and a lobbed trail requires a real trajectory.

For each batch: generate separate source assets; inspect them; preserve genuine alpha; normalize
dimensions and pivots; add a manifest/provenance record; view at gameplay scale over a lawn-like
contrast background; then commit. A later code/spec task must prove Unity import, pooled rendering,
toggle behavior, cleanup, and live readability before calling the images shippable. Assets can be
committed ahead of wiring as reviewed art candidates.

## Provenance

Generated with the built-in Codex image-generation tool. No external source art or third-party
licenses are included. Each asset's manifest records its source prompt, date, target use, and review
state. Status on creation is `candidate`, not `approved` or `production-ready`.
