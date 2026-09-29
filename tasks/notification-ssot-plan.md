# Implementation plan: `notification-ssot` (prefix `NS`)

**Map:** [notification-ssot-map.md](../docs/architecture/notification-ssot-map.md) ·
**Specs:** [notification-ssot/](../docs/architecture/notification-ssot/) (`notify-vocabulary`,
`player-routing`, `notify-store`, `notify-format`, `notify-service`, `notify-client`,
`world-notify-source`, `cache-notify-source`, `notify-centre`) ·
**Ideal:** [notification-ssot-ideal.md](../docs/architecture/notification-ssot-ideal.md) ·
**Tasks:** [notification-ssot-todo.md](notification-ssot-todo.md) ·
**Rulings:** [spec-rulings-2026-09-18.md](../docs/architecture/spec-rulings-2026-09-18.md) (R14, R17)
plus the map's R-N1–R-N6.

**Relationship to the parent.** Lane D of [summoner-convergence-plan.md](summoner-convergence-plan.md).
Independent of every other lane except two soft couplings: save identity (`SE` save-identity, R17) and
the verification registry schema (`SE0.7` → `TVB` registry-contract). Owns the parent §5 row
"notify catalog v1 → v2 → v3". Feeds parent checkpoint CC7 — updated to waves 1–6: everything landed except Gate G2 (blocked on a
missing real world-creation route) and the gated centre (see "Wave status" below).

## Overview

One path from "something happened to this save" to "the player was told", on any stage. A domain
source turns its own durable events into structured drafts (category, severity, dedup key, message key,
typed args — never text). One publisher validates them against an open category catalog, writes them
durably per save, and only then pushes one `NotificationBatch` to that save's SignalR group. The web
keeps one feed per save, dedups by key, routes each item to toast / rail / off by the player's setting,
and turns keys into words through per-domain translators built on shared formatting primitives. A
"Notices" tab in Chronicle holds the history, 100 rows per category (tunable). The first consumer is the
world turn (and it finally feeds the world rail, which today is a local `useState` nothing writes —
`WorldStage.tsx:142`); the second is the corpse-cache decay clock.

Nothing is built today (verified 2026-09-18: no `NotificationDtos.cs`, `PlayerPush.cs`,
`shell/notify/`, `notification*.json` tuning, and no `JoinPlayer`/`PlayerGroup` symbol in `src/`).

## Architecture decisions (from the map; not re-litigated)

- **Per-save routing first (R-N1).** Group `player:{id}` + `RpgHub.JoinPlayer` + `IPlayerPush`. No
  content push may merge before it. A routing group, not an auth boundary.
- **"Player" on the wire means the save (R17).** Wire names keep `player`; new columns are `save_id`;
  server params are `saveId` (`long` until `SaveId` exists — NS7.2 swaps mechanically). Nothing waits on
  `SE` save-identity.
- **Open category catalog, closed everything else (R-N2, R-N4).** Rows can never name a channel or
  severity; only the reviewed `promotions` block promotes. `critical` ships empty. Retention is a
  tunable tail (`retainPerCategory`), pruned per `(save, category)`.
- **Words on the web (R-N3).** Shared primitives and the translator contract land in wave 2, before any
  domain translator. The server sends keys and typed args only.
- **Stable dedup key from day one (R-N5)** — `UNIQUE(save_id, dedup_key)` plus a key ledger that
  outlives the prune; the client dedups on the same key; higher `rev` wins a merge.
- **One batch per save per turn (R-N6)**, labelled `live` or `catchUp`; catch-up never toasts.
- **Durable, then push.** Rows, prune and source cursor commit in one transaction; the push is
  fire-and-forget; the catch-up GET (by `rev`) is the correctness path.
- **One pump per clock.** v1 builds only the world-turn pump; it runs after `CommitWorldTurn` returns,
  never inside it, so no state hash moves.
- **Notices tab in Chronicle (R14)** — no rail entry, key or layer; authored through GUI Lego (recipe +
  fold + bus) after an `/idea-ui` pass and the owner piece review.
- No actor magnitude (ActorHub N/A), no Unity/injector surface, no generated content.

## Dependency graph (modules)

```
notify-vocabulary ──┬──► notify-store ──┐
                    ├──► notify-format ─┼───────────────┐
player-routing ─────┼───────────────────┤               │
                    └──────────────────►notify-service  │
                                            │           │
                                            ▼           ▼
                                        notify-client ◄─┘
                                            │
                  ┌─────────────────────────┼──────────────────────┐
                  ▼                         ▼                      ▼
          world-notify-source      cache-notify-source        notify-centre
          (catalog v2; A1/A2 landed) (catalog v3; A5)         (gated on the gui-lego row)
```

## Suggested order and parallel lanes (suggested, not enforced)

Only `deps:` lines and parent hard edges bind. **H7** applies to every catalog publish (NS5.6, NS6.4,
NS7.4): the Server load line and the web import move in the same commit as the publish. No other parent
hard edge (H1–H6) touches this program: it moves no golden, re-keys no `SE` table, and has no shared
tuning file other than its own.

| Lane | Tasks, in suggested order | Notes |
|---|---|---|
| D1 server | NS1.2 → NS1.3 → NS1.4 → NS1.5 · NS1.6 → NS1.7 → NS2.1 → NS2.2 → NS2.3 · NS2.4 → NS3.1 → NS3.2 → NS3.3 → NS3.4 · NS3.5 · NS3.6 → NS3.7 | NS1.6–NS1.7 (routing) parallel with NS1.2–NS1.5 (vocabulary) |
| D2 web | NS1.8 → NS2.5 → NS2.6 → NS2.7 → NS4.2 · NS4.3 → NS4.4 → NS4.1 → NS4.5 → NS4.6 | NS4.2/NS4.3 need only NS1.4; NS4.1 waits for NS3.6's REST shape |
| D3 asks | NS0.1–NS0.6 any time; NS6.6 (`/idea-ui`) during wave 4 | Asks answered early cost nothing and keep wave 5 from idling |
| World consumer | NS5.1, NS5.5 early (need only NS3.1 / NS1.3) → NS5.4 → NS5.6; A2 path NS5.2 → NS5.3 → NS5.12; A1 path NS5.7 → NS5.8 → NS5.9 → NS5.10 → NS5.11 → NS5.13 | A1/A2 were answered 2026-09-21 (both accepted); their named tasks landed |
| Wave 6 | cache: NS6.1 → NS6.2 → NS6.3 → NS6.4 → NS6.5; centre: NS6.7 → NS6.8 → NS6.9 · NS6.10 → NS6.11 → NS6.12 | cache and centre fully parallel |
| Follow-ups | NS7.1–NS7.4 when their trigger lands | Each is inert until then |

First task: **NS1.1** (map the notify path families in the verification registry) so every later
`verify-change.ps1` call selects focused tests instead of hitting an unmapped-path defect.

## Phases

| Wave | Modules | Tasks | Sizes | Parallel-safe |
|---|---|---|---|---|
| 0 | G0 asks A1–A6 | NS0.1–NS0.6 | 6 × XS | yes, with everything |
| 1 | `notify-vocabulary` ∥ `player-routing` | NS1.1–NS1.8 | XS 1, S 6, M 1 | vocabulary ∥ routing |
| 2 | `notify-store` ∥ `notify-format` | NS2.1–NS2.7 | M 1, S 5, XS 1 | store ∥ format |
| 3 | `notify-service` | NS3.1–NS3.7 | M 3, S 4 | NS3.4 ∥ NS3.5 ∥ NS3.6 |
| 4 | `notify-client` | NS4.1–NS4.6 | M 2, S 4 | NS4.2 ∥ NS4.3 |
| 5 | `world-notify-source` | NS5.1–NS5.13 | M 4, S 9 | A1 path ∥ A2 path ∥ translator/catalog path |
| 6 | `cache-notify-source` ∥ `notify-centre` | NS6.1–NS6.12 | M 2, S 8, XS 2 | cache ∥ centre |
| 7 | triggered follow-ups (`player-routing`, `world-notify-source`, identity) | NS7.1–NS7.4 | XS 1, S 3 | independent |

63 tasks. No task is L; none touches more than five files (the rail moves in NS5.7–NS5.9 are split per
component so each stays within five, counting a move as one file at its destination).

**Wave status (2026-09-21).** Waves 0–4 landed, and so did wave 6's cache half (NS6.1–NS6.5). Wave 5
landed except two rows: **NS5.11** (its remaining line is the rail's volume reason in
`docs/architecture/world-stage-map.md`, outside this lane's allowed paths — queued with its owner as
`WS-vol-1`) and **NS5.13** (Gate G2's live probe, blocked because no real world-creation route exists —
`WS-live-1`). Wave 6's centre (NS6.8/NS6.11/NS6.12) is gated on the gui-lego queue row being accepted and
dated. Wave 7: NS7.1/NS7.2 landed; NS7.3/NS7.4 were withdrawn by manager erratum (A3/A4 declined).

## Checkpoints (review points, not gates)

| # | After | Evidence |
|---|---|---|
| CP1 | Wave 1 | Empty v1 catalog loads (Server) and types (web); R-N1 isolation test quoted; `guard-dal` green |
| CP2 | Wave 2 | Store tests 1–10 on the in-memory store; `guard-dal` + `guard-test-substrate`; coverage guard green |
| CP3 | Wave 3 | **Map G1** end to end (NS3.7): stored before push, routed to one save, idempotent across the prune, crash-safe, late join by GET, boot = catch-up only |
| CP4 | Wave 4 | notify-client tests 1–7; `build` + `check:bundle`; no `stages/world/` file in the wave's diff. Fills the parent CC7 notifications line |
| CP5 | Wave 5 | fog tests **unmodified and green** (`5/5`, NS5.2) ✓; both hosts load **v3** now (NS6.4's H7 bump) ✓; **Map G2's live probe is BLOCKED** (NS5.13 — no real world-creation route; `WS-live-1`), with `NS5.12` proving the same chain in memory; the full suite is `not_run` (three attempts, each killed with no output) |
| CP6 | Wave 6 | **Map G3's first half landed** (NS6.5 `7/7`: both real sources, one batch); the centre's capped history is **gated** (NS6.11); the owner piece review is **not dated**; the full suite is still owed |

## Cross-program edges

| Edge | Other side | Kind |
|---|---|---|
| Save identity: archived-row refusal (NS7.1) and `SaveId` type (NS7.2) | `SE4.29` (archived-row filter) and `SE4.11` (`SaveId` type) | follow-up trigger; nothing here waits |
| Save switch reaching the injector | `SP6.6` builds the **one** server→injector notice on `PUT /api/players/current` | reuse it if a notification needs the injector to know the save changed; never add a second (parent §3). NS1.8 is the web-side switch only |
| Verification registry rows (NS1.1 and every new path) | `SE0.7` (schema 2) → `TVB` registry-contract (schema 3) | soft; write rows in whatever schema is current, never a third shape |
| `world-notify` relocation (NS5.7–NS5.11) | world-stage `world-notify` — ask A1 (NS0.1) | **ANSWERED 2026-09-21: accepted**; NS5.7–NS5.10 landed, NS5.11's volume line is `WS-vol-1` |
| Fog rule move (NS5.2–NS5.3) | world-stage `world-wire` — ask A2 (NS0.2) | **ANSWERED 2026-09-21: accepted**; both landed (NS5.2, NS5.3, NS5.12) |
| `claim.lost:` producer (NS7.3) | world-map `ClaimResolver` + world-stage `world-playback` — ask A3 (NS0.3) | default declined; debt adapter stays (NS5.10) |
| `legion.starved:` audience (NS7.4) | loam `loam-legions` — ask A4 (NS0.4) | default declined; unmapped |
| Cache reads (NS6.1) | deployment-hierarchy `cache-decay-void` — ask A5 (NS0.5) | default accepted; wave 6 proceeds |
| `supply.besieged` playback row (NS5.4) | world-stage `world-playback` — ask A6 (NS0.6) | default accepted |
| `notices` queue row (NS6.7) | gui-lego `menu-refactor-queue.md` | default: row added with this spec as brief |
| "The player is told" as a gate criterion | deployment-hierarchy G2/G4 | theirs to take after NS6.5; not a task here |

## Tuning publishes owned (parent §5 row "notify catalog")

| File | Version | Task | Publisher | Load sites moved in the same commit (H7) |
|---|---|---|---|---|
| `notification-catalog` | v1 (empty) | NS1.3 | written once (first file; `publish.py` has no domain yet) | `Program.cs`, `shell/notify/catalog.ts` (NS1.4) |
| `notification-catalog` | v2 (world rows, `territory.lost`, `promotions.toast`) | NS5.6 | `publish.py` (domain added in NS5.5) | both |
| `notification-catalog` | v3 (`cache.created`, `cache.decayed`) | NS6.4 | `publish.py` | both |
| `notification-catalog` | next (`legion.lost`) | NS7.4, only if A4 lands | `publish.py`, from the current version | both |
| `notification` (numbers) | v1 (`retainPerCategory` 100, `repeatWindowWorldTurns` 3, "working values") | NS1.3 | written once | `Program.cs` only (the web never reads it) |

If the wave order changes, whichever publisher lands later reads the current `vN` and takes `v{n+1}`;
no task hard-codes the version it expects to find.

## Risks and mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| A crash between commit and push loses a notice | High | Rows + cursor in one transaction; catch-up GET by `rev` after every join (NS2.3, NS3.2, NS3.7) |
| Boot catch-up toasts stale news to a client that reconnected first | Med | `delivery = catchUp` on every boot and lagging-turn batch; the client never toasts it (NS3.3, NS4.5) |
| A lagging pump triggers a turn replay (replay drops post-Step lines, shifting entry indexes and dedup keys) | High | Pump reads the stored `ReportJson` only; trimmed turn → `Report = null`, test fails on any replay call (NS3.3) |
| Pruned row re-inserted as new by an overlapping source window | Med | Key ledger sized to the widest re-read window (`DedupKeyMemoryWorldTurns`), tested at `retainPerCategory = 1` (NS2.2, NS6.2) |
| Catalog and translator drift (a key that renders the fallback) | Med | Coverage guard loops the live catalog; rows ship in the same wave as their translator (NS2.7, NS5.6, NS6.4) |
| Two hosts on two catalog versions | Med | H7: publish + both load lines in one commit; CP5/CP6 check both name the same `vN` |
| World rail's GG-50 bound is a claim with no wiring today (`onCommit` has no production caller) | Low (latent) | Fixed structurally by `worldLatestTurn` (NS4.6, NS5.10); the volume reason is rewritten with it |
| ~~A1/A2 unanswered stalls the world consumer~~ **resolved 2026-09-21** | — | Both were accepted and only their named tasks waited; those landed. The residual blockers are the volume row (`WS-vol-1`) and G2's live probe (`WS-live-1`) |
| `channelSettings` duplicated for one wave | Low | Named overlap; NS5.11 deletes the world copy; same storage key keeps players' choices |

## Defaults shipped behind (no gates)

- **G0 asks** — A1, A2: **answered 2026-09-21 (both accepted)**; the tasks they held landed
  (NS5.2–NS5.3, NS5.7–NS5.10, NS5.12; NS5.11 waits on the volume row, `WS-vol-1`). A3, A4:
  declined (debt adapter stays; `legion.starved:` unmapped). A5, A6: accepted. Resolver for all: the
  repo owner for the owning program. None is irreversible.
- **Critical list** ships empty; any addition is a reviewed `promotions.critical` edit argued in the
  source's spec.
- **Numbers** `retainPerCategory = 100`, `repeatWindowWorldTurns = 3`, marked working values; a balance
  pass publishes `v{n+1}`.
- **GUI Lego owner piece review** (NS6.8) is the authoring procedure's review of an existing recipe, not
  a pre-work gate: resolver the owner; it holds only the React surface (NS6.11). The fold, bus, store,
  history hook and volume fixture proceed.
- **Queue row** (NS6.7): added with this spec as its brief if the gui-lego program has not answered.
- **Save identity**: plays today with the player row id as the save; NS7.1/NS7.2 fire when `SE`
  save-identity lands. The irreversible migration is that program's (parent H2); nothing here writes a
  table it re-keys.
