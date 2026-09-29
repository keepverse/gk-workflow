# Notify-centre — idea-UI pass

**Status: retroactive idea-UI pass (NS6.6, notification-ssot wave 6).** A full spec already exists —
[spec-notify-centre.md](notification-ssot/spec-notify-centre.md) — and is further along than a
typical idea-phase target. This doc is the `idea-ui-phase.md`-shaped deliverable the authoring
procedure (`gui-lego-authoring.md` step 0) asks for before the recipe (NS6.8): the bug/shape-to-
module map naming which GUI Lego pieces the "Notices" surface reuses, and which do not exist yet.
R14 ([spec-rulings-2026-09-18.md](notification-ssot/spec-rulings-2026-09-18.md)) already ruled the
home — a "Notices" tab in Chronicle — and that ruling is **not reopened here**.

---

## 1. Which loop this extends

**No named loop.** Checked directly: neither `docs/guide/the-loops.md` nor `docs/guide/the-game.md`
mentions "Chronicle," "notification," "history," "review," or "dossier" anywhere. `the-loops.md` is
organized as spine loops (level-up/power, summon/fusion, …) and places (Delve, Quests, …); none of
them names a history/review loop Chronicle serves. This is a real, named gap in the source docs, not
an oversight in this pass — `spec-notify-centre.md` itself never claims a loop either. The nearest
honest framing: Chronicle is where a player closes the loop the toast/rail already ran (Place-
agnostic, cross-cutting "did I miss anything" check), the same role information-architecture.md
already gives it for run history and the XP ledger.

## 2. Load-bearing principles restated inline

1. **Every RPG feature lives in the RPG layer.** Not in tension here — the centre only reads/writes
   through `lib/bus/notifications.ts` and `notify-client`'s feed, never a PvZ field.
2. **A game is a stage with layers, not a document with pages (GG-1).** "One stage, many layers":
   *"At any moment the player is on exactly one stage… Every other surface… is a layer drawn over
   that stage, openable from anywhere, and closing it returns the player to exactly the stage state
   they left"* (`game-gui-principles.md:38-43`). The centre is a **tab inside an existing layer**
   (Chronicle), not a new layer — even more conservative than GG-1 requires.
3. **Player menus are recipe + pure fold + closed bus — never a god TSX** (`decisions.md`, GUI Lego
   row, 2026-09-09: *"Player menus… are composed as recipe + pure ViewModel fold + closed surface
   bus — never a god TSX. Pieces render payloads only (no fetch/SignalR)."*). Already how
   `foldNoticesVm.ts`/`noticesBus.ts`/`noticesUiStore.ts` (NS6.9) are built.
4. **Theme packs own paint.** No hard-coded severity/channel colors in a notice row piece.
5. **Buy before build for presentation.** Not in tension — no new chart/icon library is needed here.
6. **Each player bug is one or more modules.** There is no bug list for this pass (spec-driven, not
   bug-driven); §5 below still decomposes by module, per the procedure's own §3 requirement.
7. **No engine vocabulary on the player surface.** A notice row's text is `renderNotification`'s
   authored output (`notify-format`); the recipe/fold never touch a `messageKey` or channel id.

## 3. What this is (player language)

A "Notices" tab in Chronicle where a player finds a notification again after its toast expired and
the world rail flushed at End Turn — "did loam run short, did that legion make it, is my last stash
of loot from that dead legion still at risk." One category browsed at a time, newest first, capped
at `retainPerCategory` (the same store bound the rail and the toast already respect). It is also the
**only** place a player can turn a silenced category back on, since an `off` category never toasts
or rails.

## 4. What already exists

| Piece / module | Bucket | Evidence |
|---|---|---|
| `foldNoticesVm(input) → NoticesVm` | **Built** | `gk-web/web/fusion-rpg-web/src/features/notices/foldNoticesVm.ts` — pure, merges live feed + history, lists every category incl. zero-row/`off`, newest-first rows, text via `renderNotification`. 9 tests green (NS6.9) |
| `noticesBus.ts` (7-event closed catalog) + `wireNoticesBus` | **Built** | `gk-web/web/fusion-rpg-web/src/features/notices/noticesBus.ts` — framework-free subscribe-to-effect wiring, 3 tests green (NS6.9) |
| `noticesUiStore.ts` (`selectedCategory`) | **Built** | `gk-web/web/fusion-rpg-web/src/features/notices/noticesUiStore.ts` — module-level zustand, survives a `PanelShell` Dialog unmount (GG-51) |
| `useNotificationHistory(playerId, category)` | **Built** | `gk-web/web/fusion-rpg-web/src/lib/bus/notifications.ts` — `useInfiniteQuery` over `GET …/history`, `fetchNextPage()` is "load older" (NS6.10) |
| `tool-search` piece (category filter) | **Wiring gap** | Real chrome piece exists, kind **chrome**, role "Search" (`docs/design/gui-lego/README.md:49`), already reused by Derived and the Creatures list (`README.md:192`) — not yet bound into a notices recipe |
| `chip` piece (severity/state) | **Wiring gap** | Real Chip-kind piece, role "Rail option" (`README.md:53`), reused via `element-badge` + paint SSOT elsewhere (`README.md:187`) — not yet bound here; a notice's severity/state chip is a new **binding**, not a new piece |
| ERM **Row** rung | **Wiring gap, not a real gap** | A Row-kind piece already ships: `channel-row`, kind **Row**, role "Derived channel" (`README.md:63`). "A notice row is a Row, not a new density" (spec §2 step 2) is correct — the rung exists; the *notice*-shaped Row binding does not |
| The recipe (`docs/design/gui-lego/recipes/notices` .json, to be authored) | **Real gap** | Not authored yet (NS6.8) |
| The React surface (a `NoticesSurface` component, to be authored) + Chronicle `TABS` entry | **Real gap** | Not built yet (NS6.11, blocked on NS6.8's owner review) |
| `ChannelControl` reuse ("the same `ChannelControl` as the rail," spec §Objective) | **Cross-program dependency, named here** | `ChannelControl.tsx` exists today at `stages/world/notify/ChannelControl.tsx` (world-notify wave 1). Its move to `shell/notify/rail/ChannelControl.tsx` is `world-notify-source` NS5.9, **blocked on ask A1** (unanswered as of this pass). Until that move lands, NS6.11 either imports the pre-move path (naming the coupling explicitly) or waits — this pass does not resolve it, only names it so it is not rediscovered mid-React |
| `menu-refactor-queue.md` "notices" row | **Real gap** | Confirmed absent: the priority table (`menu-refactor-queue.md:13-23`) has no "notices" row; Chronicle is only named inside P4's own free-text Notes column (`:22`) as still-queued. NS6.7 adds the row |
| A named loop for Chronicle/Notices | **Real gap in the source docs**, not this module's to close | See §1 |

## 5. Owner bugs → module breakdown

No owner bug list drives this pass (spec-driven). The module set, restated from
`spec-notify-centre.md` §2 in this procedure's own vocabulary:

| # | Requirement (spec) | Module(s) | Bucket |
|---|---|---|---|
| 1 | Browse one category, newest first, capped at `retainPerCategory` | `foldNoticesVm` (rows), `useNotificationHistory` | Built |
| 2 | Mark read / dismiss / undo agree with the rail and a second session | `noticesBus` events → `useSetNotificationState` (`notify-client`), server state | Built (bus); the effect wiring itself is NS6.11 |
| 3 | Open a row's target when a resolver is registered | `resolveTargetAction` (`shell/notify/targetActions.ts`, wave 4) inside `foldNoticesVm`'s row mapping | Built |
| 4 | Change a category's channel from the row, using the rail's `ChannelControl` | `noticesBus`'s `notices.set-channel` event (built) + the real `ChannelControl` binding (blocked, see §4) | Built bus / blocked binding |
| 5 | List every registered category incl. zero-row/`off` | `foldNoticesVm.categories` | Built |
| 6 | Designed states: loading, empty, failed+retry, `off` | Piece-level (NS6.11) — none built yet | Real gap |
| 7 | Volume: `virtualize`, proven at 10/100/1000 | `ui/volumeMatrix.test.ts` row + e2e fixture (NS6.12) | Real gap, sequenced after NS6.11 |

**Shared reuse map:** `tool-search` (Derived, Creatures list, notices) — one category filter, not a
notices-only twin. `chip` (Derived's severity/state chips, notices' severity/state chip) — one Chip
kind bound twice, never a private mute chip. `channel-row`'s Row rung (Derived channel rows, notice
rows) — one density, two different data bindings, never a second Row-shaped kind.

## 6. Prior art (outside repo)

Path of Exile's "Recently seen" / message log and Diablo-likes' "combat log with a filter tab" both
solve the same shape: an ephemeral toast/notification stream backed by a persistent, filterable,
one-category-at-a-time browsable log — never require the player to keep every toast on screen to
"not miss it." The design choice this repo already made (`spec-notify-centre.md` §Objective, citing
the ideal's own "toasts can be dismissible only if there is another surface" prior-art line) matches
that genre convention directly: a centre exists specifically so the toast is allowed to expire.

## 7. The shape — chosen vs rejected

**Chosen:** a Chronicle tab (R14), GUI Lego recipe + fold + bus, reusing `tool-search`/`chip`/Row.

**Rejected, named so it is not re-litigated:**
- *"Give notices its own layer/key/rail entry."* Rejected by R14 itself — no rail entry, no key, no
  route (spec §1).
- *"One CSS pass over a hand-rolled notice list."* Rejected by the GUI Lego binding itself (§2) —
  a god TSX is exactly the failure mode `idea-ui-phase.md` exists to catch (Condition-glance
  incident, 2026-09-10).
- *"A brand-new Row density for a notice."* Rejected — `channel-row` already proves the Row rung;
  amending ERM for a new rung the shape does not need would be inventing a parallel density beside
  one that already exists.
- *"Fork `ChannelControl` for the centre rather than wait on the rail's own move."* Rejected — the
  spec is explicit that the centre reuses "the same `ChannelControl` as the rail," and a fork would
  be exactly the kind of private-twin GG/GUI-Lego violation this procedure exists to catch. Named as
  a real cross-program dependency (§4) instead of forked around.

## 8. Tunables

- `retainPerCategory` (`gk-core/data/tuning/notification.v1.json`) — already a tunable (notify-store, wave
  1); the centre reads it indirectly through the store's own cap, adds no new tunable.
- No new balance number is introduced by this pass. The volume row's `virtualize` threshold (NS6.12)
  is a structural rendering strategy, not a tunable — GG-50 asks for a *declared strategy*, not a
  configurable render-all ceiling.

## 9. What this deliberately does not decide

- **The recipe's exact slot tree and piece bindings** — that is NS6.8's job, constrained to reuse
  from §4/§5 above; any piece or density beyond what is named here is an ERM amendment, asked for
  explicitly, not invented mid-recipe.
- **How/when the `ChannelControl` cross-dependency resolves** — owned by `world-notify-source`'s own
  ask A1, not this pass.
- **The exact copy** (tab label, empty-state string) — authored at HTML-draft time (`gui-lego-
  authoring.md` step 6), extracted via `npm run extract` at React time (NS6.11).

## 10. Open questions

None owner-facing. R14 already ruled the home. The GUI Lego owner gate (NS6.8 step 7) is a build-
time review, not a question posed here.

## 11. The real question

Not feasibility — every module either already exists (fold/bus/store/history hook, NS6.9/NS6.10) or
has a named, narrow real gap (recipe, React mount, volume row). The real question is **sequencing**:
NS6.8's recipe can be built now, but its **owner review** (the one hard gate before React) is a
human step this pass cannot resolve, and NS6.11's actual mount additionally inherits
`world-notify-source`'s own ask-A1 timeline for `ChannelControl`'s move. Both are named, not hidden,
so neither is rediscovered mid-build.
