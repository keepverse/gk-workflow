# Module: `scene-script`

**Program:** `story-scene` · **Map:** [../story-scene-map.md](../story-scene-map.md)
**Ideal:** [../story-scene-ideal.md](../story-scene-ideal.md) — defect #4, decision 2
**Owner decision:** S3 (typed TS module), S4 (i18n throughout)
**Touches:** new `gk-web/web/fusion-rpg-web/src/features/story-scene/sceneScript.ts` (and its test)
**Depends on:** `localization` (copy resolution), `scene-tunables` (`maxBeatsPerScene`)

---

## Objective

Move beat content **out of the component** and into a declared contract, so scene 2 does not require
editing a TSX.

Today the four beats are a `const` inside the component —
`features/onboarding/RiftPrologueDialog.tsx:19-44` — and the `Beat` type couples three unrelated
concerns (`:9-15`):

```ts
speaker: string;        // presentation
teaching: string;       // first-user-guide pedagogy
cue: string;            // stage/VFX
seal?: boolean;         // stage
```

That coupling is why a scene cannot vary one concern without the others, and why `speaker` is a bare
string instead of an actor reference.

---

## Contract

```ts
/** One spoken or narrated beat. Authored content — not a generated tree, not a tunable. */
export type SceneBeat = {
  /** Stable actor id resolved through the actor-cast registry. Absent ⇒ narration (no name tag). */
  speakerId?: ActorId;
  /** Optional named variant of that actor's portrait (e.g. a mood). Absent ⇒ the cast default. */
  variant?: string;
  /** The line the player reads. One short sentence; this is the scene's own text. */
  line: string;
  /** One optional teaching sentence. Absent ⇒ no teaching line rendered. */
  teaching?: string;
  /** Semantic cue id for the FE cue layer. Absent ⇒ no cue this beat. */
  cueId?: StoryCueId;
};

export type SceneScript = {
  /** Stable scene id, e.g. "rift-prologue". */
  sceneId: SceneId;
  /** Content version, bumped when beats change. Mirrors the story-ledger version field. */
  version: number;
  beats: readonly SceneBeat[];
};
```

**`maxBeatsPerScene` is a structural guard against text walls**, not a balance number: a scene that
needs more than the cap should be **two scenes**, which is the genre answer (Ren'Py sequences scenes;
it does not cap lines arbitrarily). The cap lives in `story-scene-ui.v1.json` because it is a
per-scene structural bound a designer would tune — the file is the SSOT, the constant is not.

---

## The four Rift beats, migrated verbatim

<!-- citations-historical: RiftPrologueDialog.tsx went 203 -> 39 lines at the S6 cutover; it is now a thin wrapper and the beat/guard/acknowledgement/completion logic it used to hold lives in StorySceneHost.tsx, shared by every scene -->


Copy must be **preserved exactly** — it is authored, and the `onboarding-gnome-teaser.md:25-30` table
is its SSOT. Migration is a move, not a rewrite:

| Beat | `speakerId` | line | teaching | cueId |
|---|---|---|---|---|
| 1 | `dave` | "Uh-oh. That lawn is doing the wrong kind of wobbly." | … | `rift.portal.open` |
| 2 | `penny` | "Temporal signal unstable." | … | `rift.portal.surge` |
| 3 | *(none — narration)* | "UNSTABLE SECTOR. QUARANTINE PENDING." | … | `rift.quarantine.seal` |
| 4 | `dave` | "Then we fix it before they close the gate. Plants first. Questions later." | … | `rift.quarantine.fade` |

**Beat 3 is narration, and today it is not.** The current data types speaker `"Gnome signal"`
(`RiftPrologueDialog.tsx:33`) — a synthetic speaker that would render a name tag for a machine. The
genre rule is that narration is a line with **no** speaker (Ren'Py's single-argument say), so beat 3
becomes `speakerId` absent. **This is the one content-shaped change**, and it is a rendering
correction, not a copy edit: the line text is untouched.

**`seal?: boolean` is dropped, not migrated (audit finding).** The flag drives `data-sealed` on the
scene div (`RiftPrologueDialog.tsx:169`), and **nothing reads that attribute** — `grep sealed` over
`src/**/*.css` and `src/**/*.test.tsx` returns nothing, and `rift.css` styles nothing named `sealed`.
So it is **dead data**, not merely stage-coupled data. The quarantine mood it was reaching for is
already carried by `cueId === "rift.quarantine.seal"` (`rift.css:32-38` styles on `[data-cue=…]`), so
dropping the flag loses nothing. **Do not carry a dead field into a new contract.**

The two speaker labels also become **cast ids**, not display strings: `"Dave"`/`"Penny"` migrate to
`dave`/`penny` resolved through `actor-cast`, so the name shown comes from the actor's own
`displayName` (fiction text, one owner) rather than being repeated per beat.

---

## Where the script lives (S3 — decided: typed TS module)

**Decided (S3): a typed TS module** (`features/story-scene/sceneScript.ts`), not `data/` JSON.

Why: the script is **authored narrative content with no numeric tuning surface**, and the FE already
consumes `gk-core/data/tuning/*.json` only for catalogs and dials (`lib/bus/actorSurface.ts:3-8`,
`gui-lego/shieldPriorityLabel.ts:5`). A TS module gives compile-time checking of `ActorId` /
`StoryCueId` membership — which is exactly the class of bug that made `speaker: string` wrong. If a
later scene must be generated or hot-swapped, moving it to `data/` is a contained change because the
contract does not move.

**Localization (S4) does not change this.** Per `localization`, the script keeps its authored English
copy and the fold resolves each string through a **stable message id**
(`scene.<sceneId>.beat<n>.line` / `.teaching`). That keeps the four Rift lines byte-identical to the
narrative source while still shipping them through lingui.

**Never:** author beat copy by hand in a **generated** tree. `gk-data/packs/fusion/data/seed/**`, `gk-data/packs/fusion/data/generated/**` and
`gk-data/packs/fusion/data/seed/atoms/generated/**` are generator outputs; editing them by hand forks the corpus from its
generator. Scene copy is not in any such tree today, and the spec keeps it that way.

---

## Success criteria

- [ ] `SceneScript` / `SceneBeat` exist as above with `speakerId?: ActorId` (optional = narration).
- [ ] The four Rift beats exist as data, byte-identical copy to today's `BEATS` const.
- [ ] Beat 3 has **no** `speakerId`; the string `"Gnome signal"` no longer appears as a speaker.
- [ ] `seal` is **dropped entirely** (dead attribute — nothing reads `data-sealed`).
- [ ] Speaker labels are cast ids (`dave`/`penny`), and the displayed name comes from `actor-cast`.
- [ ] A test asserts copy parity with the narrative source (line text unchanged after migration).
- [ ] A test asserts a beat cap guard exists and reads `maxBeatsPerScene` from
      `story-scene-ui.v1.json` — **not** a hard-coded literal in the module.
- [ ] No `sceneId`/`cueId` is ever rendered as player text.
- [ ] No generated tree is edited.
- [ ] A malformed script (zero beats) fails at module load, so the fold never sees an empty scene.

## Commands

```powershell
cd gk-web/web/fusion-rpg-web
npm test -- --run sceneScript
npm test -- --run RiftPrologueDialog
npm run build
```

## Boundaries

- **Always:** authored copy moves verbatim; ids are typed; the cap is read from tuning.
- **Ask first:** changing a line's wording; adding a beat; adding a new field to `SceneBeat`.
- **Never:** put copy in a component `const`; hand-edit a generated tree; re-hard-code a beat count as
  a literal in code; add a field that only one scene needs.

## Project structure

```text
gk-web/web/fusion-rpg-web/src/features/story-scene/sceneScript.ts       # contract + Rift prologue script
gk-web/web/fusion-rpg-web/src/features/story-scene/sceneScript.test.ts  # copy parity + cap guard
```
