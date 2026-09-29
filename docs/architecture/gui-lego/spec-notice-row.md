# Piece: `notice-row`

**Program:** `gui-lego` · **Kind:** entity · **ERM rung:** Row  
**Draft:** [../../design/gui-lego/pieces/notice-row.html](../../design/gui-lego/pieces/notice-row.html)  
**Shared types:** [payload-types.md](payload-types.md) · **Composition:** [spec-composition.md](spec-composition.md)  
**Proposed by:** `notification-ssot` NS6.8 (the `notices` recipe) — this piece is **new**, and its rung is the existing Row rung (`channel-row` is the precedent that the rung is real). It is listed for the GUI Lego step-7 piece review; until that review accepts it, the surface it belongs to stays unbuilt (NS6.11).

## Role

One notification, as the Notices centre renders it: severity and state visible as text, title and body
already translated, and only the actions the row's own state and target allow.

## Structure

| | |
|---|---|
| Landmark / root | `div.row[role=listitem]` (`data-testid="notice-row"`, `data-state`) |
| Slots | _none_ (actions are buttons inside the row, never a nested interactive row) |
| CSS `>` parents | `scroll-region` content list |

**Ban:** illicit wrappers between a `>` parent and its declared child.

## Fields

| Field | Type | Required | Notes |
|---|---|---|---|
| `piece` | `"notice-row"` | yes | Registry id |
| `instanceId` | `string` | yes | Stable mount / testid |
| `dedupKey` | `string` | yes | R-N5 identity — the same row across push, GET and every state change |
| `category` | `NotifyCategoryId` | yes | Catalogue id; the channel control above the list names it |
| `severity` | `NotifySeverity` | yes | `routine|important|critical`; text chip, never colour alone |
| `state` | `NoticeRowState` | yes | `unread|read|dismissed` — see below |
| `title` | `string` | yes | `renderNotification`'s title (catalogue `displayName`) |
| `body` | `string` | yes | `renderNotification`'s body; the row never sees an engine token |
| `target` | `NotifyTarget` | no | When present **and** a resolver is registered for `refKind`, the row gains a target action |
| `actions` | `NoticeRowAction[]` | yes | Derived from `state` + `target`; never a dead button |

`state` ∈ `unread|read|dismissed` — do not invent a fourth. The rail's own `minimized` and `blocking`
are rail chrome, not centre states: a mount that shows a rail maps them onto its own presentation and
does not extend this enum.

## Theme slots

- Pack kind(s): none required — the severity/state chips use the shared `chip` tokens, and the unread
  marker is a glyph **and** weight, so the piece is legible with any pack or none.
- Reads: `--accent`, `--border`, `--muted`, `--panel`
- Vfx keys: none

## Data flow

- **Bind:** `vm.rows` (the centre's fold output for the selected category)
- **Bus out:** `notices.set-state` (`{ seq, state }`) — the row never mutates the feed, and a dismissed
  row's `reopen` is the same call with `read`

## Focus (GG-19)

yes — each action is a real `<button>` with a visible focus ring; the row itself is not focusable (no
nested interactive).

## Motion (GG-31/32)

none — a state change repaints instantly; nothing here animates, so reduced-motion is satisfied by
construction.

## Empty / error

Empty and failed states belong to the surface (`phase-empty` / `phase-error` with `notices-retry`). A row
whose target cannot be resolved renders **without** the target action rather than with a dead one; a
magnitude never appears in a row (the translator resolves it into `body`).

## Sample payloads

```json
{
  "piece": "notice-row",
  "instanceId": "notice:world:w1:t4:e0",
  "dedupKey": "world:w1:t4:e0",
  "category": "loam.shortfall",
  "severity": "important",
  "state": "unread",
  "title": "Shortfall",
  "body": "…the translator's sentence…",
  "target": { "refKind": "sector", "id": "ember-hollow" },
  "actions": ["read", "dismiss", "target"]
}
```

```json
{
  "piece": "notice-row",
  "instanceId": "notice:cache:c1:decay:7",
  "dedupKey": "cache:c1:decay:7",
  "category": "cache.decayed",
  "severity": "routine",
  "state": "dismissed",
  "title": "Cache decayed",
  "body": "…the translator's sentence…",
  "actions": ["reopen"]
}
```
