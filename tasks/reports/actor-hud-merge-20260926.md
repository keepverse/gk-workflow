# actor-hud bottom-anchor branch — merge review

**Branch reviewed:** `codex/actor-hud-bottom-anchor-20260916`, carried onto
`merge/actor-hud-bottom-anchor-20260926` (this lane's branch). Nothing was merged into
`features/mega-merge` or `main`; the manager merges the reviewed SHA.

**Verdict: do not merge yet.** One branch-caused red test remains that I deliberately did
not fix, because the fix is an architecture decision rather than a repair (§6). Everything
else that was broken is fixed and green. One large surface — the Injector — has **no compile
evidence at all** on this machine.

---

## 1. Base

| Reading | Value |
|---|---|
| Worktree | `.claude/worktrees/actor-hud-merge-20260926` |
| Branch | `merge/actor-hud-bottom-anchor-20260926` |
| Tip at session start | `110d5e3200367b88f37ffcb925a2f060bc3b9065` |
| Forked from | `codex/actor-hud-bottom-anchor-20260916` @ `110d5e32` |
| Merge-base with `main` | `e93689bf7c340eaba12269bd6b20c2a1b9f314ce` |
| Commits ahead of `main` | 39 total, of which **35 are unique** (`git cherry`: 35 `+`, **0** `-`) |
| Files changed | **146** (`+4292 / -879`) |

The brief's numbers reproduce exactly. The other 4 of the 39 are merge commits
(`96c9abc6f`, `d2b59c758`, and two lane merges).

The session record's fence holds 140 of the 146 changed paths. The 6 outside it are all
documentation/session records and no production code, so nothing with a runtime effect is
unverifiable under this lane:

```
docs/architecture/actor-sheet-ideal.md      docs/ideas/elemental-impact-vfx.md
docs/architecture/decisions.md              tasks/sessions/actor-hud-bottom-anchor-20260916.json
                                            tasks/sessions/actor-hud-element-icons-20260917.json
                                            tasks/sessions/webview-preload-20260918.json
```

---

## 2. Tuning chain — **clean, no hand-editing**

This was the highest-risk item and it came back **clean**. The chain was published through
the tool, and it is *reproducible*, not merely plausible.

### 2.1 How the versions came to exist

Every version was an `A` (add) in git; no published version was ever modified in place:

```
$ git log --oneline --name-status --format="=== %h %s" -- data/tuning/actor-hud.v{3,4,5,6,7}.json
=== 8aee7c07c fix(actor-hud): enlarge elemental identity glyphs
A       gk-core/data/tuning/actor-hud.v7.json
=== d523feedd feat(actor-hud): publish identity element geometry
A       gk-core/data/tuning/actor-hud.v6.json
=== cd58f321a feat(actor-hud): show species element glyphs
A       gk-core/data/tuning/actor-hud.v5.json
=== d4d30c036 fix(actor-hud): anchor rows to sprite silhouettes
A       gk-core/data/tuning/actor-hud.v3.json
A       gk-core/data/tuning/actor-hud.v4.json

$ git log --oneline --diff-filter=M main..HEAD -- gk-core/data/tuning/
(no output — no tuning file was edited in place by this branch)
```

v3/v4/v5/v6 each shipped **with the publisher extended in the same commit**
(`gk-core/tools/tuning/publish.py` +52, +66, +38 lines), which is the sanctioned order: extend the
tool, then publish through it. v7 shipped without a publisher change because by then the
schema existed and a plain dotted `set` is the documented path for a rebalance.

### 2.2 Replay — the decisive test

I replayed the whole chain from `actor-hud.v2.json` through the branch's own publisher into a
scratch directory (`--tuning-dir`, the flag that exists precisely so a check never writes into
the real `gk-core/data/tuning/`), then compared byte-for-byte against the committed files.

```
$ python gk-core/tools/tuning/publish.py actor-hud --tuning-dir $scratch \
      --add-actor-hud-screen-layout --label "screen silhouette bottom anchor"
  actor-hud screen layout                              ADDED (6 screen layout key(s))
published actor-hud (v2 -> v3, 6 change(s)); v2 stays on disk for revert

$ python gk-core/tools/tuning/publish.py actor-hud --tuning-dir $scratch \
      screenGapPixels=0 screenWidthFactor=1.2 screenMinWidthPixels=48 \
      screenMaxWidthPixels=144 screenRowGapPixels=4.5 screenResourceHeightPixels=10.5 \
      --label "compact rows and enlarge screen HUD"
published actor-hud (v3 -> v4, 6 change(s))
$ ... --add-actor-hud-element-layout          --label "actor HUD element row geometry"   (v4 -> v5)
$ ... --upgrade-actor-hud-identity-element-layout --label "identity-line element geometry" (v5 -> v6)
$ ... screenIdentityElementPrimaryPixels=36 screenIdentityElementSecondaryPixels=30 \
      screenIdentityElementGapPixels=4.5 --label "actor-hud V2 live-legibility scale"   (v6 -> v7)
```

Result — every version reproduced exactly:

```
actor-hud.v3.json  replay-vs-commit: IDENTICAL
actor-hud.v4.json  replay-vs-commit: IDENTICAL
actor-hud.v5.json  replay-vs-commit: IDENTICAL
actor-hud.v6.json  replay-vs-commit: IDENTICAL
actor-hud.v7.json  replay-vs-commit: IDENTICAL
element-catalog.v2.json      replay-vs-commit: IDENTICAL
vfx.v4.json                  replay-vs-commit: IDENTICAL
```

The two non-actor-hud chains replay the same way: `element-catalog.v1 -> v2` is six
`--add-element-hud-glyph` calls, and `vfx.v3 -> v4` is one `--add-vfx-impact-stamp`.

The only difference is line endings: the publisher writes CRLF on Windows (Python text mode),
the committed files are LF. Content is identical after LF normalisation, and that difference
is git's normalisation, not a content drift.

One incidental proof the refusals are real: my first element-catalog replay guessed an id
(`wind`) that is not in the catalog. The publisher **refused by name and wrote nothing**:

```
refused: "element-catalog id 'wind' must match exactly one entry"
```

…and no `v2` appeared in the scratch directory. Fail-closed, as documented.

Corroborating audits: `gk-core/tools/tuning/resource_ownership.py --check` → `OK -- 166 generated edges
match aptitudes.v10.json's 166 resource edges exactly`; `pytest gk-core/tools/tuning` → 76 passed.

**Conclusion: the tuning chain is not a defect. It is the best-evidenced part of this branch.**

---

## 3. Verification — what I ran, and what it said

### 3.1 The scoped boundary, and a fail-fast that hid half of it

```
$ powershell.exe -NoProfile -ExecutionPolicy Bypass -Command \
    "& ./scripts/verify-change.ps1 -Paths @(<140 in-fence paths>) -Session actor-hud-merge-20260926"
```

The first attempt refused on out-of-fence paths (`path is outside session scope`), which is the
fence working. On the 140 in-fence paths the plan selected 10 boundaries and, among the checks:

| Check | Result |
|---|---|
| `doc-citations` (16 Markdown paths) | OK — 0 HIGH across D1–D4 |
| `guard: actor-hub` | `ACTOR-HUB GUARD OK` |
| `guard: dal` | `DAL GUARD OK` |
| `guard: funnel-delta` | `FUNNEL DELTA GUARD OK` |
| `guard: magic-numbers` | `MAGIC-NUMBER GUARD OK` (scanned `src`) |
| `guard: secondary-no-unity` | `SECONDARY NO-UNITY GUARD OK` |
| `guard: single-writer` | `SINGLE-WRITER GUARD OK` |
| `guard: test-substrate` | `TEST SUBSTRATE GUARD OK` |
| `guard: injector-compile` | **SKIPPED — "no MelonLoader game dir; injector NOT compiled"** |
| `pytest: tuning-py` | 26 passed |
| `test: core` | **FAILED** at `FusionRpg.Core.Expeditions.Tests` — 11 failed / 27 passed / 38 |

`verify-change.ps1:309` does `if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }`, so the harness is
fail-fast. It stopped inside `test: core` at the alphabetically-ordered
`FusionRpg.Core.Expeditions.Tests`, which meant **nine later checks never ran** — including
`core-area-hud-owners`, `core-hud`, `core-residual`, `data`, `data.user-settings`, `e2e`, and
three `guard` checks. It also meant the branch's own test homes
(`Core.Hud.Tests`, `Core.Vfx.Tests`, `Core.Overlay.Tests`) were never reached inside that
69-project list.

So I ran them directly, with the runner's own default filter read from its single source
(`scripts/test-fast.ps1:24` → `Category!=DiskSemantics&Category!=Heavy`).

### 3.2 Per-project results, with the pre-existing baseline measured

To attribute every red honestly I built a **detached temporary worktree at the merge base
`e93689bf7`** (never touching this branch or the main checkout) and ran the same projects
there. Both temporary worktrees were removed afterwards; `git worktree list` shows only this
lane's entry.

| Project | At merge base `e93689bf7` | On this branch before my fixes | On this branch now |
|---|---|---|---|
| `Core.Hud.Tests` | — | — | **97 / 0** |
| `Core.Vfx.Tests` | — | 3 failed / 177 (180) | **180 / 0** ✅ fixed |
| `Core.Overlay.Tests` | — | — | **134 / 0** |
| `Core.ActorSurface.Tests` | — | — | **34 / 0** |
| `Core.Expeditions.Tests` | **11 failed / 27 (38)** | 11 failed / 27 (38) | 11 failed — **inherited, untouched** |
| `Guard.Tests` | **1 failed / 672 (673)** | 2 failed / 679 (681) | **1 failed / 680 (681)** ✅ branch-caused one fixed |
| `Data.Tests` | — | — | **1779 / 0** |
| `E2E.Tests` | **3 failed / 276 (279)** | 3 failed / 276 (279) | 3 failed — **inherited, untouched** |
| web `npm test` | not reachable (§3.3) | unknown | **1 failed / 3264 (3265)** ❌ blocker |

The `Core.Expeditions.Tests` failure is byte-identical at the merge base and on the branch — the
same 11 test names, `Sequence contains no elements` at
`ExpeditionResolver.PlannedRungFor` (`ExpeditionResolver.cs:186`). `git diff main...HEAD --
gk-core/src/FusionRpg.Core/Expeditions/ gk-core/tests/FusionRpg.Core.Expeditions.Tests/` is **empty**. It is
inherited, and it is a second problem in a second subsystem, so I did not touch it.

The branch's Guard delta is now exactly zero: baseline 1 failure / 673 tests, branch 1 failure /
681 tests. The branch's 8 added Guard tests all pass, and the branch-caused failure is gone.

The three E2E failures are checked-in **fixture drift** in subsystems the branch never touched
(commander list, unique actor, world-turn `stateHash`); identical 3 at the merge base.

### 3.3 The web suite was unreachable, and it is red

The worktree setup script had not run its `npm ci` step (`node_modules` absent). Per AGENTS.md
I verified rather than assumed, then did it by hand: `npm ci` → 433 packages, exit 0.

Then the web check, which is what §4.1 made reachable:

```
$ powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/checks/web-fusion-rpg-web.ps1
⎯⎯⎯⎯⎯⎯ Failed Tests 1 ⎯⎯⎯⎯⎯⎯
 FAIL  src/game/scenes/importGuard.test.ts > game/ lawn-plane import guard >
       does not import React or @/lib/bus from Phaser lawn trees
+   "systems/ActorHudDisplay.ts imports @/lib/bus (@/lib/bus/actorSurface)",
 Test Files  1 failed | 386 passed (387)
      Tests  1 failed | 3264 passed (3265)
web vitest suite is red
```

1 failed of 3265. `npm run build` (tsc + vite) never ran, because the script fails fastest and
stops at the red vitest.

---

## 4. What I changed, and why

Five files, three logical commits. Explicit paths only; nothing staged with `-A`/`all`.

### 4.1 `gk-core/scripts/verification-boundaries.v1.json` — the boundaries were shadowing the web check

`cca2200c6`. The two boundaries this branch added listed **16 explicit
`gk-web/web/fusion-rpg-web/...` paths**. `Resolve-Owner` takes the most specific match, so those
explicit paths outranked the broad `gk-web/web/fusion-rpg-web/**` owner, and all 22 changed web files
resolved to a **.NET** project instead of the web project's own check:

```
BEFORE: gk-web/web/fusion-rpg-web/src/lib/bus/actorSurface.ts -> actor-hud-element-icons (module)
        test: core  [69 csproj...]          <-- and no script: web-fusion-rpg-web check

AFTER:  gk-web/web/fusion-rpg-web/src/lib/bus/actorSurface.ts -> web-fusion-rpg-web (module)
        script: web-fusion-rpg-web
```

Measured against `main`, where **exactly one** owner boundary lists web paths — the glob itself,
with no web seams. The branch was the only thing making the web check unreachable. I removed the
16 web entries so those files fall back to the existing owner; the .NET paths still resolve to
their actor-hud owners, so no coverage was lost. Registry now parses (481 boundaries) and
`guard-verification-boundaries.py` with the **full coverage walk** returns
`VERIFICATION BOUNDARY GUARD OK`.

**This is why §3.3 exists.** Fixing the shadowing is what made the web suite reachable — and
the web suite is red. The branch was hiding its own failing test.

### 4.2 `gk-core/tests/FusionRpg.Core.Vfx.Tests/**` — three stale assertions, not weakened ones

`256f43b20`. The earth-pilot work added `VfxPrimitiveKind.ImpactStamp` as a **fourth** spec of the
`combat.hit` recipe, and three assertions still pinned the old count of 3. Verified against the
code, not the comment — `VfxSeedCatalog.CreateAll` in `VfxCatalog.cs` now emits
`{ Kind = ImpactStamp, RequireElement = true }` after the Flash spec, and `ReplaceAll` validates
it and `continue`s.

These are **not population counts**; each asserts the composition of one named cue, which is the
contract, and the contract changed deliberately. The cue-roster pin
(`catalog.Ids.Count == 32`) is untouched — no cue id was added, only a primitive.

Rather than bump 3 → 4 and stop, the catalog assertion now *names* the new spec and restates what
it is for — `Kind == ImpactStamp`, element-required, `Color == TagOrElement`, `LifeSeconds == 0`,
`SizeScale == 1` — because every stamp value comes from `vfx.v4 impactStamp`, which is exactly
what `ReplaceAll` refuses a stamp for spelling out. The two admission assertions now say which
four specs they expect. `Core.Vfx.Tests` went 3 failed/177 → **180 passed / 0 failed**.

### 4.3 `gk-fusion/src/FusionRpg.Injector/Fx/{UnitFrameResolver,ImpactStampPool}.cs` — a real guard violation

`e2d512140`. `ImpactStampPool.Apply` read `sprite.bounds` directly to convert a world span into a
local scale. `Fx_only_UnitFrameResolver_reads_BodyWorld_or_bounds` reserves bounds reads in
`gk-fusion/src/FusionRpg.Injector/Fx` to `UnitFrameResolver.cs`, and the resolver's own doc says
*"consumers must not call BodyWorld or bounds directly"*. The new earth-pilot file was the only
violation in the plane:

```
gk-fusion/src/FusionRpg.Injector/Fx/ImpactStampPool.cs  ->  .bounds
  line 106:  var spriteSpan = Mathf.Max(sprite.bounds.size.x, sprite.bounds.size.y);
```

I moved the read behind a sanctioned accessor rather than relaxing the guard:
`UnitFrameResolver.SpriteSpan(Sprite?)` returns 0 for a null sprite or degenerate extent and
swallows the same engine throw the inline read sat inside, so behaviour is unchanged and
`Apply` keeps its own non-positive guard. `LawnCoordsGuardTests` went 1 failed/10 → **11 / 0**,
and a rescan of every `Fx/*.cs` except the resolver reports zero `BodyWorld` /
`GetComponentInChildren<Renderer>` / `.bounds` hits.

**Caveat, stated plainly: this edit is not compiled.** See §5.

---

## 5. What I could not do, and what that leaves unproven

1. **The Injector was never compiled — and it is this branch's largest change surface.** 57 of
   the 146 changed files are under `gk-fusion/src/FusionRpg.Injector/`, plus all three host `.csproj`
   files. `FUSIONRPG_GAME_DIR` is unset, so `guard: injector-compile` reported
   `INJECTOR COMPILE GUARD SKIPPED — no MelonLoader game dir; injector NOT compiled`, and
   `FusionRpg.Injector.Tests` is not in CI either. So the 3.9 zombie-HP interop-width fix
   (`d34553ec2`) and every Harmony-side change in this branch have **no compile evidence at all**
   from this lane. My §4.3 edit is a new method plus a one-line call-site swap in the same
   namespace (`Sprite?` → `Sprite?`, braces balanced 49/49 and 31/31) and I re-read it, but
   re-reading is not compiling. **This alone is a reason not to merge on my say-so.**

2. **No live proof, and none obtainable here.** `FUSIONRPG_GAME_POOL` and
   `FUSIONRPG_GAME_SOURCE` are both unset, so the game cannot be launched and no live slot can
   be claimed. The branch's own "v7 live proof" document (`a7c8f635f docs(actor-hud): record v7
   live proof`) is **prior evidence from another session**. I did not re-run it and I do not
   re-assert it. Unproven here: that the v7 glyph scale reads correctly in the real game, that
   the screen-space silhouette anchor lands where the author intended, and that the Earth
   impact stamp renders at all. Note also that the web HUD's element glyph sizes come from
   `hudPresentation`, which only the **server** sends
   (`ActorSurfaceCatalogHub.cs:189`); the offline `fixtureCatalog` does not set it, so with the
   fixture the computed sizes are 0 and `Apply` skips the glyphs. Live-vs-offline behaviour
   therefore differ, and I could not measure either.

3. **Nine scoped checks never executed** through the harness, because it fail-fasts on the
   inherited `Core.Expeditions.Tests` red (§3.1). I covered the branch's own test homes by
   running the projects directly, but `core-residual` in particular I have no reading for.

4. **The unfiltered suite is CI/nightly/release-owned** and I did not run it, per the
   verification boundary. `post_merge_check.py` on the merged head is also not mine to run.

5. **`docs/architecture/decisions.md` and 5 other out-of-fence paths** are changed by the branch
   but outside this lane's fence, so they are unverified here. The decisions.md edit is worth a
   manager's eye before merge: this branch adds an architecture decision and the design gate
   requires it be reviewed, not inherited.

---

## 6. Why I did not fix the web import-guard violation

`src/game/scenes/importGuard.test.ts` is red because the branch added, in the Phaser lawn plane:

```ts
// src/game/systems/ActorHudDisplay.ts:4
import { actorSurfaceCatalogNow } from "@/lib/bus/actorSurface";
```

`@/lib/bus/actorSurface` imports `react` and `@tanstack/react-query`, so this drags React into a
plane whose guard exists precisely to keep it out. There is also a **second, undetected path**:
`src/features/lawn/actorHudElementArt.ts:1` imports the same module, and
`ActorHudDisplay.ts:3` imports *that* — so React reaches the Phaser plane through the back door
even though the regex guard only inspects direct specifiers.

I did not fix it, deliberately. Every honest fix is a **contract change across the FE→game seam**,
and the branch's own design points at the shape without finishing it: it already put
`elements: { primary, secondary }` on `ActorHudSnapshot`, the contract that already crosses into
the plane via `setHudDisplay(scene, go, occ.hud)`. Completing that means adding the resolved art
URL and pixel geometry to that block and populating it on the FE side — which touches the pure
`foldActorHud` contract, `hudSnapshotsEqual` dedupe, and 4 call sites in `lawnProjectorFold.ts`.

That is a second problem in a second subsystem, and AGENTS.md is explicit that architecture
changes which lock behaviour need `decisions.md` first. Fixing it silently would have been the
worse outcome: a plausible-looking seam change in an area I have not reviewed, shipped as if it
were a repair. So it stays red and visible, and §3.3 is the evidence.

### Next steps for the manager

1. **Do not merge** on this lane's evidence. The web import guard and the missing Injector
   compile both need resolving first.
2. Dispatch the web fix as its own lane: complete the `ActorHudSnapshot.elements` contract
   (geometry + resolved art URL, resolved FE-side) so the lawn plane stops reaching `@/lib/bus`
   by both paths, then re-run `scripts/checks/web-fusion-rpg-web.ps1` — which will also, for the
   first time, run `npm run build`'s `tsc --noEmit` half. A `decisions.md` line should record
   where presentation data enters the Phaser plane.
3. Get the Injector compiled on a machine with a legal game dir, or have CI cover it. Until
   then `d34553ec2` and the whole Harmony surface are unproven.
4. Route the inherited reds to their owners, not to this branch: `Core.Expeditions.Tests` (11),
   `Guard.Tests::PlayerSpeciesMaterialiseCallerGuardTests` (1), `E2E.Tests` fixture drift (3).
   The first two are in subsystems this branch never touched; the third is stale checked-in
   fixtures for commander/unique-actor/world-turn DTOs.
5. If a live proof is required for merge, it must be re-run by someone with a game pool. The
   branch's v7 document is prior evidence and should not be counted as this lane's.

---

## 7. Files changed by this lane

| File | Commit | Why |
|---|---|---|
| `gk-core/scripts/verification-boundaries.v1.json` | `cca2200c6` | 16 web paths were shadowing the web check |
| `gk-core/tests/FusionRpg.Core.Vfx.Tests/Vfx/VfxRulesAndCatalogTests.cs` | `256f43b20` | stale 3-primitive pin → names the ImpactStamp contract |
| `gk-core/tests/FusionRpg.Core.Vfx.Tests/Vfx/VfxAdmissionTests.cs` | `256f43b20` | two stale spec-count pins 3 → 4 |
| `gk-fusion/src/FusionRpg.Injector/Fx/UnitFrameResolver.cs` | `e2d512140` | added the sanctioned `SpriteSpan` accessor (**not compiled**) |
| `gk-fusion/src/FusionRpg.Injector/Fx/ImpactStampPool.cs` | `e2d512140` | use `SpriteSpan` instead of `sprite.bounds` (**not compiled**) |
| `tasks/reports/actor-hud-merge-20260926.md` | this report | the review record |
| `tasks/sessions/actor-hud-merge-20260926.json` | session record | committed with the lane's first change |

No `gk-core/data/tuning/**` file was touched — the chain was already correct. No generated seed data
was touched. No test or guard was weakened to reach green. The main checkout was never touched.

---


# Part 2 — closing the import-guard blocker

Appended, not rewritten: §§1–7 above are the record of what the first pass found, including the
two conclusions this part revisits. **§6's conclusion was wrong on the cost, and §5.1's blocker was
caused by my own environment mistake.** Both are corrected here with evidence, not argument.

**Reviewed SHA: `7ab7f188b8c0b304c7d952307f1af55b7e5b81cb`** on
`merge/actor-hud-bottom-anchor-20260926`, tree clean. Still not merged — the manager merges.

**New verdict: still do not merge, but for one reason, and it is a different one.** Both blockers
from Part 1 are closed. The import guard is green and the Injector compiles. What the live probe
turned up instead is that the branch's headline web feature **cannot render at all**, because no
server route ever sends the one field it depends on. That is a functional gap in the feature, not
a test or guard failure, so no gate would ever have caught it. Details in §9.

---

## 8. Blocker 1 closed — the Injector compiles, and my §4.3 edit with it

**My §5.1 was a false blocker, and the cause was mine.** I read `AGENTS.md`'s
`$env:FUSIONRPG_GAME_DIR = "<game folder …>"` and set nothing, then reported "no compile evidence"
as if it were a property of this branch. It was a property of my shell. The loader-wide
`FUSIONRPG_ML_GAMEDIR` is deliberately not assignable to the 3.9 cell because it serves two cells;
the sanctioned callers pass the cell explicitly. Confirmed in
`gk-fusion/src/FusionRpg.Injector.MelonLoader.39/FusionRpg.Injector.MelonLoader.39.csproj:13` —
`MlGameDir` falls back to `$(FUSIONRPG_ML_GAMEDIR)`, and `HasMelonRefs` (line 16) gates the real
compile against a `SkipStub.cs` no-op (lines 34–36), which is the "skips loudly" behaviour.

I did not re-derive the manager's finding; I re-ran it to bind the evidence to this report, and
read `$gd` out of the repo-root `.env` rather than hardcoding it:

```
$ gd = (Get-Content D:\Works\source\plant-vs-zombie-rise-of-summoner\.env |
        Where-Object { $_ -match '^\s*FUSIONRPG_ML_GAMEDIR\s*=' }) -split '=',2
FUSIONRPG_ML_GAMEDIR = H:\Games\PVZ-Fusion-3.9_MelonLoader
is a directory: True      has MelonLoader\: True      has BepInEx\plugins: True

$ powershell.exe -NoProfile -ExecutionPolicy Bypass -Command `
    "$env:FUSIONRPG_ML_GAMEDIR='$gd'; $env:FUSIONRPG_ML_GAMEDIR_PVZRH_3_9='$gd'; `
     ./scripts/guard-injector-compile.ps1 -Root . -Session actor-hud-merge-20260926"
INJECTOR COMPILE GUARD OK — MelonLoader host compiled to
  C:\Users\NeneScarlet\AppData\Local\Temp\fusionrpg-injector-compile\
GUARD_EXIT=0
```

**This really does cover my §4.3 edit.** The host has no `ProjectReference` to the Injector; it
compiles the sources directly — `FusionRpg.Injector.MelonLoader.39.csproj:41-42`:

```xml
<Compile Include="..\FusionRpg.Injector\**\*.cs"
         Exclude="..\FusionRpg.Injector\obj\**;..\FusionRpg.Injector\bin\**;..\FusionRpg.Injector\Bridges\**" />
```

So `Fx/UnitFrameResolver.cs` and `Fx/ImpactStampPool.cs` are in that compile. `SpriteSpan` is
compiler-verified. The 57-file compile gap is closed, and the caveat under §4.3 is discharged.

**Observation recorded, not fixed (as instructed):** the `scripts/guard-injector-compile.ps1` in
this branch is an **older copy than main's** — it reads the loader-wide `FUSIONRPG_ML_GAMEDIR`
only, while main's reads `FUSIONRPG_ML_GAMEDIR_PVZRH_3_9` first and names it in its skip message.
That is why the manager had to set *both* variables. It is a merge-time observation for whoever
lands this branch, not a defect in my fence.

---

## 9. Blocker 2 closed — a mechanical extraction, and a new finding

### 9.1 What I extracted

`gk-web/web/fusion-rpg-web/src/lib/actorSurfaceCatalog.ts` (**new**) — React-free. Holds the six tuning
JSON imports, the catalog and derived-surface row types, the `Window.__fusionRpgActorSurface`
augmentation, `actorSurfaceFixture()`, `derivedSurfaceFromFixture()` and
`actorSurfaceCatalogNow()`. No hooks, no fetch, no `tryGetJson`.

`gk-web/web/fusion-rpg-web/src/lib/bus/actorSurface.ts` — now only the React/REST half: `useEffect`,
`useQuery`, `tryGetJson`, `fetchActorSurfaceCatalog`, `fetchDerivedSurface`, `useDerivedSurface`,
`useActorSurfaceCatalog`, plus `export * from "@/lib/actorSurfaceCatalog"`.

`src/game/systems/ActorHudDisplay.ts` and `src/features/lawn/actorHudElementArt.ts` — line 4
(now line 4 of the former, line 1 of the latter) repointed at the React-free module.

Naming follows the tree's own convention: flat React-free leaf modules sit directly in `src/lib/`
(`cn.ts`, `almanacText.ts`); `src/lib/bus/` is the coupled layer. No parallel layout invented.

**The second, undetected path mattered more than the reported one.** The guard only inspects
*direct* specifiers, so `actorHudElementArt.ts` importing the bus module passed CI while
`ActorHudDisplay.ts` imported *that* — React one hop away from a check that reports clean. I
repointed both, so the fix is real rather than cosmetic. Re-export means all ~40 existing
importers and every public type keep the same specifier, and the `Window` augmentation is still
declared exactly once (moving it with the cache).

**The forbidden route was not taken.** Verified, not asserted:

```
$ git diff --stat 9157c1811..HEAD -- gk-web/web/fusion-rpg-web/src/features/lawn/foldActorHud.ts \
    gk-web/web/fusion-rpg-web/src/features/lawn/lawnViewModel.ts \
    gk-web/web/fusion-rpg-web/src/features/lawn/lawnProjectorFold.ts
(empty — foldActorHud, hudSnapshotsEqual, ActorHudSnapshot and the 4 call sites are byte-identical)
```

The only behavioural edit is `fetchActorSurfaceCatalog` / `fetchDerivedSurface` naming
`actorSurfaceFixture()` where they used the module-private `fixtureCatalog` — same object.

`gk-core/data/tuning/**` untouched. No guard relaxed, exempted, or narrowed; `importGuard.test.ts` was
not edited at all.

### 9.2 The transitive check the committed guard cannot do

Because the guard sees only direct specifiers, I walked the real import graph from every
`src/game/**` root (39 files, excluding `world`/`poc`) — 86 reachable modules — looking for
`react`, `react-dom`, `@tanstack/*`, `phaser-react` or any `src/lib/bus/` module, at any depth.
The same walk was run on the branch tip before the extraction and on the merge base:

| Tree | Lawn-plane violation set |
|---|---|
| merge base `e93689bf7` | 6 entries — all via `src/contract/adapt.ts`. **No `actorSurface`.** |
| branch tip `9157c1811` (before extraction) | **7** entries — the same 6 **plus `src/lib/bus/actorSurface.ts` via `src/game/systems/ActorHudDisplay.ts`** |
| after extraction | **6** — the `actorSurface` entry is gone; the set is identical to the merge base |

So the branch added exactly one reachable violation and the extraction removed exactly that one,
restoring the lawn plane to main's baseline. `src/contract/adapt.ts` and the six bus modules it
reaches are **untouched by this branch** (`git diff --name-status main...HEAD --
gk-web/web/fusion-rpg-web/src/contract/ gk-web/web/fusion-rpg-web/src/lib/bus/` lists only `actorSurface.ts`,
my own edit). That contamination is pre-existing on main, out of scope here, and left for its
owner — I am flagging it, not fixing it.

### 9.3 The finding: the glyphs cannot render, and no gate would have caught it

Chasing the live-proof gap the manager named — "glyph sizes come from `hudPresentation`, which
only the **server** sends" — I checked whether the server sends it. It does not, because the route
does not exist:

```
$ Get-ChildItem gk-core/src/FusionRpg.Server -Recurse -Include *.cs |
    Select-String 'catalogs/actor-surface|MapGet\("/api/catalogs'
  gk-core/src/FusionRpg.Server/DerivedSurfaceEndpoints.cs:10: app.MapGet("/api/catalogs/derived-surface", ...)

$ ... Select-String '"/api/catalogs[^"]*"' -AllMatches   # every catalog route that IS mapped
  "/api/catalogs/derived-surface"
```

`/api/catalogs/actor-surface` — the URL the web client calls — **is not mapped anywhere in
`FusionRpg.Server`.** Confirmed against both live servers:

```
$ GET http://127.0.0.1:5101/api/catalogs/actor-surface     (a live server for THIS branch's worktree)
status: 200  content-type: text/html        # the SPA fallback, 403 bytes of index.html
$ GET http://127.0.0.1:5101/api/catalogs/derived-surface?lang=en&side=plant
System.String[], 18080 bytes               # a real route does return JSON
```

The chain to the defect, each step verified:

1. `tryGetJson` (`src/lib/bus/rest.ts`): status is 200, not 404, and `r.ok` is true, so it calls
   `r.json()` **on HTML**, which throws.
2. `fetchActorSurfaceCatalog`'s `catch` returns `fixtureCatalog`.
3. `fixtureCatalog` has **no** `hudPresentation` key (asserted, not read).
4. `actorSurfaceCatalogNow()` returns that catalog, so `presentation` is `undefined`.
5. `ActorHudDisplay.ts`: `primarySize = presentation ? … : 0` → `0`, and the draw site is
   `if (!texture || size <= 0) return;` → **every element glyph is skipped.**

So the web-side elemental identity glyphs — the deliverable of `8aee7c07c fix(actor-hud): enlarge
elemental identity glyphs` — **never render, in any configuration.** `ActorSurfaceCatalogHub.cs:189`
builds `HudPresentation` correctly and `ElementCatalogRow.hudGlyph` is populated, but nothing
publishes them over HTTP. The Injector-side HUD is unaffected; this is the web control room only.

This is not the offline-fixture case I hypothesised in §5.2 — the fixture is a *consequence*, not
the cause. The cause is a missing route, so no test, guard, or build gate in this repo can see it.
It needs a new endpoint (or a different field on the existing derived-surface route), which is a
contract change and outside what I was authorised to do here.

---

## 10. Re-verification — every command and its real output

Run from the worktree `D:\Works\source\plant-vs-zombie-rise-of-summoner\.claude\worktrees\actor-hud-merge-20260926`.

**10.1 The guard that was red — now 2/2:**

```
$ npx vitest run src/game/scenes/importGuard.test.ts
 ✓ src/game/scenes/importGuard.test.ts (2 tests) 7ms
 Test Files  1 passed (1)
      Tests  2 passed (2)
EXIT=0
```

**10.2 Full web suite — 3265/3265, first time ever reached on this branch:**

```
$ npm test
 Test Files  387 passed (387)
      Tests  3265 passed (3265)
   Duration  40.48s
NPM_TEST_EXIT=0
```
(the repeated `[hub-provider] joinShownPlayer failed [TypeError: fetch failed]` lines are expected
noise from tests that mock `fetch`; they fail nothing.)

**10.3 `npm run build` — the `tsc --noEmit` half, unmeasured until now:**

```
$ npm run build
…
✓ built in 13.31s
NPM_BUILD_EXIT=0
```
No type errors. This is the first time the build half has run on this branch: in Part 1
`scripts/checks/web-fusion-rpg-web.ps1` fail-fasted at the red vitest and never reached it.

Build output goes to `src/FusionRpg.Server/wwwroot/`, which `.gitignore:102 (**/wwwroot/)`
covers with **0 tracked files**, so it does not dirty the tree — checked, not assumed.

**10.4 Bundle check — run because the extraction moved a module between the plane boundary:**

```
$ npm run check:bundle
check-bundle: Phaser is absent from the entry chunk (assets/index-69CLGP7N.js) — OK
CHECK_BUNDLE_EXIT=0
```

**10.5 Scoped verification runner, injector compile no longer skipped:**

```
$ ./scripts/verify-change.ps1 -Paths @(<9 in-fence paths>) -Session actor-hud-merge-20260926
    (with FUSIONRPG_ML_GAMEDIR and FUSIONRPG_ML_GAMEDIR_PVZRH_3_9 both exported)

  gk-web/web/fusion-rpg-web/src/lib/actorSurfaceCatalog.ts    -> web-fusion-rpg-web (module)
  gk-web/web/fusion-rpg-web/src/lib/bus/actorSurface.ts        -> web-fusion-rpg-web (module)
  web/fusion-rpg-web/src/game/systems/ActorHudDisplay.ts-> web-fusion-rpg-web (module)
  gk-web/web/fusion-rpg-web/src/features/lawn/actorHudElementArt.ts -> web-fusion-rpg-web (module)
  gk-fusion/src/FusionRpg.Injector/Fx/ImpactStampPool.cs          -> injector-fallback (module)
  gk-fusion/src/FusionRpg.Injector/Fx/UnitFrameResolver.cs        -> injector-fallback (module)
  gk-core/tests/FusionRpg.Core.Vfx.Tests/Vfx/VfxAdmissionTests.cs      -> core-vfx (module)
  tests/FusionRpg.Core.Vfx.Tests/Vfx/VfxRulesAndCatalogTests.cs-> core-vfx (module)
  gk-core/scripts/verification-boundaries.v1.json               -> guard-verification-boundary-tests (focused)

ACTOR-HUB GUARD OK
FUNNEL DELTA GUARD OK — Secondary enqueue via Funnel only
INJECTOR COMPILE GUARD OK — MelonLoader host compiled to …\fusionrpg-injector-compile\
SECONDARY NO-UNITY GUARD OK — plugins Grant/Withdraw only
SINGLE-WRITER GUARD OK — no combat field writes outside EntityStatWriter.cs …
script: web-fusion-rpg-web ->  Test Files 387 passed (387) / Tests 3265 passed (3265)
                            ->  ✓ built in 13.64s
test: core-vfx            ->  Passed! - Failed: 0, Passed: 180, Total: 180
test: guard               ->  FAILED on PlayerSpeciesMaterialiseCallerGuardTests (see 10.7)
```

The vfx tests now resolve to the focused `core-vfx` boundary rather than the 69-project `core`
fallback, so the inherited `Core.Expeditions.Tests` red no longer fail-fasts this run.

**10.6 Magnitude / resource audits — run, both clean, and neither was needed:**

```
$ python gk-core/scripts/audit-magic-numbers.py
  clean
M1=0  M2=0  M3=0  M4=0
total 0 finding(s), 0 high                              EXIT=0

$ python gk-core/tools/tuning/resource_ownership.py --check
OK -- 166 generated edges match aptitudes.v10.json's 166 resource edges exactly   EXIT=0
```
I touched no magnitude and no resource edge — `gk-core/data/tuning/**` is untouched by this lane, as in
Part 1.

**10.7 Where the scoped run still stops, and why it is not mine:**

`test: guard` fails on `PlayerSpeciesMaterialiseCallerGuardTests.The_nine_pick_refusal_codes_are_a_closed_vocabulary`:

```
Expected: [···, "picks.source-below-inherit-floor", "picks.source-not-a-sacrifice", …]
Actual:   [···, "picks.source-below-inherit-floor", "picks.source-below-rank-floor", …]
                                  ↑ a tenth code now exists; the test pins "nine"
```

This is the same single failure measured at the merge base in Part 1 §3.2 (1 failed / 672 passed
at `e93689bf7`, identical test name) — pre-existing, in the fusion-pick subsystem this branch
never touches. It is the same *class* of staleness as the vfx pins I fixed in §4.2, but a
different subsystem and outside this lane's problem, so it stays red and routed. Because
`verify-change.ps1` is fail-fast, `test: guard guard.verification-boundaries` after it did not
run; that check is covered by my direct `guard-verification-boundaries.py` full-coverage-walk
run in Part 1 (`VERIFICATION BOUNDARY GUARD OK`, 481 boundaries) and by
`LawnCoordsGuardTests` 11/11.

**Standings across both parts, unchanged where noted:**

| Check | Part 1 | Now |
|---|---|---|
| web vitest | 1 failed / 3264 | **3265 / 0** |
| `tsc --noEmit` + vite | never reached | **clean** |
| `check:bundle` | not run | **OK** |
| `injector-compile` guard | SKIPPED | **OK — host compiled** |
| `Core.Vfx.Tests` | 180 / 0 | 180 / 0 |
| lawn-plane import closure | 7 entries (branch added 1) | **6 — identical to merge base** |
| `Core.Expeditions.Tests` | 11 failed (inherited) | 11 failed (inherited) |
| `Guard.Tests` | 1 failed (inherited) | 1 failed (inherited) |
| `E2E.Tests` | 3 failed (inherited) | 3 failed (inherited) |

---

## 11. Live proof — attempted, and blocked. With the probe output.

I did not deploy. The pool is unconfigured, so a worktree deploy would have overwritten the
owner's single shared game install — which `docs/contributing/session-boundary.md` §7 forbids
while another session is live, and the manager told me not to take a held install.

```
$ python gk-fusion/tools/debug-mcp/cli.py --list
20 adapters: debug_act, debug_actor, debug_call, debug_click, debug_cursor, debug_evaluate_call,
  debug_evaluate_methods, debug_evaluate_search, debug_evaluate_text, debug_events,
  debug_game_state, debug_inspect, debug_lawn_setup, debug_match, debug_menu_home,
  debug_preflight, debug_restart_game, debug_screenshot, debug_ui_nav, debug_verify

$ python gk-fusion/tools/debug-mcp/cli.py debug_preflight --json '{}'
  game-dir       FAIL  no env var (FUSIONRPG_ML_GAMEDIR, FUSIONRPG_GAME_DIR) and no usable .env
                      FUSIONRPG_ML_GAMEDIR_DEFAULT          (this worktree has no .env)
  interop-refs   FAIL  no game dir            dll-freshness  FAIL  no game dir
  data-dir       FAIL  missing dist\FusionRpg.Server\data\rpg-hot.sqlite
  server-port    PASS  :5088 free            node-modules   PASS    mcp-deps  PASS  fastmcp 4.0.3
  live.ready=false  server.reachable=false  gameProcess.running=false  injector.connected=false

$ Get-Process | ? ProcessName -match 'FusionRpg|PlantsVsZombies|MelonLoader'
  56816  FusionRpg.Server     -> D:\…\plant-vs-zombie-rise-of-summoner\dist\…              :5111
  78664  FusionRpg.Server     -> D:\…\.kilo\worktrees\actor-hud-bottom-anchor-20260916\dist\…  :5101
  (no game process running)

$ scripts/live-slot.ps1 -Status
  no pool root: pass -PoolRoot or set FUSIONRPG_GAME_POOL
```

**The blocker:** PID 78664 is a **live server for this branch's own original worktree**
(`.kilo/worktrees/actor-hud-bottom-anchor-20260916`, port 5101 — the pool's default `BasePort+1`),
and PID 56816 is the owner's main-checkout server on 5111. Live work on this branch is in progress
in another session, and `scripts/live-slot.ps1` confirms I have no slot of my own. Per §7 and the
manager's instruction I did not take the install, and I killed nothing.

**The live-vs-offline question is now answered anyway, and not in the branch's favour.** The
manager's hypothesis was that the offline *fixture* omits `hudPresentation` while a live server
supplies it. Probing the two live servers showed the opposite: **no server supplies it at all**,
because the route does not exist (§9.3). So the predicted "a live run with real glyph sizes" is not
merely unavailable to me — it is **not reachable in any deployment**. A live probe would have shown
no glyphs, and per the manager's own standard that would have proved nothing while looking like a
successful run.

**Still unproven by live evidence, and honestly so:** the Injector-side HUD on the lawn (bottom
anchor, element glyphs, the Earth impact stamp) and the v7 scale. The web-side glyphs are no
longer merely unproven — they are inert (§9.3). A real live probe remains the only way to close
the Injector-side claims, and it needs a free pool slot or the owner's go-ahead to use the shared
install.

---

## 12. What this lane changed, and what the manager should do

**Changed in Part 2 (one logical commit, `7ab7f188b`):**

| File | Why |
|---|---|
| `gk-web/web/fusion-rpg-web/src/lib/actorSurfaceCatalog.ts` | **new** — the React-free catalog, types and `window` cache |
| `gk-web/web/fusion-rpg-web/src/lib/bus/actorSurface.ts` | reduced to hooks + REST, re-exports the above |
| `gk-web/web/fusion-rpg-web/src/game/systems/ActorHudDisplay.ts` | line 4 repointed (the reported violation) |
| `gk-web/web/fusion-rpg-web/src/features/lawn/actorHudElementArt.ts` | line 1 repointed (the undetected transitive path) |

No test file was edited. `importGuard.test.ts` was left exactly as written and now passes. No
`gk-core/data/tuning/**` file, no generated seed, no `decisions.md`.

**Both original blockers are closed.** What remains is one finding that is not a gate failure:

1. **Add a route for the actor-surface catalog, or fold `hudPresentation` into
   `/api/catalogs/derived-surface`.** Until one exists, the web control room cannot draw elemental
   identity glyphs at all. `ActorSurfaceCatalogHub` already builds the DTO — this is a missing
   mapping, not missing data. This is the one thing standing between this branch and a merge, and
   it is a new-endpoint contract change, so it wants its own lane and a `decisions.md` line.
2. Note for whoever lands the branch: this branch's `scripts/guard-injector-compile.ps1` is an
   older copy than main's and reads the loader-wide var rather than the per-cell one (§8).
3. Separately, and not this branch's: the lawn plane already reaches `@/lib/bus` through
   `src/contract/adapt.ts` on `main` (§9.2). Worth a lane of its own; the committed guard cannot
   see it.
4. Inherited reds, routed to their owners, all reproduced at the merge base: `Core.Expeditions`
   11, `Guard::PlayerSpeciesMaterialiseCallerGuardTests` 1 (a stale "nine refusal codes" pin, now
   ten), `E2E` fixture drift 3.
5. Live proof of the Injector HUD still needs a free pool slot or the owner's explicit go-ahead.


---

## 13. Addendum — the two numbers §10 was missing

The scoped run in §10.5 was still streaming when I wrote that section, so §10 quoted the failing
assertion but not the run's own summary line or exit code. Both are now measured, and the runner
finished on its own. Appending rather than editing §10, per this report's append-only rule.

```
$ ./scripts/verify-change.ps1 -Paths @(<the same 9 in-fence paths>) -Session actor-hud-merge-20260926
  (FUSIONRPG_ML_GAMEDIR and FUSIONRPG_ML_GAMEDIR_PVZRH_3_9 both exported)
  output lines: 2714

  ACTOR-HUB GUARD OK
  FUNNEL DELTA GUARD OK — Secondary enqueue via Funnel only
  INJECTOR COMPILE GUARD OK — MelonLoader host compiled to …\fusionrpg-injector-compile\
  SECONDARY NO-UNITY GUARD OK — plugins Grant/Withdraw only
  SINGLE-WRITER GUARD OK — no combat field writes outside EntityStatWriter.cs …
  script: web-fusion-rpg-web  ->  Test Files 387 passed (387)
                                 Tests      3265 passed (3265)
                                 ✓ built in 13.64s
  test: core-vfx               ->  Passed!  - Failed: 0, Passed: 180, Total: 180
  test: guard                  ->  Failed!  - Failed: 1, Passed: 680, Total: 681, Duration: 8 m 20 s

  Failed FusionRpg.Guard.Tests.PlayerSpeciesMaterialiseCallerGuardTests
           .The_nine_pick_refusal_codes_are_a_closed_vocabulary [474 ms]

VERIFY_CHANGE_EXITCODE=1
```

**The runner's non-zero exit is entirely that one inherited test.** Every check selected before it
— all five guards including the now-running injector compile, the whole web check (387 files,
3265 tests, and the `tsc`+vite build), and `core-vfx` 180/0 — passed. The exit code is 1 because
`verify-change.ps1:309` fail-fasts, and `test: guard` is where the pre-existing red sits.

**A useful control falls out of it.** `Guard.Tests` reads **1 failed / 680 passed / 681** both
before Part 2 (§3.2, right after my Fx fix) and after it. Part 2 changed **zero C# files** — it is
four TypeScript files — so an identical count is the expected result, and it confirms the
extraction had no C# side effect. Compare the merge base, which read 1 failed / 672 passed / 673:
the branch's 8 added Guard tests all pass and the branch's own Guard delta remains zero.

`test: guard guard.verification-boundaries` sits after `test: guard` in the sorted plan and so did
not execute. That check is not left unevidenced: §4.1 records a direct
`guard-verification-boundaries.py` run with the **full coverage walk** (481 boundaries,
`VERIFICATION BOUNDARY GUARD OK`), which is the same code that check invokes.

Nothing in §8–§12 changes as a result of this addendum. The reviewed SHA is unchanged at
`648b07d1ac9e7d381a0432664413459f47a0ceb2` — the only commit after it is this one.

