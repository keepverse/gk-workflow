# SPEC — Injector VFX v2 enhancements

**Status:** **Complete (2026-08-21)**. **F8 reopened and largely resolved 2026-09-17 — see §2a** — W1–W6 landed (T1–T7), findings F1–F7 closed. LIVE gate PASSED 43/43 + owner eyeball confirmation. The gate surfaced and fixed three render-layer defects the offline tests could not see (auto-emission whiteout, vanilla texture steal, additive color washout) and one product rule (element-only hit accents) — all folded into vfx-ssot.md.
**Scope:** Game-injector VFX only. No other feature is touched.
**Parent:** [docs/architecture/vfx-ssot.md](docs/architecture/vfx-ssot.md) stays the locked architecture SSOT. This spec adds enhancements inside that architecture; it changes no locked decision.

---

## 1. Objective

The 2026-08-20 audit of the shipped VFX layer (cue → recipe → primitive) found the architecture sound: it survived the event-pipeline-v2 rework and the element-roster growth without structural strain. What remains are three gaps, one per goal:

| Goal | Gap today | Outcome when done |
|---|---|---|
| **Producibility** | No `status.*` producer path exists — a status VFX cannot be added by "catalog entry + emit line" because nothing emits. LIVE probe never ran. Spec/doc/prove drift (light/dark elements in code, not in docs or prove script). | A new status VFX = 1 catalog entry + 1 producer line + 1 prove line, and `prove_vfx.py` passes LIVE with all 6 elements. |
| **Performance** | `VfxDirector.Tick` resolves `Camera.main` (tag scan) every frame even with zero live VFX — a named suspect in the 9.2 ms/frame `loop.tick` finding. `AnchorResolver` duplicates `InjectorEntityRegistry` with its own string-keyed cache and its own `FindObjectsOfType` sweep. | `vfx.tick` ≤ **0.5% of wall** at the 300z stress tier; **zero** `FindObjectsOfType` owned by VFX code; near-zero cost when no VFX are live. |
| **Visual quality** | Floaters are raw IMGUI labels (no shadow — unreadable on bright lawns). Every burst is the same radial puff. `Flash` is implemented but unused by any recipe. Big and small hits look identical apart from the number. | Shadowed, crit-popping, amount-tiered floaters; three burst shapes; impact flash on hits — all inside the existing primitives and pool, zero new allocations per hit. |

## 2. Audit findings (ranked)

| # | Finding | Goal | Severity | Fix shape |
|---|---|---|---|---|
| F1 | `status.{id}.apply` cues: catalog has none, `StatusRuntime` emits nothing — phase 4 of the SSOT migration never happened | Producibility | High | W5 |
| F2 | LIVE probe never ran (`_prove-vfx.json` absent); prove script covers only 4 of 6 elements | Producibility | High | W6 |
| F3 | `Camera.main` per tick, unconditional — cost paid even at zero live VFX | Performance | High | W2 |
| F4 | `AnchorResolver` duplicates `InjectorEntityRegistry` (string keys + own sweep vs IntPtr keys + frame resync); per-spawn `GameDumps.Ptr` string alloc to feed it | Performance | Med | W1 |
| F5 | Floater readability: no shadow/outline, fixed 20px, crit differs only by 1.25× static size | Visual | Med | W3 |
| F6 | One burst shape for everything; `Flash` primitive dead code (no recipe uses it) | Visual | Med | W4 |
| F7 | `vfx-ssot.md` §16.2 palette table lacks `light`/`dark` (code has them via `ElementRoster`) | Producibility | Low | W6 |
| F8 | `PerfSection.VfxTick` instrumented but no budget asserted anywhere | Performance | **REOPENED — Low was wrong, see §2a** | W6 |

**Explicitly fine (audited, no change):** thread-safe cue queue, admission/rate-limit engine, pooled bursts, element/hybrid color math, Repaint gating, `ClearAll` on `Board.Die`, funnel present path, C#-seeded catalog (JSON stays deferred), all SSOT bans.

### 2a. F8 reopened — measured by `solid-remediation`, 2026-09-17

**This section is a hand-off, not a redesign.** It records a measurement taken while proving a different
program's live gate, because that measurement contradicts this document and would otherwise have stayed
in another program's task file where this program's owner would never read it. Nothing about `vfx-v2`'s
design is changed here.

**What the header says.** *"all findings F1–F8 closed"*, and F8's own acceptance (W2) reads *"next stress
run shows `vfx.tick` ≤ 0.5% wall at 300z."*

**What was measured.** Live board, current binary, five `PerfProbe` windows read through
`GET /api/perf/recent`:

| Quantity | Measured | Reference |
|---|---|---|
| `vfx.tick` | **2.513 ms/frame — 91.8% of the whole injector loop** | F8's acceptance asks for ≤ 0.5% |
| `loop.tick` | **2.737 ms/frame** | `perf-probe-plan.md` §0 locks ≤ 2 ms/frame at 200+ entities |
| Board size | **80 zombies** | 300 spawn calls were accepted; the game's own cap held the board at 80 |

**Three separate things this says, kept apart on purpose.**

1. **F8 is not closed.** Its acceptance was never measured, and the first measurement misses it by more
   than two orders of magnitude — 0.5% asked for, 91.8% observed. A finding whose acceptance has never
   been run is instrumented, not closed.
2. **Low was the wrong severity.** F8 was filed as *"no budget asserted anywhere"*, which reads like
   missing paperwork. The quantity it lacked is now known: VFX is not a tail cost on the injector loop,
   it is effectively the whole loop, and the loop is over its own locked budget at under half the entity
   count that budget is written for.
3. **The acceptance criterion cannot be run as written.** It says *"at 300z"*, and 300z is not reachable
   — the board caps at 80. Whoever reopens this has to restate the criterion against a board size the
   game will actually produce before it can be measured at all.
4. **It is nonetheless already failing the only budget that exists, so this is not blocked on the
   budget being written.** `perf-probe-plan.md` §0 defines a whole-injector budget and no per-section
   one (confirmed 2026-09-17: the strings `vfx.tick`/`VfxTick` do not appear in that document). Against
   it, `vfx.tick` **alone** at **2.513 ms/frame** exceeds the entire injector stress budget of **2
   ms/frame**, at **80** entities rather than the 200+ that budget is written for. Setting a
   per-section number is still this program's call; whether the current one is acceptable is not an
   open question.

**✅ RESOLVED IN PRACTICE 2026-09-17 (owner ruling), though the budget itself is still unwritten.**
The 2.5 ms was attributed: it was the world-HUD walk. `VfxDirector`'s phase wake was forcing the whole
drain/tick chain every frame of every match regardless of `WorldHudEnabled` (so turning the HUD off
skipped the draw and kept paying for the wake) — fixed — and the world HUD now ships **off**, behind a
server-backed user setting.

Re-measured live on the same board size, steady state at 60 fps: `vfx.tick` **2.513 → 0.0006–0.021
ms/frame** at 80 zombies, `loop.tick` **2.737 → 0.055–0.099 ms/frame**. Toggling the setting back on
raised `vfx.tick` to **0.2838 ms/frame at 2 zombies**, which is what confirms the attribution rather
than merely asserting it.

What remains for this program is the smaller half: **author a per-section budget** so the next
regression is caught by a number rather than by someone noticing. The acceptance criterion also still
needs restating away from "300z", which is unreachable.

**Owner: `vfx-v2`.** Setting a VFX budget and attributing that 2.5 ms is this program's work, not
`solid-remediation`'s — which is why the clause that found it was left unticked there rather than
reworded into something passable.

## 3. Work items (dependency order; each ships green)

### W1 — Anchor resolution via the entity registry
Replace `AnchorResolver`'s private cache + sweep with lookups into `InjectorEntityRegistry` (`FindZombie/FindPlant(ptrHex)?.transform`). The registry is already hook-fed and frame-resynced for the combat path.
- Delete: AnchorResolver's dictionary, `Sweep()`, and the `GameDumps.Ptr` register calls in `Plant.Start`/`Zombie.Start` postfixes (registry adds already exist there).
- Keep: the `AnchorResolver.Resolve(ptr)` facade so `VfxDirector` doesn't change.
- **Accept:** zero `FindObjectsOfType` under `gk-fusion/src/FusionRpg.Injector/Fx/`; guard test updated to pin that; all suites green.

### W2 — Idle-cheap Tick
- Resolve the camera in `Draw()` only, only when floaters exist, cached and re-resolved on null (a destroyed camera on scene change must not strand stale state).
- `Tick` early-outs the per-frame work when queue, floaters, bursts, and flashes are all empty (`AnchorResolver.Tick` clock keeps running).
- **Accept:** unit-testable early-out logic in core where possible; next stress run shows `vfx.tick` ≤ 0.5% wall at 300z (F8 budget lands in `stress_test.py` expectations). ⚠️ **This acceptance was never run, and §2a measures 91.8% against it — at 80z, because 300z is not reachable. Restate the board size before re-measuring.**

### W3 — Floater visual pack (pure math + Draw)
- Shadow pass: each label draws twice — black at (+1,+1) then color — same style, ~2× label cost, floaters only exist ≤0.9s.
- Crit pop: font scale becomes a curve `PopScale(t)` in `VfxRules` (fast overshoot ~1.5× → settle 1.25×); plain hits stay flat 1.0.
- Amount tiers: `AmountScale(amount)` in `VfxRules` — e.g. <50 → 0.9×, <200 → 1.0×, ≥200 → 1.15× (exact numbers locked in code constants, test-pinned).
- **Accept:** all curves/tiers are pure `VfxRules` functions with unit tests; Draw changes compile against game assemblies.

### W4 — Burst shapes + impact flash
- `VfxPrimitiveSpec` gains `Shape: VfxBurstShape { Radial, Rising, Directional }`. Emission math per shape lives in core (`VfxBurstMath`: per-particle pos/vel from (shape, index, count, span)) so it is unit-testable; `BurstPool` consumes it. Same pool, same caps, per-particle `Emit` unchanged.
- `combat.hit` recipe adds a `Flash` spec (existing primitive, §8.5 rules already implemented) — impact feedback on the struck unit.
- `combat.heal` gets a `Rising` burst (green motes drifting up) — first visible payoff of shapes.
- **Accept:** `VfxBurstMath` unit tests pin each shape's direction envelope; catalog validation accepts the new field; rate limits unchanged.

### W5 — Status cue producer path (unblocks all future status VFX)
- `StatusRuntime` gains an optional `IVfxSink` (core interface already exists; injector wires `VfxDirector.Sink` in `InjectorStatusBridge`). On a successful status apply it emits `status.{statusId}.apply` with the host ptr; resisted applies emit nothing.
- Seed recipes for the statuses with existing prove packs (per SSOT §4.2 criterion — butter, freeze/cold, poison/blight family; exact list read from the status catalog at seeding).
- **Accept:** core test — recording sink sees `status.{id}.apply` on apply and nothing on resist; each seeded cue gets a `prove_vfx.py` line.

### W6 — Sync + LIVE gate
- `vfx-ssot.md` §16.2 gains `light` (255,232,120) and `dark` (150,90,220) rows; status line updated.
- `prove_vfx.py`: 6-element coverage, one shape case, one status-apply case; verdict JSON unchanged in shape.
- Stress expectations: `vfx.tick` budget assertion noted in `stress_test.py` docs.
- **Final gate: run `gk-core/scripts/prove_vfx.py` LIVE** (lawn open, via `setup_lab_run.py`) — this closes F2, which has been open since the VFX layer shipped.

## 4. Commands

```powershell
# offline verification (after every work item)
dotnet test tests\FusionRpg.Core.Tests
dotnet test tests\FusionRpg.CheatCore.Tests
dotnet test tests\FusionRpg.Guard.Tests

# injector compile check against game assemblies (no deploy)
$env:FUSIONRPG_ML_GAMEDIR = 'H:\Games\PVZ-Fusion-3.9_MelonLoader'
dotnet build src\FusionRpg.Injector.MelonLoader.39\FusionRpg.Injector.MelonLoader.39.csproj -p:OutputPath="$env:TEMP\fusionrpg-vfx-build\"

# LIVE gate (W6, owner-run with game open)
.\scripts\setup-lab-run.ps1
.\scripts\prove-vfx.ps1
```

## 5. Project structure (touched files only)

```
gk-core/src/FusionRpg.Core/Vfx/            VfxRules (curves/tiers), VfxRecipes (+Shape), VfxBurstMath (new),
                                   VfxCatalog (seed additions), ElementFxPalette (no change)
gk-core/src/FusionRpg.Core/Status/         StatusRuntime (+optional IVfxSink emit)
gk-fusion/src/FusionRpg.Injector/Fx/         AnchorResolver (registry facade), VfxDirector (idle-cheap tick,
                                   shadow draw), BurstPool (shape consumption)
gk-fusion/src/FusionRpg.Injector/Effects/    InjectorStatusBridge (sink wiring)
gk-fusion/src/FusionRpg.Injector/GameHooks.cs  remove now-duplicate anchor Register lines
gk-core/tests/FusionRpg.Core.Vfx.Tests/Vfx/    new: burst math, curves, status-cue tests
gk-core/tests/FusionRpg.Guard.Tests/       LawnCoordsGuardTests: no-FindObjectsOfType-in-Fx pin
scripts/prove-vfx.ps1              6-element + shape + status coverage
docs/architecture/vfx-ssot.md      §16.2 palette rows, status line
```

## 6. Code style

Repo rules apply unchanged: no throws into the game loop (guarded try/catch, skip + `debug.fx.skipped`); every tunable constant lives in `VfxRules`; decision logic stays in pure Core (injector classes are thin shells); no `renderer.material`, no per-cue `FindObjectsOfType`, no per-burst instantiate (SSOT ban list); comments state constraints, not narration; neutral project voice, no vendor names.

## 7. Testing strategy

- **Unit (core, no Unity):** every new curve, tier, shape envelope, and the status-emit decision — same pattern as the existing `gk-core/tests/FusionRpg.Core.Vfx.Tests/Vfx/` suite.
- **Guard:** source-level pin that `Fx/` contains no `FindObjectsOfType` after W1.
- **Compile:** MelonLoader 3.9 build against the real game assemblies after every injector-touching item.
- **LIVE:** `prove_vfx.py` is the only acceptance for on-screen behavior; it runs once at W6 and its JSON lands in `docs/research/perf/../effect-runtime/`. Perf acceptance reads the next stress run's `vfx.tick`.

## 8. Boundaries

**Always:** ship each W item green before the next; keep `vfx-ssot.md` as the SSOT and sync it in the same change that alters behavior it locks; presentation-only (no HP/stat/status writes from VFX).
**Ask first:** any new primitive kind beyond the locked three; any change to rate-limit values or caps; anything touching non-VFX systems beyond the listed integration lines; running the LIVE gate (needs the game open on the owner's machine).
**Never:** timeline/keyframe DSL, runtime recipe files, per-VFX sink interfaces, `renderer.material`, gameplay reads/writes from VFX, git commits (owner commits manually).
