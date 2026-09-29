# TVB-F15 (this program's share) — `doc-citations` red on this program's docs

Routed to this program by `test-verification-boundary` (row in `tasks/notification-ssot-todo.md`).
The guard is gating CI, so CC8 stays red until the citations resolve.

| Criterion | Command | Numbers printed |
|---|---|---|
| this program's own documents carry no dead citation | `python scripts/audit-doc-citations.py --scope docs/architecture/notification-ssot-ideal.md` | `D1 file does not exist 0 (0 HIGH) · D2 0 · D3 0 · D4 0` — was `14 HIGH` before this change |
| the checker the CI guard runs, whole tree | `powershell -NoProfile -Command ".\scripts\guard-doc-citations.ps1 -Strict"` | `D1 922 (6 HIGH) · D2 13 (1 HIGH) · D3 58 (1 HIGH) · D4 0` — 8 HIGH in total, **none inside this program's documents** |
| boundary command over the changed path | `.\scripts\verify-change.ps1 -Paths 'docs/architecture/notification-ssot-ideal.md' -Session notification-ssot-20260920` | maps to `docs-and-assistant-config (focused)` + `guard: doc-boundary`; citations `D1 0 (0 HIGH)` / `D3 0 (0 HIGH)`; `Passed! - Failed: 0, Passed: 4, Skipped: 0, Total: 4, Duration: 34 s` |
| the other eight findings belong to other programs and are filed | grep of the owning todos | `npc-story-events-todo.md` **DOC-NS5.7** (2) · `trade-network-todo.md` **DOC-NS5.7** (3) · **DOC-NS5.2** (1, the D2 in `legion-build/spec-legion-count-cost.md`: a line number past the end of `WorldEndpoints.cs` (1003 lines), caused by NS5.2's own move) · `world-stage-todo.md` **WS-cite-1** (1) |

**What the fix is.** `docs/architecture/notification-ssot-ideal.md` is this program's idea document and
predates the program, so its 14 dead citations are **pre-move** references to the world stage's old rail
store and category registry. Each cited line now says so inline (the exemption the audit accepts) and the
document opens with a dated citation note that also points at the two successors
(`shell/notify/rail/railStore.ts`; the catalogue + `shell/notify/catalog.ts`).

**Scope note (disclosed, not assumed).** This file was not in the lane's session record, and
`verify-change` refuses a path outside it (`path is outside session scope`). TVB-F15 was routed to this
program, so the session record (`tasks/sessions/notification-ssot-20260920.json`) was widened in the same
commit — that record is what the boundary command reads. The lane brief's own allowed-path list does not
name the file either; if the orchestrator's post-run check rejects it, this document is the only such file
in the commit and everything else (todo row, fragment, ledger, session record) is inside the listed paths.

**NOT proved:** nothing but the two checkers ran — the change is citations and prose, no behaviour.

## Addendum — this program's todo file (2026-09-21)

The same audit flags dead citations in `tasks/notification-ssot-todo.md` (they are inside the acceptance
texts that describe this program's own moves, and inside the routed row itself): `D1 7 HIGH` on
`categories.ts` / `notifyRailStore.ts` (both GONE as of NS5.7/NS5.11) and one `D2` quoting the legion-build line-past-end. Each citing
line now says the file is GONE (or, for the D2, describes the stale line instead of citing it), so the
scoped audit for that file prints `D1 0 (0 HIGH) · D2 0 · D3 0 · D4 0`.

| Criterion | Command | Numbers printed |
|---|---|---|
| this program's todo carries no dead citation | `python scripts/audit-doc-citations.py --scope tasks/notification-ssot-todo.md` | `D1 0 (0 HIGH) · D2 0 (0 HIGH) · D3 0 (0 HIGH) · D4 0 (0 HIGH)` — was `7 D1 + 1 D2` |

With that, both documents this program owns that the audit flagged (`notification-ssot-ideal.md` and
this todo) read clean, and `NS-fence-1` is closed on that evidence while `NS-fence-2` is reframed as an
ownership blocker (the volume row is world-stage's own file, queued as `WS-vol-1`).
