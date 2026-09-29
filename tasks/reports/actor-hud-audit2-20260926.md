# AUDIT-2 — the Band B element glyph: shape chosen, falsification, and the five-event measurement

**Session** `actor-hud-audit2-20260926` · **program** `actor-hud` · **branch** `features/mega-merge` ·
**base** `d06ebbd95` · **date** 2026-09-26 · **does not merge** — the manager reviews this SHA.

Defect under repair, quoted from [`tasks/actor-hud-todo.md:224`](../actor-hud-todo.md): *"The first
board-stats never draws a glyph, even on a correct build."* That file is **outside this lane's
fence**, so the AUDIT-2 row itself is left open for the manager to close; this report is the
evidence it was waiting for.

---

## 1. The shape I chose, and why the other one was rejected

**Chosen: shape 1, the defer-to-load-complete variant, reusing the loader seam the repo already
had.** Rejected: shape 2 (make the assertion patient).

Shape 2 was rejected on evidence, not taste. `syncFromModel` early-returns unless the model
revision moves — `if (model.revision <= ctx.lastApplied) return ctx.lastApplied;`
(`gk-web/web/fusion-rpg-web/src/game/systems/SyncFromModelSystem.ts:398`) — so **`setHudDisplay` is not
called per frame**. Whether a glyph appears therefore depends on *how many board-stats events have
happened*, not on whether the glyph resolves. A patient assertion makes the gate green while the
spectator canvas still shows no glyph: the same "delete the assertion" failure the audit exists to
stop, in a new position. §2 below measures that exact end state (`draws=1`, no glyph, ever).

The awaitable variant of shape 1 is also wrong *here*, and for a concrete reason rather than a
stylistic one: `syncFromModel` is synchronous, so an awaitable loader would have **no caller able
to await it**. The deferral seam already existed one function away, built for the type icons:
`ensureIcon` hooked `scene.load.once(Phaser.Loader.Events.COMPLETE, …)` into a per-scene callback
that `LawnWorldScene` wires as `SyncContext.onIconsReady` → `refreshOccupantIcons`
(`SyncFromModelSystem.ts:68-94`, `LawnWorldScene.ts:249-252`). Band B was never wired into it. So
the fix **extends the one existing art-ready refresh** rather than adding a second loader path,
which is what makes it the SOLID answer under §2.15.

### What changed

| File | Change |
|---|---|
| `src/game/systems/sceneArtState.ts` *(new)* | One owner for per-scene async art state: `requestSceneTexture` (de-dupe + failure memo + single art-ready callback), `sceneArtState`. |
| `src/game/systems/ActorHudDisplay.ts` | `ensureElementTexture` defers via `requestSceneTexture`; `setHudDisplay` takes `onReady` and threads it to the draw site. |
| `src/game/systems/SyncFromModelSystem.ts` | `ensureIcon` routes through the shared helper; `onReady` threaded through `syncOccupantBandB` / `makeOccupantGo` / `updateOccupantInPlace`; `refreshOccupantIcons` → **`refreshOccupantArt`**, which now also repaints Band B; `bustLawnIconTextures` scoped to `icon-` keys. |
| `src/game/scenes/LawnWorldScene.ts` | The `refreshOccupantIcons` → `refreshOccupantArt` rename, plus a read-only probe `__fusionRpgLawnHudElements` (see §5). |
| `e2e/helpers/actor-hud-e2e.ts` | `element0` / `element1` added to `CanvasHudExpect`; the key→child map is now data; `mockActorSurfaceCatalog` serves the shipped tuning. |
| `e2e/actor-hud.spec.ts` | Two new tests whose falsifiable property is **one** event. |
| `e2e/actor-hud-live.spec.ts` | A real-event glyph test whose window starts where a glyph is expected. |
| `docs/architecture/decisions.md` | The seam-locking row (§3). |

**No relayout risk, read rather than assumed.** The identity row's centring is computed from
`widths`, which reserves element space from the *catalog* geometry (`primarySize` / `secondarySize`),
not from texture availability (`ActorHudDisplay.ts:101-109`), and the element loop is last in the
row so nothing after it reads `identityX`. The pre-fix early return therefore left a
correctly-sized, correctly-centred hole, and filling it later cannot move the row. That is asserted
(`reserves the element slot from catalog geometry…`), not assumed.

### One latent defect the obvious fix would have introduced

A naive deferral loops forever on a 404. The pre-fix condition re-issues `scene.load.image`
whenever the key is absent and the loader is idle — and after a `FILE_LOAD_ERROR` the key is
*still* absent, so every repaint re-requests it. The fix therefore reuses the **existing**
`_iconFails` memo (`noteIconLoadFailure`, `src/features/lawn/lawnSyncGate.ts:24-32`), which is
keyed by texture key and so covers `actor-hud-element-*` with no change to the existing
`FILE_LOAD_ERROR` handler. Asserted: `does not re-request a glyph whose load failed, so a 404 cannot
loop`.

A second, subtler one, found by reasoning about what my own change implied: `bustLawnIconTextures`
cleared the shared memos **wholesale**. Once element glyphs share those memos, an icon epoch landing
mid-glyph-load would forget an in-flight request and the next repaint would re-request a key the
loader is already fetching. A type icon's key embeds the epoch and is genuinely stale; a HUD glyph's
key carries no epoch and is not. The bust is now scoped to `icon-`, with a test.

---

## 2. The falsification

**Required, and the most important thing in this report. Both halves of the fix were reverted and
both gates were observed going red.**

### 2a. The vitest gate — falsified on each half independently

Files were backed up byte-exact outside the repo and restored with `Copy-Item` (never a
`read_text`/`write_text` round-trip, per the CRLF trap).

Revert **A** — remove the Band B repaint from the refresh seam (drop `syncOccupantBandB(ctx.scene,
rec.go, occ, ctx.onIconsReady)` from `refreshOccupantArt`):

```
× draws the glyph on the FIRST snapshot, with no further HUD event
× repaints through refreshOccupantArt, so a HUD that never changes still gains its glyph
✓ does not re-request a glyph whose load failed, so a 404 cannot loop
✓ requests nothing for an element the catalog gives no glyph, and draws no empty slot
✓ reserves the element slot from catalog geometry, so filling it later cannot move the row
Tests  2 failed | 3 passed (5)
```

Revert **B** — restore, then drop the loader arming (`requestSceneTexture(scene, key, url)` with
no `onReady`): the **same two** tests fail, the same three pass. So neither half alone is
sufficient, and neither is load-bearing on its own — which is the property a two-part fix needs.

Restored hash: `SyncFromModelSystem.ts` `392BD6E8…`, `ActorHudDisplay.ts` `3E769ABC…`.

### 2b. The e2e gate — and a false green I caught in my own test

**My first browser falsification was invalid, and the way it was invalid is worth recording.** I
reverted the source and re-ran Playwright: **8 passed**. Not a red. The reason: the mocked e2e runs
`npm run preview`, which serves the **built** bundle from `src/FusionRpg.Server/wwwroot`
(`vite.config.ts` `build.outDir`). Reverting source without rebuilding changes nothing the browser
runs, so the run silently exercised the *fixed* bundle. I only found it because a throwaway
counter I added reported `draws=0` — a value that could only mean the served bundle predated my
edit. **Any agent falsifying a web e2e must rebuild between the revert and the run**, and the
`playwright.config.ts` header already warns that `reuseExistingServer` can silently test another
worktree's build.

With the revert **and a rebuild** (`npm run build`, then `E2E_PREVIEW_PORT=4471` so no stale server
could be reused):

```
1) … both glyphs draw from ONE board-stats, with no second HUD event
   Test timeout of 30000ms exceeded.
   Error: page.waitForFunction: Test timeout of 30000ms exceeded.
     at helpers\actor-hud-e2e.ts:171
2) … the glyph is still there after unrelated model revisions, and is not re-requested
   Test timeout of 30000ms exceeded.
  2 failed
  7 passed (33.5s)
```

Both AUDIT-2 tests red; **the six pre-existing `actor-hud.spec.ts` tests stayed green** — so the
gate fails for the defect and not for collateral damage.

### 2c. The mechanism, measured rather than argued

A throwaway probe (removed before commit) counted Band B draws on the reverted, rebuilt bundle over
20 polls across ~6.5 s and four `board-stats` poll cycles:

```
433ms REQ flame.png
433ms REQ crystal.png
425ms poll0  glyph=false identity=true catalog=true draws=1 epochs=0
  …  (polls 1-19 unchanged)
1857ms POST /api/debug/board-stats   → 404
3357ms POST /api/debug/board-stats   → 404
4856ms POST /api/debug/board-stats   → 404
```

**`draws=1` and `glyph=false` for the entire window.** One draw, no glyph, ever — the audit's
"false, false, true, true" is the *benign* form of this; the malignant form is that it never
becomes true at all. `epochs=0` also **disproves** the masking theory I had formed while reading
the code: I suspected `lawn:iconEpoch` was force-resyncing the scene
(`LawnWorldScene.ts:221-227` sets `lastApplied = 0` and re-applies) and hiding the race. It fired
zero times here. Recorded because a plausible mechanism I did not verify would have been a wrong
line in this report.

`LawnPage.tsx:181` *does* poll `board-stats` every 1500 ms, but every one of those 404s in the
mocked environment, so it never bumps the revision and never redraws. It is not what saved the
pre-fix build either.

---

## 3. `decisions.md` — the seam is locked, so the row is in the same commit

I do lock the seam, so per `AGENTS.md` ("Architecture changes that lock behavior need
`decisions.md` first") the row ships with the code. It is a **new** row, appended, touching no
existing row — placed directly after the existing *Unity Actor HUD placement* row, which is the
adjacent decision. Full text as committed, at `docs/architecture/decisions.md:39`:

> **Async canvas art — one loader seam, and what a draw site may do before a texture arrives
> (2026-09-26)** — **A canvas draw site NEVER blocks on a texture and NEVER treats "not loaded yet"
> as "not in the catalog".** `scene.load` is asynchronous, and the lawn plane's model apply is
> synchronous (`syncFromModel` early-returns unless `model.revision` moves), so a draw site that
> skips a slot it has just requested produces a HUD that stays wrong until some *later* snapshot
> happens to redraw it — on a quiet board, forever. **The rule: geometry is decided from data,
> pixels are deferred to load-complete.** A slot's size, position and centring come from the runtime
> catalog (`hudPresentation`) and are computed as if the texture were already there, so the row is
> correctly laid out with a hole; the hole is filled by the loader's own completion, never by a
> retry and never by a wait in the caller. **Exactly one loader seam per scene:**
> `requestSceneTexture` (`gk-web/web/fusion-rpg-web/src/game/systems/sceneArtState.ts`) owns the request
> de-dupe, the load-failure memo and the single art-ready callback, and both draw families go
> through it — type icons and Band B glyphs. A second request/failure/repaint path for a new art
> family is a defect, not an extension. **A failure memo is mandatory, not hygiene:** a key that
> 404s is still absent, so without the memo every repaint re-requests it forever. **An epoch bust is
> scoped to the keys the epoch actually invalidates** (`icon-`); a HUD glyph's key carries no epoch
> and clearing its memo mid-flight would re-request a key the loader is already fetching. **A gate
> on this is falsifiable only by counting redraws, not by waiting:** a patient assertion is
> satisfiable by any later snapshot (this is exactly how AUDIT-2 survived a merge), so the acceptance
> is *"the glyph is present after exactly ONE event"*, never *"the glyph is present after N"*.

Citation audit on the touched doc, per the §5 checklist:
`python scripts/audit-doc-citations.py --scope docs/architecture/decisions.md` →
`115 resolvable citations checked`, **0 HIGH** on all five finding classes, exit 0.

---

## 4. The five-event measurement

### How the window was chosen, and why it is not reading an absence as a presence

The recorded caution from the Unity live lane is that **a real Peashooter's first two HUD events
carried `elements: null`**, so a window starting at board entry can contain no glyph at all, and
reading that as "still broken" would be a **third** false red. Two consequences, both applied:

1. **Every event in the window carries `elements` by construction.** The five events are built with
   `elements: { primary: … }` from the committed catalog, so the data the assertion depends on is
   guaranteed present. This is stated as a property of the window rather than left implicit.
2. **Five DISTINCT textures, not five repeats.** A first version of this measurement sent the same
   `fire`/`ice` element five times and reported `firstSample=true` from event 2 onward — which
   proves only that the texture was cached, not that event 2's draw survived a race. The published
   run therefore uses five different elements (`fire, ice, air, earth, light`), so each event's
   texture has never been requested and **each event is a genuine first-load race**. The naive run is
   not reported as a result; it is the reason the window is shaped this way.

The property measured is per-event: *after exactly ONE event for that ptr, is the glyph on the
canvas?* The pre-fix sequence `false, false, true, true` is precisely "true only because later
events arrived", so the fix must make the **first** one true.

### Raw sequence — fixed build

```
=== AUDIT-2 FIVE-EVENT SEQUENCE ===
event1 ptr=Z1 element=fire  firstSample=false -> glyphWithin5s=true
event2 ptr=Z2 element=ice   firstSample=false -> glyphWithin5s=true
event3 ptr=Z3 element=air   firstSample=false -> glyphWithin5s=true
event4 ptr=Z4 element=earth firstSample=false -> glyphWithin5s=true
event5 ptr=Z5 element=light firstSample=false -> glyphWithin5s=true
  1 passed (3.6s)
```

**Raw sequence — same measurement, fix reverted and rebuilt**

```
event1 ptr=Z1 element=fire  firstSample=false -> glyphWithin5s=false
event2 ptr=Z2 element=ice   firstSample=false -> glyphWithin5s=false
event3 ptr=Z3 element=air   firstSample=false -> glyphWithin5s=false
event4 ptr=Z4 element=earth firstSample=false -> glyphWithin5s=false
event5 ptr=Z5 element=light firstSample=false -> glyphWithin5s=false
  1 passed (28.7s)
```

Five `false → true` transitions against five `false → false`, over five distinct events and five
distinct textures. The 3.6 s vs 28.7 s wall time is the same difference seen from the other side:
the fixed build resolves each glyph as its texture lands; the reverted build burns the full 5 s
budget on each. (28.7 s not 25 s because the board-stats poll and page teardown add to it.)

---

## 5. The live-spec window, and a new probe

`e2e/actor-hud-live.spec.ts` gets a glyph test, and it cannot use the mocked spec's trick (injecting
`elements`), because its whole value is that the events are real. So the window is chosen by
**observing the data instead of assuming it**, which needed one small addition:
`window.__fusionRpgLawnHudElements` in `LawnWorldScene.ts`, a read-only view of the same fold the
canvas draws from (`{ ptr, element }` for on-canvas occupants only). It sits beside the existing
`__fusionRpgHasHudChild` probe and is deleted in `shutdown()` with it.

The live test gates on `hasElements` **first**, with a bounded budget, and its failure message names
the real cause — *"no on-canvas occupant's snapshot carried an element within 60s — the data is
absent, so the glyph cannot be asserted (do NOT read this as a broken glyph)"*. That is the third
false red closed by construction rather than by luck.

**This live test was not executed.** See §7.

---

## 6. Verification — every command, with its real output

| Command | Result |
|---|---|
| `npx vitest run src/game/systems/ActorHudElementTexture.test.ts` | **5 passed** (later **6 passed** after the epoch-bust test) |
| `npx vitest run src/game/systems/` | **7 files / 28 tests passed** |
| `npx vitest run src/game/` | **43 files / 210 tests passed** |
| `npm test` (full web suite) | **388 files / 3282 tests passed**, exit 0 |
| `npx tsc --noEmit -p tsconfig.json` | **exit 0** (run separately, because a red vitest would stop `npm run build` before tsc) |
| `npm run build` | **exit 0**, `✓ built in 12.86s` |
| `npm run check:bundle` | `Phaser is absent from the entry chunk (assets/index-dwmUKq_Y.js) — OK`, exit 0 |
| `npx playwright test e2e/actor-hud.spec.ts` (fixed) | **8 passed (5.4s)** — 6 pre-existing + 2 new |
| `npx playwright test e2e/actor-hud.spec.ts` (reverted + rebuilt) | **2 failed / 7 passed** — §2b |
| `python gk-core/scripts/verify-change.py --paths <9 paths> --session actor-hud-audit2-20260926` | **EXIT 0** — plan: 9 paths → `actor-hud-screen-anchor` + `web-fusion-rpg-web` module, `doc-citations`, `script: web-fusion-rpg-web`, `test: core`; 63 core projects executed; "full evidence: CI/nightly/release" |
| `python scripts/audit-doc-citations.py --scope docs/architecture/decisions.md` | 115 citations, **0 HIGH**, exit 0 |
| `python scripts/session-boundary-check.py --session actor-hud-audit2-20260926` | **exit 1 — one DRIFT**, see §8 |

Note on the prior lanes' claim that `Core.Expeditions.Tests` is 11/38 red: the scoped run executed
that project as part of `test: core` and the gate exited **0**, so that red did not reproduce here.
I did not investigate it (out of fence); I am not claiming it fixed, only that it was not observed.

**No new path needed a registry entry.** Asked the planner rather than grepping, per the exemption
warning: both new files (`sceneArtState.ts`, `ActorHudElementTexture.test.ts`) resolve to the
`web-fusion-rpg-web` module boundary, so `gk-core/scripts/verification-boundaries.v1.json` is **unmodified**.

---

## 7. What is NOT proven

1. **The live e2e test never ran.** `e2e/actor-hud-live.spec.ts` needs a real game, a real Injector
   and a live slot; `ACTOR_HUD_LIVE_E2E` was not set and no slot was claimed. It compiles and
   typechecks (`tsc --noEmit` exit 0 covers it) and its logic is the `hasElements` gate, but **its
   behaviour is unobserved.** The five-event measurement in §4 is the *mocked* real-browser path
   (real Chromium, real Phaser, real HTTP for the PNGs, board snapshots injected through the FE's
   own `__fusionRpgAppendLogEvent` hook) — it is **not** the Unity → Server → web ingest.
2. **The Unity HUD is untouched and unmeasured.** The Unity canvas is `ScreenSpaceOverlay` and
   cannot appear in a camera capture (`actor-hud-unity-live-20260926.md`), so whether Unity's own
   glyph has the same defect is **unknown**. It is a different presenter with its own loader, in a
   different program surface. **If the Unity path has the same race, it is not mine to fix** — the
   brief fences `src/**`, and the manager should route it. I did not go looking in `src/`.
3. **Real-run redraw cadence is unmeasured.** §2c shows a mocked board drawing once. Whether a real
   board redraws often enough to have masked this in production is not established, and it does not
   matter to the fix — but it does mean I cannot say how visible the defect was to a player.
4. **`omni` / no-glyph behaviour is asserted, not re-litigated.** A test proves the UI requests
   nothing and draws no empty slot for an element the catalog gives no glyph. Deciding whether
   `omni` *should* carry a glyph belongs to `actor-hud-element-icons-20260917` and is untouched.
5. **No screenshot.** Playwright asserted the named child exists and is bound to the catalog's art
   (`texture === "actor-hud-element-fire"`), not that it looks right. A visual check is a
   screenshot gate, and the evidence for the *pixels* is CI/owner-eyeball territory.
6. **Only Chromium, one device profile, and only the mocked project.** Firefox/WebKit/mobile not
   run.

---

## 8. Open questions and hand-offs

1. **AUDIT-2's row in `tasks/actor-hud-todo.md` is still open — deliberately.** That file is outside
   this lane's fence. It should be closed by the manager on the strength of §2 and §4.
2. **A §5 checklist box I could NOT tick: "the boundary checker is clean for my session."**
   `session-boundary-check.py` exits **1** on exactly one DRIFT: my record and
   `mega-merge-program-manager-20260925-f78e` (active, direct, same branch) both claim
   `docs/architecture/decisions.md`. I did not resolve it, because both prescribed remedies are
   unavailable to me — I cannot move the other session, and narrowing my `paths` would mean shipping
   a behaviour-locking change with no `decisions.md` row, which `AGENTS.md` forbids. What I did
   instead, and the manager should weigh:
   - `git diff --stat -- docs/architecture/decisions.md` → **`1 file changed, 1 insertion(+)`** — my
     row is the *only* uncommitted change to that file in the tree.
   - The other session's last `decisions.md` commit is `05bb50f45` ("re-point deploy-play.ps1
     citations at the Python tool (91 files)"), already landed, not in flight.
   - My change is a pure single-row append, so a textual merge is clean unless that lane adds a row
     at the same anchor.
   - `verify-change.py --session actor-hud-audit2-20260926` **exits 0** — the scoped gate does not
     fail on this box, so the merge is not blocked by tooling, only by the declaration.
   **Recommendation:** accept the row at merge; if the manager prefers a formally clean record, the
   fix is for the *mega-merge* session to drop `docs/architecture/decisions.md` from its `paths`
   (its actual work is the `.ps1`→`.py` port and does not need it), not for this lane to retreat.
3. **Worth a follow-up lane, not fixed here:** `bustLawnIconTextures` also runs on
   `lawn:iconEpoch`, which force-resyncs the whole scene (`lastApplied = 0`). A type-icon epoch bump
   therefore **rebuilds every Band B HUD stack**, destroying and recreating it. Harmless today
   (`setHudDisplay` is idempotent) and out of this lane's problem, but it is the kind of coupling
   that becomes a frame-cost or a GC problem once Band B grows.
4. **The three `_icon*` field names now cover non-icon art.** Renaming them to `_art*` would be
   clearer, but the sets are read by the existing epoch-bust and the existing `FILE_LOAD_ERROR`
   handler, so a rename buys clarity at the cost of a wider diff in a lane whose problem is the race.
   I kept the names and said why in the module comment.
5. **Any other async art on this canvas should go through `requestSceneTexture`.** That is now a
   locked rule (the `decisions.md` row), so the next art family inherits the failure memo and the
   single repaint instead of growing a second path.

---

## 9. DESIGN-GATE §5 pre-proposal checklist

| Box | Status |
|---|---|
| Subsystem(s) identified | **Yes** — §1 rows *"Anything a player sees (UI)"* and *"Proving a feature works live / any debug call used as evidence"*. |
| Session boundary recorded before first edit | **Partly — see the ordering fault below.** Record written before any code edit, but I ran `session-boundary-check.py` only at the end. |
| Boundary checker clean for my session | **NO — could not tick.** One DRIFT, another active session's declared claim on `docs/architecture/decisions.md`; both prescribed remedies unavailable to me. Measured and escalated in §8.2 rather than hidden. |
| Every doc in the §1 row(s) read this session | **Yes** — `actor-hud-map.md`, `actor-hud-ideal.md` §4.1 / §5.1a / §6, `game-gui-principles.md` GG-58 + GG-59, `fe-game-foundation.md`, `session-boundary.md`, plus §1/§2/§3/§4/§5 of the gate itself. |
| `decisions.md` checked for a covering lock | **Yes** — no row covered the FE→game async-texture seam; the nearest neighbours are *Actor-surface catalogs* (row 50) and *Unity Actor HUD placement* (row 38), both read. Hence a **new** row, not an amendment. |
| Every factual claim cites `file:line` | **Yes** throughout. |
| `audit-doc-citations.py` reports no HIGH for the doc I touched | **Yes** — 115 citations, 0 HIGH, exit 0. |
| Claims verified against CODE, not comments | **Yes** — and it changed a conclusion twice: the icon-epoch masking theory was **disproved** by measurement (`epochs=0`), and `hudPresentation`'s absence from the fixture was read in `actorSurfaceCatalog.ts:141-158` rather than taken from the prior report's prose. |
| Read the surrounding section of every rule quoted | **Yes** — notably GG-58, where I read "art has a contract and a fallback" as scoped to *absent* art and did **not** stretch it to author a new placeholder design; that would be a product decision, not this defect. |
| Tested, not assumed, every constraint reported | **Yes** — including two of my own: "the fix is falsifiable" (**it was not, at first** — §2b) and "an epoch bust is harmless" (**it was not** — §1). |
| Nothing contradicts a §2 invariant | **Yes** — §2.15 is the reason shape 1 defers through the *existing* seam instead of adding an awaitable API; §2.16 does not apply (no edge-refreshed cache here). |
| Corrections propagated to prose / map / tasks | **Partly, by fence** — the ADR row landed. `tasks/actor-hud-todo.md` AUDIT-2 is **not** updated: out of fence, handed to the manager in §8.1. |
| No assertion pins a derived-population count | **Yes** — the e2e reads the shipped `actor-hud.v7.json` + `element-catalog.v2.json` for geometry and glyph names rather than hardcoding pixels or a glyph count; the vitest asserts behaviour and one layout vector, not a roster size. |
| §2.16 trigger-set / ordering boxes | **N/A** — no event-refreshed cache, and the acceptance is order-independent (it holds with one event *or* many, and the "is not re-requested" test covers the second order explicitly). |
| No second compose / no SOLID-violating parallel path | **Yes** — this is the core of the shape decision; the loader seam is extracted and shared, not duplicated. |
| New rule has a registry row or `unguardableReason` | **Partly** — the ADR row states the rule; a *mechanical* guard for "a new draw site must go through `requestSceneTexture`" does not exist and I did not add one (a grep guard over `scene.load.image` in `src/game/**` is the obvious shape, but a new enforcement row means touching `gk-core/scripts/enforcement-registry.v1.json`, which is **actively fenced** by `mega-merge-program-manager-20260925-f78e` — named here as a hand-off, not worked around). |
