# Spec: notify-client

**Status: Draft — Phase 1 (Specify), awaiting owner review.** Module `notify-client` of the
[notification-ssot map](../notification-ssot-map.md), wave 4. Depends on `notify-vocabulary`,
`notify-format`, `notify-service` and `player-routing`.

**Rulings it carries:** R-N4 (Critical first at the three-toast cap), R-N5 (dedup on `dedupKey`),
R-N6 (a batch is evaluated as one ordered set), R17 (the feed is per save; map §Identity).

**Strengthen pass 2026-09-18:** the catch-up cursor is `rev`, not `seq`, so a reconnect also sees
state changes made elsewhere; a merge keeps the higher `rev`, so a slow page cannot undo a newer
change; a batch labelled `catchUp` never toasts (map §Strengthen pass S2, S3).

---

## Objective

One feed per save on the web, fed only by the server. Every stage uses it:

- **Toasts** go through the shipped band-4 stack (`gk-web/web/fusion-rpg-web/src/shell/toastStack.ts:36-58`,
  rendered by `shell/Toasts.tsx`, mounted once at `app/App.tsx:29`). That stack already has
  `action` and `category` (`toastStack.ts:10-16`). This module adds `severity` and a selection that
  puts Critical first.
- **The rail** gets its items through a declared **mount policy**, which this module defines. The
  rail itself (`world-notify`'s components) moved to `shell/notify/rail/` in `world-notify-source`
  (NS5.7–NS5.9, landed 2026-09-21 once the owner accepted ask A1, map §G0 answers), and the world
  copy is gone (NS5.11). It is mounted on the world stage only in v1.
- **State** (read, dismissed, undo) is the server's, through `notify-service`'s REST, so a reload or a
  second session sees the same thing.

What this replaces: today the rail is fed by one local `useState` (`stages/world/WorldStage.tsx:142`,
landed when the wire was built), and nothing in production calls its End Turn flush (`onCommit`, which
lived at the old `stages/world/notify/notifyRailStore.ts:23-25` — that file is GONE as of NS5.7; it is
`shell/notify/rail/railStore.ts` now, and `flush`/`onCommit` were retired in favour of `worldLatestTurn`).
So the GG-50 bound the rail declares (`ui/volumeMatrix.test.ts`, "World notification rail") was, at this
spec's writing, a claim with no wiring behind it. The mount policy below makes that bound structural.

## Design

### 1. Where the code lives

- **Server access only through `lib/bus`** (software-architecture §2, Web row). The new
  `lib/bus/notifications.ts` subscribes to `NotificationBatch` and `NotificationStateChanged`, pages
  the catch-up GET, and exposes `useSetNotificationState()` as a TanStack mutation (the `decisions.md`
  "Web UI kit / bus" row: "Features call `useX()` only"). It uses `getHubConnection()` directly
  rather than adding more handlers to `HubProvider`'s list (`lib/bus/hub-provider.tsx:187-201`). One
  responsibility per file.
- **Feed state** lives in `shell/notify/feed/feedStore.ts` (zustand, like `toastStack`), with **pure**
  reducers in `feedReducer.ts`: `applyItems`, `applyStateChange`, `resetForPlayer`. The rail store is
  already written this way (the world's old `notifyRailStore.ts`, GONE as of NS5.7 — now
  `shell/notify/rail/railStore.ts` — is pure `(items) => items`).
- **One app-level mount**, `shell/notify/NotificationWire.tsx`, placed beside `<Toasts />` in
  `App.tsx`. It wires bus → feed → toasts, and it renders nothing itself.

### 2. The feed

```ts
export type FeedItem = NotificationItem & {           // NotificationItem = notify-vocabulary's wire mirror
  /** Set only from the server's state; the rail never invents one. */
  state: "unread" | "read" | "dismissed";
};
export type FeedState = {
  playerId: number | null;           // the save being shown (R17)
  byKey: Record<string, FeedItem>;   // keyed by dedupKey — R-N5, the one identity
  maxRev: number;                    // since-cursor for the next catch-up (notify-store property 4)
  status: "idle" | "loading" | "ready" | "error";
};
```

**The full trigger set for this cache (DESIGN-GATE §2 invariant 16).** It is keyed by save, so the
key-set edge is a save switch:

| # | Trigger | Effect | Toasts? |
|---|---|---|---|
| F1 | `player-joined(id)` (`player-routing` T1) | `resetForPlayer(id)` if `id ≠ playerId`, then page `GET …/{id}?since=maxRev` until `hasMore = false`, then `applyItems(…, "catch-up")` | **Never** |
| F2 | Reconnect (`player-routing` T2 emits `player-joined` again) | Same as F1, from the current `maxRev`, with no reset. Because every state change bumps `rev`, this also brings back a dismiss or read another session made while this one was offline | Never |
| F3 | **Save switch** (`player-routing` T3) | Reset (the old save's items leave, which is the key-set edge), then catch up from 0 | Never |
| F4 | `NotificationBatch` for the current save with `delivery = live` | `applyItems(batch.items, "live")` | Yes, through §4 |
| F4b | `NotificationBatch` for the current save with `delivery = catchUp` (a boot run or a lagging turn, `notify-service` §2) | `applyItems(batch.items, "catch-up")` | **Never** |
| F5 | `NotificationStateChanged` | `applyStateChange`, per `{ seq, rev }` | — |
| F6 | This session's read / dismiss / undo | Mutation, then apply the server's `changed` list (GG-15: acknowledge at once by showing the control as pending; never paint the new state before the server returns) | — |
| F7 | A batch for a save other than `playerId` | Ignored, and logged in development. Routing (R-N1) should make it unreachable | — |

**Order independence (DESIGN-GATE §5).** F4 can arrive before, during or after an F1 page, and F5
can arrive while an F1 page is in flight. Two rules make every order end in the same state:

1. `byKey` dedups on `dedupKey`, so a row delivered twice is one item.
2. **A merge keeps the copy with the higher `rev`.** A page fetched before a dismiss can land after
   the dismiss's F5. Without this rule the older page would paint the row unread again.

An item toasts only when it first arrives through F4. An item seen first through catch-up (F1, F2,
F4b) never toasts, and a later live copy of an item already held does not toast it again. Tests cover
push-then-GET, GET-then-push, and page-in-flight-then-state-change.

**Error state (GG-17).** A failed catch-up sets `status = "error"`. The rail and the centre render the
designed failed state with a retry. The feed is never shown empty in its place.

### 3. Channel routing

`shell/notify/channelSettings.ts` (new) is the open-id successor to
`stages/world/notify/channelSettings.ts`. It has the same shape (localStorage behind a try/catch, and a
change event so two mounted controls cannot drift), its category type is the open `NotifyCategoryId`,
and its defaults are `defaultChannelOf(id)` (`notify-vocabulary` §4). It **reuses the storage key**
`fusionrpg.world-notify.channels.v1` (`shell/notify/channelSettings.ts:14`; the world's old
`stages/world/notify/channelSettings.ts`, which first used the same key, is GONE as of NS5.11), so a player's
existing choices survive. The world copy stays in use until `world-notify-source` deletes it in wave
5. That one-wave overlap is named here and has a removal step. The player's setting is authoritative
for every category, Critical included (map §Open questions).

### 4. Toast selection (R-N4, R-N6)

- Only items that arrive first through F4 (`delivery = live`) and whose resolved channel is `toast` are pushed, each with `title` and `body` from
  `renderNotification` (`notify-format`), plus `category`, `severity` and an action if the mount
  resolves one (§6).
- `ToastEntry` gains `severity?: NotifySeverity` (additive). Mutation-feedback toasts
  (`lib/bus/mutationFeedback.ts:17-34`) have none and count as routine.
- `Toasts.tsx` replaces `toasts.slice(-VISIBLE_CAP).reverse()` (`Toasts.tsx:18`) with a pure
  `selectVisibleToasts(toasts, VISIBLE_CAP)`. It takes Critical toasts first, newest first, and fills
  the remaining slots with the rest, newest first. The rest go behind the existing "+N more" count.
  That is R-N4's preemption.
- It is **deterministic**. The selection reads the whole stack, so the order in which a batch's items
  were pushed does not change what is visible. R-N6 gives one ordered batch, and the selection makes
  the result independent of arrival order. The test runs one batch in two push orders and expects the
  same visible set.
- Duration stays `DEFAULT_DURATION_MS` (`toastStack.ts:29`). A per-severity duration is future work,
  and the ideal flags it (finding H3).

### 5. The rail's state mapping (the move itself is `world-notify-source`'s)

When the rail moves (`world-notify-source` §4), its five item states (`spec-world-notify.md` §3) map
onto the feed like this. This module provides the selector that does it,
`railItemsFrom(feed, policy, ctx, channels)`:

| Rail state | From |
|---|---|
| `unread` / `opened` | Server `unread` / `read` |
| `dismissed` (with its undo) | Server `dismissed`; undo writes `read` (`notify-store` §2) |
| `minimized` | The per-category local setting, unchanged |
| `blocking` | `world-turn`'s declared list, which ships empty (`spec-world-notify.md` §5), so no v1 source sets it |

Items whose resolved channel is `off` are excluded here.

### 6. Mount policies (replacing "dismiss-only")

```ts
// shell/notify/rail/mountPolicies.ts
export type RailMountPolicy<Ctx> = {
  id: string;
  /** The GG-50 bound, stated as the filter itself. Registered in ui/volumeMatrix.test.ts. */
  includes(item: FeedItem, ctx: Ctx): boolean;
};

/** world: the End Turn flush, as a filter — only the most recently resolved turn of this world.
 *  Survives a reload (a flush on a transient array did not), and needs no commit wiring. */
export const worldLatestTurn: RailMountPolicy<{ worldId: string; lastResolvedTurn: number }> = {
  id: "world",
  includes: (i, c) => i.worldId === c.worldId && i.worldTurn === c.lastResolvedTurn,
};
```

- `lastResolvedTurn` is `dto.currentTurn - 1`, the value the playback panel already uses
  (`WorldStage.tsx:543`). It moves **only** on an advancing commit, so spec-world-notify's rule "fires
  on `advanced`, not on the button" (§2) holds by construction. The ported test asserts that a
  non-advancing commit leaves the rail alone.
- **v1 registers only `world`.** Every stage gets toasts (app-level). History for every stage is in
  the centre (`notify-centre`). A rail on another stage needs its own policy **and** its own
  `volumeMatrix` row first (ideal finding C1). Without both, the stage does not mount the rail.
- **Actions.** A translator returns an optional `target` (`notify-format` §1). The active mount
  registers a `TargetActionResolver` (the world stage maps `sector` and `legion` to its existing
  select/centre handlers). A toast or rail item gets a button only when a resolver is registered for
  its target kind. This keeps `spec-world-notify.md` §7's "act on one important event = 1 click".

### 7. GG-50

This module mounts no collection surface of its own. The world rail's reason text is updated in
`world-notify-source`, when `worldLatestTurn` actually feeds it. The centre's row is `notify-centre`'s.

## Commands

```powershell
cd web\fusion-rpg-web
npm test -- shell/notify lib/bus/notifications shell/Toasts
npm run build
npm run check:bundle
.\scripts\verify-change.ps1 -Paths <every changed file> -Session <session-id>
```

## Project structure

```
gk-web/web/fusion-rpg-web/src/lib/bus/notifications.ts          → hub subscription, catch-up pager, state mutation
gk-web/web/fusion-rpg-web/src/shell/notify/NotificationWire.tsx → app-level wiring; renders nothing
gk-web/web/fusion-rpg-web/src/shell/notify/feed/feedStore.ts
gk-web/web/fusion-rpg-web/src/shell/notify/feed/feedReducer.ts  (+ .test.ts)
gk-web/web/fusion-rpg-web/src/shell/notify/feed/toastRouting.ts (+ .test.ts)
gk-web/web/fusion-rpg-web/src/shell/toastSelection.ts           (+ .test.ts)  → selectVisibleToasts
gk-web/web/fusion-rpg-web/src/shell/toastStack.ts               → ToastEntry.severity? (additive)
gk-web/web/fusion-rpg-web/src/shell/Toasts.tsx                  → uses selectVisibleToasts
gk-web/web/fusion-rpg-web/src/shell/notify/channelSettings.ts  (+ .test.ts)  → open-id successor (§3)
gk-web/web/fusion-rpg-web/src/shell/notify/rail/mountPolicies.ts (+ .test.ts) → RailMountPolicy + worldLatestTurn
gk-web/web/fusion-rpg-web/src/shell/notify/rail/railItems.ts    (+ .test.ts)  → railItemsFrom (§5)
gk-web/web/fusion-rpg-web/src/shell/notify/targetActions.ts     → TargetActionResolver registry (§6)
gk-web/web/fusion-rpg-web/src/app/App.tsx                       → <NotificationWire />
```

## Code style

```ts
// feedReducer.ts — pure; the whole dedup story is one keyed merge.
export function applyItems(s: FeedState, items: readonly NotificationItem[], playerId: number): FeedState {
  if (playerId !== s.playerId) return s; // F7: another save's batch never lands here
  const byKey = { ...s.byKey };
  let maxRev = s.maxRev;
  for (const it of items) {
    const held = byKey[it.dedupKey];
    if (!held || it.rev > held.rev) byKey[it.dedupKey] = { ...it }; // the higher rev wins; order-free
    if (it.rev > maxRev) maxRev = it.rev;
  }
  return { ...s, byKey, maxRev };
}
```

## Testing strategy

Vitest, colocated, with fake hub and fake fetch. Queries use role and accessible name, never class
(the `spec-world-notify.md` Testing convention).

1. **Triggers F1–F7 and F4b**, one test each. F3 asserts that the old save's items are gone before
   the new catch-up lands.
2. **Order independence.** Push-then-GET and GET-then-push each end with one item. A live item toasts
   once. A catch-up-only item never toasts, and neither does an item in a `catchUp` batch (F4b). A page
   that was fetched before a dismiss and lands after its F5 leaves the item dismissed. A reconnect
   after another session dismissed an item shows it dismissed.
3. **Selection.** Three routine toasts then one Critical: the Critical is visible and one routine drops
   behind the count. The same set pushed in reverse order gives the same visible set.
4. **Channel.** A category the player set to `off` never reaches the toast stack or the rail, Critical
   included. Settings saved under the old storage key are read after the move.
5. **Mount policy.** Items from turns `R-1` and `R` exist, and `worldLatestTurn` selects only `R`. A
   non-advancing commit (same `currentTurn`) leaves the selection unchanged. A feed restored from
   catch-up selects the same items. These are the ported forms of `spec-world-notify.md`'s flush tests
   1–2.
6. **State mapping.** `railItemsFrom` maps each server state as in §5, and excludes `off` categories.
7. **Error state.** A failed catch-up renders the designed failed state with a retry.

## Boundaries

- **Always:** reach the server only through `lib/bus`; dedup on `dedupKey` and keep the higher `rev`;
  toast only items first seen in a `live` batch;
  declare a mount policy and a `volumeMatrix` row before mounting the rail anywhere new.
- **Ask first:** mounting the rail on a stage other than world (a GG-50 row and a flush boundary are
  owed); a per-severity toast duration (H3).
- **Never:** a client-side local push into the feed (the server is the one source); a rail with no
  declared bound ("dismiss-only"); a notification opening a band-3 layer by itself (GG-53 / D6,
  `spec-world-notify.md` §5); an engine token or raw id on screen.

## Success criteria

1. The feed, the toast selection, `channelSettings`, `worldLatestTurn` and `railItemsFrom` exist
   with tests. No world-stage file changes in this module. The relocation and the `WorldStage.tsx`
   swap are `world-notify-source`'s, behind G0.
2. Every stage receives notification toasts, with Critical first at the cap.
3. Tests 1–7 green; `npm run build` and `check:bundle` green.

## Seedsmith / generator

None. Web state and routing. The copy comes from `notify-format` translators, which are authored.

## Open questions

None. Catch-up never toasting, the player setting beating Critical, and the rail being mounted on the
world stage only are decisions recorded in the map (§Open questions), each with its reason.
