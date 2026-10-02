# Live-probe standard

**Status: binding for every "prove this feature works live" session.** A live probe proves the real
RPG server pipeline works for a real player object, through the same centralized backend the normal
game/web frontend uses. It never proves that a debug tool can make an API *respond as if* that were
true. This is the standard [`DESIGN-GATE.md`](../DESIGN-GATE.md) points debug-API and live-verification
work at, the same way [`testing-standard.md`](testing-standard.md) governs `tests/**` substrate and
[`validation-ssot.md`](../architecture/validation-ssot.md) governs what a guardrail may assert.

**Why this exists.** 2026-09-13, `actor-hub-and-combat-power-solid-fixing` T14 (`bound-loadout-hub`):
a live probe deployed a WallNut with a debug loadout JSON (`{"absolutes":{"hp":2000,"maxHp":5000,
"atk":500}}`) directly through the Game Injector's debug bind path, then read the result back through
the SAME injector's debug telemetry (`debug.board-stats`). `hp` matched (2000); `maxHp` (4000) and
`attack` (1) were untouched vanilla baseline — the feature was actually broken. The probe's *shape* was
sound engineering practice (real numbers, not a screenshot), but its *scope* was wrong on both ends:
the actor was never a real player-owned `UniqueActor` created through the real acquire/level/build
flow, and "prove it worked" meant "the injector says the field changed," not "the RPG server's own
domain logic and persisted state say so." A debug tool that can fabricate the precondition can equally
fabricate a false pass — the T12 half of the SAME probe (aptitude allocation) happened to be real
Server-persisted state reached through a real endpoint (`POST /api/aptitudes/unique/allocate`), which
is exactly why it caught the T14 defect instead of hiding it too.

---

## 1. Two debug scopes — name which one you are in

| | **Game Injector Debug** | **RPG Server Debug** |
|---|---|---|
| Lives in | `FusionRpg.Injector`'s `debug.*` commands (`CheatCommandRunner.cs`), relayed by `DebugEndpoints.cs`'s thin `MapPost(g, path, "debug.xyz")` wrappers | `FusionRpg.Server`'s own application/domain/persistence code — `RpgStore`, the real `/api/*` endpoints the web FE calls, `EffectGrantSession`, `AptitudeEndpoints`, etc. |
| Purpose | Simulate/inject a game-side situation, inspect client behavior, reproduce a hard-to-trigger case, read live Unity/board telemetry | Invoke a **real** server operation, create/mutate **real** persisted records, exercise the **same** domain/application logic the normal FE depends on |
| May fabricate | Board/entity state inside the game engine (`debug.spawn-plant`, `debug.set-mods`, a raw loadout JSON bound straight to a ptr) | Nothing. It may only call the real endpoint/service with real inputs |
| Already-correct examples | Most of `DebugEndpoints.cs`'s `MapPost(g, ..., "debug.*")` lines | `POST /api/debug/derived-audit-actor` ("real UniqueActor → Hub → /sheet (never a synthetic 269 paint)" — its own comment already states this rule) · `GET /api/debug/derived-audit-coverage` (DAL-only, no injector round trip, reports real Hub-derived-channel coverage for a real specimen) · `POST /api/aptitudes/unique/allocate` (real, used correctly by T12's half of the 2026-09-13 probe) |
| May prove | "the game engine reflects X" | "the RPG server's domain logic and persistence produce X for a real record" |
| May NOT prove | Server-side correctness — the injector has no domain logic, no persistence, no validation | Game-engine wiring — a real DB record proves nothing about whether the Injector applies it |

**An agent must be able to say which scope a given debug call belongs to before using it as evidence.**
If you cannot say, stop and find out — do not treat a response from either scope as proof of the other.

---

## 2. The rule

**A debug API may trigger a real operation. It must never fabricate the state that operation is
supposed to produce.**

Concretely, for any "does feature X work" probe:

- The subject (an actor, an item, an allocation, a deployment — whatever the feature is about) must be
  a record a **real** player-facing flow could have created: real summon/fusion/acquire, real level-up,
  real stat allocation via the real endpoint, real deploy. `uniqueActorId`/`instanceId` etc. passed to a
  debug call must resolve to a row that already exists in `RpgStore`, not one the debug call invents.
- A debug call may **skip tedium** (clicking through a UI, waiting for a timer) but must still route
  through the real application/domain/persistence path — same service, same validation, same DB write.
- Fabricating stats, level, definition, inventory, or a deployment *result* directly — bypassing the
  service/domain layer that would normally compute or gate it — is the exact defect this standard bans.

---

## 3. Proof requires persistence and read-back, never a response alone

An HTTP 200 or a plausible JSON body is not evidence. At minimum, a live probe for feature X must show:

1. The subject record existed (or was created through a real flow) **before** the operation under test.
2. The operation was invoked through the real endpoint/service — not a hand-rolled shortcut into the
   same final state.
3. `RpgStore` (or the relevant persistence) actually holds the new/changed row afterward — read it back
   through the **same query path** the normal frontend uses, not a debug-only accessor built to make the
   test convenient.
4. Where the feature also has a live-engine half (the Injector reflecting server state onto a Unity
   entity), that half is checked **separately**, and a pass on one half is never reported as covering
   the other — see §1's "may prove / may not prove" rows. The 2026-09-13 incident's actual lesson is
   that these are two independent chains that happen to look like one pipeline.

---

## 4. Anti-cheat checklist — each of these is an outright fail

- **Fake actor/subject.** The id under test does not resolve to a record real gameplay could have
  produced.
- **Fake stats/state supplied by the debug call** instead of loaded from persisted backend state.
- **Injector-only proof of a server claim**, or **server-only proof of an injector claim** (§1).
- **Database bypass.** The operation "succeeds" without the expected persisted row existing or changing.
- **Mocked pipeline.** A stub/mock stands in for the real application/domain/persistence path.
- **Unwired implementation.** Code exists but nothing in the real API/application pipeline can reach
  it — an implementation that can only be exercised by a test-only shortcut is incomplete, not proven.
- **Response-only proof.** No read-back through the normal query path.

---

## 5. Applying this to Actor Hub (and every future feature)

The intended chain for any Actor-Hub-adjacent live probe:

```
real game/web flow → acquire/create real UniqueActor → RPG backend persists it
  → real level/stat-allocation calls persist real changes → real deploy operation
  → RPG backend persists deployment state → Actor Hub / Injector reads that real state
```

Building or extending a **dedicated RPG Server Debug surface** (endpoints that chain the real
acquire/allocate/deploy calls the web FE already uses, without needing a human to click through them)
is in scope and encouraged — that is what turns a slow manual proof into a fast one **without**
fabricating anything. What is never in scope is a debug endpoint that hands the "already computed"
result to the reader instead of making the real pipeline compute it.

**This document does not itself create that dedicated surface.** `DebugEndpoints.cs` today mixes both
scopes in one file (mostly Game Injector Debug relays, with `derived-audit-actor`/`derived-audit-coverage`
as the two RPG-Server-Debug-shaped exceptions). Splitting it, and building out a fuller RPG Server Debug
API/skill, is real design work and belongs behind this repo's own `/idea` → `/spec` pipeline
([DESIGN-GATE.md](../DESIGN-GATE.md) §0), not a drive-by refactor — named here as the open follow-up,
not claimed as done.

---

## 6. Lawn run state awareness — never claim success from a single response

**Why this exists.** 2026-09-14, chasing the `lawn/quick-start` seed-picker/cycling/defeat fixes: an
agent read `/lawn/quick-start`'s `{ ok: true, targetPtr: ..., plantPtr: ... }` response, with real
`plant.spawn` events behind it, and reported the board recovered. The operator was looking at the
actual game at the same moment and saw the vanilla defeat overlay ("重新开始") still on screen. Both
readings were correct about different layers — the simulation had moved on (the scenario's own reset
step really did clear and respawn entities), the rendered screen had not — and there was no single,
queryable fact either side could check instead of one person silently eyeballing the game and the
other reading an HTTP body. That gap, not either individual reading, was the defect.

**The rule: before reporting a live probe's outcome, query the lawn's actual state — never infer it
from one response, and never require a human to describe it by eye.** `GET /api/debug/lawn/state`
(`DebugEndpoints.cs`) exists for exactly this: it classifies the board into one of six states
(`Cycling` / `Defeated` / `Victorious` / `InMatch` / `LevelEntryPending` / `Unknown`, in that
precedence) from the **full inventory** of lifecycle signals the injector emits, and reports which
event decided it (`asOf`) and how long ago (`sinceMs`) — a "where and when" answer traceable to a real
timestamp, never a guess. The full state machine — every signal, its reliability, and every known
blind spot — is [lawn-run-state-machine.md](../architecture/live-probe/lawn-run-state-machine.md).
**Read that document, not just this summary, before changing the classifier or adding a new state.**
It exists because a first version of this endpoint was built from three signals chosen ad hoc under
time pressure and produced a confusing, stale-looking answer against a genuinely defeated board — the
fix was not a fourth patch, it was reading the whole hook surface once and mapping it properly.

**What it cannot do — say so, do not paper over it.** `state: "Unknown"` cannot distinguish the main
menu, the vanilla seed-picker screen, or a paused match: nothing passively telemetered fires for any
of them (confirmed live — zero `board.start` events across a whole multi-hour session while `Board`
stays null, and pause/resume hooks exist but emit no event at all). And no passive state query can see
what is actually *rendered*: `debug.reset-board` restores API-level spawn capability after a defeat,
but the game's own defeat/victory overlay has no sanctioned dismiss command today, so the simulation
and the screen can genuinely disagree for a while. When the question is what a player or operator
sees, the answer is "ask them" — a state query is not a substitute for eyes on the actual game, it is a
substitute for guessing when nobody's eyes are on it, or when two parties each have a different half of
the picture and neither one's half is labeled as partial.

**Every ad-hoc fix to a stuck live run is a debt until it is a tool.** Diagnosing the seed-picker
screen, the `board.start`-never-fires profile quirk, the cycling-board loop, and the defeat state all
started as one-off `curl`/event-log archaeology in a single session. Each is now a permanent,
queryable capability (`lawn/quick-start`'s self-healing steps, `lawn/state`'s classification, or a
runbook-documented manual sequence) — not a war story repeated next time the same state recurs. When
the next live-run mistake is found, the fix is the same shape: a metric or endpoint that answers the
question mechanically, added here and to [live-test-ssot.md](../runbook/live-test-ssot.md) §0/§6, not
another paragraph of "if you see X, try Y" for a future reader to rediscover by trial and error.

---

## 7. Definition of done for a live probe

Not:

> "The API returned `ok: true`."

But:

> "A real record, created through a real flow, was changed by a real operation, and I read the changed
> state back through the same path the normal frontend uses — and, separately, confirmed or denied
> whether the live game engine reflects it."

State explicitly, per probe:

- Which scope (§1) each debug call belonged to.
- What was read back, from where, and whether that read used the normal query path.
- If either half (server-persisted vs. live-engine) was not checked, say so — do not let a pass on one
  stand in for the other.

---

## 8. Enforcement

- [`DESIGN-GATE.md`](../DESIGN-GATE.md) §1 topic index points here for any debug-API or live-verification
  work.
- `AGENTS.md`/`CLAUDE.md` may restate this rule in full; this document is the source and wins when they
  disagree (same convention as [`testing-standard.md`](testing-standard.md) §4).
- `gk-core/scripts/guard-debug-scope.py` (spec:
  [`live-probe/spec-debug-scope-guard.md`](../architecture/live-probe/spec-debug-scope-guard.md), wired
  into `deploy-play.py`) mechanically classifies every route handler in `DebugEndpoints.cs` as
  Game-Injector-Debug-shaped or RPG-Server-Debug-shaped — any relay call to the Injector anywhere in a
  handler body makes it Game-Injector-Debug-shaped, full stop, regardless of what real persisted-write
  work the same handler also does. It also checks each route's `// Game Injector Debug` /
  `// RPG Server Debug` banner comment against that computed classification, so a route that drifts
  from its own banner (or a stale banner miscategorizing a route) fails CI instead of misleading the
  next reader. `gk-core/tests/FusionRpg.Guard.Tests/DebugScopeGuardTests.cs` carries the regression fixtures.

---

## 9. The game pool — three live slots, claimed by file lock, no human sequencing

**Owner ruling 2026-09-21 (in conversation):** *"each lane agent should clone [the game install] into [a
pool root] then make json file to manage free game and agent should register slot and use, maximum is 3
live run at same time, agent need manage and shared by lock the json and release lock, no human need to
command to do that."* And on paths: *"remember dont have coded game folder."*

- ⛔ **No install path is hardcoded — not here, not in a script default, not in any committed file.**
  The pool root and the install to clone come from the environment (`FUSIONRPG_GAME_POOL`,
  `FUSIONRPG_GAME_SOURCE`) or explicit parameters (`scripts/live_slot.py -PoolRoot -SourceInstall`).
  Machine-specific values live in the environment or in gitignored runtime state (`.kilo/sessions/**`).
  A committed drive letter is a defect in whichever file carries it, including this one.
- **Three live runs at a time, machine-wide.** `gk-core/scripts/live_slot.py` is the entire protocol: `-Status`
  lists each slot's state, holder, install, age and any live game process; `-Clone -Session <id>` populates a
  slot once and **verifies** it against the required install shape; `-Acquire -Session <id>` claims it (cloning
  on first use); `-Release -Session <id>` returns it to `ready` **keeping the install** so the next session
  reuses it; `-Reclaim -Slot <n>` force-releases a stale claim. A clone is per **slot**, so one agent's probe
  cannot corrupt another's install, and occupancy is a **state** (`free`/`ready`/`occupied`/`broken`) rather
  than the absence of an entry.
- **Agents coordinate through a lock file, never a human.** The registry (`<pool-root>/slots.json`) is
  read-modified-written only while holding an exclusively-created `<pool-root>/slots.lock`; the lock is
  released immediately after that write, never held for the duration of a probe. This is deliberately a
  *different* lock from `game_lock.py`, which fences one install against another session: the pool lock
  allocates slots, the game lock protects an install.
- **Each slot has its own SERVER and PORT.** The owner's server is one process on `:5088`; a lane runs its own via
  `scripts/lane_server.py -Start -Slot <n>` on `BasePort + slot` (default `5101`, `5102`, `5103`) with its own data
  directory (`<pool-root>/slot-<n>-data`) — two servers sharing one SQLite file corrupt each other's state, so the
  data directory matters as much as the port. The server takes both from `FUSIONRPG_URLS` / `FUSIONRPG_DATA`
  (`gk-core/src/FusionRpg.Server/Program.cs:14-17`). `-Stop` kills only the PID the tool recorded, and a slot resolving to
  `:5088` is refused. Deploy with `-NoServer -ServerUrl http://127.0.0.1:<your port>`: omitting it is refused,
  because the default is the owner's URL.
- **All three slots held is a wait, not an override.** The next agent waits for a release, or asks the
  owner for a fourth. It must never kill another session's game to free a slot — the path-scoped kill rule
  above is unchanged and a held game lock still refuses the restart.
- **Release is part of the probe.** A slot registered after the probe finished is a slot no other agent can
  use; release it before the fragment is written up. A lock left by a dead holder is broken automatically
  after `-StaleLockMinutes` (default 15) and **the break is recorded in the registry**, so an auto-break is
  auditable rather than silent.
