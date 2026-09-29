# `actor-hud-browser-proof-20260926` — the actor HUD element glyphs, in a real browser, over real HTTP

**Session:** `actor-hud-browser-proof-20260926` · **Branch:** `proof/actor-hud-browser-20260926`
**Worktree:** `C:/Users/NeneScarlet/AppData/Local/Temp/opencode/actor-hud-browser-proof-20260926`
**Base:** `merge/actor-hud-bottom-anchor-20260926` @ `2b220b26`, re-read with `git rev-parse` and
`git merge-base --is-ancestor 2b220b263 HEAD` (exit 0) after `git worktree add` — not taken on
trust. **Diff vs base: empty.** This lane changed no code; it adds this report and its session
record. **Not merged** — the manager merges the reviewed SHA.

---

## 1. The one-paragraph answer

**The glyphs render.** With the Server's `GET /api/catalogs/actor-surface` answering, the page's own
boot fetch receives JSON carrying `hudPresentation` 36/30/4.5 and six non-null `hudGlyph` values,
the element-art URLs it derives from those glyphs return `200 image/png`, and the Phaser canvas
identity row draws **two visible glyph images** — a larger orange flame and a smaller blue crystal —
which I can point at in a screenshot. Blocking that one route back to the SPA fallback, on the same
build and the same board, removes both glyphs from the canvas while every other HUD row (tier frame,
level band, shield bar, status chips) stays. **So the manager's hypothesis is confirmed, with one
material correction (§6) and one caveat that matters for any future test (§5).**

---

## 2. Setup — exact commands

Nothing outside the worktree was touched. No game, no install, no other session's port.

```powershell
# 1. web build. vite writes straight into the Server's wwwroot (the deployed shape).
cd <worktree>\web\fusion-rpg-web
npm run build                      # tsc --noEmit && vite build -> built in 16.70s, exit 0

# 2. server build
cd <worktree>
dotnet build gk-core/src/FusionRpg.Server -c Debug -v m
#   Build succeeded. 0 Warning(s) 0 Error(s)

# 3. give the exe a wwwroot to serve + fall back to (build output, gitignored)
Copy-Item src\FusionRpg.Server\wwwroot src\FusionRpg.Server\bin\Debug\net8.0\wwwroot -Recurse

# 4. start MY server: MY port, MY data dir. FUSIONRPG_URLS only -- this app ignores
#    --urls and ASPNETCORE_URLS (Program.cs:15-16).
$env:FUSIONRPG_URLS = "http://127.0.0.1:5131"
$env:FUSIONRPG_DATA = "C:\Users\NeneScarlet\AppData\Local\Temp\opencode\actor-hud-proof-data-20260926"
Start-Process src\FusionRpg.Server\bin\Debug\net8.0\FusionRpg.Server.exe -WorkingDirectory `
  src\FusionRpg.Server\bin\Debug\net8.0 -RedirectStandardOutput $env:FUSIONRPG_DATA\stdout.log `
  -RedirectStandardError  $env:FUSIONRPG_DATA\stderr.log
```

Server boot log (`stdout.log`), which is also the receipt that the data dir was mine:

```
[data] C:\Users\...\opencode\actor-hud-proof-data-20260926 (hot=rpg-hot.sqlite media=rpg-media.sqlite)
[species] imported the roster - 904 written, 0 unchanged, from gk-data/packs/fusion/data/generated/creatures beside the exe
[content] imported the passive-tree catalog - 42 tree(s), now at revision 1
info: Microsoft.Hosting.Lifetime[14]  Now listening on: http://127.0.0.1:5131
info: Microsoft.Hosting.Lifetime[0]   Hosting environment: Production
```

**Ports.** `5131` = this lane's Server (mine alone). **`:5088` and `:5111` were never used, and
`:5101` — the branch's own original worktree server — was left listening and untouched.** Measured
before and after:

```
5088 : free
5101 : LISTENING  (pid 78664, not mine, untouched before and after)
5111 : LISTENING  (pid 56816, not mine, untouched before and after)
5131 : free  -> mine -> free after shutdown
```

`FUSIONRPG_GAME_POOL` is unset, as the brief said. No injector was built or deployed, no game was
launched or killed, no install was read or written. `node_modules` was already present in this
worktree, so **`npm ci` did not run** — `node 25.9.0.0` against CI's Node 22 is the one environment
difference I did not eliminate.

### Why the SPA is served *by the Server* rather than by `vite preview`

`gk-web/web/fusion-rpg-web/src/lib/bus/rest.ts:1-6`:

```ts
const DEV_API = "http://127.0.0.1:5088";
export function apiBase(): string {
  if (import.meta.env.DEV) return DEV_API;
  return "";
}
```

There is no Vite proxy. In `npm run dev` the page would fetch the owner's **`:5088`**, which is
forbidden; in `vite preview` `apiBase()` is `""` and there is no backend at all, so every catalog
route 404s and the *offline* arm is reached for a fake reason. So the page had to come from the real
Server with the real SPA in its `wwwroot`: that is both the deployed shape and the only
configuration where the page's own `fetch` reaches a real `app.MapGet`.

---

## 3. The control, established before the claim

A JSON response only means something if HTML would otherwise have answered. Measured from my own
process against `:5131`, which was serving a real SPA, so the fallback had something real to return
(`Program.cs:1336` `UseStaticFiles`, `Program.cs:2289` `MapFallbackToFile("index.html")`):

```
$ python http_probe.py
control-unmapped-api       200  text/html                          403B  first80='<!doctype html> <html lang="en">   <head>     <meta charset="UTF-8" />     <meta'
control-unmapped-root      200  text/html                          403B  first80='<!doctype html> <html lang="en">   <head>     <meta charset="UTF-8" />     <meta'
positive-actor-surface     200  application/json; charset=utf-8  24968B  first80='{"tabs":[{"kind":"condition","label":"Condition","order":0,"hidden":false,"icon'
positive-derived-surface   200  application/json; charset=utf-8  18091B
positive-glyph-art         200  image/png                          4676B

=== control verdict ===
  control-unmapped-api: 200-and-html = True  (text/html, 403B)
  control-unmapped-root: 200-and-html = True  (text/html, 403B)
```

**Both unmapped paths answer `200 text/html`.** So the `200 application/json` on the actor-surface
route is a real route response and not the fallback — and a bare `200` assertion would have passed on
that HTML for this route's entire missing life. Reproduced here, not cited from the prior lane.

### The positive, through the page's own fetch path

Not by calling the endpoint in a script. The page's own boot query
(`src/app/providers.tsx:11-14` -> `useActorSurfaceCatalog` -> `fetchActorSurfaceCatalog` ->
`tryGetJson("/api/catalogs/actor-surface")`) issued the request, and the page's own
`window.__fusionRpgActorSurface` cache is what I read back. The network log is the browser's:

```
200 application/json; charset=utf-8  /api/catalogs/actor-surface
200 image/png                         /actor-hud-elements/flame.png
200 image/png                         /actor-hud-elements/crystal.png
```

`window.__fusionRpgActorSurface` as the page held it:

```
hudPresentation: {"identityElementPrimaryPixels":36,"identityElementSecondaryPixels":30,"identityElementGapPixels":4.5}
versionStamp:    aptitude:1|derived:3|status:2|resource:1|element:2|sheet:2
rows with hudGlyph: 6/7
  omni:null  fire:flame  ice:crystal  air:wind  earth:stone  light:star  dark:eclipse
```

`element:2` in the stamp is the glyph lane's fix visible in the browser, not just in a test.

---

## 4. The screenshots, and what is actually visible in them

Artifacts are under
`C:\Users\NeneScarlet\AppData\Local\Temp\opencode\actor-hud-proof-data-20260926\screenshots\`
(**not committed** — see §9).

### 4a. Server-fed canvas, cell crop — `A3-server-fed-canvas-cell.png`

The occupant's identity row, at 4x device scale. Visible, left to right: the tier frame (rounded
square), the level band `12`, then **an orange four-pointed flame glyph and a blue crystal glyph**,
sitting on the identity row above the sprite. Both element images are present and legible.

### 4b. Fixture-fed canvas, same board, same build — `B3-fixture-fed-canvas-cell.png`

Tier frame, level band `12` — **and then nothing.** The element glyphs are gone. The rest of the HUD
is unchanged (the shield bar and status chips are on their own rows and are identical). This is the
whole difference between the two arms, and it is a picture of it.

```
A3-server-fed-canvas-cell.png   sha256 497405783BA24117...
B3-fixture-fed-canvas-cell.png   sha256 2C266FD5711D46E8...   (differ, as they must)
```

### 4c. The React Inspector — the correction

`A3-server-fed-canvas-inspector.png` and `B3-fixture-fed-canvas-inspector.png` are **byte-identical**:

```
A3-server-fed-canvas-inspector.png   sha256 80EDDC09788ECF0D...
B3-fixture-fed-canvas-inspector.png  sha256 80EDDC09788ECF0D...
```

Both show the tier frame, `12`, `V`, **the orange flame and the blue crystal at 24 px**, `SHIELD
45/80`, and status chips `C` and `E`. So the Inspector renders the glyphs in *both* arms. See §6.

---

## 5. The caveat that matters more than the green: it is not immediate

The first browser arm I ran showed **no** glyph in either configuration, which would have read as
"still broken". It is not. The cause is in `ActorHudDisplay.ts:21-33`:

```ts
function ensureElementTexture(scene, elementId) {
  const url = actorHudElementArtUrl(elementId);
  if (!url) return undefined;
  const key = `actor-hud-element-${elementId}`;
  if (!scene.textures.exists(key) && !scene.load.isLoading()) {
    scene.load.image(key, url);   // async
    scene.load.start();
  }
  return scene.textures.exists(key) ? key : undefined;   // still false on this call
}
```

The call that *starts* the PNG load necessarily returns `undefined`, and
`if (!texture || size <= 0) return;` (`:133`) skips the glyph. The texture lands afterwards, but
nothing re-runs `setHudDisplay` until another board-stats arrives. Measured, arm A (server-fed),
one board-stats at a time, each a genuinely distinct snapshot so `hudSnapshotsEqual` cannot dedupe:

```
event 1 (first board-stats)                  element0=false element1=false  identity=true shield=true status0=true
event 2 (board-stats #2, distinct snapshot)  element0=false element1=false  identity=true shield=true status0=true
event 3 (board-stats #3, distinct snapshot)  element0=TRUE  element1=false  identity=true shield=true status0=true
event 4 (board-stats #4, distinct snapshot)  element0=TRUE  element1=TRUE   identity=true shield=true status0=true
event 5 (board-stats #5, distinct snapshot)  element0=TRUE  element1=TRUE   identity=true shield=true status0=true
```

Arm B (fixture-fed) over the same five events: `element0=false element1=false` throughout, and the
PNG was fetched twice by Phaser's loader in both arms (`200 image/png /actor-hud-elements/flame.png`
x2) — so the texture *was* resident in arm B too, and the only thing that differed was the size.

**What this means for the program, stated as a claim I can support:** the route fix is *necessary but
not sufficient* for a glyph to be on screen. A single-board-stats observation, or an e2e assertion
that does not re-drive the board, will read as "still broken" on a correct build. Real play sends
board-stats continuously, so the steady state is the five-event one above — but any test written from
this feature should drive the board past the load, or it will be a false red.

---

## 6. The correction: "the fixture renders nothing" is true on the canvas and FALSE on the Inspector

The brief carried the prior lane's claim that with no `hudPresentation` the sizes compute to 0 and
every glyph is skipped, so the fixture renders nothing. **Half of that is wrong, and the wrong half
is the half a player is most likely to look at.**

| surface | reads `hudPresentation`? | fixture-fed result | server-fed result |
|---|---|---|---|
| Phaser canvas identity row (`ActorHudDisplay.ts:101-136`) | **yes** — `primarySize = presentation ? …/2 : 0` | **no glyph** | **glyph, 18 px / 15 px** |
| React Inspector (`ActorHudInspector.tsx:48-51`) | **no** — fixed Tailwind `h-6 w-6` | **glyph, 24 px** | **glyph, 24 px** |

The reason the Inspector is unaffected is `src/lib/actorSurfaceCatalog.ts:16` — the offline
`fixtureCatalog` imports **`element-catalog.v2.json` directly**, the same revision the Server now
reads, so its rows already carry `hudGlyph`. The fixture is only missing `hudPresentation`, and only
the canvas consumes that. Measured as image loads through the page:

```
B3 (fixture-fed) <img> actor-hud-element-fire src=/actor-hud-elements/flame.png   loaded=true natural=64x64 rendered=21x21
B3 (fixture-fed) <img> actor-hud-element-ice   src=/actor-hud-elements/crystal.png loaded=true natural=64x64 rendered=21x21
```

(`rendered=21x21` is the 24 px Tailwind box after the flex row's layout; the point is it is
non-zero and the bitmaps decoded.)

So the accurate statement is: **before the route existed, the two HUD surfaces disagreed with each
other** — the Inspector showed the element glyphs and the canvas did not, from the same catalog and
the same snapshot. The route fix closed that disagreement. It did not turn "nothing renders" into
"something renders" on the Inspector, because the Inspector was never broken.

---

## 7. `omni` — what the UI actually does with a null glyph

`omni` declares no `hudGlyph` and is `presentationOnly: true`; `actor-hud-ideal.md:235` says
"`omni` is never a species slot". **I did not touch the data** — that belongs to the active session
`actor-hud-element-icons-20260917`. Here is only the observed behaviour, and it is a clean skip, not
a defect:

Measured on the **server-fed** configuration with two occupants in one frame — `ZO` carrying `omni`
(row 2) and `ZF` carrying `fire` (row 3), same page, same catalog, same snapshot shape:

```
omni occupant ZO  canvas: {"identity":true,"element0":false,"shield":true,"status0":true}
fire occupant ZF  canvas: {"identity":true,"element0":true, "shield":true,"status0":true}
inspector on omni: present=true, testids=[actor-hud-inspector, actor-hud-tier, actor-hud-level,
                  actor-hud-shield, actor-hud-status-command], imgCount=0
error boundary shown: false
glyph-art network requests: ["200 /actor-hud-elements/flame.png"]
```

and visible in `C2-omni-two-cells.png`: the upper (omni) identity row is the tier frame plus `12`
and nothing after it; the lower (fire) row is the tier frame, `7`, `V` and the orange flame.

Answering the brief's three possibilities directly:

- **Crash?** No. No `pageerror`, no ErrorBoundary, and the same occupant's shield and status rows
  render normally.
- **Broken image / 404?** No. `imgCount=0` means **no `<img>` element is created at all** — not a
  broken one. `actorHudElementArt.ts:6` returns `undefined` before a URL is ever built, and
  `ActorHudInspector.tsx:50` renders `url ? <img …/> : null`. The network log confirms it: only
  `flame.png` was ever requested, from the *other* occupant. **No request is made for an omni art
  URL**, so there is no wasted fetch and no console 404 for the glyph.
- **Blank cell?** Not a reserved blank — the element slot is simply **absent**, and because
  `ActorHudDisplay.ts:106` filters zero-width entries out of the layout array, the remaining identity
  items re-centre. The row is shorter and centred, not padded with a hole.

This is consistent with `actor-hud-ideal.md:235` and with the element-icons lane's existing guard
`ActorHudElementArt_covers_every_non_presentation_catalog_glyph`, which deliberately skips
`presentationOnly` rows. **I am not claiming `omni` is correct** — that is the owning lane's call and
it needs a publisher call (`gk-core/tools/tuning/publish.py`), never a hand edit.

---

## 8. What the board data was, and what that limits

Live Unity is out of scope for this lane (no `FUSIONRPG_GAME_POOL`, shared default install, and the
brief forbids deploying the injector). So the **occupant HUD snapshot was injected through the FE's
own log-event hook** — `window.__fusionRpgAppendLogEvent`, registered at
`src/lib/bus/log-store.ts:123` — carrying `board.start` + `debug.board-stats` events with the repo's
own `e2e/fixtures/actor-hud-golden.json` shape plus the branch's `elements: {primary, secondary}`
field. That is the same path the shipped mocked spec `e2e/actor-hud.spec.ts` uses.

**Therefore, precisely:**

- **Proven:** the web control room, served by the real Server, fetches the real actor-surface route
  through its own boot path, receives non-null `hudGlyph` rows and `hudPresentation`, fetches the
  element-art PNGs the HUD derives, and **draws the glyphs on the Phaser canvas** — with a
  screenshot, a display-list read, and a network log, all three agreeing.
- **Not proven:** the Unity -> Server -> web ingest. Nothing here shows that a real game produces
  these `elements` ids, or at what cadence, or that the ids a real species resolves to are among the
  six that declare a glyph.

One measured wrinkle worth recording, because it cost me a probe run and would cost a test author the
same: **`debug.board-stats` carries the whole board, not a delta.** Sending two occupants as two
events leaves only the later one on the board. Both must ride in one payload.

### Shell mocks, stated rather than hidden

To get the app to boot and stay on `#/lawn` I mocked the same shell set `e2e/helpers/mock-shell.ts`
installs (`/health`, `/api/players*`, `/api/sim` 404, `/api/unique/actors*`, `/api/relics`,
`/api/runs`, `/api/souls/**`, `/api/contracts/**`, SignalR aborted) **plus one more**:

```
/api/onboarding/*/first-open -> { opened: false, ... }
```

Needed because the rift-gate entry-landing rule (`src/shell/useEntryLanding.ts:40-49` ->
`shouldLandOnSanctum`) navigates to `/sanctum` and **replaces** the pinned route once the durable
first-open fact is true. On a deployed Server that fact genuinely is true — measured:
`{"playerId":1,"opened":true,"openedUtc":"2026-09-26T01:50:30.14Z",...}` — so a pinned `#/lawn` is
correctly overwritten and `panel-lawn-inspector` never appears. This is **correct product behaviour,
not a defect**; `opened: false` is the contract's own "not a first open" answer. The mocked routes
are all shell/progression endpoints. **`/api/catalogs/actor-surface` and `/actor-hud-elements/*` were
never mocked in the positive arm** — they went to the real Server.

In the `omni` arm only, the console also logged seven `404 (Not Found)` resource errors from
endpoints I did not mock in that particular script. They are other API calls; every HUD row under
test rendered, and they do not touch any reading above. Stated so it is not mistaken for silence.

---

## 9. What remains UNPROVEN

- **The Unity HUD.** Not started. The Injector already read `element-catalog.v2.json` before this
  branch and is unaffected by it; the Injector was **not compiled** in this lane (no game dir, so
  the injector-compile guard skips). Nothing here is evidence about the in-game HUD.
- **The real cadence.** §5's "glyphs appear after the texture lands and a later snapshot arrives" was
  measured against injected events on a synthetic cadence. Whether a real run re-drives the board
  often enough for the first-frame skip to be invisible is **not** measured, and I would not assume it.
- **The screenshots are not committed.** My fence allows exactly two added files — this report and
  the session record — so the 29 PNGs and the probe scripts live at
  `C:\Users\NeneScarlet\AppData\Local\Temp\opencode\actor-hud-proof-data-20260926\` and are **not in
  the repo**. That is a real weakness in this evidence: a merge decision resting on these images
  depends on a temp path. The owner or the manager should decide whether to admit them under
  `tasks/reports/`. The probe scripts regenerate all of it in ~4 minutes.
- **Nothing was run through `verify-change.py`.** Correct for an evidence lane: I changed no
  production path, so there is no path-owned boundary to select. The unfiltered suite is
  CI/nightly/release-owned, as the route lane and the glyph lane both stated.
- **Not re-verified by me:** the pre-existing reds the prior lanes reported
  (`FusionRpg.Core.Expeditions.Tests` 11/38, one `FusionRpg.Guard.Tests` failure in
  `PlayerSpeciesMaterialiseCallerGuardTests`). Both lanes proved them pre-existing at base; I neither
  confirmed nor contradicted that, and I did not run either project.
- **A single browser, a single build.** Chromium via Playwright 1.62.1, one `deviceScaleFactor`, one
  viewport. No Firefox, no WebKit, no mobile. The repo's own suite also runs `Desktop Chrome` only,
  so this does not narrow existing coverage — but it is one engine.

---

## 10. Open questions

1. **Should the first-frame skip be fixed, or specified?** §5 is a real behaviour: a correct build
   shows no glyph on the first board-stats. It is invisible under continuous board-stats and
   glaring under a single event. The honest options are (a) leave it and make the contract explicit,
   or (b) have `setHudDisplay` refresh once the texture's `load` completes. That is an FE behaviour
   decision in a file (`src/game/systems/ActorHudDisplay.ts`) that is inside the branch, and it is
   **not mine to make** — I am reporting it, not proposing the change as settled.
2. **Should the Inspector and the canvas be reading one sizing source?** Today one reads
   `hudPresentation` and the other hardcodes `h--w-6`, which is exactly why they disagreed for the
   route's whole missing life. Whether that asymmetry is intended is a design question for the
   actor-hud program, and `actor-hud-ideal.md` §4.1's "geometry stays in `actor-hud.v{n}.json`"
   arguably speaks to it. Not a fence decision for this lane.
3. **Does a real board ever produce `omni` in `elements.primary`?** The catalog says it is never a
   species slot, so probably not — but I never observed a real board, so "probably not" is all I
   have. The owning lane should confirm before treating the clean skip as the designed behaviour.

---

## 11. Next steps

1. **The manager can treat the web half of the actor-hud program as render-proven**, with §5 quoted
   alongside it, and with §6's correction attached: the canvas was the broken surface, the Inspector
   never was.
2. **A Unity probe is still owed and is blocked**, not optional. The blocker, named: no
   `FUSIONRPG_GAME_POOL` / `FUSIONRPG_GAME_SOURCE` is configured, so no live slot can be claimed and
   the default install is shared. Closing it needs the owner to configure the pool (or grant a clone
   path) — not an agent decision. Until then, "the in-game HUD shows the element glyphs" rests on the
   branch's own prior v7 evidence, which **I did not re-run and do not re-assert**.
3. **Add a browser regression that drives the board past the texture load.** The repo already has
   `e2e/actor-hud.spec.ts` with `expectCanvasHud`; the missing assertion is
   `hudElement0`/`hudElement1` after a second distinct `board-stats`. That is the assertion which
   would have caught the whole defect class — no route, wrong catalog revision, and the size-0 skip
   all make it red — and none of the three existed. `gk-web/web/fusion-rpg-web/e2e/**` was outside my fence
   to add.
4. **Decide the screenshots' fate** (§9).

---

## 12. Boundary

`session-boundary-check.py --session actor-hud-browser-proof-20260926` -> `clean`, exit 0.

- **Edited:** nothing. `git diff --name-only 2b220b263 HEAD` is **empty**; `git status` shows only
  this report and my own session record.
- **Read-only:** all of `src/**`, `data/**`, `gk-web/web/fusion-rpg-web/src/**`.
- **Build output written** (gitignored, not committed): `src/FusionRpg.Server/wwwroot/**` from
  `npm run build`, and a copy at `src/FusionRpg.Server/bin/Debug/net8.0/wwwroot/**`.
- **Scratch data outside the repo:** `C:\Users\NeneScarlet\AppData\Local\Temp\opencode\actor-hud-proof-data-20260926\`
  (the Server's own `rpg-hot.sqlite`, my probe scripts, and the screenshots).
- **No `git stash` / `checkout` / `reset` was run against anything.** The main checkout's dirty
  files belong to other lanes and were left alone. `:5088`, `:5101` and `:5111` were not used.
- **No game, no injector, no install.**
