# The seed seam — `seed-seam` (rpg-simulator RS-F4)

**Module id:** `seed-seam` (capability map [rpg-simulator-map.md](rpg-simulator-map.md), module row 11).
**Program:** `rpg-simulator`. Plan: `tasks/rpg-simulator-plan.md` (§11). Todo: `tasks/rpg-simulator-todo.md` (RS-F4).
**Owner ruling this spec needs:** **none yet — the shape below is a recommendation and the predictability
question in §6 wants a ruling before the call sites change.** Owner ruling **D3 (b)** already binds it: an
unreachable condition is a finding, not a licence for a new route.
**Machine:** to be written — one named helper beside the four minting sites (see §4), reusing the existing
derivation chain; **no new hash and no new RNG**.
**Tests:** to be written with the machine — the double-run falsifier already exists and is the measurement.

> **Where this document lives, and why.** The map promises
> `docs/architecture/rpg-simulator/spec-seed-seam.md`. The delivery lane's fence is
> `docs/architecture/rpg-simulator*`, a *file prefix*, so this spec is a sibling of the program's other
> documents and the map's seed row points here — the same class of erratum as **RS-F5** (the clock seam's
> own spec has the same shape).

---

## 0. The measurement this spec starts from, and the row's correction

**RS-F4's row names two server-minted seeds. There are four**, and the correction is measured, not inferred:

| # | Site | The idempotency key already in scope |
|---|---|---|
| 1 | `gk-core/src/FusionRpg.Server/CreatureEndpoints.cs:95` — the summon route | `body.CorrelationId` (required, ≤64, `:88-92`) |
| 2 | `gk-core/src/FusionRpg.Server/ExpeditionEndpoints.cs:38` — expedition dispatch | `body.CorrelationId` (required, ≤64, `:286-290`) |
| 3 | `gk-core/src/FusionRpg.Server/FusionEndpoints.cs:39` — fusion execute | `body.CorrelationId` (required, ≤64, `:33-37`) |
| 4 | `gk-core/src/FusionRpg.Server/WebMatchService.cs:122` — the web-match battle seed | `corr` (`:106`, trimmed; the atomic append at `:130` is its replay gate) |

All four mint the same way — `BitConverter.ToUInt64(Guid.NewGuid().ToByteArray(), 0)` — and all four already
have a caller-supplied idempotency key in scope, which is what makes one seam possible instead of four
mechanisms. (Two of the four are what RS-F4's row measured; the fusion and web-match sites are the additions
this lane found by scanning for the mint idiom rather than trusting the row's count.)

**What the row measured, kept as the acceptance's yardstick:** two fresh in-process hosts, the same scenario
file — the **declared** digest is identical
(`daa9df408054f32e762eae9abdd5ea5c98312170e175abdb295e2c210cf9db3e`) while the falsifier over every reading
moves **71–110 named pointers** (the count itself varies), all of them downstream of those four seeds.

---

## 1. The one sentence the seam obeys

> **A run's RNG seed is an INPUT the idempotency key already carries, not an ambient fact.**

Everything below is that sentence made mechanical: the seed is a pure function of inputs the caller supplied,
it is the same on a fresh host as on the host that minted the row first, and no route exists whose purpose is
to set it.

## 2. Why this is product surface (and what that obliges)

The idempotency contract is already the product behaviour: every one of the four routes takes a
`correlationId`, dedupes on it, and stores the outcome (`rpg_summon_log.rng_seed`,
`rpg_expeditions.seed`, the web-match log row). Today that contract is **half-honest**: a replay of the same
key returns the stored outcome, but the FIRST mint is ambient — so "the same request" and "the same run" are
only accidentally the same, and the sim can only prove digest identity over a residue (a terminal state, a
tier, a row id, the run engine).

The obligation, concretely:

| Obligation | Shape |
|---|---|
| **Named** | One helper with a name a reader can find, beside the four sites (§4). Not a bool, not an inline expression copied four times. |
| **One derivation, reused** | The seed derives through the **existing** chain — `WorldSeed.DeriveRollSeed` (`gk-core/src/FusionRpg.Core/Effects/Atoms/WorldSeed.cs:24`), whose own doc says it is *"the ONE place `hash(worldSeed, streamName, targetId)` is computed … never reimplements it, or two runtimes could disagree on the same seed"*. A new hash here would be the third-vocabulary defect that file exists to prevent. |
| **Reachable without a SIM build** | It is not behind `SimFlags.Enabled`: a release build derives the same seed, and a player's retry with the same key gets the same run. |
| **Declared in a verdict** | The verdict already carries the scenario seed and its derived correlation id; once this lands, the corpus's declared digest can cover roster and battle values for the first time, and the falsifier's residue is what proves it. |
| **The refusal it protects still works** | No new route. The scenario cannot *send* a seed; it sends a correlation id, which it already does (`derived:correlationId`, `gk-core/tools/RpgSim/ScenarioVocabulary.cs`). |

## 3. The shape

```
seed = unchecked((ulong)WorldSeed.DeriveRollSeed(playerId, "<route stream>", correlationId.Trim()))
```

- **`playerId` is the run seed's base**: a per-player stream, so two players using the same key never share a
  roll. `WorldSeed.DeriveRollSeed` takes it as its `worldSeed` axis.
- **The stream name is the route's own, stable and authored** — `"summon"`, `"expedition"`, `"fusion"`,
  `"web-match"` — matching the `system:purpose` convention `WorldSeed`'s own doc names. Two different routes
  rolling for the same player and key therefore never collide, and neither does one route at two moments.
- **The correlation id is the target axis**, trimmed exactly as the routes already trim it.
- **One helper, four callers.** The helper is a named static in the server (e.g.
  `FusionRpg.Server.CorrelationSeed.For(playerId, stream, correlationId)`) — a thin, testable wrapper that
  exists so the four sites cannot drift and so the choice of stream names is in one place. It adds no
  algorithm: it calls the Core chain.
- **Nothing else changes.** The stores keep taking a `seed` parameter (they already do:
  `ExecuteSummon(..., seed, focus)`, `DispatchExpedition(..., seed)`, `ExecuteFusion(..., seed)`), the
  replay paths keep returning the stored outcome, and the resolvers stay the pure functions they already are
  (`gk-core/src/FusionRpg.Core/Expeditions/ExpeditionResolver.cs:41`, `BattleEngine`).

## 4. The measured surface (this lane's own scan, 2026-09-23)

Binary-safe scan of `src/**/*.cs` for the mint idiom `BitConverter.ToUInt64(Guid.NewGuid().ToByteArray(), 0)`:

| Site | Route / caller | Migration |
|---|---|---|
| `CreatureEndpoints.cs:95` | `POST /api/creatures/summon` | `seed = CorrelationSeed.For(pid, "summon", body.CorrelationId!)` |
| `ExpeditionEndpoints.cs:38` | `POST /api/expeditions/dispatch` → `ExpeditionService.DispatchAsync` | `CorrelationSeed.For(playerId, "expedition", correlationId)` |
| `FusionEndpoints.cs:39` | `POST /api/fusion/execute` | `CorrelationSeed.For(pid, "fusion", body.CorrelationId!)` |
| `WebMatchService.cs:122` | the web-match battle seed (called by expedition collect and by `/api/test/web-match`) | `CorrelationSeed.For(playerId, "web-match", corr)` |

**Four sites, one commit.** The change is mechanical and the measurement is the existing double-run test —
there is no separate harness to build.

## 5. What it buys, and what it costs

**Buys.** The corpus's declared digest can cover the roster (`roster[*].profile.speciesId`/`.rarity`/
`.elementPrimary`, `actor.typeId`, `actor.side`) and the battle outcomes, because a fresh host now derives
the same seeds from the same file. The falsifier's residue shrinks from 71–110 pointers to the genuinely
per-run values (fresh GUIDs, insert counters, wall-clock stamps — all already named in
`readback-verdict.md` §3), which is exactly what RS-F4's acceptance asks for and what the S2/S3 checkpoints
want. The idempotency contract also becomes honest *before* the row exists, not only after.

**Costs, stated rather than discovered later.** The derivation is public, so a client that knows it can
compute the roll for a chosen key *before* sending it and search offline for a favourable one. Today a client
can only retry, and every retry costs it the souls/materials the route charges. The **capability is therefore
not new** — a player can already reroll without limit — but the *cost of searching* drops from "pay per roll"
to "compute per roll". That is the one thing here that wants the owner's eye, and §6 says why the obvious
defences do not work for this program.

## 6. Refused shapes, each with its reason

| Shape | Why it is refused |
|---|---|
| **An explicit `seed` field on the four bodies** | It is a client-supplied RNG input by a clearer name: the same predictability as §5, with none of the "the key already means the run" reasoning, and it invites a *different* seed per retry (the exact reroll-farming the correlation id exists to stop). |
| **A `/api/sim/*` route that sets the seed** | Owner ruling **D3 (b)**: an unreachable condition is the finding, never a licence for a new route — and a sim-only seed route is a store-shaped bypass wearing a URL. |
| **A server-global seed configuration** (the clock seam's analogue) | **Wrong scope.** A clock is per-process; a seed is per-request. A global would make every player's summon, every expedition and every battle in one server process roll identically — a real defect, not a test seam. |
| **A salted / per-save secret** (`HMAC(saveSecret, correlationId)`) | It defends §5's predictability, and it **defeats this program's purpose**: the double-run falsifier runs on *fresh hosts*, so a per-save secret is freshly generated in each and the two hosts derive different seeds. The digest could never become stable across hosts, which is the property RS-F4 exists to buy. A *constant* salt is not a secret; a *configured* salt is the clock seam's `FUSIONRPG_CLOCK_OFFSET` shape applied to a per-request quantity, and would make the sim's reproducibility depend on an env var the scenario cannot see. |
| **Deriving from a timestamp, an insert id, or any ambient value** | It reintroduces the ambient fact this seam removes, and the world-simulation purity scan's whole argument (`WorldDeterminismGuardTests`) is that a replayable roll may read no ambient state. |

## 7. Migration order

One increment, one commit, because the four sites are one mechanical change and a partial landing leaves the
digest covering nothing:

| # | Increment | Files | State |
|---|---|---|---|
| 0 | **This spec**, and the map's module row | `docs/architecture/rpg-simulator-spec-seed-seam.md`, `docs/architecture/rpg-simulator-map.md` | **this commit** |
| 1 | `CorrelationSeed` + the four call sites | the four files in §4 + the new helper | owed — **waits on the §6 ruling** (predictability), because it changes what a live player can compute |
| 2 | The corpus's declared digest covers the roster and the battle values, and the falsifier's residue is re-measured | `gk-core/tests/fixtures/rpg-scenarios/first-session-forward.json` (the `digest` step), `tasks/reports/rpg-sim-rs3.md`-style evidence | owed — depends on 1 |

**What "done" looks like, as a reading:** the same scenario file on two fresh hosts reports the same declared
digest *and* the falsifier's moved-pointer count drops to the named per-run values — the count is the
measurement, and it is reported, never smoothed.

## 8. NOT covered here

- **The corpus's digest scope today.** Until increment 1 lands, the digest is deliberately scoped to
  host-stable readings, and `tasks/rpg-simulator-plan.md` §11 says so with this row as the reason — that is
  RS-F4's acceptance branch (b), and it is satisfied by that statement rather than by silence.
- **The resolvers' own determinism.** `ExpeditionResolver` and `BattleEngine` are already pure functions of
  `(tier, squad, seed, elapsedTicks)`; nothing here changes them.
- **The XP ledger's one-letter timestamp** — RS-F7, closed separately (`gk-core/tools/RpgSim/readback-verdict.md` §3).
- **`SquadHarness` / `CombatSim`** — their `--seed` is already required and caller-supplied
  (`gk-core/tools/SquadHarness/Program.cs:35-39`); they have no ambient mint.
- **A guard.** Unlike the clock seam, this one needs no new guard: the mint idiom is four lines, and a guard
  that fails a fifth is worth adding *with* increment 1 — recorded here as owed rather than assumed.
