# Lane brief — `sim-t3-1` (t3: the real-process host, the honesty guard, the clock)

## Program

`rpg-simulator` — the offline RPG simulator. Plan: `tasks/rpg-simulator-plan.md` · Map:
`docs/architecture/rpg-simulator-map.md` · Todo: `tasks/rpg-simulator-todo.md` · **Owner-cleared decisions:
`tasks/rpg-simulator-decisions.md` (read it first — every row below carries its ruling)**.

**Already delivered, do not redo:** RS1 (the first-session scenario), RS5 (map + plan), RS2.1–RS2.4 (the scenario
contract, the verdict/digest contract, `gk-core/tools/RpgSim` itself, the in-process host) — all merged.

⛔ **Read the design gate first.** `docs/DESIGN-GATE.md` §1 topic index → read the documents its rpg-simulator /
clock rows name, **in this session**, then verify each claim against code. Code beats docs; docs beat comments.

## The three rows, in this order

### 1. RS2.5 — the real-process slow lane (completes RS2's own contract)

RS2's contract is *"the same scenario file, two hosts (in-process default, real process slow lane)"*. Only the
in-process host was delivered. Deliver the real-process host so `gk-core/tools/RpgSim` runs a scenario against **both
approved hosts** — same file, same checks, different transport. Evidence: the same scenario's verdict from each
host, with the digest comparison naming any pointer that moved (the digest contract already does this).

### 2. RS4 — the scenario-honesty guard (S; approved D4 (b))

*"A scenario may not assert on state it created through anything but a real route."* Build the guard that refuses a
scenario whose `expect.*` reads back something the scenario itself fabricated (a seed route, a direct store write, a
debug endpoint that invents the result). It must **bite on a planted violation** — a scenario written to cheat must
fail the guard, and the real scenarios must pass. A rule that has never been seen to fail is not known to work.

### 3. RS3 — the clock: full `TimeProvider` migration, then retire `ForceExpeditionDue` (L)

Owner rulings: **B1 (a)** full migration · **B2 (b)** the clock is **product surface**, not a test-only seam ·
**B3 (a)** retire `ForceExpeditionDue`. The measured surface is in the `decisions.md` row: **203 sites, 143
mechanical, 25 already injectable, and 9 that must NOT be simulated** — those 9 are the row's own risk; name them
in your report rather than silently skipping or migrating them. RS3 is **gated by the `decisions.md` row plus a spec
that names the seam's product shape** — if that spec does not exist yet, writing it is the first task, and saying so
is a valid segment outcome.

Do RS3 **incrementally**: one commit per coherent group of sites, each with its own verification. A 203-site
migration that lands as one commit cannot be reviewed or bisected.

## Fence (your session paths)

- `gk-core/tools/RpgSim/**` — the tool and its hosts
- `tests/FusionRpg.E2E.Tests/Rpg*Tests.cs`, `gk-core/tests/fixtures/rpg-scenarios/**`
- `gk-core/src/FusionRpg.Core/**`, `gk-core/src/FusionRpg.Server/**` — the clock seam and `ForceExpeditionDue`
- `docs/architecture/rpg-simulator*`, `docs/architecture/decisions.md`
- `tasks/rpg-simulator-todo.md`, `tasks/rpg-simulator-plan.md`, `tasks/rpg-simulator-ledger.jsonl`
- `scripts/**` — only what a row you close requires

Anything else is another session's fence — name it as a dependency instead of reaching across.

## Hard rules

1. **A scenario may not fabricate what it asserts on** (that is RS4's whole point) — every step goes through a real
   route, and a `read.*` names an FE-facing route or a hub message.
2. **No magic numbers on the balance surface** — a number a balance pass would change lives in
   `gk-core/data/tuning/<domain>.v{n}.json`; publish `v{n+1}` through `gk-core/tools/tuning/publish.py`, never edit in place.
3. **Numeric range is a constraint**: widen before multiplying, integer overflow throws, divide by 1000 last in
   per-mille math.
4. **Test substrate**: tests run **in memory**; `gk-core/scripts/guard-test-substrate.py` enforces it (a `tests/**` file
   constructing a file-backed store carries `[Trait("Category","DiskSemantics")]` — tag only what genuinely tests files).
5. **A row you close needs its evidence in the same commit**, and the row id asserted present after the edit.
6. **One ActorHub compose** — contribute through `IActorStatSubsystem` / registered atom readers, never a parallel composer.

## Verification

- `dotnet test gk-core/tests/FusionRpg.E2E.Tests -c Release --filter "<your tests>"` — read the printed counts.
- `dotnet run --project gk-core/tools/RpgSim -- --validate <scenario>` and the same scenario against **each** host.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-change.ps1 -Paths @('<every path you changed>') -Session sim-t3-1`
- For the clock row: the migration's own test must fail against the unmigrated seam (planted violation) and pass after.

Read the **printed numbers**, never an exit code alone. A selected check that fails is diagnosed at that boundary —
it never authorises a broad retry, and the full suite is not yours to run.

## Report (end every segment with this)

```
<<<REPORT
{"status": "partial|done|blocked",
 "summary": "<what landed, with commit shas and row ids>",
 "closed": ["<row id>: <one-line evidence>"],
 "open": ["<row id>: <what it now waits on, named>"],
 "blocked": ["<row id>: <the named dependency or the sharpened question>"],
 "next": "<the single next row you would take>"}
REPORT
```

Every claim in the report must already be a commit in this worktree.
