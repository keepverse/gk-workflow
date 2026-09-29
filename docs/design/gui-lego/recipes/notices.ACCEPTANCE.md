# Notices drafts — resolver-accept checkpoint

**Task:** `NS6.8` (`tasks/notification-ssot-todo.md`). **Spec:** `docs/architecture/notification-ssot/spec-notify-centre.md`.
**Brief:** `docs/architecture/notify-centre-ideal.md` (the `/idea-ui` pass, NS6.6). **Queue row:** `P4 · Notices`
(`docs/architecture/gui-lego/menu-refactor-queue.md`).
**Status:** `pending-resolver-acceptance` — the owner declined to be the reviewer and named the **gui-lego
program** as the resolver (2026-09-21). This lane may not date that acceptance; it may only hand over what
the review is *of*, which is what this checkpoint is.
**Date:** 2026-09-21 · **Lane:** `ns-1` · **Branch:** `cmdc/ns-1`

## Drafts under review

| # | Artifact | Path | Landmarks |
|---|---|---|---|
| 1 | `notices` recipe JSON (slot tree) | `docs/design/gui-lego/recipes/notices.json` | `surfaceId: notices`, `host: chronicle-tab`, slots `tools/sidebar/main/channelControl` + `lifecycleOverlays` |
| 2 | `notices` assembled draft (structure + all designed states) | `docs/design/gui-lego/surfaces/notices.html` | `notices`, `notices-category-search`, `notices-split`, `notices-category-list`, `notices-category-chip`, `notices-category-name/-unread/-off`, `notices-channel-control`, `notices-channel-label`, `notices-rows-scroll`, `notice-row` ×3 (unread / read / dismissed), `notice-row-title/-body/-severity/-state/-unread-dot/-open/-dismiss/-reopen/-target`, `notices-load-older`, `notices-cap-note`, `notices-phase-loading/-empty/-error`, `notices-retry`, `notices-category-off` |

| 3 | `notice-row` piece draft (the one NEW piece) | `docs/design/gui-lego/pieces/notice-row.html` | `notice-row` x3 (unread / read / dismissed), `notice-row-title`, `-body`, `-severity`, `-state`, `-unread-dot`, `-open`, `-dismiss`, `-reopen`, `-target`, `-dismissed-label` |
| 4 | `notice-row` piece contract | `docs/architecture/gui-lego/spec-notice-row.md` | ERM rung Row; closed `state` vocabulary; fields; bus out |

## Entry criteria for a queue row (`menu-refactor-queue.md` §Entry criteria)

| # | Criterion | State |
|---|---|---|
| 1 | DESIGN-GATE **Player menus** docs read in-session | met 2026-09-21 — read this session: `gui-lego-authoring.md` (the step 0-8 procedure and the three registries), `docs/design/gui-lego/README.md` (the piece index + rung list), `gui-lego-ideal.md`, `gui-lego-map.md`, `idea-ui-phase.md` |
| 2 | Recipe JSON drafted (or reuse existing pieces only) | met — `notices.json`; every piece it names resolves in the index (`surface-shell`, `tool-search`, `source-list`, `chip`, `scroll-region`, `phase-loading`/`-empty`/`-error`, `channel-control`), and the one NEW piece, `notice-row`, now has a draft and a spec at the existing Row rung |
| 3 | Fold / bus catalog named | met — `foldNoticesVm`, `noticesBus`, `noticesUiStore` (NS6.9/NS6.10), green |
| 4 | HTML piece or assembled surface for owner gate | met — `surfaces/notices.html` (assembled) and `pieces/notice-row.html` (the new piece) |
| 5 | React only after accept | **pending** — the resolver's dated acceptance; `NS6.11`/`NS6.12` stay gated until then |

## Piece boundaries — what step 7 accepts or amends

- **Consumed by name, already existing** (per `notify-centre-ideal.md`'s piece map): `surface-shell`,
  `tool-search`, `source-list`, `chip`, `scroll-region`, `phase-loading` / `phase-empty` / `phase-error`,
  `channel-control`.
- **One new piece:** `notice-row`, at the **already-existing ERM Row rung** (`channel-row` is the precedent
  that the rung is real — this is not a new density). Its proposed field set is exactly what the draft
  shows: severity chip, state chip, title, body, and the actions a row's own state allows (Read, Dismiss,
  Reopen, plus a target action when a resolver is registered for the row's target kind).
- No new layer, key, route or rail entry: the surface is **one `TABS` entry** in the Chronicle layer (R14).

## What the resolver is asked to accept

1. The two artifacts above — structure, landmarks and the five rendered situations.
2. `notice-row`'s field set at the Row rung (or an amendment naming a different rung).
3. The four designed states — loading, empty, failed-with-retry, and the category-routed-`off` state — as
   the binding targets for `NS6.11`.

## Gate effect

`NS6.11` (the React surface) and `NS6.12` (its volume row) stay gated until this is accepted **and dated**
in the queue row or in the recipe's meta. Nothing in this program ships React before that date; the recipe,
fold, bus and store above are the only artifacts until then.

## Verification behind this checkpoint (run 2026-09-21, head `287a3256`)

| Check | Command | Numbers printed |
|---|---|---|
| the GUI Lego suites (recipe schema and piece contracts) | `cd gk-web/web/fusion-rpg-web; npx vitest run src/features/gui-lego` | `Test Files 13 passed (13)`, `Tests 121 passed (121)` |
| this program's fold/bus/store (NS6.9, NS6.10) and the rail it shares vocabulary with | `cd gk-web/web/fusion-rpg-web; npx vitest run src/features/notices src/shell/notify` | `Test Files 18 passed (18)`, `Tests 102 passed (102)` |

`renderNotification` owns every sentence the finished surface shows; this draft authors none (its strings
are marked DRAFT or are display-catalog keys, GG-62).
