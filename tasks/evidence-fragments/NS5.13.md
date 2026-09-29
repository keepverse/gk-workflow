# NS5.13 — Gate G2 live probe (RPG Server Debug scope) — BLOCKED, not_run

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| full suite once (`.\scripts\test-fast.ps1 -AllDefault` — wave 5 crosses Core, Server and Web, and precedes a live probe: AGENTS.md points 2 and 3), output quoted | `powershell -NoProfile -Command ".\scripts\test-fast.ps1 -AllDefault"` | **`not_run`** — run twice, in two consecutive segments; both were killed by an infrastructure error mid-command with **no output at all** (no tally, no partial log; nothing salvageable). Recording `not_run` rather than a pass: a suite whose output nobody can read is not evidence. The lane's own contract also places the full suite with CC8 / this program's final checkpoint rather than a wave-1 row, so this line needs a manager ruling either way | — |
| on a world created through the real path, a real `POST /api/world/{worldId}/commit` that starves a component produces a `loam.shortfall` toast for the committing save and no one else; `GET /api/notifications/{playerId}` reads it back; the world rail shows exactly the just-resolved turn and a reload rebuilds it from catch-up alone; the real screen is looked at | — | **BLOCKED on two proven obstacles, neither of them code this lane may write:** (1) **there is no real world-creation path at all** — `RpgStore.CreateWorld` has exactly ONE caller in all of `src/`: the SIM route, `WorldEndpoints.cs:602`, inside `MapWorldTest` (`/api/test/world/create`); the real `MapWorld` group (`WorldEndpoints.cs:24-586`) maps no creation route, and nothing in the FE, launcher or injector calls one (grep, this session). So "a world created through the real path" cannot be satisfied, and using the SIM route is the debug fabricator this row's own last sentence forbids. (2) **no route can make a component starve**: the SIM create builds the *shipped* template unchanged, while the only fixture that starves (NS5.12/NS6.5's) mutates the in-memory world before `CreateWorld` — the real homeworld is not empty, so no `POST /commit` produces a `loam.shortfall` in probe time. Also: `:5088` is held by ANOTHER lane's `FusionRpg.Server.exe` (PID 30644, `netstat`/`tasklist`, this session), so a probe would have to stand up its own server — and the acceptance's "look at the real screen" needs the owner's live install | — |
| what IS proven in its place (same chain, without the live install) | `dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~WorldNotify"`; `…~CacheNotify`; `npx vitest run src/stages/world src/shell/notify` | NS5.12 `12/12` (real commit route -> real pump -> real source -> real publisher -> one live batch for the world's own save only, read back through the real catalog) · NS6.5 `7/7` (both real sources, one batch, R-N6) · FE `97 files / 856 tests` + `npm run build` clean — i.e. every link of the chain is exercised through its real entry point, just not on a running install | tasks/evidence-fragments/NS5.12.md, NS6.5.md |

**Gap filed with its owning program (same change):** `tasks/world-stage-todo.md` — the missing real
world-creation route belongs to world-stage's `world-wire` module (`world-stage-map.md:72`), which owns
the `/api/world` projections. This lane may not add a route (its fence is not world-stage's), so the row
exists rather than the code.

**NOT proved:** everything in row 2 (a live server, a live screen, a live toast), and the full suite in
row 1. NS5.13 stays open and blocked; it is the only row in this lane's queue that is not done or
otherwise dispositioned.

## Full-suite attempts (three, all `not_run`)

`powershell -NoProfile -Command ".\scripts\test-fast.ps1 -AllDefault"` was launched **three times** in
this lane (twice before the manager's ~4h pause, once on 2026-09-21 after resuming onto `4bce1fe5`).
Every run died mid-command with an infrastructure error and produced **no output at all** — no per-project
tally, no summary, no partial log to salvage. The most recent attempt is the third.

Recording this as `not_run`, not as a pass, and not retrying a fourth time: three identical failures is
an environment limit on long foreground commands here, not something another attempt fixes. The lane's own
contract puts the full suite with CC8 or the program's final checkpoint anyway, so this line needs a
manager ruling — either CC8 runs it and quotes it for Gate G2, or the row's acceptance is re-worded to
name the scoped evidence that does exist (`NS5.12` `12/12`, `NS6.5` `7/7`, `WorldNotify`/`CacheNotify`
filters, the FE `856` tests and `npm run build`).

## The suite line, MEASURED per project (2026-09-21, head `287a3256`)

`test-fast.ps1 -AllDefault` was killed three times with no output, so the default project set was
measured project by project instead. Every number below is from a command run in this session.

| Project | Command | Numbers printed |
|---|---|---|
| Core | `dotnet test gk-core/tests/FusionRpg.Core.Tests -c Release` | `Passed! - Failed: 0, Passed: 13180, Skipped: 0, Total: 13180, Duration: 1 m 8 s` |
| Data | `dotnet test gk-core/tests/FusionRpg.Data.Tests -c Release` | `Passed! - Failed: 0, Passed: 1797, Skipped: 0, Total: 1797, Duration: 11 m 41 s` |
| Server | `dotnet test gk-core/tests/FusionRpg.Server.Tests -c Release` | `Failed! - Failed: 2, Passed: 761, Skipped: 0, Total: 763, Duration: 2 m 9 s` |
| Guard | `dotnet test gk-core/tests/FusionRpg.Guard.Tests -c Release` | `Failed! - Failed: 1, Passed: 579, Skipped: 0, Total: 580, Duration: 7 m 16 s` |

**Three reds, none of them this program's**, each traceable to its owner:

1. `FusionRpg.Server.Tests.CombinationImportTests.A_refused_recipe_is_never_seeded` — `CombinationImportTests.cs`
   is that program's own new file (its task names it), so the red is mid-flight work, not a regression
   here. Filed as a status row in `tasks/strain-splice-host-todo.md`.
2. `FusionRpg.Server.Tests.BaseTypeSocketMaxCorpusTests.A_base_row_above_its_role_ceiling_is_refused_at_load`
   — `BaseTypeSocketMaxCorpusTests` is the class `tasks/data-test-substrate-todo.md` deliberately left on a
   baseline (its T18d note), and the assertion is about socket rows, not notifications.
3. `FusionRpg.Guard.Tests.PlantSideStatusGuardTests.BattleEffects_is_byte_identical_to_its_current_core_baseline`
   — `CAI-guard-1`'s re-pin, tracked on the manager's board. The Guard project is down to ONE red from two
   (`SubprocessPipeDrainGuardTests`, `TVB-F2`'s offender, now passes).

**So Gate G2's suite line reads: measured, not `not_run`** — the default set is 16,922 tests with three
reds, all in other programs' rows, and the live half remains blocked on the missing world-creation route
(`WS-live-1`). That is the strongest form of this acceptance line that exists until those rows land.

**Correction carried forward (see the three fragments amended in this commit):** the "four pre-existing
Core reds" those fragments recorded are **fixed** at this head — the whole Core project is green, and the
three classes in question pass `41/41` on their own filter.

**Attribution corrected 2026-09-21:** the missing real world-creation route is not a product gap and not
world-stage's row — it is the **world-continuity** program's own spec'd deliverable.
`docs/architecture/world-continuity/spec-world-creation.md`’s §Wiring gap records the same fact ("the only
caller of `CreateWorld` is `POST /api/test/world/create`"), and its §Real gap plans the production path
while keeping the test route as a caller of the same service. So `NS5.13` waits on **another lane's
unmerged work**, which is a legitimate external blocker; the program map's §Cross-program dependencies now
carries it as its own row.

## Program close state (2026-09-21) — the consolidated reading

One place recording what the program's close has and what it still owes, after the segments that closed
NS5.11, measured the suite and completed NS6.8's step 6:

| Element | State |
|---|---|
| Gate G1 | green — `NS3.7`, re-proved end to end by `NS5.12` |
| Gate G2's suite line | measured: 16,922 tests, three reds all owned elsewhere (Server: `CombinationImportTests`, `BaseTypeSocketMaxCorpusTests` -> `SSH-RED-1`; Guard: `PlantSideStatusGuardTests` -> `CAI-guard-1`); Core and Data fully green |
| Gate G2's live line | blocked on another lane's unmerged work — the real world-creation route is `world-continuity`'s (`spec-world-creation.md` §Wiring gap / §Real gap) |
| Gate G3's first half | green — `NS6.5` (`Passed! 7/7`; one batch carries `loam.shortfall` + `cache.created` + `cache.decayed`) |
| Gate G3's second half | gated on the resolver's dated acceptance; `NS6.8`'s entry criteria 1–4 are met and the artifacts exist (`surfaces/notices.html`, `pieces/notice-row.html`, `spec-notice-row.md`) |
| Program docs | citation-clean (`0 HIGH` in all classes for every document this program owns) |
| Ledger | `check` exits 0 |

## Feasibility measurement (2026-09-21): can a real commit sequence starve a component?

Two obstacles were asserted for this row: the missing real world-creation route, and "no route can make
a component starve". The second was an assumption; it is now measured, on an isolated instance of this
lane (own port, own data dir, no browser, `FUSIONRPG_SIM=1` so the SIM surface exists at all):

| Step | Command shape | Result |
|---|---|---|
| species roster for an isolated data dir | `FUSIONRPG_DATA=<own dir> dotnet run --project gk-forge/tools/CreatureSpeciesImport -c Release` | `904 species: 904 written, 0 unchanged, 0 deleted` |
| world for the measurement (SIM route) | `POST /api/test/world/create {"templateId":"first-light","worldId":"probe-w5","seed":"7"}` | `{"ok":true,"worldId":"probe-w5","templateId":"first-light"}` |
| 25 real turns | `POST /api/world/probe-w5/commit` for `zomboss`,`wild`,`dave` per turn, then `GET /api/world/probe-w5/turn/{t}?asFaction=dave` | **25 report reads succeeded**, carrying 1/5/12/19/24/31 entries across the turns — so the scan was not blind |
| shortfall scan over those reports | `ConvertTo-Json` + match `loam.shortfall` | **none in 25 turns** |

**What that means for this row, stated as a measurement and not as a conclusion:** the shipped
first-light template does not starve a component within 25 real turns for the committing save's faction,
so the probe cannot reach its `loam.shortfall` subject by simply committing turns. (Not attested beyond
25 turns, and a shortfall for a faction other than the viewer would not appear in this view.) The row
therefore needs either the real creation route **plus** a real starvation path (a player spending loam
over many turns, or a scenario), or a re-worded acceptance.

**Second fact this measurement produced:** on a **default** server the only creation route is not merely
fabricated, it is absent — `/api/test/world/create` answers `405 Method Not Allowed` unless
`FUSIONRPG_SIM=1` is set (`SimFlags.Enabled`, `gk-core/src/FusionRpg.Server/SimFlags.cs`). So a live probe cannot
even borrow the SIM world on a stock host.

## Feasibility measurement 2 (2026-09-21): is there a cheap starvation path?

The 25-turn run produced no shortfall, so the next question was whether a *player command sequence*
could produce one. Tested on the same isolated instance:

| Step | Command shape | Result |
|---|---|---|
| file 10 develop orders on the committing faction's own sector | `POST /api/world/probe-w6/commands {"commanderId":"dave","commands":[{"commandId":"dev-1..10","kind":"develop","sectorId":"homeworld"}]}` | **all ten refused**: `{"ok":false,"reason":"project.unknown"}` — a `develop` order names a **project**, not just a sector, so "develop the sector until upkeep bites" is not a bare command a probe can file |
| three real turns on that world | `POST /commit` per commander, then `GET /turn/{t}?asFaction=dave` | each turn's report carries exactly one entry: **`loam.overflow:50`** |

**What that means, as a measurement:** the shipped first-light world runs a **surplus** for the
committing faction (+50 loam overflow per turn), which is the mechanism behind measurement 1's "no
shortfall in 25 turns". Reaching `loam.shortfall` therefore needs a *designed* scenario — high-development
projects raised until upkeep exceeds production — not a probe-scale script. That is worth stating plainly,
because it changes what this row needs: the real creation route alone is not enough; G2 also needs either
a starvation scenario (an authored world or a scripted project sequence) or an acceptance re-worded to the
in-process evidence NS5.12/NS6.5 already provide.

**Superseded 2026-09-21 by tvb58's Core test-project split:** see the post-split re-measure in `tasks/evidence-fragments/NS-reverify-20260921.md` Addendum 8 — this lane's tests stayed in `gk-core/tests/FusionRpg.Core.Tests` (83/83 on our scope), while the project total is now 12,704 with 2,404 more across eleven split projects.

## Feasibility measurement 3 (2026-09-21): is the subject reachable by ANY player action?

Measurements 1 and 2 ruled out "commit enough turns" and "develop the sector". This one checks every
remaining lever a real player has, against the shipped template's own numbers:

| Reading | Value |
|---|---|
| sectors the committing save owns | **1** (`homeworld`) of the template's six |
| that component | production **50** · upkeep **16** · stock **500** · net **+34** per turn (capacity 300) |
| each turn's report entry | `loam.overflow:50` |
| the only project in the catalog | `raise-development-placeholder`: cost 100 milli, **+1 development**, 1 turn (`gk-core/src/FusionRpg.Core/World/Growth/ProjectCatalog.cs`, the one seed row) |

Lever by lever, with why it cannot starve the component:

| Lever | Verdict |
|---|---|
| commit turns | no: production 50 vs upkeep 16 leaves a 3x surplus and 500 stock (measurement 1: 25 turns, no shortfall) |
| `develop` | no: development adds production (`LoamProduction.cs:64`) as well as upkeep (`LoamUpkeep.cs:101`), and the repo's own A8 note records the yield rate exceeding the upkeep rate — developing makes the sector **richer** |
| raise `danger` | impossible: danger is the only upkeep input no command touches (`WorldCommand.cs`'s kinds: stand-fast, move, clear, claim, stance, sustain, build, cede, bind-warden, raise, develop, assault, load-cargo, unload-cargo) |
| `cede` | no: the save owns exactly one sector, so ceding it removes the whole component rather than shrinking it |
| build / raise / assault | they do not move a sector's loam stock or danger in the starved direction |

**Conclusion, as a measurement rather than an opinion:** on the shipped `first-light` world, **no player
command sequence can produce `loam.shortfall` for the committing save**. The probe's subject therefore
needs an *authored scenario* (a world/template with a sector that cannot pay its upkeep, or an authored
save), not a script. That is the second prerequisite in
`tasks/notification-ssot-probe-runbook.md`, and it is a content task or a manager ruling — not something
this lane can reach from a client.

## Feasibility measurement 4 (2026-09-21): march-and-claim, the last player lever

Measurement 3 checked the levers on dave's *own* component. The one untried path was to create a
**second, starvable component**: march the legion to a remote zero-stock sector (the template's
`ash-waste` danger 2, `black-gate` danger 3, `verdant-shelf` danger 3 all start with no owner and no
stock) and claim it, so it stands alone in a component that cannot pay its upkeep. Played it out:

| Turn | What the report says (dave's view) |
|---|---|
| 0 | `arrival:ember-hollow` (first leg marches) |
| 1 | `arrival:ash-waste` **`halt:zoc:ash-waste`** `sector:ash-waste:none` |
| 2 | `arrival:l-ash-black` (on the lane, movement spent) |
| 3 | `arrival:black-gate` **`halt:zoc:black-gate`** `sector:black-gate:none` |
| 4 | claim filed on `black-gate`; **ownership does not change** (`blackgateOwner=` empty) |
| 5-7 | no ownership change, still `sector:black-gate:none`, still `loam.overflow:50` |

**Read:** every remote sector in this template is **guarded** (the zone-of-control halt names the ground
it stops on) and the claim resolves without taking it, so reaching a starvable component by play would
mean winning a battle first (`clear`/`assault`), then holding a zero-stock sector for a turn — a campaign
sequence, not a probe script, and one that depends on battle resolution rather than on the notification
pipeline this row is about.

**Conclusion (all four measurements together):** on the shipped content there is **no probe-scale player
path** to `loam.shortfall`. The probe needs an authored scenario, which is exactly what the runbook's
second prerequisite says; the two ways forward remain an authored world/save or a re-worded acceptance.
