# Spec: notify-centre

**Status: Draft — Phase 1 (Specify); the piece review is DELEGATED, not personal.** The owner declined
to be the reviewer and named the **gui-lego program** as the resolver (owners ruling 2026-09-21,
`tasks/notification-ssot-todo.md` NS6.8), so the gate on this module is that program accepting its queue
row (P4 · Notices) and dating it — while that row is open, NS6.11/NS6.12 stay gated. Module `notify-centre` of the
[notification-ssot map](../notification-ssot-map.md), wave 6. Depends on `notify-client` and
`notify-service`. **Home ruled (R14, [spec-rulings-2026-09-18.md](../spec-rulings-2026-09-18.md)): a
"Notices" tab in the Chronicle layer.** No rail entry, no key, no change to the player layers.

**Strengthen pass 2026-09-18:** R14 applied (the open question and the "its own layer" alternative
are removed); the selected category moved out of component state, because the layer unmounts on close
(map §Strengthen pass S6, S7).

---

## Objective

R-N2: *"we still have notification center but make it 100 for each kind of notification."* It is the
surface where a player finds a notification again after the toast expired and the rail flushed. That
is what makes a dismissible toast acceptable at all (the ideal's §Prior art: "toasts can be
dismissible only if there is another surface… where the customer can find this content again
later").

- Browse **one category at a time**. The newest row is first, and each category holds at most
  `retainPerCategory` rows (`notify-store`).
- Mark read, dismiss and undo, all through `notify-client`'s state mutation, so the centre, the rail
  and any other session agree.
- Open a row's target through the active stage's resolver, when one is registered
  (`notify-client` §6). If none is, the row has no action button at all. A hidden action is not a
  disabled control, so GG-55 ("never disable a control without saying why") does not come into it.
- **Change the category's channel from the row**, using the same `ChannelControl` as the rail
  (`spec-world-notify.md` §6). The centre is also the only place a player can find a category they
  set to **off**, since off categories never toast or rail (`notify-client` test 4). It therefore
  lists every registered category, including those with zero rows, each with its channel, as §6 of
  that spec requires for settings.

## Design

### 1. Home: a "Notices" tab in Chronicle (R14)

Chronicle is the reading layer for history (`docs/design/information-architecture.md` §3, Chronicle
row: key `H`), and its tabs are one small array (`gk-web/web/fusion-rpg-web/src/layers/chronicle/ChronicleLayer.tsx:7-11`).
Adding `{ id: "notices", label: "Notices", Component: NoticesSurface }` adds no rail entry, no key and
no route (GG-1, GG-7, GG-9). The surface is still a recipe and not a Chronicle-specific TSX, because
GUI Lego requires it (§2), not because the home is undecided.

**What the home implies, stated so it is not rediscovered:**

- **Where it can be opened.** Wherever the Chronicle layer is hosted. Today that is the Sanctum stage
  (`gk-web/web/fusion-rpg-web/src/stages/sanctum/SanctumStage.tsx:332`). The centre adds no host of its own.
  Toasts reach every stage regardless (`notify-client`), and the world rail shows the latest turn.
- **When it can be opened.** Chronicle unlocks on "first run completed" (information-architecture §7,
  unlock ladder). Nothing is lost before that: the store keeps every row, and the tab shows them once
  Chronicle unlocks. A locked layer says what unlocks it (GG-17), which is Chronicle's existing
  behaviour.

### 2. GUI Lego (binding for a band-2 body — `gui-lego-authoring.md` §1–§3)

A surface = **recipe + fold + bus**, never a god TSX. Authoring follows the procedure:

1. `/idea-ui` over this spec → a bug/shape-to-module map (authoring step 0).
2. A queue row in `architecture/gui-lego/menu-refactor-queue.md` (step 1). That file belongs to the
   gui-lego program, so the row is an ask at build time. Its first reusable pieces are `tool-search`
   (category filter), `chip` (severity, state) and the ERM **Row** rung. A notice row is a Row, not a
   new density.
3. Recipe `docs/design/gui-lego/recipes/notices.json` (step 3), beside the existing recipes such as
   `hall-console.json`.
4. **Fold** `foldNoticesVm(feed, page, catalog, channels) → NoticesVm`, a pure function
   (spec-derived-surface-vm pattern). Pieces never fetch (`gui-lego-ideal.md` principle 6). History
   pages come through `lib/bus/notifications.ts` (`useNotificationHistory(category)`), which calls
   `GET /api/notifications/{playerId}/history?category=&before=` (`notify-service` §4).
5. **Closed bus catalog** for this surface:

   | Event | Payload | Effect |
   |---|---|---|
   | `notices.select-category` | `{ category }` | Writes `selectedCategory` in `features/notices/noticesUiStore.ts` (a module-level zustand slice, like `toastStack`). Not component state: `PanelShell` is a Radix `Dialog` (`gk-web/web/fusion-rpg-web/src/shell/PanelShell.tsx:2`), which unmounts its content on close, so component state would reset. GG-51 needs it to survive close and reopen |
   | `notices.mark-read` | `{ seqs }` | `useSetNotificationState("read")` |
   | `notices.dismiss` | `{ seqs }` | `useSetNotificationState("dismissed")` |
   | `notices.undo-dismiss` | `{ seq }` | `useSetNotificationState("read")` |
   | `notices.load-older` | `{ beforeSeq }` | Next history page |
   | `notices.open-target` | `{ target }` | The active mount's `TargetActionResolver` |
   | `notices.set-channel` | `{ category, channel }` | `setChannel` (`notify-client` §3) |

6. Theme packs own paint. There are no hard-coded tones in pieces.
7. **Piece review gate** — the GUI Lego authoring step 7 the owner delegated to the gui-lego program
   (2026-09-21) — on pieces, payloads and the assembled look **before** React (step 8). A personal owner
   review is not what is outstanding here; that program's acceptance of the queue row is.

### 3. Designed states (GG-17)

Loading, empty ("Nothing in this category yet"), failed with a retry (`notify-client` feed
`status = "error"` or a failed history page), and a category the player routed **off**. That last one
shows its rows and its channel, so it can be turned back on (`spec-world-notify.md` §6: "the only place
to find a category you have already silenced").

### 4. Volume (GG-50)

A new `volumeMatrix` row, owned by this module:

| Surface | Strategy | Reason |
|---|---|---|
| Notification centre (per-category list) | `virtualize` | One category at a time, at most `retainPerCategory` rows. That bound is a **tunable**, so a balance pass can raise it past a render-all threshold without touching code. Windowed from day one, as the Creatures roster is |

The matrix's `toHaveLength` assertion is a count of **declared surfaces**, a closed registry that the
code owns, so adding this row is the reviewed change that assertion exists to force. It is not a
population pin.

## Commands

```powershell
cd web\fusion-rpg-web
npm test -- layers/chronicle features/gui-lego ui/volumeMatrix shell/notify
npm run build
npm run extract          # new authored copy (tab label, empty state)
.\scripts\verify-change.ps1 -Paths <every changed file> -Session <session-id>
```

## Project structure

```
docs/design/gui-lego/recipes/notices.json                  → recipe (after /idea-ui; owner gate)
gk-web/web/fusion-rpg-web/src/features/notices/foldNoticesVm.ts   (+ .test.ts)
gk-web/web/fusion-rpg-web/src/features/notices/noticesBus.ts      → the closed catalog above
gk-web/web/fusion-rpg-web/src/features/notices/noticesUiStore.ts  → selectedCategory (GG-51), outside the unmounting layer
web/fusion-rpg-web/src/features/notices/NoticesSurface.tsx → bindSurface(recipe, vm, themes); no fetch
gk-web/web/fusion-rpg-web/src/lib/bus/notifications.ts            → useNotificationHistory(category)
gk-web/web/fusion-rpg-web/src/layers/chronicle/ChronicleLayer.tsx → one TABS entry (the seam)
gk-web/web/fusion-rpg-web/src/ui/volumeMatrix.test.ts             → the row above
```

## Code style

```ts
// foldNoticesVm.ts — pure; the surface renders what this returns and nothing else.
export function foldNoticesVm(input: NoticesInput): NoticesVm {
  const category = input.selected ?? input.catalog.categories[0]?.id ?? null;
  return {
    categories: input.catalog.categories.map((c) => ({
      id: c.id, name: c.displayName, channel: input.channels[c.id], unread: countUnread(input.feed, c.id),
    })),
    rows: category ? rowsFor(input.feed, input.history, category).map(toNoticeRow) : [],
    selected: category,
  };
}
```

## Testing strategy

1. **Fold (pure).** Every registered category appears, including those with zero rows and those set to
   off. Rows are newest first. Every row's text comes from `renderNotification`, and no id appears
   in it.
2. **Bus.** Each catalog event calls exactly its effect. There is no other event.
3. **States.** Loading, empty, failed with a retry, and off are each rendered and each queried by role.
4. **GG-51.** The selected category survives closing and reopening the layer, tested by unmounting
   and remounting `NoticesSurface` (the unmount a closed Dialog performs).
5. **Volume.** Using the e2e volume-fixture pattern (`e2e/volume-fixtures.spec.ts`, as the Creatures
   row cites), a category at 10, 100 and 1000 rows renders a windowed node count, not all of it.
6. **Agreement.** A dismiss in the centre shows as dismissed on the world rail, and a dismiss on the
   rail shows as dismissed in the centre (the one server state, `notify-client` F5/F6).

## Boundaries

- **Always:** recipe + fold + bus; history through `lib/bus`; every registered category listed.
- **Ask first:** the queue row (the gui-lego program); any new piece or density (amend ERM,
  `gui-lego-authoring.md` §2 step 2). The home is ruled (R14) and is not reopened.
- **Never:** a fetch or a SignalR read inside a piece; a second shell (`PanelShell`/`ActorPanel`
  only); React before the owner gate; a render-all list for a category; a new layer, key or rail
  entry for the centre (R14).

## Success criteria

1. The centre lists every category with its channel, and one category's history, newest first.
2. Read, dismiss, undo and channel changes agree with the rail and with a second session.
3. The volume row is `virtualize` and proven at 10, 100 and 1000.
4. The owner gate passed before any React landed.

## Seedsmith / generator

None. A GUI Lego recipe and fold. The chrome copy is authored (lingui `npm run extract`), and the row
text comes from the domain translators.

## Open questions

None. R14 ruled the home. The GUI Lego owner gate (§2 step 7) is a build-time review, not an open
question.
