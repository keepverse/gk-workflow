Digest of this repo's hard rules. `AGENTS.md` in your workspace has the full text; these are the ones
that most often decide whether a change is accepted.

- **Git:** commit with plain `git` in your own worktree (`git add <explicit paths>` then `git commit`; never `-A`/`-a`). Never push (only the owner asks for that). The git gate was retired 2026-09-19.
- **Verification:** for C#/web changes run
  `.\scripts\verify-change.ps1 -Paths <every file you changed> -Session <session id from the brief>`.
  Do not run full, unfiltered test suites "to be safe" (about 9 minutes, and it competes with other
  sessions). If a path has no mapping, report it; do not fall back to the full suite.
- **RPG layer only:** features live in the RPG layer (channels, atoms, effects, ActorHub). Never patch the
  PvZ game or add ad-hoc Unity stat writes. Combat writes go through `EntityStatWriter`, and HP deltas go
  through the Funnel.
- **One ActorHub:** actor combat stats are composed only in `ActorHub`. Never add another `*Composer*` or
  a private fold of combat numbers.
- **SQL** exists only inside `FusionRpg.Data`.
- **Generated data is never hand-edited:** `gk-data/packs/fusion/data/seed/items/**`, `gk-data/packs/fusion/data/seed/actions/**`, `gk-data/packs/fusion/data/generated/**`,
  `gk-data/packs/fusion/data/seed/atoms/generated/**`. Fix the generator and regenerate instead. Never edit
  `gk-core/data/tuning/*.v{n}.json` in place.
- **Numbers:** integer magnitudes use `long` and `checked` arithmetic. Widen before you multiply. Narrowing is
  checked or reported. Floating point is allowed. Balance numbers go in `gk-core/data/tuning`, not in code.
  Anything derived from level goes through the power ladder (`docs/architecture/power/ssot-power-scale.md`).
- **No hard caps on progression.** Structural limits need a comment saying why.
- **Tests** assert contracts and closed enums, never the size of a content population (such as a species
  count) or generated text. Store tests run in memory.
- **Naming:** `demon` is a legacy word; use `creature`.
- **Never end a turn waiting on your own job.** A verification run is work you do, not work you wait
  for: start it in the foreground, read its output in the same turn, and act on it. Six lanes in one
  2026-09-20 run each idled a whole segment waiting on a job nobody was watching. If a run is
  genuinely long, do the next task's read-only work while it runs — draft the wiring edits, read the
  next spec row — and end the turn having advanced something.
- **A defect you find outside your own scope is not filed by mentioning it.** Report it with
  `file:line` and the cause you read (never the symptom alone), AND open a row in the owning
  program's todo in the same commit. A finding that lives only in your evidence fragment or your
  final report dies with your lane: the owning program never sees it. If you cannot tell which
  program owns it, say so in the row and let the manager route it.
- **Re-anchor doc citations in the same commit as the code move that breaks them.** A move, a shrink
  or a delete invalidates every `file:line` citation pointing into it. Run
  `scripts/guard-doc-citations.ps1 -Strict` before you commit such a change. Two lanes each broke
  their own docs in one run, and both breaks surfaced at merge — in someone else's lane.
- **Foreground commands only:** run builds, tests and scripts as normal foreground commands and
  wait for them. Do not start background shell tasks. On this Windows machine a background task
  opens a visible console window that steals the owner's keyboard focus while they type.
- **The pipeline is guarded and audited.** A hook blocks edits to
  pipeline files (guards, `verify-change.ps1`, `anchor-ledger.py`, hooks, CI,
  `.commandcode/`) and writes outside your workspace. If a rule blocks you, record a blocker note
  (`anchor-ledger.py ... note --text "BLOCKED: <what, why>"`) and continue with other eligible work;
  the orchestrator answers it. Never read or search the runner, the hook settings, or your agent
  directory to understand how the guard works, and never look for another path, file name or script
  that achieves the blocked action. Both are flagged, and both count as a violation. After you finish, an audit checks:
  - every ledger line came from an `anchor-ledger.py` call;
  - every task you mark done has a commit naming its id;
  - the commands in your evidence match commands you actually ran;
  - whether you removed asserts or added `Skip`.
- **Evidence shows the exact command you ran**, copied from the command line with no placeholders
  such as `<files>`. A task whose acceptance allows "no change" (for example a no-move re-bless)
  must say so in its evidence as a row containing `No commit: <reason>`.
- **No watermarks:** no tool or assistant names, "AI-generated", or `Co-authored-by` in code, comments or docs.
- An acceptance line you believe cannot pass as written is never closed `done`. Prove why, then run the
  strongest check that IS achievable (the one you would name "for whoever picks this up" — that is you),
  record a `blocker`/`finding` note asking the manager for an erratum ruling, and continue. The manager
  rules; the task closes against the ruled acceptance. (Retro 2026-09-19, ST3.5.)
- `blocked` means an EXTERNAL dependency you cannot act on: an owner decision, a live/owner-only probe,
  another lane's unmerged work, a denied path. Work you simply have not done yet — however long,
  multi-stage or risky — is never `blocked`; it is the next thing you do, in this session. Marking your
  own unstarted work blocked stops the lane and is treated as a premature stop. (Retro 2026-09-19, ST5.2.)

## Commit hygiene: code first, paperwork rides along (owner ruling 2026-09-19)
- A commit exists to land a change. Status is not a change: "in flight", "state", "re-read", "implementation
  map" and progress notes go in the ledger ONLY (a script write, no commit), and ride along in the next
  task's commit. Never commit a ledger/evidence-only "Record ..." commit.
- Each task is ONE commit: its code + tests + evidence fragment + ledger lines + ticked todo box together.
- A checkpoint closes inside the commit of the last task it depends on (its evidence fragment added there).
  Only a checkpoint that needed new work of its own (a new run, a new measurement) gets its own commit.
- A docs-only commit is legitimate only when the task's deliverable IS the doc (a spec erratum, a register
  row, a status line) or it records an orchestrator-run gate (full suite, live probe).
- Evidence fragments stay short: the `| Criterion | Command | Result | Artifact |` table, one row per
  acceptance line, results quoted as numbers. No narrative beyond one line per row; the commit message
  carries the why. Target <= 25 lines per fragment.
- Corrections to an earlier fragment ride along with the next task's commit, never alone.
- A mechanism that no production host reaches is NOT done, even behind an "optional" seam with a
  documented no-op. Done means a real caller in the real pipeline exercises it, proven by a test that
  enters through the real endpoint/host. If the wire truly belongs to another task, say so and keep
  THIS task open (or blocked on that task), never "done, one wire remains". (Retro 2026-09-19, T24.)
