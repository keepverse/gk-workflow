# Module: `story-scene-fold`

**Program:** `story-scene` · **Map:** [../story-scene-map.md](../story-scene-map.md)
**Ideal:** [../story-scene-ideal.md](../story-scene-ideal.md) — defect #7, decisions 4/5
**Touches:** new `gk-web/web/fusion-rpg-web/src/features/story-scene/foldStorySceneVm.ts` (+ test)
**Depends on:** `scene-script`, `actor-cast`, `cue-seam`, `piece-contract`

> **Audit correction (G1).** The first version of this spec invented a VM shape
> (`root: PiecePayload | null`, `payloads: Record<instanceId, PiecePayload>`) that **does not exist in
> the repo**. `bindSurface` resolves each recipe `bind` against the VM object itself, and there is no
> `payloads` map anywhere (`grep payloads` over `src/` returns only unrelated bus comments). A spec
> that invented a mechanism would have failed at the first implementation step. The contract below
> follows the shipped convention — `ConditionSurfaceVm` (`foldConditionSurfaceVm.ts:22-29`) and
> `AptitudesTab.tsx:380` / `ConditionTab.tsx:73`.

---

## Objective

<!-- citations-historical: RiftPrologueDialog.tsx went 203 -> 39 lines at the S6 cutover; it is now a thin wrapper and the beat/guard/acknowledgement/completion logic it used to hold lives in StorySceneHost.tsx, shared by every scene -->


One **pure** fold from scene state + script to the surface view-model. It joins the script, resolves
the cast, computes speaking state, formats labels, and owns the omit rules. A surface is
`recipe + fold + bus` (`gui-lego/spec-composition.md:25`) — this is the fold.

Today six independent concerns live in one component —
`features/onboarding/RiftPrologueDialog.tsx:62-68`: `beatIndex`, `busyRef`, `finishedRef`,
`advanceGuardRef`, `ackError`, `assetMissing`. That is the god-TSX shape in miniature; pieces cannot
be extracted while the state lives there.

---

## The VM contract (follows the shipped convention)

The VM **is the bind root**: the recipe's root binds `vm`, and each child slot binds a **relative
field name** on it. This mirrors `condition-console.json` (`bind: "vm"` at `:9`, relative `bind`s like
`"phaseBadge"`/`"shield"` on children) and `derived-console.json`'s `"$bindArray": "rows"`.

```ts
export type StorySceneVmInput = {
  script: SceneScript;
  /** 0-based current beat. Session-only; never persisted. */
  beatIndex: number;
  /** Server-owned acknowledgement state, owned by the host. */
  ack: { pending: boolean; error: boolean };
  /** Resolved art per actor/variant. `null` ⇒ labelled fallback (never a 404 string). */
  art: Record<ActorId, Record<string, string | null>>;
  /** Bumped by the host when any input changed; stamped onto payloads (Q5 parity). */
  revision?: number;
};

export type StorySceneVm = {
  phase: Phase;                              // required by bindSurface (bindSurface.ts:255)
  revision: number;                          // required by bindSurface (:256)
  /** Host-consumed shell props. `scene-stage` must NOT render these (see rule 11). */
  shellTitle: string;
  shellSubtitle?: string;
  /** scene-stage fields (root binds `vm`, so the root payload IS this object). */
  sceneId: string;
  cueId: StoryCueId | null;
  themeRef: ThemeRef;                        // scene.<mood>
  /** Root slot fills. */
  actors: PiecePayload[];                    // $bindArray: "actors" (parent-relative)
  window: DialogueWindowPayload;             // relative bind "window"
  progress?: PiecePayload;                   // omitted ⇒ mount omitted
  advance: PiecePayload;                     // relative bind "advance"
  /** What a press means. The host performs it — the fold stays pure. */
  terminal: { action: "advance" | "skip"; outcome: "completed" | "skipped" } | null;
};

export type DialogueWindowPayload = PiecePayload & {
  line: string;
  teaching?: string;
  narration: boolean;
  /**
   * Nested slot — bound against THIS payload, never the VM root.
   * Undefined ⇒ the mount is omitted (narration beat).
   */
  nameTag?: PiecePayload;
};
```

### G5 — nested slot binds are parent-relative, and this is easy to get wrong

`mountRef` resolves a bind that does **not** start with `vm` against the **parent payload**
(`features/gui-lego/bindSurface.ts:123-127`), and `mountBindArray` does the same (`:188-194`).
Verified against a shipped nested recipe: `condition-console.json` binds `cond-hero` to
`"vm.main.2"` and its `shield` child to the plain `"shield"` — which resolves on the **cond-hero
payload**, not the VM.

Consequences, both binding:

1. **`nameTag` is a field on the `window` payload**, not a top-level VM field. The first version of
   this spec put it at the top level, which would have left the name tag permanently omitted (the
   path resolves to `undefined` on the window payload) — i.e. **every spoken beat would silently lose
   its speaker tag**, and only a narration beat would look right.
2. **`progress` and `advance` are top-level** only because `scene-stage` is the root and its `bind` is
   `vm` — so the root payload *is* the VM object. Any piece nested deeper must bind relative to its
   own parent.

**Omit mechanics are `undefined`, not a flag.** `bindSurface.mountRef` returns `null` when
`resolved === undefined` and the slot is `optionalOmit` (`bindSurface.ts:129-132`) — how
`docs/design/gui-lego/recipes/condition-console.json:50-55` omits the shield card. So the fold **omits the field**; it never emits a
payload with `phase: "empty"` in its place.

**A slot child with no `bind` is a bug.** `getByPath` returns the **root** when the path is absent
(`bindSurface.ts:25-26`), so an un-bound child receives the entire parent payload. Every slot child in
the recipe must name its `bind`.

---

## Binding rules

1. **Pure.** No fetch, no `Date.now()`, no random, no mutation of inputs. Same input ⇒ same output.
2. **Speaking state is derived, not stored.** `speaking` is true only for the beat's `speakerId`
   (when present); every other actor is inactive. A narration beat has **no** speaking actor and
   therefore no `nameTag`.
3. **Variant continuity.** The fold carries `variantId` per actor across beats, so a speaker change
   does **not** reset the other actor's variant. (Genre failure mode: re-showing an image with the
   same tag drops its attributes — Ren'Py's `show` replaces by tag.)
4. **Actor ordering is stable.** `actors[]` keeps a deterministic cast order so two renders of the
   same beat are identical; emphasis is a per-actor `speaking` flag, never a reorder.
5. **Omit rules, owned here:**
   - `nameTag` — **field absent on the `window` payload** when the beat has no `speakerId`.
   - `progress` — **VM field absent** when `beats.length <= 1` (decision 4: a reveal is a one-beat
     scene, so it reuses these pieces without a meaningless "1 of 1").
   - `advance` — always present, with `isLastBeat` computed.
   - Nothing is emitted for a slot the recipe does not declare.
6. **One terminal path.** `advance` on the last beat and `skip` both describe an outcome through the
   **same** `terminal` field, so the host has one code path. `skip` is reachable on **every** beat
   (decision 5) and is never gated by beat index.
7. **Labels are fold-authored.** `progress.label` (`"Beat 2 of 4"`) and the control labels are
   formatted here, so there is one place to localize and test; the pieces render them verbatim.
8. **`sceneId`/`cueId` are payload fields, never rendered text.**
9. **No balance numbers.** Timing and caps come from `gk-core/data/tuning/story-scene-ui.v1.json` and
   `storySceneTokens.ts`; the fold reads or receives them, it does not invent them.
10. **`revision` is stamped onto every payload**, including nested ones — mirroring
    `foldConditionSurfaceVm.ts:67-79`'s `stampRevision`. **The key `"revision"` is a string literal
    that trips `i18n/vocabularyGuard`** (`bandDelta`-class words are banned; `"revision"` is on the
    list at `vocabularyGuard.ts:50`). Both shipped folds are **red** on it today
    (`foldConditionSurfaceVm.ts:71`, `foldAptitudesSurfaceVm.ts:66`). The story-scene fold must write
    `if (key === "revision") continue;` — the guard's `CASE_LABEL_PATTERN`/`STRING_LITERAL_PATTERN`
    heuristics allow a comparison value only in a `case` label, so a bare comparison **fails the
    guard**. Use the case-label form or destructure:
    `const { revision: _skip, ...rest } = payload;` — whichever the shared-kit fix lands on, this
    module **inherits the fix rather than shipping a new violation**.
11. **Shell title/subtitle are host props, not piece fields.** `shellTitle`/`shellSubtitle` exist on
    the VM for the host's `<DialogShell title=…>`, and **`scene-stage` must not render them** — the
    shell owns that chrome. This is why they are named `shellTitle`/`shellSubtitle` rather than
    `title`/`subtitle` (the name makes a wrong read visible).

---

## Success criteria

- [ ] The VM matches the shape above; **no** `root`/`payloads` map is introduced.
- [ ] The recipe's root binds `vm`; **every** slot child declares a `bind` (audit assertion).
- [ ] `nameTag` is a field on the **window payload**, and a spoken beat renders the tag (this is the
      G5 regression test — a top-level bind silently omits it on every beat).
- [ ] Fold is pure: two runs with identical input are deep-equal.
- [ ] A narration beat emits **no** `nameTag` field (asserted as absence, not as an empty piece).
- [ ] A one-beat script emits **no** `progress` field.
- [ ] `speaking` is true only for the beat's speaker; a narration beat has no speaking actor.
- [ ] A variant set on beat 1 survives to beat 3 unchanged (continuity test).
- [ ] `terminal` covers `advance` and `skip` through one shape; `skip` is reachable on every beat.
- [ ] `beats.length` is read from the input script — never a literal in the fold or its test.
- [ ] `revision` is stamped on every payload **and** the fold does not introduce a new
      `vocabularyGuard` violation (G6).
- [ ] Missing art resolves to `null` and reaches `actor-sprite` as `phase: "empty"`, not `"error"`.
- [ ] No banned engine word appears as a string literal or JSX text in the fold (asserted by the real
      guard: `npx vitest run src/i18n/vocabularyGuard.test.ts`).

## Commands

```powershell
cd gk-web/web/fusion-rpg-web
npm test -- --run foldStorySceneVm
npm test -- --run bindSurface
npm run build
```

## Boundaries

- **Always:** pure; VM-as-bind-root; omit via `undefined`; one terminal path; labels here; stamp revision.
- **Ask first:** adding a bound field; adding a persisted field (beat position is session-only).
- **Never:** a `payloads` map or a bespoke binding mechanism; fetch/mutate in the fold; persist beat
  position; gate skip; a hard-coded beat count; assemble a label inside a piece.

## Project structure

```text
gk-web/web/fusion-rpg-web/src/features/story-scene/foldStorySceneVm.ts
gk-web/web/fusion-rpg-web/src/features/story-scene/foldStorySceneVm.test.ts
gk-web/web/fusion-rpg-web/src/features/gui-lego/foldConditionSurfaceVm.ts   # parity source
```
