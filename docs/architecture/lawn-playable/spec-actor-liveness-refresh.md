# Spec: `actor-liveness-refresh` (lawn-playable module 1)

**Program:** [lawn-playable](../lawn-playable-map.md) · **Depends on:** nothing ·
**Unblocks:** `hub-snapshot-cache` · **Closes:** live-probe Tasks 23, 24, 25
**Status:** spec, 2026-09-16. Not built.

## Objective

Make an actor's live numbers follow the player's actual state. Today the injector hydrates Θ, the
commander allocation, the unique allocations, the tree atoms and the deploy roster **once, at connect**,
and refreshes some of them on a hand-picked set of SignalR events. Everything else silently keeps the
value it had when the game started.

Measured consequences, all live on 2026-09-16:

| Observed | What it means |
|---|---|
| Player went level 1 → 5; server read `theta 7`; every injector `debug.aptitude-trace` still read `theta 1` | Θ is the input to every magnitude (`k × share^γ × P(Θ)`). A player who levels during a session gets none of it. |
| `PUT /api/players/current {"id":6}` — server reported player 6 and attributed board events to 6, injector traces read `ctxPlayerId 1, currentPlayerId 1` | Every stat, and every soul credited by `MatchHost`, is attributed to the boot-time player. |
| 12 Might allocated to a Bound specimen: no change live; kill + redeploy: `attack 2939 → 3116` | An entity composes at bind time and never again, so an allocation "does nothing" until the next deploy. |
| A commander allocation made mid-session did not reach a freshly spawned plant (`attack 20`, vanilla) while species-scoped zombie aptitudes on the same board did apply | Two caches, refreshed by different events, disagree. |

This module replaces "a hand-picked set of events refresh a hand-picked set of caches" with **one typed
invalidation, one per-actor revision**. It is also the precondition for `hub-snapshot-cache`: caching a
snapshot that already never refreshes would freeze these bugs permanently.

## Signal ownership (recorded 2026-09-20, `backlog-clean-up` `lawn-signal-ownership`)

**`SP6.6`** (`summoner-convergence` lane B, `species-progression-todo.md`) owns the one generic
server → injector notice on `PUT /api/players/current` — the parent convergence plan's own rule, which
`solid-enforcement` and `notification-ssot` already reuse rather than duplicate. This module's `Player`
row below **is `SP6.6`'s notice, extended, not a second channel.** It rides `SP6.6`'s transport and adds:
- the closed kinds `Ladder`, `CommanderAllocation`, `UniqueAllocation`, `Equip`, `Tree` (this module's
  own scope, P3/P4);
- a reserved `empireId` field on the shared payload, so `SE4.31`–`SE4.36` (save-identity's SignalR
  `empireId` work) never has to retrofit the shape once it ships.

This is hard edge E1/E2 (`backlog-clean-up-plan.md`): no lawn build task on this module starts before
`SP6.6` ships, and this module never adds its own `Player`-kind notice.

## ⛔ One of those four rows is not a bug — audit correction, 2026-09-16

**The commander allocation is frozen for the duration of a match, on purpose.**
`MatchCommanderSnapshotHolder.ResolveAllocation` is one line and says so: *"Hot-path allocation: frozen
snapshot during a match, live cache outside"*, with `BeginMatch` called at `board.start`
(`MatchHost.cs:194`) and cleared on every match-end path. So "a commander allocation made mid-session
did not reach a freshly spawned plant" is the design working: the snapshot was taken when the player had
nothing allocated, and every entity in that match correctly read nothing.

This module **must not silently overturn that.** Two things follow:

1. **Owner ruling 2026-09-16: the freeze stays, and is made legible.** A match is a fixed contract —
   a player cannot rebuild mid-wave against a wave they are losing.
2. What is genuinely wrong — and is this module's own work — is that the freeze is
   **indistinguishable from a failure**. A player who
   allocates mid-match sees nothing happen and has no way to learn that it applies next match. Making
   the frozen state *legible* — the sheet and the injector both able to say "this build applies from the
   next match" — is in scope here, and is the honest half of this row.

The other three rows are real defects and stay: Θ never moves after connect (that is not match-scoped —
the player levelled between matches and it still read 1), a player switch never reaches the injector,
and the unique-specimen scope did not apply mid-match even though it is **not** covered by the match
freeze (`RefreshUniqueAptitudesAsync` maintains a live cache keyed by Bound instance id). That last one
is a hypothesis with two candidates — the unique cache did not carry the new allocation, or the
ptr → instanceId mapping for the bound entity did not resolve — and this module's first task is to
determine which, not to assume.

## Tech stack

`FusionRpg.Server` (the sender), `FusionRpg.Injector` (`RpgClient`, `CheatState`), existing SignalR
`Command` channel and `InjectorCommandInbox`. `FusionRpg.Core` owns the revision type. No new transport,
no new dependency.

## Commands

```powershell
dotnet test gk-core/tests/FusionRpg.Core.Tests --filter "FullyQualifiedName~ActorRevision|Liveness"
dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~Invalidat|Aptitude|Player"
python gk-core/scripts/guard-actor-hub.py ; python gk-fusion/scripts/guard-single-writer.py
.\scripts\verify-change.ps1 -Paths <changed files> -Session <session id>
```

Live check (this machine, after `deploy-play.py --no-server`): allocate mid-match and read
`debug.aptitude-trace` for a living ptr; switch player and read `ctxPlayerId`; level up and read `theta`.

## Project structure

| What | Where |
|---|---|
| The revision type + the closed invalidation vocabulary | `gk-core/src/FusionRpg.Core/Stats/Derived/ActorLivenessRevision.cs` (new) |
| Server-side send | beside the existing `AptitudesUpdated` / `CreaturesUpdated` broadcasts |
| Injector receive + refresh | `gk-fusion/src/FusionRpg.Injector/RpgClient.cs`, `CheatState.ApplyPowerSnapshot` |
| Tests | `gk-core/tests/FusionRpg.Core.Tests/Stats/ActorLivenessRevisionTests.cs`, `gk-core/tests/FusionRpg.Server.Tests/LivenessInvalidationTests.cs` |

## The shape

**One closed vocabulary of what can change**, owned by the code (so its membership IS the contract and a
test may pin it):

| Kind | Bumped by | Scope |
|---|---|---|
| `Player` (owned by `SP6.6`, not this module — see "Signal ownership" above; carries a reserved `empireId` field for `SE4.31`–`SE4.36`) | `PUT /api/players/current` | whole session |
| `Ladder` | a progression level change (Θ inputs) | one player |
| `CommanderAllocation` | `POST /api/aptitudes/allocate` | one player — **and it lands at the next `board.start`, not mid-match**, because of the freeze above; the invalidation still fires so the out-of-match cache is correct |
| `UniqueAllocation` | `POST /api/aptitudes/unique/allocate` | one specimen |
| `Equip` | equip / unequip, either scope | one holder |
| `Tree` | a passive-tree spend | one player |

Rules:

1. **The server names what changed; the injector decides what to re-read.** The server never sends
   values through this channel — it is an invalidation, not a push. (The existing atom-grant push stays
   exactly as it is; this does not replace it.)
2. **One revision per actor, monotonic.** `ActorLivenessRevision` is a `long` counter per
   `(playerId, entityKey)`; every consumer keys on it. It is a counter, not a hash — cheap to compare,
   impossible to collide.
3. **A living entity re-composes when its revision moves**, not only at bind — for the scopes that are
   not match-frozen (unique specimen, equip, tree, Θ). The commander scope re-composes at the next
   `board.start`, which is the existing design, and the entity path must not special-case it: it reads
   whatever `ResolveAllocation` returns, frozen or live, exactly as it does today.
   ⚠️ **Bound the re-compose.** An invalidation during a 300-zombie wave must not recompose 300 actors
   inside one frame — that would hand `rider-hit-cost` a new spike to fix. Re-compose lazily (mark
   dirty, recompose on next read) rather than eagerly, and assert the bound in test.
4. **`Player` invalidation (`SP6.6`'s notice) re-hydrates Θ**, which is the Task 24 + Task 25 fix in one
   line: the injector already has `RefreshPowerIndexAsync`; nothing ever calls it after connect. This
   module adds the injector-side handler; it does not send the notice itself.
5. **A missing or unknown kind is a refusal, never a silent skip** — an unknown kind means the server is
   newer than the injector, and quietly ignoring it is how P3 survived.

## Testing strategy

Contract and closed vocabulary (`validation-ssot.md`), never a reading:

- ✅ The invalidation kind enum's membership is pinned (a closed vocabulary the code owns — say why in
  the test).
- ✅ Each server verb that changes an input sends exactly one invalidation naming the right kind and
  scope — asserted per verb, so a new verb that forgets it fails.
- ✅ A revision bump makes the next compose differ; no bump makes it identical.
- ✅ An unknown kind is refused and reported, not swallowed.
- ❌ Never assert Θ, a bonus value, or how many entities re-composed. Those are readings.

**Mutation to kill:** delete the bump from one verb — its test must go red. That is the only property
that matters here.

## Boundaries

- **Always:** send an invalidation from the same transaction that changed the input; keep the vocabulary
  closed; make the injector's refresh idempotent (a duplicate invalidation is free).
- **Ask first:** nothing.
- **Never:** send values on this channel (that is the grant push's job, and two writers for the same
  numbers is the `BattleStatComposer` mistake); re-compose every actor on every invalidation (scope it,
  or P1 gets worse, not better); add a second composer or a private fold.

## Numeric types

The revision is a `long` counter. No magnitude is introduced.

## ActorHub gate

**Consumes Hub, and re-runs the existing compose.** No new subsystem, no second composer. The only
change to `ActorHub` is that a caller may now ask "has this actor's input changed since revision N",
which module 2 uses to skip work.

## Success criteria

1. Allocating **unique-specimen** points mid-match changes that specimen's live numbers with no
   redeploy (Task 23's real half). The commander scope still lands at the next `board.start`, and the
   sheet says so in words rather than looking broken.
2. `PUT /api/players/current` changes `ctxPlayerId` in the next injector trace (Task 24).
3. A level-up during a session moves `theta` in the next trace (Task 25).
4. A commander allocation and a species allocation reach a freshly spawned plant the same way.
5. No invalidation storm: a single allocation produces one invalidation, not one per living entity —
   asserted by counting sends, which is a contract, not a reading.

## Open questions

None. The one that existed — whether the commander build stays frozen for a match — was ruled on
2026-09-16: **keep it frozen, and say so to the player.** The sheet and the lawn surface must show a
queued build as queued ("applies next match"), which turns today's silent no-op into a stated rule.
