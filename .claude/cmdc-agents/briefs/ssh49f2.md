# Lane `ssh49f2` — a socketed gem never fires: the mint's container id and the read path disagree

**Session:** `ssh49f2` · **Program:** `strain-splice-host` · **Mode:** worktree
**Fence:** `gk-core/src/FusionRpg.Server/DebugEndpoints.cs`, `gk-core/src/FusionRpg.Data/**`, `gk-core/src/FusionRpg.Core/**`,
`gk-core/tests/FusionRpg.E2E.Tests/**`, `tasks/strain-splice-host-todo.md`, `docs/architecture/item/**`, `tasks/reports/**`

## The defect — measured by a live probe, do not re-derive it

Row **`SSH4.9-F2`** in `tasks/strain-splice-host-todo.md` (line ~989) carries the full reading. In short: a real
4-socket core-guard chassis, four bores and four inserts, all **HTTP 200** — and the socketed word **never
fires**. `socket-insert` stores a socket row whose `insert_container_id` is the **minted, name-derived** container
(`gem.sturdy-layering`), while the read path keys on the **corpus** container id. The lane that found it recorded
both sides and asked for a ruling on which one moves.

## The ruling question, and how to answer it without the owner if the spec answers it

**Read `docs/architecture/item/spec-sockets.md` and `docs/architecture/item/ssot-sockets.md` first.** They own
the `item_socket.insert_container_id` semantics (`src/FusionRpg.Data/Sqlite/RpgStore.ItemCards.cs:50` documents
the gem catalog contract). If the spec says which id is canonical, **that is the ruling** — implement it and say
in the commit which sentence decided it.

If the spec is genuinely silent, do **not** pick a side: present both options with evidence (one paragraph each,
naming what breaks in the other direction) and leave the row open with the question sharpened. The owner rules.

## Deliverable

1. **The seam, named by `file:line`** on both sides: where the mint derives its container id, and where the read
   path resolves it. State which side the spec makes canonical (or that it does not).
2. **The fix**, at the responsible layer. If the mint is wrong, the mint changes; if the read path is wrong, the
   read path changes — ⛔ never "make both work" with a fallback that hides a disagreement, and never widen a
   validator to accept both shapes.
3. **A regression proof that a socketed gem fires**: the strongest available form is an E2E test through the real
   routes (the in-process `RpgApiFactory` host) that sockets a gem and asserts the word fires on a read-back —
   the same chain the live probe ran, without a game. **The live re-probe is the manager's, not yours.**
4. **`SSH4.9`'s own four steps** stay the manager's; do not tick `SSH4.9` itself.

## Verification

- `dotnet test gk-core/tests/FusionRpg.E2E.Tests --nologo --verbosity quiet`
- `python scripts/session-boundary-check.py --repo-root D:/Works/source/plant-vs-zombie-rise-of-summoner --session ssh49f2`

## Evidence contract

- exact command text and the numbers printed
- the committed artifact (SHA)
- an explicit **NOT-proved** list
- findings routed to the owning todo in the same commit, **with the id asserted present**

## Boundaries

- ⛔ Do not touch `gk-core/src/FusionRpg.Server/DebugEndpoints.cs` beyond the mint's own id derivation — the grant
  routes are loopback-gated RPG Server Debug surface and their contract (real writes, shipped corpus, read-back)
  is binding.
- Do not edit generated data; fix the generator. Do not hand-edit `gk-core/data/tuning/**`; publish `v{n+1}`.
- Your session record's `worktree` path must be **ABSOLUTE**.
