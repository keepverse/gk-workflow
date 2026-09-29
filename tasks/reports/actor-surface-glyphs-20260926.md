# actor-surface-glyphs-20260926 — the Server served an element catalog that predates `hudGlyph`

**Session:** `actor-surface-glyphs-20260926` · **Branch:** `fix/actor-surface-glyphs-20260926` ·
**Base:** `merge/actor-hud-bottom-anchor-20260926` @ `06a0a085e664b87ce72a23b6ac49853acc49dfd5`
**Reviewed SHA for the manager: `4b7041615`** (plus `78295bf79`, the boundary record).

I do not merge. The manager merges `4b7041615`.

**What this closes:** the glyph half of the actor-surface catalog. **What it does not close:** any
claim that a glyph is on screen. I did not render a frame — see §7.

---

## 1. The defect, re-measured on this branch

| Reader | File | Revision |
|---|---|---|
| Server (composition root) | `gk-core/src/FusionRpg.Server/Program.cs:102` (pre-fix) | `element-catalog.v1.json` |
| Injector (host boot) | `gk-fusion/src/FusionRpg.Injector/Host/RpgHost.cs:133` | `element-catalog.v2.json` |

v2 is a **strict superset** of v1 — measured, not assumed:

```
rows v1/v2: 7 7
ids only in v1: []            ids only in v2: []
keys only in v1: []           keys only in v2: ['hudGlyph']
rows differing in a SHARED key: [('fire', {'hudGlyph': (None, 'flame')}),
                                 ('ice',  {'hudGlyph': (None, 'crystal')}),
                                 ('air',  {'hudGlyph': (None, 'wind')}),
                                 ('earth',{'hudGlyph': (None, 'stone')}),
                                 ('light',{'hudGlyph': (None, 'star')}),
                                 ('dark', {'hudGlyph': (None, 'eclipse')})]
rows WITHOUT hudGlyph: ['omni']   presentationOnly of that row: True
```

Zero rows differ in any shared key. So this was **stale wiring, not two contracts**, and the bump's
whole blast radius is one nullable field plus the `element:` segment of `BuildVersionStamp`.

The doc had already settled it before either reader was written:
`docs/architecture/actor-hud-ideal.md:234` — *"`element-catalog.v2.json` owns each concrete glyph
kind and colour"* — and §4.1's forbidden/replace table requires the renderer to accept only the
catalog-declared visual vocabulary. The Server was the reader that did not know it yet.

---

## 2. The fix

`gk-core/src/FusionRpg.Server/Program.cs`, one line (now at `:108` after the comment block):

```diff
     FusionRpg.Core.ActorSurface.ResourceSurfaceCatalogLoader.Parse(
         File.ReadAllText(Path.Combine(tuningDir, "resource-catalog.v1.json"))),
+    // v2, not v1: v2 is a strict superset ... (reason recorded in the file)
     FusionRpg.Core.ActorSurface.ElementSurfaceCatalogLoader.Parse(
-        File.ReadAllText(Path.Combine(tuningDir, "element-catalog.v1.json"))),
+        File.ReadAllText(Path.Combine(tuningDir, "element-catalog.v2.json"))),
```

**No data was edited.** `gk-core/data/tuning/**` is byte-identical to the base, and
`git log --oneline --diff-filter=M features/mega-merge..06a0a085e -- gk-core/data/tuning/` is **empty** — v2
arrived whole in the publisher commit `d523feedd` via `gk-core/tools/tuning/publish.py
--add-element-hud-glyph`, so the generator-first rule holds and still holds after this change.

---

## 3. Files changed

| File | Change |
|---|---|
| `gk-core/src/FusionRpg.Server/Program.cs` | the reader line + a comment recording why v2 |
| `gk-core/tests/FusionRpg.Server.Tests/ActorSurfaceEndpointsTests.cs` | harness correction + 3 assertions + 2 helpers |
| `tasks/sessions/actor-surface-glyphs-20260926.json` | boundary record (commit `78295bf79`) |
| `tasks/reports/actor-surface-glyphs-20260926.md` | this report |

Nothing else. `gk-web/web/fusion-rpg-web/**` was **read only** — the client already models the field
(`gk-web/web/fusion-rpg-web/src/lib/actorSurfaceCatalog.ts:89` → `hudGlyph?: string | null`), so there was
nothing to change and no reason to touch another lane's tree.

---

## 4. Tests

Three assertions, each with a **distinct** failure to catch. None pins a population
(`docs/architecture/validation-ssot.md` §1–§3): no entry count, no glyph count, no glyph name.

1. **`Server_and_Injector_hosts_read_the_same_element_catalog_revision`** — the two hosts must name
   the same file. Asserted as *agreement*, not as the literal `"v2"`, so a future v3 that moves both
   hosts stays green while a one-sided move — the exact shape of this bug — fails.
2. **`The_element_catalog_the_hosts_read_actually_carries_glyph_kinds`** — every row that *declares*
   `hudGlyph` declares it non-empty, **and** at least one row declares one.
   *Why the second half, and why it is not a population pin:* without it, assertion (1) alone would be
   satisfied by both hosts agreeing on a catalog with the field absent from every row, and "every
   declared glyph is non-empty" is vacuously true of exactly that. The bound is `>= 1` — the
   **existence of the field in the artifact**, i.e. the envelope contract of §2. It carries no upper
   bound, so shipping more elements or fewer cannot fail it; only dropping the field can. Rows that
   do *not* declare `hudGlyph` are asserted nothing at all.
3. **`Served_element_rows_carry_the_catalog_glyphs`** — through the real route, on the
   **deserialized DTO**, media type re-asserted and first non-whitespace byte asserted `'{'`. This
   catches `BuildDto` dropping the field, which nothing else in the suite would notice, and it cannot
   be satisfied by the SPA fallback. Values are compared against the catalog rows (a cross-artifact
   join), never against literals.

### The pre-existing test that encoded v1 as correct

`ActorSurfaceEndpointsTests.InitializeAsync` hardcoded
`ElementSurfaceCatalogLoader.Parse(ReadTuning("element-catalog.v1.json"))` — a literal copy of the
composition root's own stale revision. Every route assertion in that file was therefore reasoning
about a catalog production never served, which is exactly why the split stayed invisible. That line
is corrected to read whatever `Program.cs` names (`ServerElementCatalogFileName()`), with the reason
in the code and in the commit message. This is the case the brief names: a pre-existing test
encoding v1 as correct is the thing to fix.

The consequence is stated rather than hidden: the harness no longer independently pins *which*
revision. That is deliberate — the revision is pinned by assertions (1) and (2), which read
production source, so nothing became vacuous. §5 proves it.

### Results

```
dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~ActorSurfaceEndpointsTests"
Passed!  - Failed: 0, Passed: 10, Skipped: 0, Total: 10
```

### Falsification — the tests are not vacuous

Reverted the reader to `element-catalog.v1.json` and re-ran the same filter:

```
ActorSurfaceEndpointsTests.Served_element_rows_carry_the_catalog_glyphs                        [FAIL]
ActorSurfaceEndpointsTests.Server_and_Injector_hosts_read_the_same_element_catalog_revision     [FAIL]
ActorSurfaceEndpointsTests.The_element_catalog_the_hosts_read_actually_carries_glyph_kinds       [FAIL]
Failed!  - Failed: 3, Passed: 7, Skipped: 0, Total: 10
```

All three new assertions fail on the defect; **the 7 pre-existing ones stayed green with the bug
present** — direct evidence that the existing suite was blind to it. `Program.cs` was then restored
from the commit and the filter returned to 10/10 with `git status` clean.

---

## 5. Scoped verification

```
.\scripts\verify-change.ps1 -Paths @(
  'gk-core/src/FusionRpg.Server/Program.cs',
  'gk-core/tests/FusionRpg.Server.Tests/ActorSurfaceEndpointsTests.cs',
  'tasks/sessions/actor-surface-glyphs-20260926.json') -Session actor-surface-glyphs-20260926
```

Selected: `gk-core/src/FusionRpg.Server/Program.cs -> actor-hud-player-preferences (focused)`, guard
`session-boundary`, test group `guard`; DAL guard **OK**; injector-compile guard **SKIPPED** (no
MelonLoader game dir — the Injector is not compiled, stated rather than implied).

- `FusionRpg.Data.Tests` — **Passed! 8/8**
- `FusionRpg.Guard.Tests` — **Failed! 1, Passed: 680**

The single failure is
`PlayerSpeciesMaterialiseCallerGuardTests.The_nine_pick_refusal_codes_are_a_closed_vocabulary`:

```
Expected: [..., "picks.source-below-inherit-floor", "picks.source-not-a-sacrifice", "picks.source-not-materialised", "picks.source-rarity-unknown"]
Actual:   [..., "picks.source-below-inherit-floor", "picks.source-below-rank-floor",    "picks.source-not-a-sacrifice", "picks.source-not-materialised", ...]
```

**Proven pre-existing, not mine.** Same test, same failure, in a pristine detached worktree at the
base commit with `git status --porcelain` returning **0** modified files. It is a species-rank
refusal-code vocabulary, owned by the active `creature-seed-rank` (`cmdc/cs-rank`) lane, and has no
path to an element catalog. It is routed, not fixed — not this lane's fence.

Unfiltered full evidence is CI/nightly/release-owned, as `verify-change.ps1` itself states.

---

## 6. Live proof against a real server

Two real processes, each on its **own** port and its **own** scratch data directory. Never `:5088`,
never the owner's `:5111` (5111 was left listening and untouched). `FUSIONRPG_URLS` set explicitly
(`--urls`/`ASPNETCORE_URLS` are ignored by this app — `Program.cs:15-16`).

| | base `06a0a085e` (**the defect**) | fixed `4b7041615` (this lane) |
|---|---|---|
| port / data dir | `:5148` / `…\glyphs-data-base` | `:5147` / `…\glyphs-data` |
| `/health` | ready in 12s | ready in 9s |
| **CONTROL** `/api/catalogs/no-such-route` | `HTTP 200` `text/html` | `HTTP 200` `text/html` |
| `/api/catalogs/actor-surface` | `HTTP 200` `application/json; charset=utf-8` | `HTTP 200` `application/json; charset=utf-8` |
| `versionStamp` | `…\|element:1\|sheet:2` | `…\|element:2\|sheet:2` |
| rows with non-null `hudGlyph` | **0 of 7** | **6 of 7** |

### The control, which is what makes the first line mean anything

```
CONTROL  /api/catalogs/no-such-route -> HTTP 200  text/html
<!doctype html><html><head><title>glyphs control</title></head><body><div id="root">SPA FALLBACK</div></body></html>
```

An unmapped path on this Server answers **`200 text/html`**. So the JSON above is a real route
response and not the SPA — and a bare `200` assertion would have passed on that HTML for this
route's entire missing life. Both servers were given an identical `wwwroot/index.html` so the
fallback had something real to answer with; that file is **build output** (`bin/Debug/net8.0/wwwroot/`),
gitignored, not a committed artifact.

### Raw bytes relied on — fixed `:5147`

```
"elements":[{"id":"omni","displayName":"Omni","ordinal":-1,"color":"#d0d4dc","presentationOnly":true,"hudGlyph":null},
{"id":"fire","displayName":"Fire","ordinal":0,"color":"#ff5a36","presentationOnly":false,"hudGlyph":"flame"},
{"id":"ice","displayName":"Ice","ordinal":1,"color":"#7ec8ff","presentationOnly":false,"hudGlyph":"crystal"},
{"id":"air","displayName":"Air","ordinal":2,"color":"#c8f0ff","presentationOnly":false,"hudGlyph":"wind"},
{"id":"earth","displayName":"Earth","ordinal":3,"color":"#c4a35a","presentationOnly":false,"hudGlyph":"stone"},
{"id":"light","displayName":"Light","ordinal":4,"color":"#ffe566","presentationOnly":false,"hudGlyph":"star"},
{"id":"dark",…
```

```
versionStamp: aptitude:1|derived:3|status:2|resource:1|element:2|sheet:2
hudPresentation: {"identityElementPrimaryPixels":36,"identityElementSecondaryPixels":30,"identityElementGapPixels":4.5}
```

### Raw bytes relied on — base `:5148`, same request, same moment

```
"elements":[{"id":"omni",…,"presentationOnly":true,"hudGlyph":null},
{"id":"fire","displayName":"Fire","ordinal":0,"color":"#ff5a36","presentationOnly":false,"hudGlyph":null},
{"id":"ice",…
versionStamp: …|element:1|sheet:2
```

`omni` is `null` in **both** — see §8. Every other row goes `null` → its glyph kind. That single
column is the whole change.

Both servers were stopped; `:5147` and `:5148` verified free afterwards; the probe worktree was
removed with `git worktree remove --force`.

---

## 7. What remains UNPROVEN — read this before merging

- **I did not render a frame. No glyph was observed on screen.** I make no claim that the HUD draws
  a glyph. What is proven is that the served catalog now carries a glyph kind for six of seven
  elements, and that a `200 text/html` SPA fallback cannot be mistaken for that.
- **The web client was not run.** `web/fusion-rpg-web/node_modules` is absent in this worktree and I
  did not run `npm ci`. More importantly, the only render path available without a live board is the
  element-icons lane's `e2e/fixtures/actor-hud-golden.json`, which **bypasses the route entirely** —
  a screenshot from it would have been *less* probative than the live route probe and, reported as
  "the HUD renders now", actively misleading. That is the exact shape of the 2026-09-13 incident
  (`ok:true`-shaped evidence for a feature that was broken). I declined rather than manufacture it.
- **Static trace, offered as a trace and not as a render.**
  `gk-web/web/fusion-rpg-web/src/features/lawn/actorHudElementArt.ts` returns
  `/actor-hud-elements/${entry.hudGlyph}.png` when `hudGlyph` is truthy and `presentationOnly` is
  false. Against the live response above that yields `flame / crystal / wind / stone / star /
  eclipse`, and `gk-web/web/fusion-rpg-web/public/actor-hud-elements/` contains exactly those six PNGs
  (`crystal, eclipse, flame, star, stone, wind` + `manifest.json`). A path that resolves is not a
  picture that draws.
- **Not exercised:** the Unity/in-game HUD. The Injector already read v2 and is unaffected by this
  change. The injector-compile guard was **skipped** (no game dir), so the Injector was not compiled
  here.
- **The one Guard failure is pre-existing**, proven at base in a clean tree (§5).

---

## 8. Routed findings — NOT fixed here, each for a named reason

### 8a. One row of seven declares no `hudGlyph` → `actor-hud-element-icons-20260917`

`omni` carries no `hudGlyph`; its `presentationOnly` is `true`. Evidence that this is probably
intentional: `actor-hud-ideal.md:234` — *"`omni` is never a species slot"* — and that lane's own
existing guard `ActorHudHostInjectionTests.ActorHudElementArt_covers_every_non_presentation_catalog_glyph`
deliberately skips `presentationOnly` rows. **But "probably intentional" is that lane's call, not
mine, and not this lane's to make.** Both `gk-core/data/tuning/**` and the Core/Injector HUD trees are outside
my fence, so this is a report. Deciding it needs a publisher call
(`gk-core/tools/tuning/publish.py --add-element-hud-glyph`), not an edit.

### 8b. The repo already owns a guard for this exact bug class, and `element-catalog` is not on it

`gk-core/tests/FusionRpg.Guard.Tests/TuningVersionAgreementGuardTests.cs` exists for precisely this drift:

> *"**Agreement, never 'latest'.** Pointing every reader back at an older version to revert a
> balance pass stays legal; what this refuses is two readers disagreeing, which is the drift that
> makes a retune reach one path and not another."*

It scans `<domain>.v<n>.json` inside string literals under `src` and `gk-forge/tools/seedsmith/seedsmith`,
skipping comment lines, and asserts one version per domain. Its real-tree rows cover **`action-base`
and `action-rungs` only** — `element-catalog` was never added, which is why this shipped green.

Replaying that guard's own scan logic (it is `public static`, roots are parameters) over the two
trees:

```
BASE  06a0a085e:      element-catalog -> [1, 2]   (an agreement row would be RED)
FIXED (my worktree):  element-catalog -> [2]       (an agreement row would be GREEN)
```

So adding one line — `new object[] { "element-catalog" },` to `AgreedDomains()` — would have caught
this bug before it shipped and is green now. **It is the durable fix, and it is in the wrong file
for this lane:** `gk-core/tests/FusionRpg.Guard.Tests/**` is outside my fence. Route it to whoever owns that
file. My `Server_and_Injector_hosts_read_the_same_element_catalog_revision` is a deliberate stopgap in
the wrong layer, and this row should replace it rather than sit beside it.

### 8c. Pre-existing red → `creature-seed-rank` (`cmdc/cs-rank`)

§5. Unrelated, proven at base.

---

## 9. Boundary

`session-boundary-check.py --session actor-surface-glyphs-20260926` → **clean**, exit 0, before the
first edit.

Five active records claim `gk-core/src/FusionRpg.Server/Program.cs`; all five are worktree-mode, which
`session-boundary-check.py:106` permits since two worktrees meet only at the merge. Recorded with
region evidence in my session record. In short: this session's entire `Program.cs` change is one line
at `:102`; the element-icons lane's work is already merged into my base and its dirty `RpgHost.cs`
hunk is at `~:220` (elemental action VFX) with its working copy still reading `v2` at `:133`; the
previous lane's `Program.cs` hunk is the 5-line `app.MapActorSurface()` registration at `~:1365`.

The main checkout's 125 dirty files belong to other lanes and were left untouched. No `git stash`,
`checkout` or `reset` was run against anything but my own committed file.

---

## 10. Next steps

1. **Merge `4b7041615`** into `merge/actor-hud-bottom-anchor-20260926`.
2. **Route 8b** to the owner of `TuningVersionAgreementGuardTests.cs` — one line, and it closes the
   whole bug class rather than this instance. This is the highest-value follow-up in this report.
3. **Route 8a** to `actor-hud-element-icons-20260917`: confirm `omni` is meant to stay glyph-less, or
   publish it through `gk-core/tools/tuning/publish.py` (never a hand edit).
4. **A real frame is still owed** to the actor-hud program, by whoever can run the board: this report
   closes the *served-glyph* half and nothing about what is drawn.
5. `FusionRpg.Guard.Tests` is red at the base commit (§5) — the merged-head gate
   (`.claude/cmdc-agents/scripts/post_merge_check.py`) will surface it; it is not from this change.
