# Evidence — the clock seam's §4 ask to `world-continuity`, ANSWERED from their spec and this lane's guard

Lane `sim-t3-2`, worktree `D:\Works\source\plant-vs-zombie-rise-of-summoner\.claude\worktrees\cmdc-sim-t3-2`
(branch `cmdc/sim-t3-2`). `docs/architecture/rpg-simulator-spec-clock-seam.md` §4 carried an ask *"open until
answered"* to `world-continuity`: confirm that `hibernation-clock` reads the wall clock only where a **duration**
is pro-rated and never for **pending turns**, and that those reads go through `ServerClock`. It is answered —
from their own spec plus this lane's guard, because the module is not built — and the residue is filed as RS-F26.

| Criterion | Command / read | Result |
|---|---|---|
| The pending-turns half is confirmed, by their spec | `docs/architecture/world-continuity/spec-hibernation-clock.md` §3 and §6 | `Pending(saveEndTurns, clockMark, catchUpCapTurns)` is **pure**, and §6 says *"`Pending` is pure and reads no clock; the Core file sits under the world determinism guard's scan root."* |
| …and there is no wall-clock read to confirm IN CODE, because the module is a declared gap | their spec's own summary table + `grep -rn "GetPendingTurns\|clock_mark\|end_turns" src/ --include=*.cs` | summary puts **"save counter, clock mark, pending"** under **Real gap** and `catch_up_cap`/`turn_period_seconds` under **Wiring gap — never read**; the grep returns **nothing**; `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs:27-28` declares the two columns with no reader |
| The duration half is already a MECHANISM, not a promise | `python gk-core/scripts/guard-clock-seam.py` | the idle window / yield accrual / freshness belong to `idle-world` / `background-yield` (their §2 non-goal, also unlanded), and any new ambient read fails CI: the guard reads `1502 files, 21 ambient reads (2 in the clock type, 19 allowlisted), 0 simulation-tree references` and a stale allowlist entry is itself a violation |
| Every citation in the answered section resolves | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/guard-doc-citations.ps1 -Strict` | exit **0**, `D1 file does not exist 683 (0 HIGH)`, `D2 line past end of file 7 (0 HIGH)` |
| Nothing else regressed | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/run-guards.ps1 -Tier ci` | exit **0** — `GUARDS OK - 25 guard(s) run, 0 red` |

**What the answer changes.** The plan recorded `idle-world` and `background-yield` as waiting on this agreement.
They are not waiting on it any more: they are waiting on their own code, with the seam's constraint enforced by
`gk-core/scripts/guard-clock-seam.py` rather than by a promise from another program.

**The residue, filed as RS-F26** (world-continuity's module `hibernation-clock`, map row 2): when the save
counter / clock mark / pending land, `Pending` stays pure and clock-free and every duration read goes through the
seam. Filed here because that program's todo is outside this lane's allowed paths.

**How this was answered, stated so nobody over-reads it.** Not by a reply from the module's owner — by *their*
specification (the authority for a module that is not built) and by *this* program's guard (the authority for
what a duration read may touch in `src/`). If the world-continuity owner disagrees with either half, the
disagreement is a finding about their spec, not a missing answer from this lane.
