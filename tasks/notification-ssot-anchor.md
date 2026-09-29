# Anchor: notification-ssot

Map: `docs/architecture/notification-ssot-map.md`
Plan: `tasks/notification-ssot-plan.md` · Todo: `tasks/notification-ssot-todo.md`
Specs: `docs/architecture/notification-ssot/**` — the active module per the todo row
Session: `notification-ssot-20260920` (direct, branch `features/mega-merge`) · Paths: `gk-web/web/fusion-rpg-web/src/**`, `gk-core/src/FusionRpg.Contracts/**`, `gk-core/src/FusionRpg.Core/**`, `gk-core/src/FusionRpg.Data/**`, `gk-core/src/FusionRpg.Server/**`, `gk-core/tests/FusionRpg.Core.Tests/**`, `gk-core/tests/FusionRpg.Data.Tests/**`, `gk-core/tests/FusionRpg.Server.Tests/**`, `gk-core/tests/FusionRpg.Guard.Tests/**`, `gk-core/data/tuning/**`, `gk-core/tools/tuning/**`, `docs/architecture/notification-ssot/**`, `tasks/**`
Standards: `PRINCIPLES.md` + the DESIGN-GATE §1 row for every subsystem this program touches + the
  `decisions.md` locks it cites. **The lane's own session reads them at its first task** — anchor setup
  did not (writing eight subsystems' standards into this file would claim a reading that never happened).
Open rows: 12 unchecked `- [ ]` lines (measured 2026-09-21 after waves 0–6 landed; was 26 at anchor
  creation). Eight are task rows — **NS5.11** (blocked: its `world-stage-map.md:241` volume line is a
  denied path, `NS-fence-2`), **NS5.13** (blocked: Gate G2's live subject is unreachable — no real
  world-creation route, `WS-live-1`/`NS-fence-4`), **NS6.8/NS6.11/NS6.12** (gated on the gui-lego
  queue row being accepted and dated) and **NS-fence-1/-2/-4** (outside this lane's paths or awaiting
  a manager ruling; `NS-fence-3` is ROUTED to `TVB-F1`) — plus four checkpoint lines that state their own
  reason (G2 blocked; the full suite `not_run`). The bar is 0
Queue (todo order; ✓ = landed under the owner's A1/A2 answers of 2026-09-21): NS0.1✓, NS0.2✓, NS5.2✓,
  NS5.3✓, NS5.7✓, NS5.8✓, NS5.9✓, NS5.10✓, NS5.11 (blocked), NS5.12✓, NS5.13 (blocked), NS6.5✓,
  NS6.8 (gated), NS6.11 (gated), NS6.12 (gated), NS7.1✓, NS7.2✓, NS7.3 (withdrawn by erratum),
  NS7.4 (withdrawn by erratum)
Next: nothing unblocked — every remaining row needs the manager (see Open rows). Gate status lives in
  the map's §Gates paragraph; per-row evidence is `tasks/evidence-fragments/NS*.md`.
Peers:
| `web` surfaces | per that map | the notify rail, channel control, debt adapter | the report/feed vocabulary |
| `save-identity` | per that program | one generic save-switch notice | the server notification bus |
Drift gates: `python scripts/session-boundary-check.py` ·
  `.\scripts\verify-change.ps1 -Paths <every changed path> -Session notification-ssot-20260920`
Evidence: `tasks/evidence-fragments/<task-id>.md`, one per task (`| Criterion | Command | Result | Artifact |`)
Ledger: `tasks/notification-ssot-ledger.jsonl` — append-only run state, written only through
  `python gk-core/scripts/anchor-ledger.py tasks/notification-ssot-ledger.jsonl ...`; `check` must exit 0
Verify: each task's own Verify line (focused filter + its guard). The full suite belongs to CC8 or this
  program's final checkpoint — never to an ordinary task.
