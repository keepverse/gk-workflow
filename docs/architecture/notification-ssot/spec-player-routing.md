# Spec: player-routing

**Status: Draft — Phase 1 (Specify), awaiting owner review.** Module `player-routing` of the
[notification-ssot map](../notification-ssot-map.md), wave 1, no dependencies. **R-N1's blocking
prerequisite:** `notify-service` may not push payload content until this module ships.

---

## Objective

Route a server push to **one player's** web sessions. R-N1 rules that we assume more than one
session, for multiplayer or for an LLM playing as another player. Today every push fans out to all web
clients:

- `RpgHub.Join(role)` adds a connection to exactly one of two groups, `injector` or `web`
  (`gk-core/src/FusionRpg.Server/RpgHub.cs:29-35`; constants at `gk-core/src/FusionRpg.Contracts/Dtos.cs:244-245`).
- No per-player group exists anywhere. The server's idea of "the player" is one global setting,
  `current_player_id` (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs:1147-1151`, set at `:1191-1197`),
  which `HealthDto.CurrentPlayerId` exposes (`gk-core/src/FusionRpg.Contracts/Dtos.cs:49`).
- The web joins `web` on start and again on reconnect, and does nothing else
  (`gk-web/web/fusion-rpg-web/src/lib/bus/hub-provider.tsx:212-218` on start, `:205-208` on reconnect).

**"Player" means the save (R17).** The `players` row is the save and its id is the `SaveId`
(`solid-enforcement/spec-save-identity.md` Decision 1, ruling R17). The wire keeps the word
"player", as `save-identity` §Contracts does for every existing `{playerId}` route and payload: the
group `player:{id}` and the hub method `JoinPlayer` route to a **save**. Server-side parameters are
named `saveId` and become the `SaveId` type once `save-identity` ships (map §Identity). A connection
joins the save **it is showing**. That is not necessarily the server-wide `current_player_id`, which
this module never reads on the server.

This module adds a per-player group plus a push seam that routes on the player id, following
`IDelveLivePush`'s shape (`gk-core/src/FusionRpg.Server/DelveLivePush.cs:54-80`): a plain interface tests can
fake, one hub-backed implementation, fire-and-forget.

**What this is not: a security boundary.** The server is localhost-only with no auth in v1
(`software-architecture.md` §1, "No auth in v1. Localhost only"), and the world endpoints already call
the client trusted (`WorldEndpoints.cs:394-397`). A group is **routing**: it keeps player A's text off
player B's screen, which is what R-N1 asks for. It does not defend against a hostile client that
claims another player's id.

## Design

### 1. Server

```csharp
// gk-core/src/FusionRpg.Contracts/Dtos.cs — beside InjectorGroup/WebGroup (new members)
public const string PlayerGroupPrefix = "player:";
public static string PlayerGroup(long playerId) => PlayerGroupPrefix + playerId.ToString(CultureInfo.InvariantCulture);

// gk-core/src/FusionRpg.Server/PlayerPush.cs (new)
public interface IPlayerPush
{
    /// <param name="saveId">The save (players.id, R17). Routes to group PlayerGroup(saveId).</param>
    void Push(long saveId, string eventName, object payload);
}

public sealed class HubPlayerPush : IPlayerPush
{
    readonly IHubContext<RpgHub> _hub;
    public HubPlayerPush(IHubContext<RpgHub> hub) => _hub = hub ?? throw new ArgumentNullException(nameof(hub));

    /// <summary>Fire-and-forget, like HubDelveLivePush: a push is a notice about an ALREADY-durable
    /// write (the catch-up GET is the correctness path), so a dropped frame costs a live update only.</summary>
    public void Push(long saveId, string eventName, object payload) =>
        _ = _hub.Clients.Group(RpgConstants.PlayerGroup(saveId)).SendAsync(eventName, payload);
}
```

- `RpgHub.JoinPlayer(long playerId)` (new) returns `bool`. It refuses (returns `false`) an id with no
  `players` row. Once `save-identity` adds `players.archived_utc`, it also refuses an archived row
  (the legacy Zomboss row, that spec's D2), by reading the same filter `ListPlayers` uses. It never
  reads `current_player_id`. Otherwise it removes the connection from its previous player group, if any, then
  adds it to `PlayerGroup(playerId)`. One connection is in **at most one** player group.
- The previous-group record is an in-memory map `connectionId → playerId` in a singleton
  `PlayerConnectionRegistry` (new). `RpgHub.OnDisconnectedAsync` (`RpgHub.cs:249-253`) removes the
  entry. That method already exists for the delve freeze, and this adds one line to it.
- The registry is structural runtime state and is never persisted. A server restart drops every
  connection, and every client re-joins through the reconnect trigger below.

### 2. Web (`lib/bus` only — software-architecture §2, Web row)

`lib/bus/playerRouting.ts` (new) owns one effect: after `Join("web")` succeeds, invoke
`JoinPlayer(currentPlayerId)`, then emit a local `player-joined(playerId)` signal that `notify-client`
uses to start its catch-up. `hub-provider.tsx` changes only by calling it on the paths that already
call `Join`.

**The full trigger set (DESIGN-GATE §2 invariant 16).** The per-connection group is an edge-refreshed
cache keyed by player, so every edge that can change it is listed here and tested:

| # | Trigger | What happens | Why it is a separate edge |
|---|---|---|---|
| T1 | Connection start | `Join("web")` → `JoinPlayer(shownSaveId)`, where `shownSaveId` is the save the web is showing (today `/api/players` `currentPlayerId`, `gk-web/web/fusion-rpg-web/src/app/SaveSelect.tsx:26`) | First membership |
| T2 | **Reconnect** | Same pair, on `onreconnected` | A reconnected connection has a **new** connection id and no groups. This is the exact defect §2 invariant 16 records (`gk-fusion/src/FusionRpg.Injector/RpgClient.cs:143-147`) |
| T3 | **Save switch** in this session: `useSelectPlayer` succeeds (`gk-web/web/fusion-rpg-web/src/lib/bus/mutations.ts:184-194`, which calls `PUT /api/players/current`, `gk-core/src/FusionRpg.Server/Program.cs:965-966`) | `JoinPlayer(newId)`, which also leaves the old group | This is the **key-set** edge: nothing reconnects, but the save whose pushes the connection should get has changed. The PUT pushes nothing to other sessions, and `Health` is pushed only on an injector heartbeat (`gk-core/src/FusionRpg.Server/RpgHub.cs:177`). That is correct here: another session keeps showing its own save, so it keeps that save's group. If a `Health` push does change what a session shows, it re-joins through this same path |
| T4 | Disconnect | Server removes the registry entry | Keeps the registry from growing without bound |
| T5 | `JoinPlayer` refused (unknown id) | The client stays in no player group and logs once. `notify-client` shows its designed error state, never a blank feed (GG-17) | The failure edge |

T1 → T3 → T2 in any order must end with the connection in exactly the current player's group. That
criterion does not depend on order, and the tests cover both T2-then-T3 and T3-then-T2.

## Commands

```powershell
dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~PlayerRouting"
cd web\fusion-rpg-web; npm test -- lib/bus/playerRouting; npm run build
.\scripts\verify-change.ps1 -Paths <every changed file> -Session <session-id>
```

## Project structure

```
gk-core/src/FusionRpg.Contracts/Dtos.cs                       → PlayerGroupPrefix, PlayerGroup(id)
gk-core/src/FusionRpg.Server/PlayerPush.cs                    → IPlayerPush, HubPlayerPush
gk-core/src/FusionRpg.Server/PlayerConnectionRegistry.cs      → connectionId → playerId (runtime only)
gk-core/src/FusionRpg.Server/RpgHub.cs                        → JoinPlayer; one line in OnDisconnectedAsync
gk-core/src/FusionRpg.Server/Program.cs                       → DI registration (singletons)
gk-web/web/fusion-rpg-web/src/lib/bus/playerRouting.ts       → T1–T3 invocations + player-joined signal
gk-web/web/fusion-rpg-web/src/lib/bus/hub-provider.tsx       → calls playerRouting on the existing Join paths
gk-core/tests/FusionRpg.Server.Tests/PlayerRoutingTests.cs
gk-web/web/fusion-rpg-web/src/lib/bus/playerRouting.test.ts
```

## Code style

```ts
// lib/bus/playerRouting.ts — one function, called from every path that joins "web".
export async function joinCurrentPlayer(c: HubConnection, playerId: number): Promise<boolean> {
  const ok = await c.invoke<boolean>("JoinPlayer", playerId);
  if (ok) emitPlayerJoined(playerId); // notify-client starts its catch-up on this, never before
  return ok;
}
```

## Testing strategy

- **Server (xUnit, `Server.Tests`).** `JoinPlayer` with an unknown id returns `false` and joins
  nothing. A second `JoinPlayer` on the same connection leaves the first group (asserted through a
  fake `IGroupManager`). Disconnect clears the registry. `HubPlayerPush` sends to
  `PlayerGroup(id)` and never to `WebGroup` (fake `IHubContext`).
- **Isolation.** Two connections joined as players 1 and 2. A push to 1 reaches only the first. This is
  the R-N1 acceptance test, and G1 in the map re-runs it end to end.
- **Web (vitest).** Each of T1–T3 invokes `JoinPlayer` with the right id; T3 without a reconnect; T2
  and T3 in both orders end on the shown save's id; T5 renders the designed error state. A second
  session that did not switch keeps its group after the first session's T3.
- **Archived row.** Once `save-identity` has shipped, `JoinPlayer` on an archived row returns `false`.
- The in-memory store is used (testing-standard). No temp directories.

## Boundaries

- **Always:** route content pushes through `IPlayerPush`; join on every path that joins `web`; keep
  one connection in at most one player group.
- **Ask first:** moving any of the ~50 existing id-only `WebGroup` pushes onto player groups. That is
  follow-up work the map names and does not schedule.
- **Never:** a second hub (ideal §Prior art); a content push to `WebGroup` or `Clients.All`;
  presenting the group as an auth boundary; persisting the connection registry.

## Success criteria

1. `JoinPlayer` exists, refuses unknown ids, and moves a connection between player groups.
2. `IPlayerPush` reaches only the target player's connections, proven by the isolation test.
3. The web re-joins on start, reconnect and player switch, each with its own test.
4. `verify-change.ps1` green; `guard-dal.py` green (this module adds no SQL).

## Seedsmith / generator

None. Transport code with no content.

## Open questions

None. R-N1 decided the prerequisite, and R17 decided what "player" means. The trust model is the one
the repo already documents.
