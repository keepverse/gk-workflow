# Module: `scene-trigger`

**Program:** `story-scene` · **Map:** [../story-scene-map.md](../story-scene-map.md)
**Owner decision:** N3 (2026-09-15) — add a **minimal** trigger contract
**Touches:** new `gk-web/web/fusion-rpg-web/src/features/story-scene/sceneTrigger.ts` (+ test),
`gk-web/web/fusion-rpg-web/src/stages/sanctum/SanctumStage.tsx`
**Depends on:** `scene-script` (scene identity), the existing story-ledger read

---

## Objective

Name and type the seam that answers exactly one question — **"should this scene play for this player
right now?"** — so scene 2 has a home for its trigger without this program becoming a story engine.

The owner chose to add this contract rather than declare it out of scope. **The scope stays minimal on
purpose:** eligibility and trigger *wiring*, never arc authoring.

---

## What exists today (the seam is real, just unnamed)

`SanctumStage.tsx:85-89` already does this, inline, for one hard-coded story:

```ts
const riftStory = onboardingQuery.data?.stories.find(
  (story) => story.storyId === "rift-prologue" && story.version === 1);
const [riftOpen, setRiftOpen] = useState(false);
useEffect(() => {
  if (openLayer === null && riftStory?.eligible) setRiftOpen(true);
}, [openLayer, riftStory?.eligible]);
```

The data is **server-owned**: `useOnboarding(playerId)` returns `stories[]` with
`storyId` / `version` / `state` / `eligible`, backed by the real ledger
(`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Onboarding.cs:51-88`) and the ack endpoint
(`gk-core/src/FusionRpg.Server/OnboardingEndpoints.cs:35-40`). **The FE never invents eligibility** — this is
a read, not a rule engine.

---

## Contract

```ts
/** One server-reported story row, as the FE reads it. */
export type StoryLedgerEntry = {
  storyId: string;
  version: number;
  state: "pending" | "acknowledged" | string;
  eligible: boolean;
};

/** A scene the FE can present. Identity only — no copy lives here. */
export type SceneTriggerSpec = {
  sceneId: string;            // "rift-prologue"
  version: number;            // 1
  /** Optional extra gate evaluated IN ADDITION to the server's `eligible` flag. */
  when?: (ctx: SceneTriggerContext) => boolean;
};

export type SceneTriggerContext = {
  /** True when no other layer is open — a scene must not interrupt a panel. */
  noLayerOpen: boolean;
};

export function isSceneEligible(
  spec: SceneTriggerSpec,
  ledger: readonly StoryLedgerEntry[],
  ctx: SceneTriggerContext
): boolean;
```

### Rules (binding)

1. **The server is the authority.** `eligible` comes from the ledger; the FE's `when` can only
   **narrow**, never widen. A scene the server says is ineligible **cannot** be played by a `when`
   that returns true.
2. **`noLayerOpen` is a required precondition.** A scene open over a panel is the interrupting-dialog
   failure mode; `SanctumStage.tsx:88` already checks `openLayer === null`, and this contract keeps
   that as a first-class input rather than an inline detail.
3. **Version-pinned.** A row matches on `storyId` **and** `version` (`:85` does the same) — a bumped
   script version re-presents rather than silently matching an old acknowledgement.
4. **No copy, no arcs, no scheduling.** The spec carries identity and a predicate. **What** plays and
   **when in the story** is a future program's problem.
5. **Read-only.** The trigger never writes; only the host's acknowledgement writes (`story-scene-host`).
6. **One trigger per scene, not a queue.** Ordering among several eligible scenes is **explicitly out
   of scope** — with two eligible scenes the caller's order decides, and a future program owns
   priority. Saying this now prevents a half-built scheduler.

---

## The Sanctum integration (contained)

`SanctumStage` stops hard-coding one story id and reads the trigger instead:

```ts
const riftEligible = isSceneEligible(
  RIFT_PROLOGUE_TRIGGER,
  onboardingQuery.data?.stories ?? [],
  { noLayerOpen: openLayer === null }
);
```

Behaviour is **identical** for the prologue — same field, same version, same `openLayer === null`
guard — so this is a refactor of an inline expression into a named, typed, testable seam.

**`showFirstUserGuide={riftStory?.state === "acknowledged"}` (`:239`) is unchanged** and keeps reading
the ledger directly: it is a *guide* concern, not a scene-trigger concern, and folding it into this
contract would widen the module for no reason.

---

## Success criteria

- [ ] `isSceneEligible` exists, is pure, and is unit-tested.
- [ ] A server-`ineligible` row returns **false** even when `when` returns true (the narrow-only rule).
- [ ] `noLayerOpen: false` returns false regardless of eligibility.
- [ ] A version mismatch does not match (v2 row does not trigger a v1 script).
- [ ] A missing row returns false.
- [ ] `SanctumStage` uses the seam and its observable behaviour is unchanged (existing tests pass).
- [ ] No copy, no scene ordering, and no scheduling logic exists in this module.
- [ ] The FE never writes eligibility.
- [ ] No `stage === …` branch is added (`noStageSpecificBranch.test.ts` green).

## Commands

```powershell
cd gk-web/web/fusion-rpg-web
npm test -- --run sceneTrigger
npm test -- --run SanctumStage
npx vitest run src/shell/noStageSpecificBranch.test.ts
npm run build
```

## Boundaries

- **Always:** server-authoritative eligibility; `noLayerOpen` precondition; version pinning; pure.
- **Ask first:** adding a `when` predicate to a new scene; adding a second scene id to the FE.
- **Never:** FE-invented eligibility; scene ordering/priority; a queue or scheduler; writing from the
  trigger; a stage branch.

## Project structure

```text
gk-web/web/fusion-rpg-web/src/features/story-scene/sceneTrigger.ts
gk-web/web/fusion-rpg-web/src/features/story-scene/sceneTrigger.test.ts
gk-web/web/fusion-rpg-web/src/stages/sanctum/SanctumStage.tsx        # reads the seam
gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Onboarding.cs              # unchanged; the authority
gk-core/src/FusionRpg.Server/OnboardingEndpoints.cs                   # unchanged
```
