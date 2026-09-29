# CP2 live proof — executed 2026-09-17

**`solid-remediation` CP2, live-proof clause. Run on the live game, on this build.** Injector deployed
to the MelonLoader pack, server republished and restarted (the previous one had been idle since
2026-09-16T17:43 on pre-change code), injector connected, lab board entered via
`POST /api/debug/lawn/quick-start`.

The clause has two halves. **The first passed. The second did not, and the reason is not this
program.**

---

## Half 1 — the resolve claim: **PASS**

**What was asserted** (the corrected wording, see `solid-remediation-map.md`): on a live lawn, an
effect-driven hit that authored **no element payload** resolves through the element matrix, because
`EffectBag.ApplyOwnerElementFallback` gives the packet the acting actor's own element.

**Why it can fail.** `GateCounterHost.HandleDamageApplied` takes the packet's element *components*. No
components means no elemental-mastery credit, no matter how well `CombatMath` is wired. Before the
fallback, an effect hit with no authored payload carried none.

**Method.**

1. Baseline read through the ordinary `GET /api/gate-counters/1`: `ice` = **0**, `dark` = 0. An element
   already at zero is the discriminator — any movement is unambiguous.
2. Fresh lab board. Attacker (plant) pinned to `ice` via `POST /api/debug/combat/pin-element` — Game
   Injector Debug, **board setup only, never the proof**.
3. 12 × `POST /api/debug/effect/fire-synthetic` and 6 × `POST /api/debug/combat/probe`, all with **no
   authored `elementPayload`**.
4. Waited out the 5 s gate-counter flush window.
5. Read back through the **same ordinary non-debug endpoint**.

**Result: `ice` 0 → 8.**

The credit landing proves two things at once: the fallback put element components on a packet that
authored none, and the resolver consumed them. Read back from the server's persisted player row, not
from the injector telemetry that produced it — `LawnCombatObserver` rides the `/api/perf` window and is
exactly the telemetry the clause disqualifies, so it was deliberately not used.

**A false start worth recording.** The first attempt read `ice` 0 → 0 and looked like a clean failure.
It was a real one, with a real cause: `OverlayCombatFeature.Enabled` requires env
`FUSIONRPG_OVERLAY_COMBAT=1` **or** the `OVERLAY-COMBAT` cheat toggle, and the game had been launched
with neither, so `ConditionalOverlayCombatMath` was disabled and `Finalize` passed through. Diagnosed
from the gate rather than guessed at, the toggle was set through `PUT /api/cheats`, and the probe then
passed. Had the probe been written to read its own telemetry it would have "passed" both times.

---

## Half 2 — the perf budget: **NOT MET, and not by this program**

Measured on the same live board, five 5 s `PerfProbe` windows read through `GET /api/perf/recent`.

### The board would not reach 300 zombies

300 spawn calls were accepted; the board held at **80 zombies**. The "300-zombie tier" is not reachable
through `debug.spawn-zombie` — the game's own cap, not a refusal from our side. Everything below is
therefore the **80-zombie** tier, which makes the result worse rather than better: the budget it misses
is written for 200+.

### The numbers (window 0; the other four agree within 10%)

| Section | avg ms/frame | share of `loop.tick` |
|---|---|---|
| `loop.tick` (whole injector) | **2.737** | 100% |
| `vfx.tick` | **2.513** | **91.8%** |
| everything else, summed | **0.224** | 8.2% |

`match.apply` 22.7 µs · `poll.board` 16.2 µs · `cheat.continuous` 6.9 µs · `effect.onCapture` 0.9 µs ·
`pump.main` 0.4 µs · `cheat.autocollect` 0.2 µs. Frame rate held at 59.7 fps; worst frame 37.1 ms.

### Against the locked number

`perf-probe-plan.md` §0 locks **≤ 2 ms/frame avg for the injector at 200+ entities, max speed**. The
injector is at **2.737 ms/frame at 80 entities** — over budget at under half the entity count.

### What this program costs

**0.224 ms/frame**, which is the entire non-VFX injector loop, or about 11% of the 2 ms budget.
`combat.dispatch` does not appear in the window at all, and `effect.onCapture` is 0.9 µs. So the D1 fix
is demonstrably **not paid for in frame time** — which is the thing the clause exists to check.

### The finding

**VFX is 91.8% of injector frame cost and has no budget of its own.** `vfx-v2-spec.md` F8 already
records *"`PerfSection.VfxTick` instrumented but no budget asserted anywhere"* — filed as Low. This
measurement is the quantity that was missing from it: it is not a tail cost, it is effectively the
whole loop, and it is what puts the injector over its locked stress budget.

⚠️ **The clause cannot be ticked as written.** It asks for `vfx.tick` "within its locked share", and
there is no locked share to be within — that is F8. What can be said, and is said above, is that the
budget that *is* locked is missed, that VFX is 92% of the miss, and that this program's own surface is
0.224 ms/frame. Attributing the VFX cost, or setting a budget for it, is `vfx-v2`'s work and this
program does not own it.

---

## Reproducing

```powershell
# half 1
powershell -File <scratch>/live-proof.ps1     # exits 0 on PASS, prints the before/after mastery
# half 2
powershell -File <scratch>/perf-300z.ps1      # spawns, waits, writes perf-raw.json
```

Prerequisites, both of which cost a first attempt: `OVERLAY-COMBAT` on, and pointers from a **fresh**
`lawn/quick-start` — a board that has ended leaves dead pointers and every command silently no-ops.
