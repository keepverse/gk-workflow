# Evidence — rpg-simulator row dispositions (RS-F9, RS-F16, RS-F4→RS-F22, RS4, RS6) + the segment's gate readings

Lane `sim-t3-2`, worktree `D:\Works\source\plant-vs-zombie-rise-of-summoner\.claude\worktrees\cmdc-sim-t3-2`
(branch `cmdc/sim-t3-2`). This fragment records the **dispositions** of five rows whose work landed in earlier
commits (so the tick and its evidence are in the tree, and this file names where each landed), plus the gate
readings taken at the segment's end.

| Row | Disposition | Where its work landed |
|---|---|---|
| **RS-F9** (RS3's fence) | **closed** — the acceptance's first branch: a fence covering Data/Injector/Launcher/CheatCore existed and every increment landed. The manager's own erratum (`58e68d6fd`) closed it by disposition too; this adds the measured proof. | increments 2–4 in `dec15f8fc`, `8d7bb1472`, `30eca17e1`; the guard's reading (`1502 files / 21 ambient / 0 simulation-tree refs`) in `e6ab1c599` |
| **RS-F16** (the rewind needs a mid-run clock) | **closed** — the acceptance's first branch: the mid-run input exists and `ForceExpeditionDue`'s `UPDATE` + its route are deleted with the corpus re-pointed. Ruled by the owner in `f49cd83b4`. | 5a `ad18f78f6`, 5b `3cc193cb6` |
| **RS-F4** (the seeds) | **closed** — the acceptance's *second* branch: the plan states the digest is intentionally scoped to host-stable readings and names the reason. The seam itself is not dropped; it has its spec and its implementation is carried forward. | spec `fd42f0f01`; plan §11 item 3 in the same commit |
| **RS4** (wave-header pointer) | **ticked** — the pointer row lagged its real Wave-3 row, the staleness the todo's own note warns about. | guard + wiring in `f8a066b6a`; the real row's note in the same commit |
| **RS6** (`DataTestStore`'s home) | **still open, and it needs ONE manager ruling** — the map now records its premise as retired (no `tools/` consumer exists, and RS-F6 decided the CLI the same way), while the fence blocker (314 files across five projects, four outside every `rpg-simulator` lane) is unchanged. | map module 6 in `1d7078a33`; the row's note in `01ee7fe46` |
| **RS-F22** (new) | **filed** — the seed seam's implementation, waiting on the predictability ruling. | `fd42f0f01` |

**Gate readings at the segment's end** (printed, not inferred):

- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/run-guards.ps1 -Tier ci` → **25 guards, 24 green, 1 red**;
  the one red is `doc-citations` (RS-F18, a LOAM document). `clock-seam`, `sim-fabrication`, `population-pin`
  and `narrative` are all green.
- `guard-sim-fabrication.ps1` → `scenarios=1 steps=36 reads=7 test.* steps=1 | /api/sim handlers=60 (take RpgStore: 0) | /api/test handlers=12 (take RpgStore: 11, allowlisted: 11)`.
- `guard-clock-seam.py` → `source files=1502 ambient reads=21 (clock type=2, allowlisted=19, entries=19) | simulation-tree ServerClock references=0`.
- `guard-test-substrate.py` → `TEST SUBSTRATE GUARD OK`.
- `guard-doc-citations.ps1 -Strict` → `D1 file does not exist 714 (0 HIGH)`, `D3 ambiguous basename 58 (2 HIGH)`; both HIGHs are `docs/architecture/loam-relics-and-wonders/spec-relic-item-kind.md:76` (RS-F18).

**Disclosure — where the ticks landed, and why it is not tidy.** The five row dispositions above were written
into `tasks/rpg-simulator-todo.md` in the same working session as the RS-CF3 fix, so they were **carried by
`01ee7fe46`**, whose message names RS-CF3 only. The hygiene rule wants a row's tick in the commit that lands
its work; here the work had already landed in four earlier commits, so the ticks are a *bookkeeping sweep* and
should have been their own commit. This fragment is that commit's missing record: it names each row, its
disposition and the commit its work actually landed in, so the audit's "a commit naming the id" is satisfiable
from the history rather than only from the ledger.
