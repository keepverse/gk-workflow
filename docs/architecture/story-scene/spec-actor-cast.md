# Module: `actor-cast`

**Program:** `story-scene` · **Map:** [../story-scene-map.md](../story-scene-map.md)
**Ideal:** [../story-scene-ideal.md](../story-scene-ideal.md) — defects #2/#3/#4, decision 2
**Touches:** new `gk-web/web/fusion-rpg-web/src/features/story-scene/actorCast.ts` (and its test)
**Depends on:** `scene-script` (defines `ActorId`)

---

## Objective

<!-- citations-historical: RiftPrologueDialog.tsx went 203 -> 39 lines at the S6 cutover; it is now a thin wrapper and the beat/guard/acknowledgement/completion logic it used to hold lives in StorySceneHost.tsx, shared by every scene -->


Give the FE a first-class **actor** concept, so a scene can say *who* is on stage and resolve them to
art — instead of a bare `speaker: string` with one shared sprite role.

Today the art contract has **one** sprite for the whole scene. Corrected 2026-09-20:
`features/onboarding/riftAssets.ts` is not found anywhere in `web/` — only
`RiftPrologueDialog.tsx`/`.test.tsx` and two PNG assets remain under `features/onboarding/`. The
shape it used to declare, unverified against any current file:

```ts
storySprite: { role: "storySprite", version: RIFT_ASSET_VERSION, … }
```

That cannot express Penny *and* Dave, and it is why the fallback is one shared `◈` string for every
actor (`RiftPrologueDialog.tsx:170-174`).

---

## Contract

```ts
export type ActorId = "penny" | "dave";

export type ActorVariant = {
  /** Variant id, e.g. "neutral" | "alarmed". */
  id: string;
  /** Resolved art URL for this variant, or null when art is not yet authored. */
  spriteUrl: string | null;
};

export type ActorDefinition = {
  id: ActorId;
  /** Player-facing name. Fiction only — never an id, path, or engine term. */
  displayName: string;
  /** Initial used by the honest labelled fallback. Derived, not authored twice. */
  initial: string;
  /** Named variants; the entry with id "default" is the fallback variant. */
  variants: readonly ActorVariant[];
  /** Pack reference for this actor's paint. */
  themeRef: { kind: "actor"; id: ActorId };
};
```

**v1 cast is exactly two actors** (owner decision 2): `penny`, `dave`. **Dr. Zomboss is deliberately
out of v1** — a story deferral, not a technical one, so the contract must not need a rewrite to add
him later. Adding an `ActorId` is an **ask-first** content change.

### `initial` is not localized (settled 2026-09-23, F12)

`displayName` resolves through the catalog (`actor.<id>.name`, `messages.ts`), so a translated name is
pseudo-marked or translated on every surface. `initial` does **not**, deliberately: it is an *identity
glyph*, not prose — the monogram in the labelled fallback, `aria-hidden` and decorative — so a
translated name keeps the authored initial instead of one derived from a different script. The
alternative (a translatable `actor.<id>.initial`) would re-author the name's own first letter in a
second place, which is exactly the drift this field's "derived, not authored twice" rule prevents, and
it would let the two disagree in a 44px circle. Pinned by `StorySceneHost.pseudo.test.tsx`: under the
pseudo locale the fallback's name is marked while the initial is the authored glyph, so the decision
cannot be changed by accident. A future locale whose monogram must differ is a **new ruling**, not a
defect in this one.

### No plant/zombie side axis

The existing honest stand-in is tinted by a **side** —
`ui/actor/shared.tsx:45-46` applies plant/zombie styling through `ActorFrame`. Penny and Dave are
**neither** plant nor zombie; they are people. `ActorDefinition` therefore carries its own
`themeRef` and must **not** be shoehorned into the `side` theme kind. This is the concrete reason
`theme-packs-scene` must widen `ThemeKind` (S2).

### N sprites, not one role

`variants[]` exists because the genre's portrait systems are variant-based: Dialogic gives a character
unlimited named portraits and selects by name; Ren'Py tracks image attributes and replaces an image
when the same tag is re-shown — which is precisely how an unexplained variant swap drops state. A
scene must therefore name the variant it wants, and a **missing variant degrades to
`"default"`**, then to the labelled shape (see `actor-sprite`).

---

## Asset naming and versioning (extends, does not replace, the deleted `riftAssets.ts`)

Corrected 2026-09-20: `riftAssets.ts` and `RIFT_ASSET_VERSION` are not found anywhere in `web/`
today — not under `features/story-scene/`, `features/onboarding/`, or elsewhere; whether this
manifest was renamed, folded into `sceneScript.ts`, or never actually built was not checked in this
pass. The existing manifest this section assumed already establishes the pattern worth keeping: a
**version** (`RIFT_ASSET_VERSION = 1`) plus **roles**, with filenames
indirected so a future asset swap does not churn call sites.

`actor-cast` extends that with per-actor, per-variant roles:

```
storyActorSprite(actorId, variantId, version)  → url | null
```

Rules:

1. **The version is the cache-buster.** Bumping it invalidates every actor sprite together; it must be
   bumped in the same change that swaps art, never separately.
2. **A missing file resolves to `null`, never to a 404 string.** `null` is the signal that drives the
   labelled fallback — a broken URL string would drive a broken-image glyph, which decision 2 bans.
3. **No hand-maintained duplicate of the actor list.** `ActorId` is the single source; the asset
   resolver is keyed by it.

---

## Success criteria

- [ ] `ActorId` is a closed union with exactly `penny` and `dave` in v1.
- [ ] `ActorDefinition` carries `displayName`, `initial`, `variants[]`, and an `actor` `themeRef`.
      **Plus:** `displayName` is catalog-resolved and `initial` is intentionally not (see § `initial`
      is not localized).
- [ ] No actor is tinted by a plant/zombie side axis.
- [ ] A missing actor/variant resolves to `null` and is distinguishable **per actor** (name + initial).
- [ ] Penny and Dave are visually distinguishable in the fallback path (tested, not asserted by eye).
- [ ] Adding a third actor requires no change to `ActorDefinition`'s shape.
- [ ] `displayName` values are fiction-only: no id, path, or engine term.
- [ ] Dr. Zomboss appears nowhere in v1 data.

## Commands

```powershell
cd gk-web/web/fusion-rpg-web
npm test -- --run actorCast
npm test -- --run riftAssets
npm run build
```

## Boundaries

- **Always:** `null` for missing art; per-actor distinguishable fallback; fiction-only names.
- **Ask first:** adding an `ActorId`; adding a variant; changing an asset version.
- **Never:** a plant/zombie side tint for a person; a 404 string as a missing-art signal; a second
  hand-maintained cast list; Zomboss in v1.

## Project structure

```text
gk-web/web/fusion-rpg-web/src/features/story-scene/actorCast.ts       # ActorId, definitions, resolver
gk-web/web/fusion-rpg-web/src/features/story-scene/actorCast.test.ts  # per-actor distinguishability
web/fusion-rpg-web/src/features/onboarding/riftAssets.ts        # gone (corrected 2026-09-20) -- was the pattern source
```
