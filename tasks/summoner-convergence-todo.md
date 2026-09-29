# Tasks — `summoner-convergence` (parent)

Plan: [summoner-convergence-plan.md](summoner-convergence-plan.md). This todo carries **only**
cross-program work and checkpoints; every program task lives in its own todo (plan §1).

## Cross-program tasks

- [ ] **CV.1 — Keep the shared tuning ledger true** · XS · deps: — · *(plan §5)*
  - Acceptance: whenever a sub-plan publishes a shared tuning file, the §5 row is updated in the same
    commit (revision taken, next revision named)
  - Verify: `python gk-core/tools/tuning/publish.py --help` unchanged; `git log -p tasks/summoner-convergence-plan.md`
  - Files: `tasks/summoner-convergence-plan.md`
- [x] **CV.2 — Golden re-bless register** · XS · deps: — · *(plan §4 H1)* — closed 2026-09-20: the
  register below lists every H1 mover in order, each with its own commit; the two earliest moved
  nothing, and no re-bless landed out of order, so nothing was reverted and redone. Evidence:
  `tasks/evidence-fragments/CV.2.md`
  - Acceptance: each H1 re-bless commit is listed here with its cause and hash, in H1 order; a
    re-bless that lands out of order is reverted and redone
  - Verify: `git log --oneline --grep "re-bless"`
  - Files: this todo

### Golden re-bless register (CV.2, H1 order)

The movers, in the order H1 fixes. "What moved" is the commit's own diff, not a summary line: a row
with no golden in it moved no golden.

| # | Task | Cause | Commit | What moved |
|---|---|---|---|---|
| 1 | `ST2.3` | action-skill-tiers — cost scaled once in `CostLedger` | `75553de4` (2026-09-18) | **nothing** — the commit records the no-move (`tasks/evidence-fragments/ST2.3.md`) |
| 2 | `ST1.3` | action-skill-tiers — the tier window | `a4fc08d2` (2026-09-18) | **nothing** — recorded no-move (`tasks/evidence-fragments/ST1.3.md`) |
| 3 | `AE1.5` | action-enrich — the hit's base comes from the action, not `atk` (H6) | `04b8daa0` (2026-09-19) | the battle goldens and their traces: `gk-core/tests/FusionRpg.Core.Tests/Battle/BattleGoldenTests.cs`, `gk-core/tests/fixtures/action-traces/{stomp,wipe}.trace.txt`, `gk-core/tests/fixtures/battle-traces/{stomp,wipe}.trace.txt`, `WaveCDRegressionLockTests.cs` |
| 4 | `SP1.2` C1 fix | species-progression — world-turn uniques stop leaking the species term | `283ab83b` (2026-09-19) | **not a re-bless** — a defect correction (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs`); H1 names it as the edge between the two movers |
| 5 | `SP6.1` | species-progression — each `AllocationScope` resolves alone, weighted (R2/R16/R21) | `eceb08f1` (2026-09-20) | `docs/research/class-system/_baseline-goldens.json` and the aptitude/tuning pins the layer change moves |
| 6 | `EP4.18` | empire-progression — R23 Zomboss pool layer | — | **pending**: wave D is not built (EP4.x rows open) |

Independent single-cause movers (any point, never sharing a commit with another cause):

| Task | Cause | Commit | What moved |
|---|---|---|---|
| `EP1.14` | empire-progression — every production reader calls `EffectiveUniqueAllocation` | `03bdd5cc` (2026-09-20) | own H1 commit; readers + guard test, no golden |
| `EP2.7` | empire-progression — published balance weights + `crowdingFactor` | — | **pending** (EP2.x not built) |
| `EP2.13`+`EP2.14` | empire-progression — the regenerated build plan under the lead/shape caps | — | **pending** (EP2.x not built) |

**Order audit (`git log --oneline --diff-filter=M -- '*Golden*' '*golden*'`).** Inside this program the
only commits touching a golden artifact are `AE1.5` (`04b8daa0`, 2026-09-19) and `SP6.1` (`eceb08f1`,
2026-09-20), which land in H1's stated order; `ST2.3` and `ST1.3` precede them and moved nothing. **No
re-bless landed out of order, so none was reverted.** Two commits touch the class-system research
artifact without being re-blesses and must not be read as causeless moves: `SE1.4` (`243b2aa66`,
publish `aptitudes.v9` through `publish.py` removal ops) and `SP6.0` (`17a15a7d`, H7 publish of
`read.layerWeightMilliByScope` with its reader switch in the same commit).

H1 also forbids two causes in one re-bless: every row above is its own commit, and the two movers
share no commit with any other cause.
- [x] **CV.3 — Stale `decisions.md` line citations** · S · deps: — · *(decisions commit `1575db58`)* — closed 2026-09-21: the blank line that split the ADR table removed (`c3b78fb4`), and all 52 `decisions.md:<N>` citations with `N >= 118` re-pointed to the row NAME the prose names. Evidence: `tasks/evidence-fragments/CV.3.md`
  - Acceptance: citations of `decisions.md:<line>` in docs written 2026-09-18 re-pointed to row names;
    the blank line that split the decisions table (between 'Combat mitigation shapes (2026-08-25)' and
    'Class system (2026-08-26)') removed in the same change, with every citation below it re-pointed
  - Verify: `python scripts/audit-doc-citations.py --scope docs/architecture/decisions.md`
  - Files: `docs/architecture/decisions.md` + the citing docs

## Checkpoints (review points — plan §6)

### CC1 — Live defects closed
- [x] `ST2.2` cost scaled once · `SP0.4` fusion picks accepted (production-path regression) · `T39` free-ward fix · `TVB0.1` release exit checks — verified 2026-09-20 on the merged `features/mega-merge` tree: `tasks/evidence-fragments/CC1.md`

### CC2 — Identity foundation
- [ ] `SE4.1`–`SE4.4` commander-identity + `SE4.11`–`SE4.43` save-identity landed (SE Checkpoint 4b = this checkpoint); migration run on a real save copy is a no-op the second time; timestamped backup present
  **BLOCKED 2026-09-20, re-checked 2026-09-20** — migration mechanism (SE4.15-SE4.29) is built and
  green (29/29, `SaveIdentity` filter). `SE4.4`'s gap (`scripts/guard-open-identity.ps1` missing) is
  **CLOSED** this session — see `tasks/evidence-fragments/SE4.4-guard-gap-closure.md`. Remaining:
  `SE4.30` (real-save migration run) is routed to the live QA lane with an exact probe. See
  `tasks/evidence-fragments/CC2.md`.
  **Live probe 2026-09-20 (live-qa lane): PASS on the migration itself.** A copy of the real save's
  pre-migration snapshot booted the real server on a spare port: report quoted, `.bak` present, human
  numbers read back equal through `/api/players/current` + `/api/rpg/progression/1/summary`, and a
  second boot wrote no new marker or backup. **SE4.30 CLOSED 2026-09-20 by owner ruling** on that
  migration probe. The two other clauses are recorded, not left silently unmet: the full suite is red
  only on four pre-existing facts (`gk-core/tests/FusionRpg.Core.Items.Tests/Items/SocketOperationsTests.cs:340`
  and `:329`, `gk-core/tests/FusionRpg.Core.Items.Tests/Items/UniqueCorpusTests.cs:524`,
  `gk-core/tests/FusionRpg.Core.Atoms.Tests/Atoms/Generation/FamilyExpansionTests.cs:193`), which are
  routed to the `test-verification-boundary` program as a knownRed registration so no lane is charged
  for them; and the rollback rehearsal cannot run in that worktree at all, because it holds no
  pre-SaveIdentity binary. Details + the regression hand-over: `tasks/evidence-fragments/CC2.md`.
  **Re-anchored 2026-09-23 (lane `tvb60`, which owns the Core split):** the three paths above moved —
  `Items/SocketOperationsTests.cs` and `Items/UniqueCorpusTests.cs` to `gk-core/tests/FusionRpg.Core.Items.Tests/`,
  `Items/FamilyExpansionTests.cs` to `gk-core/tests/FusionRpg.Core.Atoms.Tests/Atoms/Generation/` — so the
  pre-split paths no longer resolved (this file's own `doc-citations` check flagged
  `tasks/summoner-convergence-todo.md:78  D3`). The four facts themselves are **green** at this head
  (measured: the Core group 68 projects / 15,836 tests / 0 failures, `SocketOperationsTests` 22/22
  focused), so no `knownRed` entry was registered — see `tasks/test-verification-boundary-todo.md`.

### CC3 — Damage from the action
- [x] `AE` Checkpoints 1–2; H1 re-blesses so far registered in CV.2 — verified 2026-09-20 on the merged `features/mega-merge` tree: `tasks/evidence-fragments/CC3.md`

### CC4 — Layers resolve alone
- [x] `SP` 6.1 re-bless with its explained table; zombie XP on Zomboss's empire — verified 2026-09-20 on the merged `features/mega-merge` tree: `tasks/evidence-fragments/CC4.md`

### CC5 — Empire progression live
- [ ] `EP` CP1–CP6
  **BLOCKED 2026-09-20** — all six checkpoints unticked; only `EP1.1`/`EP1.2` landed (on a separate,
  not-yet-merged branch), `EP1.3`–`EP1.18` remain. See `tasks/evidence-fragments/CC5.md`.

### CC6 — Items converge
- [ ] species-gear-chain + `SSH` checkpoints; combo-budget report green
  **BLOCKED 2026-09-20** — species-gear-chain's own closing "Checkpoint — Complete" unticked (owner
  sign-off pending); SSH Checkpoint 6 (parent CC6) unticked, and `combo-budget --report` (named
  directly by plan §6) does not exist anywhere in the repo yet. See `tasks/evidence-fragments/CC6.md`.
  **Blocker (2026-09-20, live-qa): the two remaining CC6 clauses are SSH-program work, routed to the
  `ssh27` lane.** (1) helm-hosts-words: `gk-core/data/tuning/sockets.v1.json:13` still has `"head-guard": 3`
  while `docs/architecture/strain-splice-host/spec-circuit-topology.md:47` (R11) requires **4** in the
  new `sockets.v2.json`; the fill it gates is `tasks/strain-splice-host-todo.md:298` **SSH5.13**
  (OWNER-RUN helm-host re-run under v2), deps SSH5.12/SSH2.5/SSH2.7. (2) the combo-budget report:
  `python -m seedsmith items combo-budget --report` (named by
  `docs/architecture/strain-splice-host/spec-combo-budget.md:155`) does not exist —
  `gk-forge/tools/seedsmith/seedsmith/report/cli.py:624` lists only generate/validate/combogen-migrate/fill/repair-*
  (`seedsmith items: invalid choice: 'combo-budget'`). Green this lane: materials 2/8/0 (trophy `--check`
  drift 0), 95 combination entries, socket-words retirement, combo bind/evaluate 63/63 — but no live item
  was reachable to bind.

### CC7 — Infrastructure
- [ ] `TVB` + `NS` checkpoints
  **BLOCKED 2026-09-20** — sharding (TVB Checkpoint 1) and notifications waves 1-4 (NS Checkpoints
  1-4) verified green; `TVB` Checkpoint 3 (python lane) and Checkpoint 5 (Core split) unticked, and
  `TVB` Checkpoint 6 (explicitly "parent CC7") unticked. See `tasks/evidence-fragments/CC7.md`.
  **Blocker (2026-09-20, live-qa): the Core-split clause is `test-verification-boundary` work, routed
  to the new `tvb58` lane.** `tasks/test-verification-boundary-todo.md` Checkpoint 5 ("Every manifest
  project applied; residual green; no test→test `ProjectReference`") and Checkpoint 6 (parent CC7) are
  both unticked; nothing in this lane's paths produces or validates the split. Sharding (14/14),
  notifications waves 1-4 (43/43) and the python lane (TVB Checkpoint 3, all bullets `[x]`) are green.

### CC8 — Convergence
- [ ] full suite green (`.\scripts\test-fast.ps1 -AllDefault`); live probe on a real save per `docs/contributing/live-probe-standard.md`

### Findings routed in (2026-09-23, lane `tvb60`)

- [ ] **SE-F1 — SE4.31's `empireId` invalidated the checked-in FE contract fixture, and the change's own
  verification never selected the test that sees it** · S · *(found by lane `tvb60` at the merged head
  `f585d8d6e` while running TVB5.9's `-AllDefault` acceptance; `gk-web/web/fusion-rpg-web/**` is outside that
  lane's fence)*
  `0770c0f81` (SE4.31) added `gk-core/src/FusionRpg.Contracts/UniqueActorDtos.cs:22`
  `[JsonPropertyName("empireId")] public string? EmpireId`, set from
  `gk-core/src/FusionRpg.Server/UniqueActorService.cs:201`. The live `POST /api/unique/actors` DTO now carries
  `"empireId": "dave"`, while the checked-in fixture
  `gk-web/web/fusion-rpg-web/e2e/fixtures/unique-actor.json` (last written `e588c251a`, 2026-08-23) does not — so
  `FusionRpg.E2E.Tests.ContractFixtureTests.Unique_actor_fixture_still_matches_the_live_dto` fails:
  measured `Failed: 3, Passed: 273, Skipped: 0, Total: 276` from
  `pwsh -NoProfile -File scripts/test-fast.ps1 -Project gk-core/tests/FusionRpg.E2E.Tests` (2 m 18 s), the other two
  failures being the pre-existing stale fixtures TVB-F25 already routes.
  **Cause read:** the fixture is the FE's shared contract source and the test that guards it lives in
  `gk-core/tests/FusionRpg.E2E.Tests/ContractFixtureTests.cs`, but no verification boundary selects that project
  for a `gk-core/src/FusionRpg.Contracts/**` path — `verify-change -PlanOnly -Paths
  gk-core/src/FusionRpg.Contracts/UniqueActorDtos.cs` plans `contracts-fallback (module)` / `test: core` (the
  68-project group) only. The missing local signal is filed as **TVB-F28** in
  `tasks/test-verification-boundary-todo.md`, which owns that surface.
  **Fix (one command, needs a lane or the manager holding `web/**`):**
  `FUSIONRPG_BLESS_CONTRACT_FIXTURES=1 dotnet test gk-core/tests/FusionRpg.E2E.Tests/FusionRpg.E2E.Tests.csproj
  --filter "FullyQualifiedName~ContractFixtureTests"` rewrites the fixture from the live DTO
  (`ContractFixtureTests.AssertFixtureMatches`), then commit
  `gk-web/web/fusion-rpg-web/e2e/fixtures/unique-actor.json`. Do not hand-edit it.
  **Verify:** the same filter is green and `git diff` shows `empireId` added.
  **Owner:** `summoner-convergence` (SE4.31's program). Evidence:
  `tasks/evidence-fragments/tvb60-register-reverify-merged-head.md`.
