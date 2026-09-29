# Actor HUD — task list

**Program:** `actor-hud` · **Plan:** [actor-hud-plan.md](actor-hud-plan.md) ·
**Map:** [docs/architecture/actor-hud-map.md](../docs/architecture/actor-hud-map.md)

**Program status (2026-08-31):** **Implementation complete** for the six ship modules.
**Open amend (2026-09-07):** catalog-token **H1–H3** (see Post-ship). LIVE manual remains optional polish.

---

## P0 — Review gate

- [x] Owner review: [actor-hud-map.md](../docs/architecture/actor-hud-map.md) — signed off with shipped implementation
- [x] Owner review: [actor-hud-data-pipeline-audit-2026-08-30.md](../docs/research/actor-hud-data-pipeline-audit-2026-08-30.md) — SSOT table, pipeline, forbidden reads
- [x] Owner review: [spec-actor-hud-core.md](../docs/architecture/actor-hud/spec-actor-hud-core.md)
- [x] Owner review: [spec-actor-hud-dump.md](../docs/architecture/actor-hud/spec-actor-hud-dump.md)
- [x] Owner review: [spec-actor-hud-fold.md](../docs/architecture/actor-hud/spec-actor-hud-fold.md)
- [x] Owner review: [spec-actor-hud-unity.md](../docs/architecture/actor-hud/spec-actor-hud-unity.md)
- [x] Owner review: [spec-actor-hud-phaser.md](../docs/architecture/actor-hud/spec-actor-hud-phaser.md)
- [x] Owner review: [spec-shield-slot-migration.md](../docs/architecture/actor-hud/spec-shield-slot-migration.md)
- [x] Cross-program sign-off: commander-surface (Band A), vfx/UnitFrame, shield-system-spec
- [x] Confirm v1: boss tier omitted, HP sliver off, Phaser required for done
- [x] Confirm pipeline: Hot-only HUD read; EntityApply pin for `levelBand`; no SQL/REST mid-match

---

## P1.5 — EntityApply derived pin

Spec: [spec-actor-hud-dump.md](../docs/architecture/actor-hud/spec-actor-hud-dump.md) § EntityApply derived pin

- [x] `InjectorDerivedOverride.Pin` in `EntityApply.RunPlant` after `ActorHub.Resolve`
- [x] `InjectorDerivedOverride.Pin` in `EntityApply.RunZombie` after `ActorHub.Resolve`
- [x] Clear on match end (existing `InjectorDerivedOverride.Clear()` hook)
- [x] Doc comment updated — production cache, not cheat-only
- [x] Unit test: pin survives until die/end
- [x] Acceptance: builder can read `progression.power` for `levelBand` (pin + `PowerBandDisplay` tested; builder lands slice 2)

---

## `actor-hud-core`

Spec: [spec-actor-hud-core.md](../docs/architecture/actor-hud/spec-actor-hud-core.md)

- [x] Spec approved
- [x] DTO types in `FusionRpg.Core/Hud/`
- [x] `ActorHudLayout.Prioritize` + overflow
- [x] `PowerBandDisplay.FromTheta`
- [x] `gk-core/data/tuning/actor-hud.v1.json` + tuning hub
- [x] `ActorHudLayoutTests` green
- [x] `audit-magic-numbers.py` clean on new files
- [x] Acceptance share: priority + overflow + band tests pass
- [x] Reads pipeline SSOT only (DTO is view — no runtime reads in Core)

---

## `actor-hud-dump`

Spec: [spec-actor-hud-dump.md](../docs/architecture/actor-hud/spec-actor-hud-dump.md)

- [x] Spec approved
- [x] P1.5 EntityApply derived pin complete (prerequisite for `levelBand`)
- [x] `ActorHudBuilder` + `ActorHudCache`
- [x] `actorHud` on GameDumps plant/zombie rows
- [x] `actorHud` on `debug.board-stats` rows
- [x] Optional `debug.actor-hud` delta emit
- [x] Golden JSON tests
- [x] Invalidation unit tests
- [x] Acceptance share: golden shield + dual status snapshot
- [x] Reads pipeline SSOT only — read surface contract; no banned sources

---

## `actor-hud-fold`

Spec: [spec-actor-hud-fold.md](../docs/architecture/actor-hud/spec-actor-hud-fold.md)

- [x] Spec approved
- [x] `ActorHudSnapshot` + `Occupant.hud` in lawnViewModel
- [x] `foldActorHud` in lawnProjectorFold
- [x] OBSERVE_CHIPS extended to 13 custom status ids
- [x] `ActorHudInspector` + LawnPage integration
- [x] `lawnProjectorFold.test.ts` cases green
- [x] Acceptance share: fold populates `Occupant.hud` from `actorHud`
- [x] Reads pipeline SSOT only — fold maps wire `actorHud`; no REST/typeId tier math

---

## `actor-hud-unity`

Spec: [spec-actor-hud-unity.md](../docs/architecture/actor-hud/spec-actor-hud-unity.md)

- [x] Spec approved
- [x] `ActorHudPool` + row renderers
- [x] `ActorHudDirector` tick sync (dirty cache)
- [x] Element-colored shield segments
- [x] Status token strip + overflow pip
- [x] Guard: `ActorHudPool_uses_UnitFrameResolver`
- [x] **Visual correction (2026-09-05):** Body + worldYOffset root; TextMesh glyphs; stack pips; bar size from actor-hud tuning
- [ ] LIVE lab board eyeball (quick-start) — owner after deploy — **`live-qa` 2026-09-20 attempted**
      (evidence [actor-hud-live-eyeball.md](evidence-fragments/actor-hud-live-eyeball.md)): found the
      real reason this and the two shield-row items below were never signed off —
      `ActorHudPool.WorldHudEnabled` defaults to `false`, only the web FE's `lawn.worldHud` setting
      turns it on, and no debug-API-only probe ever flipped it. After `PUT /api/settings
      {"key":"lawn.worldHud","value":true}` (the real setting endpoint), `debug.shield.bar-status`
      showed `hudSlots` move 0→2 and `shaderOk` move false→true on a real 2-entity board — the pool is
      genuinely active. Could not conclusively read bars vs. floaters vs. status icons apart at the
      debug screenshot's 960x531 resolution. `scripts/prove-actor-hud-live.ps1` now sets
      `lawn.worldHud=true` itself as a first step so this is not rediscovered. Still needs an actual
      owner eyeball (or a higher-res live-qa screenshot pass) to tick.
- [x] Acceptance share: guard green
- [x] Reads pipeline SSOT only — builder/cache output; no direct ShieldRuntime/StatusRuntime in pool

---

## `actor-hud-phaser`

Spec: [spec-actor-hud-phaser.md](../docs/architecture/actor-hud/spec-actor-hud-phaser.md)

- [x] Spec approved
- [x] `ActorHudDisplay` helpers
- [x] `setHudDisplay` in SyncFromModelSystem
- [x] Unit test with fixture occupant
- [x] Browser canvas visual check — covered by `e2e/actor-hud.spec.ts` (`__fusionRpgHasHudChild`)
- [x] Acceptance share: sync test matches fold fixture
- [x] Reads pipeline SSOT only — `Occupant.hud` model; no raw event parse
- [x] Program E2E: `e2e/actor-hud.spec.ts` (Inspector + canvas hook)
- [x] Audit 2026-08-31: `shouldShowShield` hp guard (Unity parity); `clearEmptyShield` drops hp≤0; `syncOccupantBandB` seam + strip/overflow/chipRow unit tests; legacy chipRow e2e

---

## `shield-slot-migration`

Spec: [spec-shield-slot-migration.md](../docs/architecture/actor-hud/spec-shield-slot-migration.md)

- [x] Spec approved
- [ ] Shield row parity vs old ShieldBarPool (Body+offset, size, stack pips) — LIVE owner eyeball —
      **`live-qa` 2026-09-20 attempted**, same `world-hud-off` gate found (see the lab-board eyeball
      entry above). Could not get a live shield instance to visually confirm parity: `item.
      fx-shield-grant`'s atoms are `OnDamageDealt`/`OnTimer`/`OnSpawn`-triggered, not an instant
      grant, and none fired in the window checked (`hasInstances:false` throughout). Still open.
- [x] Remove `ShieldBarPool.TickSync` from VfxDirector
- [x] Deprecate or delete ShieldBarPool
- [x] Update shield-system-spec.md §2.6 pointer
- [ ] LIVE: no double shield bar; sustain VFX intact — owner after deploy — **`live-qa` 2026-09-20**:
      same blocker as the two items above (no live shield instance obtained in this pass to compare
      against). Still open.
- [x] Acceptance share: no TickSync; single bar per unit
- [x] Reads pipeline SSOT only — confirms no second shield data path

---

## P6 — Program E2E

- [x] `e2e/actor-hud.spec.ts` — mocked program scenarios (CI)
- [x] `e2e/actor-hud-live.spec.ts` — live injector path
- [x] Lab board + shield + statuses scenario (`setupLiveActorHudBoard` helper)
- [x] Phaser canvas assertions (`expectCanvasHud` + `__fusionRpgHasHudChild`)
- [x] Inspector `Occupant.hud` assertions match canvas
- [x] `gk-core/scripts/prove_actor_hud_live.py` owner runbook (ported from
      `scripts/prove-actor-hud-live.ps1`, retired 2026-09-29)
- [x] P6 audit fixes (2026-08-31): `live-chromium` argv auto-gate, `requestBoardSnapshot` in poll loop, `live-debug-api-core` vitest, ptr normalize in `expectCanvasHud`, mocked shield ratio / hud-clear / elite tier asserts
- [ ] Unity LIVE manual check (owner) — optional polish; see table
- [ ] **Program LIVE sign-off** (optional) — `prove_actor_hud_live.py` green + Unity eyeball

### P6 Unity LIVE manual (optional owner polish)

| Check | How |
|-------|-----|
| Single shield bar | `quick-start` + `shield/demo` — no double bar (closes P5 LIVE) |
| Sustain VFX intact | `status/apply` `expose` or `pact_mark` — marker/aura + HUD bar |
| F9 hides shield row only | Toggle F9 — identity/status rows remain |
| Stack pips | Known gap vs old pool — optional note, not blocker |

---

## Post-ship

### Catalog-token amend (required — ideal §4.1)

- [x] **H1** Core resolve API from injected status/resource catalogs (`hudToken`/`color`/`displayName`)
- [x] **H2** Unity + Phaser + fold Inspector consume H1
- [x] **H3** Delete `StatusInitials` / hashed RGB; guard against id-slice player tokens
- Coordinate with actor-sheet T16 (FE catalog fetch) — HUD owns renderer resolve; no second writer

### Optional

- [ ] Boss tier signal from expeditions → builder emits `boss`
- [ ] HP sliver when owner enables tunable
- [ ] Authored glyph *art* upgrades (sprites replacing text tokens) — only after H1–H3; not a substitute for catalog resolve
- [ ] Perf probe B2 before/after published in research
- [x] LIVE harness script — `gk-core/scripts/prove_actor_hud_live.py`

---

## Audit 2026-09-21 (routed from species-gear-chain lane sgc-1) — the v2 publish never switched its reader

- [ ] **AUDIT-1 — the host still reads `actor-hud.v1.json`, so the published v2 has no effect** · XS · deps: —
  - Found while auditing tuning files whose LATEST revision is named nowhere in code. `actor-hud.v2.json` exists
    and is the latest; `grep -rn "actor-hud.v2.json"` over `src/`, `tools/`, `web/` and `scripts/` returns
    **nothing**, while the Injector's own boot path loads **v1**:
    `gk-fusion/src/FusionRpg.Injector/Host/RpgHost.cs:203` — `ActorHudTuningLoader.Parse(File.ReadAllText(Path.Combine(tuningDir, "actor-hud.v1.json")))`.
  - The difference is real and visible, not cosmetic bookkeeping: `worldYOffset` is **0.08 in v1** and
    **-0.35 in v2** (all other keys agree). So a HUD placement correction was published and never took effect
    — the parent H7 rule ("the reader switch lands in the SAME commit as the publish") is what was missed.
  - ⚠ Also worth the owner's eye while here: `ActorHudTuningHub.Tuning` **throws** when unconfigured (it has no
    default), and the only `Configure` caller in `src/` is that same Injector site. A sweep of `src/` outside
    `Hud/` found no other reader, so the Server does not appear to read it — but any new server-side reader
    would throw at runtime rather than fall back, which is worth knowing before one is added.
  - Acceptance: either the host reads `actor-hud.v2.json` (v1 may stay on disk for revert), with the switch in the
    same commit as any future publish, or v2 is withdrawn with the reason recorded.
  - Verify: `grep -rn "actor-hud.v" --include=*.cs src/` names the version the host loads, and a test proves a
    non-default `worldYOffset` reaches the display path.
  - Files: `gk-fusion/src/FusionRpg.Injector/Host/RpgHost.cs`, `gk-core/data/tuning/actor-hud.v2.json`.


---

## Audit 2026-09-26 (routed from the actor-hud merge review and its browser-proof lane) — the branch merged, and three things it exposed

Context: `merge/actor-hud-bottom-anchor-20260926` merged into `features/mega-merge` at `679501f7f`
after its review said "do not merge" and three lanes closed the blockers. The browser-proof lane then
measured the result on a real server and a real browser. These are its findings, which are not the
same as the review's and are not closed by the merge.

- [x] **AUDIT-2 — the first board-stats never draws a glyph, even on a correct build** · S · deps: —
  - **FIXED (2026-09-26) at `730f92614`; report `tasks/reports/actor-hud-audit2-20260926.md`.** The Band B element glyph is now **deferred to load-complete** rather than skipped.
  - **Why not a patient assertion, and why not an awaitable loader** — both rejected on evidence, not taste. `syncFromModel` early-returns unless the model revision moves (`SyncFromModelSystem.ts:398`), so `setHudDisplay` is **not** per-frame: whether a glyph appears depends on *how many board-stats have happened*, not on whether the glyph resolves. A patient assertion makes the gate green while the canvas stays wrong. And an awaitable loader has no caller able to await it, because `syncFromModel` is synchronous. The deferral seam already existed one function away, built for type icons (`ensureIcon` → `load.once(COMPLETE)` → `onIconsReady`), so the fix extends that seam rather than forking it — now the single owner of request de-dupe, failure memo and art-ready callback in `src/game/systems/sceneArtState.ts`. The seam is locked, so `docs/architecture/decisions.md:39` ships with the code.
  - **Measured, 5 distinct elements × 5 distinct textures** (so caching cannot masquerade as a fix): fixed `fire/ice/air/earth/light` each `false→true`; reverted **and rebuilt** all five `false→false`. Every event carries `elements` by construction, so the window cannot read an absence as a presence. The reverted build also measured `draws=1, glyph=false` across 20 polls / 6.5 s / 4 poll cycles — which shows `false,false,true,true` is only the *busy*-board form and a **quiet board never got the glyph at all**.
  - **The lane caught three of its own errors**, recorded because each would have produced a false green: its first falsification was invalid (the mocked e2e serves the **built** bundle, so reverting source without rebuilding tested the *fixed* build — caught by a throwaway counter reading `draws=0`); its masking theory was wrong (`lawn:iconEpoch` was not force-resyncing; measured `epochs=0`); and its change would have introduced an infinite 404 retry loop and an epoch bust stranding in-flight loads, both fixed and tested.
  - **Verified by the lane:** `npm test` 388 files / 3283 tests · `tsc --noEmit` exit 0 · `npm run build` exit 0 · `check:bundle` OK · mocked e2e 8/8 · `verify-change.py --session` exit 0 · citation audit 0 HIGH.
  - **Still unproven, and not claimed:** the **live** e2e never ran (no game/slot in that lane) — it typechecks, its behaviour is unobserved. The five-event measurement is the mocked real-browser path, **not** the Unity→Server→web ingest. Whether **Unity's own** glyph has the same race is unknown; if it does it is `src/**` and is routed separately, not searched for here. No screenshot: the assertions prove a named child is bound to the catalog's art, not that it looks right.
  - **Routed, not done:** a mechanical guard for "new draw sites must use `requestSceneTexture`" needs an `enforcement-registry.v1.json` row, which another active session fences. `Core.Expeditions.Tests` 11/38 was reported as **not observed** to be red on this branch, not fixed.

- [ ] **AUDIT-3 — correction: the React Inspector never depended on `hudPresentation`** · XS · deps: —
  - The framing that reached the manager — and that I passed into the browser-proof brief — was "with no
    `hudPresentation` the fixture renders nothing". That is true **on the Phaser canvas and false on
    the Inspector**: `ActorHudInspector.tsx:50` uses a fixed `h-6 w-6` and never reads the field, and
    the offline fixture already imports `element-catalog.v2.json` (`actorSurfaceCatalog.ts:16`).
  - Consequence for the record: the two surfaces **disagreed** for the whole life of the missing
    route, and the route fix closed that disagreement — it did not rescue an Inspector that was never
    broken. Any acceptance or incident note that says the Inspector was broken is wrong.
  - Acceptance: the claim is corrected in the places it was written down; no code change.
  - Verify: read `ActorHudInspector.tsx:50` and the fixture import, and the statement holds.

- [x] **AUDIT-4 — the Unity live probe is DONE for the ingest path, and one half is not closable on this machine (2026-09-26, superseding the "OWED and BLOCKED" reading above).** Run on live-pool slot 1; report at `tasks/reports/actor-hud-unity-live-20260926.md`, commit `192bdca7d`.
  - **Proven — the Unity→Server HUD ingest**, which is exactly what the browser proof had stubbed out: 21 real `debug.actor-hud` events out of the running game (`ActorHudCache.DeltaEmit` → `ActorHudInvalidator.cs:49-60`), read back through the Server's own `/api/debug/events`. No FE hook, no fixture. The subject is a real record: real Hub stats applied (**270→411 HP, 0→177 defense**), `sourceKind: creature.progression.v1`. Element resolution holds end to end — `elements:{primary:"earth"}` → `hudGlyph: stone` → `stone.png` deployed and served `200 image/png`. `INJECTOR COMPILE GUARD OK` against the slot's own install (cell pvzrh-3.9, not SKIPPED), connecting to *its* server (`catalogRevision: 1`, its own cold import, against the owner's `15` on `:5111`).
  - **Not closable here — the rendered frame.** The HUD canvas is `ScreenSpaceOverlay` (`ActorHudPool.cs:395`), so it **cannot** appear in a camera capture; the repo's own comment on that primitive already says *"Misses UI overlays"*. `repaintsSeen=0` across seven captures, four of them with the window foregrounded and byte-identical. So the screenshots showing no HUD are **uninformative, not evidence of absence** — closing this needs a Repaint/UI-inclusive capture primitive, which does not exist. Do not read those screenshots as a red, and do not spend another lane re-measuring until such a primitive exists.
  - **Two blockers had to be fixed before a slot could be deployed at all**, both found by using the pool rather than reading about it: the seed importer never configured `LeadNamesHub`, so a cold import into an empty data dir rolled the whole import back (`47c9d1f60`); and `deploy-play.py` could not launch `npm` at all, dying at stage 3 of 12 on every deploy (`f71c31788`).
  - **AUDIT-2 sharpened, not closed.** Its mechanism is confirmed and *telemetry cannot detect it at all* — which is why it survived the merge. Its measurement is not re-taken; a browser lane can now, because the input exists for real. Recorded caution: the Peashooter's first two events carried `elements=null`, so a window starting at board entry can contain no glyph at all — reading that as "still broken" would be a **third** false red.
  - Lane discipline worth keeping: it came within one report of two false reds (`early:"idle", hudSlots:0` on an *empty* board reads as "nothing drew"; and a capture showing the level-select map while `debug_game_state` said `InMatch`), and it did not edit the Injector mid-probe, so the next lane inherits a clean baseline. Slot released; `lawn.worldHud` restored to its documented default; no code changed.

- [x] **AUDIT-5 — `union_append_only.py` silently destroys a structured registry and exits 0** · M · deps: —
  - **FIXED (2026-09-26) at `5b23d6aa3`; report `tasks/reports/union-append-only-20260926.md`.** The tool now decides the input's shape **before writing anything** and refuses by name with a **non-zero exit**, writing nothing.
  - Two independent signals, because the only caller (`resolve-append-only.ps1:38-39`) renames both sides to `ours.txt`/`theirs.txt` while `--out` keeps the real name — so a suffix rule alone would have missed the incident: the **declared suffix** (`.json .yaml .yml .toml .xml .ini .cfg .conf`) and the **content** (does it parse as one JSON document, probed per conflict-free *region* — a conflicted file's marker-stripped text is two documents concatenated and parses as nothing, so a whole-file-only probe would also have missed it).
  - **The write is staged, re-read, re-validated, then `os.replace`d**, so a refusal leaves the destination byte-identical and a staged file that cannot be removed is a named refusal rather than a swallowed delete.
  - **Verified by the manager, independently of the lane:** on a 7-boundary registry pair cut from the real registry, the fixed tool prints `REFUSED [classify-input] INPUT-SHAPE-UNSUPPORTED`, names the file, states `shape=structured (declared suffix '.json' is block-structured, not append-only text)`, points at `union-registry-sides.py` as the tool to use instead, **exits 2**, and **creates no output file**.
  - The lane's falsification: pre-fix, the same pair gave `ours=101 theirs=100 theirs_only=2 result=62`, **exit 0**, and an output that does not parse. Six suite tests fail against the pre-fix source **on behaviour**, not on a missing name. Append-only **ledger** parity was run, not asserted: both implementations over 7 real inputs (ledgers to 144 KB, task lists to 76 KB) are byte-identical with the same exit codes, and those parity tests pass against the pre-fix tool too, which is the claim they make.
  - **Deferred deliberately:** `--structured` was NOT built. The manager plane already has two *conflicting* boundary-union rules (`union-registry-sides.py` takes ours and exits 3; `union-verification-registry.py` refuses when any shared entry differs and preserves formatting where the other reformats all 186 KB). Choosing between them is a product decision, and a second JSON merge implementation is a drift risk. The refusal names the right tool — a pointer, not an implementation.
  - Not verified by the lane, recorded as such: `resolve-append-only.ps1` was never run end to end (it needs a real in-progress merge; its invocation *shape* is reproduced), and the YAML/TOML/XML refusals are reasoned rather than observed.

- [ ] **AUDIT-6 — `omni` declares no `hudGlyph`; the UI skips it cleanly** · XS · deps: —
  - `omni` is `presentationOnly: true` and the catalog doc says it is never a species slot, so this is
    probably intentional. Measured on both surfaces: **no crash, no error boundary, no `<img>` created,
    and no network request at all** for an art URL.
  - It belongs to `actor-hud-element-icons-20260917`, whose fence covers
    `gk-core/src/FusionRpg.Core/ActorSurface/**` and `gk-fusion/src/FusionRpg.Injector/Hud/**`. Recorded here so the
    decision is visible in the owning program; **not** fixed by the merge lane.


