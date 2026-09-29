# `actor-surface-route-20260926` — serve `GET /api/catalogs/actor-surface`

**Branch:** `fix/actor-surface-route-20260926` (worktree `.claude/worktrees/actor-surface-route-20260926`)
**Base:** `merge/actor-hud-bottom-anchor-20260926` @ `648b07d1ac9e7d381a0432664413459f47a0ceb2` — read with
`git rev-parse`, not taken on trust. Matches the number in the brief.
**HEAD:** `ca3c35c7208fc4320d33d05685607984eb87decf` (2 commits: `11e8241e0`, `ca3c35c72`)
**Not merged.** The manager merges the reviewed SHA.

> ⚠️ **The branch tip moved while this lane worked.** It is now **`dec17dff8`**
> (`docs(actor-hud): addendum — the scoped run's own summary and exit code`), not `648b07d1a` — see
> `git reflog show merge/actor-hud-bottom-anchor-20260926`. My two commits sit directly on `648b07d1a`
> and do **not** contain `dec17dff8`. That commit touches exactly one file relative to my base
> (`tasks/reports/actor-hud-merge-20260926.md`, the branch lane rewriting its own report), so there is
> **zero path overlap** with my seven, and a dry-run merge is clean:
>
> ```
> $ git merge-tree --name-only dec17dff8 HEAD | Select-String CONFLICT
>   conflict lines: 0
> $ git merge-tree --write-tree dec17dff8 HEAD
> 2765bbc4b7cee99ecf2598116649434b9db832fd
> ```
>
> This also explains a red herring worth not re-investigating: `git diff --stat 648b07d1a..HEAD` after
> the tip moved shows `tasks/reports/actor-hud-merge-20260926.md` as deleted, because the *branch* has a
> newer version of it. `git log 648b07d1a..HEAD -- <that path>` is empty — neither of my commits
> touched it.

---

## 1. The defect, re-verified independently

The manager's measurement is **confirmed**, from my own process, both ways.

The route was never mapped:

```
$ git log --all --oneline -S 'api/catalogs/actor-surface' -- gk-core/src/FusionRpg.Server
(no output)
```

`Program.cs` mapped exactly one catalog route (`app.MapDerivedSurface()`), and the SPA fallback
`app.MapFallbackToFile("index.html")` (`Program.cs:2278`) catches everything else.

### BEFORE — my own server, my own port (5199), my own scratch data dir

Bare build, no published SPA, so the fallback has no `index.html` to serve:

```
/api/catalogs/actor-surface   -> 404
/api/catalogs/derived-surface -> 200 application/json; charset=utf-8  18091 bytes
```

Deployed-server shape (a stand-in `wwwroot/index.html` written into the build output, which is what a
published Server has):

```
$ curl -s -D - http://127.0.0.1:5199/api/catalogs/actor-surface
HTTP/1.1 200 OK
Content-Length: 101
Content-Type: text/html
...
<!doctype html><html><head><title>FusionRpg</title></head><body><div id="root"></div></body></html>
```

`200` + `text/html` — exactly what the reviewing lane measured.

### Why it was invisible — and this is the part worth keeping

`gk-web/web/fusion-rpg-web/src/lib/bus/rest.ts:27-32`:

```ts
export async function tryGetJson<T>(path: string): Promise<T | null> {
  const r = await fetch(apiBase() + path);
  if (r.status === 404) return null;
  if (!r.ok) throw new Error(await httpErrorMessage(path, r));
  return r.json() as Promise<T>;
}
```

Both failure shapes land on the same fixture, by **two different lines**:

| server shape | `tryGetJson` | result |
|---|---|---|
| `200 text/html` (SPA fallback) | `r.ok` is true → `r.json()` on HTML → **throws** | caller's `catch` → `actorSurfaceFixture()` |
| `404` (no published SPA) | returns `null` at line 29 | caller's `?? actorSurfaceFixture()` |

The fixture fallback is **doubly robust**, which is exactly why a bare "200 OK" test would have passed
against HTML for the route's entire missing life. Both paths reach
`actorHudDisplay.ts:101` reading `hudPresentation` off a fixture that has no such field; the sizes
compute to 0 and `if (!texture || size <= 0) return` skips every glyph.

---

## 2. What I built

### Shape chosen: (1) a new dedicated route

`app.MapGet("/api/catalogs/actor-surface", () => Results.Ok(ActorSurfaceCatalogHub.BuildDto()));`

in a new `gk-core/src/FusionRpg.Server/ActorSurfaceEndpoints.cs` (static `MapX(this WebApplication)` extension,
the shape `DerivedSurfaceEndpoints.cs` already uses), registered in `Program.cs` beside
`app.MapDerivedSurface()`. No query parameters — the FE requests the bare path and the DTO's only
dimension is fixed at boot by `ConfigureAll`.

**Why not (2), folding `hudPresentation` into `/api/catalogs/derived-surface`:** that response is a
shipped, versioned contract (`DerivedSurfaceDto`, `SchemaVersion 2`, asserted in
`DerivedSurfaceEndpointsTests.cs:53`) with a different shape and a different consumer, and (2) would
also have required a client edit inside the branch's fence. (1) perturbs no existing response and adds
the surface `decisions.md` already declared.

### The ADR: an amendment, not a new row

`docs/architecture/decisions.md:50` — **"Actor-surface catalogs (2026-09-07)"** — already names this route
and marks it **"still open"**. So this is not a new architecture decision; it is a declared-but-unbuilt
route, and the honest ADR action is to close that declaration in place. A second row would have
duplicated a row that already governs this surface.

Text of the amendment as committed (appended to row 50, table intact at 3 pipes):

> **Amendment 2026-09-26 (`actor-surface-route`, closing this row's own "still open"): `GET
> /api/catalogs/actor-surface` now ships and answers `ActorSurfaceCatalogDto`
> (`FusionRpg.Core.ActorSurface`) — the fan-in of `tabs` / `defaultOpen` / `aptitudes` / `families` /
> `resources` / `elements` / `statuses` / `kitRoles` / `hudPresentation` / `versionStamp`. It is a PURE
> READ of the tuning-derived Hub: no store, no request, no side effect, and the response is a function of
> process state alone. It is its own route, deliberately NOT a field folded into
> `/api/catalogs/derived-surface` — that is a shipped versioned contract (`DerivedSurfaceDto`,
> `SchemaVersion 2`) and a fan-in catalog is a different shape for a different consumer. Mapped at
> `ActorSurfaceEndpoints.MapActorSurface` (`gk-core/src/FusionRpg.Server/ActorSurfaceEndpoints.cs`) beside its
> sibling `MapDerivedSurface`. The route had been requested by the FE since it landed and mapped by no
> host, ever; the gap was invisible because the client's own fallback absorbed both failure shapes (SPA
> fallback `200 text/html` → `tryGetJson` throws parsing HTML → catch → fixture; or `404` → `null` → `??`
> → the same fixture). Its `defaultOpen` field is the sheet catalog's own value, which the DTO had been
> dropping. Evidence: `tasks/reports/actor-surface-route-20260926.md`.**

and the row's own clause now reads `**shipped 2026-09-26 — the amendment at the end of this row**`
in place of `still open`.

### A second defect I found while building it, in my fence

`ActorSheetSurfaceCatalog` **has parsed `defaultOpen`** since the catalog shipped
(`ActorSheetSurfaceCatalog.cs:34,49`; `actor-sheet.v1.json` has `"defaultOpen": "condition"`), and
`BuildDto()` **dropped it**. The FE type declares it required —
`gk-web/web/fusion-rpg-web/src/lib/actorSurfaceCatalog.ts:110` — and `ActorPanel.tsx:71` seeds its active tab
from it: `useState<ActorSheetTabKind>(surface.defaultOpen)`.

So mapping the route **without** this would have traded one defect for another: the fixture path gives a
real `defaultOpen`, the served path would have given `undefined`. I added `string DefaultOpen` to
`ActorSurfaceCatalogDto`, projected through the same closed `TabKindWire` vocabulary the tab kinds use, so
`condition` stays `condition`. Verified: only one construction site of the DTO exists repo-wide
(`BuildDto`), and the call site uses named arguments, so the inserted positional parameter is safe.

---

## 3. Tests, and the falsification that shaped them

`gk-core/tests/FusionRpg.Server.Tests/ActorSurfaceEndpointsTests.cs` — 7 tests, real Kestrel on a free port
(the `DerivedSurfaceEndpointsTests` pattern; there is no `WebApplicationFactory` in this project, which
`ContentBootStartupWiringTests.cs:18-21` records as a checked fact).

| test | what it earns |
|---|---|
| `MapActorSurface_registers_the_actor_surface_pattern` | the extension's mapping, read from the built endpoint table |
| `Program_registers_the_actor_surface_route` | **the defect itself** — `Program.cs` really calls it, comments stripped |
| `Served_path_matches_the_path_the_web_client_requests` | the served path and the FE's requested path are the same string, read from both files |
| `Get_answers_json_not_the_spa_fallback` | media type is `application/json` and the first non-whitespace byte is `{` |
| `Serves_the_hub_dto_with_hud_presentation` | `hudPresentation` present with positive pixels; `defaultOpen` closes into the served tab kinds |
| `Served_shape_matches_the_fe_contract_and_is_internally_consistent` | top-level property names == the FE's own `ActorSurfaceCatalog` field list; stamp names all six catalogs; id uniqueness |
| `Two_reads_are_byte_identical` | determinism |

**No population is pinned anywhere** — no entry count, no glyph count. Asserted instead: presence,
shape, a closed property-name vocabulary, closure, uniqueness, determinism, and a structural bound
(`> 0` on the pixel fields, which is the loader's own `RequiredPositiveForVersion` bound and exactly the
zero that skipped every glyph). `guard-population-pin` reports **0 findings**.

### Two things the falsification probe caught that a green run would have hidden

I commented out the `Program.cs` registration and re-ran, twice, because a test that cannot fail is
worse than no test:

1. **The endpoint-table test was tautological.** My harness calls `_app.MapActorSurface()` itself, so
   the first draft stayed green with the registration deleted — while its doc comment claimed it "fails
   the moment the `Program.cs` registration is dropped". That claim was false. The registration now has
   its own assertion, and the endpoint-table test's claim was corrected to what it actually proves.
2. **The first comment-stripper deleted real code.** It used a `/* … */` regex, and `Program.cs` holds
   15 `/*` against 3 `*/` because `/*` occurs *inside string literals* (`"gk-data/packs/fusion/data/seed/dungeon/layouts/*.json"`).
   A lazy block regex pairs a string's opener with an unrelated closer and swallows a large span — which
   silently unregistered the very call under test. Now only `//` is stripped, and the residual gap (a
   token inside a `/* */` block) is stated in the code rather than hidden.

Final measured behaviour with the registration commented out — **only** the registration test fails:

```
Not found: "MapActorSurface()"
Failed  ActorSurfaceEndpointsTests.Program_registers_the_actor_surface_route
Passed  ActorSurfaceEndpointsTests.Served_shape_matches_the_fe_contract_and_is_internally_consistent
Passed  ActorSurfaceEndpointsTests.MapActorSurface_registers_the_actor_surface_pattern
Passed  ActorSurfaceEndpointsTests.Get_answers_json_not_the_spa_fallback
```

Restored: `Select-String '^\s*app\.MapActorSurface\(\);'` → one hit, `Program.cs:1372`.

---

## 4. Live HTTP proof

A real `FusionRpg.Server.exe` process, started by me from the worktree's own build, on
`FUSIONRPG_URLS=http://127.0.0.1:5199` with `FUSIONRPG_DATA` pointed at a scratch dir (never `:5088`,
per `session-boundary.md` §7).

### AFTER — response headers and first bytes

```
HTTP/1.1 200 OK
Content-Type: application/json; charset=utf-8
Date: Fri, 25 Sep 2026 21:04:41 GMT
Server: Kestrel
Transfer-Encoding: chunked

{"tabs":[{"kind":"condition","label":"Condition","order":0,"hidden":false,"icon":"heart-pulse"},
{"kind":"aptitudes",…},{"kind":"derived",…},{"kind":"shield",…
```

24 913 bytes. Served property names:

```
tabs, defaultOpen, aptitudes, families, resources, elements, statuses, kitRoles, hudPresentation, versionStamp
hudPresentation = {"identityElementPrimaryPixels":36,"identityElementSecondaryPixels":30,"identityElementGapPixels":4.5}
defaultOpen     = condition
two reads byte-identical: True
```

### The differential proof — all four lines from the same live process

```
/api/catalogs/derived-surface -> 200 application/json; charset=utf-8  18091B   (control, unchanged)
/api/catalogs/actor-surface   -> 200 application/json; charset=utf-8  24948B   (the fix)
/api/catalogs/no-such-route   -> 200 text/html                             101B   (SPA fallback, still live)
/health                       -> 200
```

The third line is the one that matters: the SPA fallback is **demonstrably still active on this server**
and still swallows unmapped `/api/*` paths. The new route is therefore not being answered by the
fallback — it is a real mapped route. That is a differential proof, not an assertion.

---

## 5. Verification — exact commands and real results

| command | result |
|---|---|
| `dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~ActorSurfaceEndpointsTests"` | `Passed! - Failed: 0, Passed: 7, Skipped: 0, Total: 7` |
| `dotnet test gk-core/tests/FusionRpg.Server.Tests` (whole project) | `Passed! - Failed: 0, Passed: 866, Skipped: 0, Total: 866` |
| `dotnet test gk-core/tests/FusionRpg.Core.ActorSurface.Tests` (my DTO change's own project) | `Passed! - Failed: 0, Passed: 34, Skipped: 0, Total: 34` |
| `.\scripts\guard-dal.ps1` | `DAL GUARD OK — no SQLite/SQL outside FusionRpg.Data` · exit 0 |
| `.\scripts\guard-population-pin.ps1` | `total 0 finding(s)` · exit 0 |
| `.\scripts\guard-doc-citations.ps1` | exit 0 |
| `python gk-core/scripts/guard-verification-boundaries.py` | `VERIFICATION BOUNDARY GUARD OK` · exit 0 |
| `.\scripts\guard-actor-hub.ps1` | `ACTOR-HUB GUARD OK` · exit 0 |
| `python gk-core/scripts/guard-test-substrate.py` | `TEST SUBSTRATE GUARD OK` · exit 0 |
| `python gk-core/scripts/guard-tuning-immutability.py` | `no gk-core/data/tuning/*.json changes vs HEAD` · exit 0 |
| `python scripts/session-boundary-check.py --session actor-surface-route-20260926` | `[session-boundary] clean for 'actor-surface-route-20260926'` · exit 0 |
| `.\scripts\verify-change.ps1 -Paths <6 paths> -Session actor-surface-route-20260926` | **exit 1 — see below** |

### The scoped runner is red, and it is not mine

`verify-change.ps1` selected the **whole Core test set** because `gk-core/src/FusionRpg.Core/ActorSurface/ActorSurfaceCatalogHub.cs`
is in my change, and stopped at `FusionRpg.Core.Expeditions.Tests`: **11 failed / 27 passed**.

Proven pre-existing, not inferred: I created a pristine detached worktree at the base commit and ran the
same project with none of my changes present.

```
$ git worktree add --detach .claude/worktrees/asroute-basecheck 648b07d1a
$ dotnet test gk-core/tests/FusionRpg.Core.Expeditions.Tests        # at the BASE, none of my changes
Failed! - Failed: 11, Passed: 27, Skipped: 0, Total: 38
```

Identical 11/27. The failures are `Sequence contains no elements` in
`ExpeditionResolver.PlannedRungFor` (`ExpeditionResolver.cs:186`) and a
`CreatureRankFloors.ExpeditionWildBand` admission failure — the species-rank / creature-rank area, with
no relationship to actor-surface, the route, or the catalogs I touched. The base-check worktree has been
removed.

**This matters to the manager for two reasons:** the branch tip is not green on that project, and any
lane that touches `gk-core/src/FusionRpg.Core/**` will pull the same red into its scoped run.

### Boundary mapping, and a hand-off

`gk-core/scripts/verification-boundaries.v1.json` has no focused boundary for
`gk-core/src/FusionRpg.Server/ActorSurfaceEndpoints.cs`, so it resolves to the module-level `server-fallback`
entry (`gk-core/src/FusionRpg.Server/**` → project `server`, guard `dal`). That is mapped, so it is not a
verification-boundary defect — but it is broader than the sibling `server-derived-surface` entry. **The
registry is outside my fence** (and `actor-hud-element-icons-20260917` claims
`gk-core/scripts/verification-boundaries.v1.json`), so a curated `server.actor-surface` entry with
`verificationId: server.actor-surface` is a hand-off item, not something I did.

---

## 6. Files changed

| file | change |
|---|---|
| `gk-core/src/FusionRpg.Server/ActorSurfaceEndpoints.cs` | **new** — `MapActorSurface`, the one route + the reasoning |
| `gk-core/src/FusionRpg.Server/Program.cs` | +5 — the registration beside `MapDerivedSurface()` |
| `gk-core/src/FusionRpg.Core/ActorSurface/ActorSurfaceCatalogHub.cs` | +7 — `DefaultOpen` on the DTO, projected from the sheet catalog |
| `gk-core/tests/FusionRpg.Server.Tests/ActorSurfaceEndpointsTests.cs` | **new** — 7 contract tests |
| `docs/architecture/decisions.md` | row 50 amended in place (the ADR) |
| `tasks/sessions/actor-surface-route-20260926.json` | the boundary record + the region-check and findings |
| `tasks/reports/actor-surface-route-20260926.md` | this report |

Not touched: `gk-web/web/fusion-rpg-web/**`, `data/**`, `scripts/**`,
`gk-core/tests/FusionRpg.Core.ActorSurface.Tests/**`.

Two commits: `11e8241e0` (route + DTO + tests + session record), `ca3c35c72` (ADR + this report +
record update), plus a third recording that the branch tip moved (§ header).

## 6a. Merge readiness

- Branch tip is `dec17dff8`; my base is `648b07d1a`; **0 conflicts** (`git merge-tree`).
- Path overlap with `dec17dff8`: **none**.
- No file of mine is touched by any other active session's unmerged work (§8).
- `git status` clean.

---

## 7. Open finding I did NOT fix — the element glyphs stay blank

**The Server reads `element-catalog.v1.json` (`Program.cs:102`); the Injector reads
`element-catalog.v2.json` (`RpgHost.cs:133`).** v2 is the only shipped catalog carrying `hudGlyph`:

```
v1: omni/fire/ice/air/earth/light/dark   hudGlyph = None (all seven)
v2: omni=None  fire=flame  ice=crystal  air=wind  earth=stone  light=star  dark=eclipse
```

Live measurement on my own server, from the served payload: **`hudGlyph` is null on all 7 elements.**
The FE then does `if (!entry?.hudGlyph || entry.presentationOnly) return undefined;`
(`actorHudElementArt.ts:6`), so `/actor-hud-elements/<glyph>.png` never resolves. The Unity half of the
feature has its glyphs; the web half gets nulls.

This is **not** the bug I was sent to fix, and it is **not** in my fence:

- `gk-core/data/tuning/**` is out of fence, and is never hand-edited in place regardless.
- `git log --all -S 'element-catalog.v2.json' -- gk-core/src/FusionRpg.Server/Program.cs` returns **nothing** —
  no branch has the switch, so this is an unowned gap rather than something already fixed elsewhere.
- The active session **`actor-hud-element-icons-20260917`** claims *both*
  `gk-core/data/tuning/element-catalog.v2.json` *and* `gk-core/src/FusionRpg.Server/Program.cs`, and its stated problem
  is "Show compact species-element icons in the Unity Band B Actor HUD". This is its row.

**The fix is one line** — `Program.cs:102` `element-catalog.v1.json` → `v2.json` — and the blast radius
is exactly one nullable field: same 7 ids, same `displayName`, same `color`, same `ordinal`, same
`presentationOnly`; v2 adds only `hudGlyph` (and a `_meta` block). I recommend also adding `element` to
the domain list in `ContentBootStartupWiringTests.The_server_boot_reads_the_latest_revision_of_the_domains_it_owns`
(it currently covers only `items`, `ai`, `build-preset`), because that H7 tripwire is precisely the
mechanism meant to catch a host sitting on a stale catalog revision, and `element` is not in its list.

**Do not read this commit as "the HUD renders now."** It closes the *sizing* half — `hudPresentation`
now serves 36/30/4.5 instead of nothing, so the `size <= 0` skip is gone. The *glyph URL* half is still
open and belongs to the element-icons lane.

---

## 8. Session boundary

`session-boundary-check.py --session actor-surface-route-20260926` → `clean`, exit 0.

Two **active** records claim three files I edited — `actor-hud-element-icons-20260917` and
`actor-hud-bottom-anchor-20260916`, both on `codex/actor-hud-bottom-anchor-20260916`. Region-checked per
`session-boundary.md`, no overlap, and both are already merged into my base
(`git merge-base --is-ancestor` → 0; only `dec17dff8`, a docs addendum, is unmerged):

- `Program.cs` — their hunks are at ~86-104 and ~887; mine is a 5-line block at ~1368-1372.
- `ActorSurfaceCatalogHub.cs` — theirs added `HudPresentation`/`HudGlyph`; mine adds one parameter and
  one line, and their version is already in my base.
- `decisions.md` — a whole-file table several records claim; I amend row 50 in place, so a textual
  merge stays clean unless another lane edits that same row.

Recorded in the session record, which is what makes it auditable.

---

## 9. Next steps

1. **Merge** `fix/actor-surface-route-20260926` (`11e8241e0` + the ADR commit) into the integration
   branch. No conflict expected in the three shared files.
2. **Decide the element-catalog reader** (§7). If the element-icons lane is not taking it, it is a
   one-line `Program.cs` change plus an `element` entry in the H7 tripwire test.
3. **The branch tip is red** on `FusionRpg.Core.Expeditions.Tests` (11/38), pre-existing at
   `648b07d1a`, species-rank area. It should be triaged before or alongside the merge — it is not a
   merge blocker for *this* change, but it will keep reddening scoped runs for any Core-touching lane.
4. **Optional, needs the registry owner**: a focused `server.actor-surface` verification boundary.
5. **Not done, deliberately**: no caching on the route. The DTO is a pure function of process state, so
   caching is safe to add later, but it would lock behaviour for no measured benefit — the FE calls it
   once at boot with `staleTime: Infinity`.
