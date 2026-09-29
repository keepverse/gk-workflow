# Lane `cai4` evidence index

This lane's fragments are split across two directories, and the split is deliberate rather than drift:

- `tasks/evidence-fragments/` — **the canonical home**, used for everything written after the manager
  widened this lane's fence to include it (2026-09-22).
- `tasks/reports/` — where the first segment's fragments had to go, because
  `tasks/evidence-fragments/**` was outside the fence at the time and a changed file outside it fails
  the run. Each of those carries a **supersession pointer** to its canonical twin where one exists, and
  stays where it is because this lane's earlier commits and its ledger lines reference it.

| Row | Canonical fragment | Earlier copy |
|---|---|---|
| `CAI4.2` | `tasks/evidence-fragments/CAI4.2.md` | `tasks/reports/CAI4.2.md` (supersession pointer) |
| `CAI4.6` | — | `tasks/reports/CAI4.6.md` (the row's only fragment) |
| `CAI4.7` | — | `tasks/reports/CAI4.7.md` (the row's only fragment) |
| `CAI4.9` | `tasks/evidence-fragments/CAI4.9.md` | `tasks/reports/CAI4.9.md` (supersession pointer) |
| `CAI-cite-2` | `tasks/evidence-fragments/CAI-cite-2.md` (the filing lane's) | `tasks/reports/CAI-cite-2.md` (this lane's closing evidence) |
| `CAI-cite-3` | — | `tasks/reports/CAI-cite-3.md` |
| lane status, the blocked-row re-read | — | `tasks/reports/cai4-lane-summary.md`, `tasks/reports/cai4-blocked-reread.md` |

`CAI4.6` and `CAI4.7` were not re-filed into the canonical directory on purpose: their fragments are
complete and referenced by commit messages and ledger lines, and copying them would put two divergent
copies of one row's evidence in the tree — the thing the supersession pointers exist to avoid.
