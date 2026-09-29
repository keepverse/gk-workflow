# ip-censor release readiness — reading of 2026-09-23

**Program:** `ip-censor` · **Lane:** `ip-censor-2` · **Row:** T23 (part 1 — the reading)
**Verdict: NOT RELEASE-READY.** Four of the five rows plan §9 gates on are blocked outside this lane's
allowed paths or on owner input, so this file records the reading each item can already be given,
names the blocking owner, and states plainly which item has no reading yet. Nothing here is a suite
assertion: the gate's exit code is a reading, never a test (`ip-censor-ideal.md`, principle 3).

---

## 1. Plan §9, item by item

| §9 item | Verdict | What blocks it, and who owns the unblock |
|---|---|---|
| 1. `python -m ipcensor.report scan --fail-on enforced` exits 0 on the release commit | **NOT MET** — exits **1** | 281 enforced findings, none of them unexplained: **277 are identity-rename's** (R9's player guide, its locale catalogs, and its `default-commanders.v1.json` row) and **4 are this program's T16** (IC-4.1). This red gate is the gate working, exactly as plan §6 says. Owner: identity-rename (its Phases 3–4) + ip-censor T16 |
| 2. IC-4.1: the regenerated node carries the new `promptVersion` and the scan reports no `overwatch` finding under `gk-data/packs/fusion/data/seed/passive-tree/**` | **NOT MET** | `gk-data/packs/fusion/data/seed/passive-tree/nodes/command.json:538` still holds `"name": "Overwatch Protocol"` (and `:539` its `nameKey`), `promptVersion` is still `tree-language/3`, and the same row sits in the generator ledger. T16 is blocked on `gk-forge/tools/seedsmith/**` and `gk-data/packs/fusion/data/seed/passive-tree/**` (outside this lane's paths) and on the local model endpoint. Owner: T16's own lane |
| 3. IC-4.2: T19's import-output test is green **and** T19b's migration and id-closure tests are green | **NOT MET** | Neither exists yet: T19 needs `gk-forge/tools/seedsmith/**`, `gk-data/packs/fusion/data/seed/creatures/**` and `gk-data/packs/fusion/data/generated/**`; T19b additionally needs `gk-core/src/FusionRpg.Data/**` and `gk-core/tests/FusionRpg.Data.Tests/**`; both also wait on the owner's replacement strings, because the map's keys are authored by the owner, never by this program. The trace and the validator are landed (`tasks/ip-censor/jackson-trace.md`, `registry.parse_import_renames`). Owner: the fence grant + the owner's strings |
| 4. The release workflow runs the gate before publishing (T12) | **NOT MET** | `.github/workflows/release.yml` carries no ip-censor step, and `gk-core/tests/FusionRpg.Guard.Tests/WorkflowExitCheckTests.cs`'s command-prefix list does not yet recognise `python -m ipcensor.report scan `. Both are outside this lane's allowed paths. The enforcement-registry row (the one part of T12 that *is* in scope) deliberately rides with the step: a register entry claiming an enforcement that does not exist yet would be a false entry, not progress. Owner: the fence grant for `release.yml` + `gk-core/tests/FusionRpg.Guard.Tests/**` |

Five rows in the plan's own dependency list decide these four items: **T12** (item 4), **T16**
(item 2), **T19 + T19b** (item 3), **T22** (feeds item 1 through any further admitted marks), and
**T21** (the dataset round; item 1 does not wait on it while no candidate is admitted). All five are
blocked on paths outside this lane or on owner input; none is blocked on work this lane could do.

## 2. The gate reading itself

```
cd D:/Works/source/plant-vs-zombie-rise-of-summoner/.claude/worktrees/cmdc-ip-censor-2
python -m ipcensor.report scan --format json --fail-on enforced      # PYTHONPATH=gk-core/tools/ip-censor
RELEASE_GATE_EXIT=1
```

- **6,848 findings** over the tracked tree; **281 enforced**; exit code **1** (findings in an enforced
  bucket), which is the gate's designed behaviour, not a tool failure — a non-zero exit from a *crash*
  would be the code defect (IC-3).
- Enforced by mark: `dr-zomboss` 207, `pvz` 58, `crazy-dave` 6, `penny` 6, `overwatch` 4.
- Nothing unowned: every one of the 281 resolves to one of two owners (§3). CP3's audit rule — an
  enforced finding with no owner is a classifier defect — is satisfied.
- The rest of the tool's own readings, taken at the same head: `python -m pytest -q` in
  `gk-core/tools/ip-censor` → **218 passed**; `scripts/run-guards.ps1 -Tier ci` → **21 guards, 0 red**;
  `gk-core/scripts/guard-verification-boundaries.py` → **OK**, with the `ipcensor` pytest lane registered.

## 3. Residue list — every remaining enforced finding, with its owner

67 distinct paths, 281 findings. Owner by path: **identity-rename** for the player guide, the locale
catalogs and the commanders registry (277); **ip-censor T16** for IC-4.1 (4).

| enforced | path | owner |
|---:|---|---|
| 4 | `gk-data/packs/fusion/data/seed/commanders/_registry/default-commanders.v1.json` | identity-rename |
| 5 | `docs/guide/README.md` | identity-rename |
| 6 | `docs/guide/features.md` | identity-rename |
| 2 | `docs/guide/glossary.md` | identity-rename |
| 1 | `docs/guide/how-you-play.md` | identity-rename |
| 4 | `docs/guide/mechanisms/README.md` | identity-rename |
| 1 | `docs/guide/mechanisms/_content/actor-meters.json` | identity-rename |
| 2 | `docs/guide/mechanisms/_content/aptitudes.json` | identity-rename |
| 8 | `docs/guide/mechanisms/_content/counter-development.json` | identity-rename |
| 8 | `docs/guide/mechanisms/_content/fog-of-war.json` | identity-rename |
| 3 | `docs/guide/mechanisms/_content/lawn-match.json` | identity-rename |
| 1 | `docs/guide/mechanisms/_content/layer-rail.json` | identity-rename |
| 1 | `docs/guide/mechanisms/_content/map-orders.json` | identity-rename |
| 3 | `docs/guide/mechanisms/_content/save-select.json` | identity-rename |
| 3 | `docs/guide/mechanisms/_content/siege.json` | identity-rename |
| 2 | `docs/guide/mechanisms/_content/species-builds.json` | identity-rename |
| 1 | `docs/guide/mechanisms/_content/specimen-fusion.json` | identity-rename |
| 1 | `docs/guide/mechanisms/_content/system-settings.json` | identity-rename |
| 7 | `docs/guide/mechanisms/_content/virtual-turns.json` | identity-rename |
| 2 | `docs/guide/mechanisms/_content/world-events.json` | identity-rename |
| 9 | `docs/guide/mechanisms/_content/world-map.json` | identity-rename |
| 9 | `docs/guide/mechanisms/_content/zomboss-commander.json` | identity-rename |
| 9 | `docs/guide/mechanisms/_gen-stubs.ps1` | identity-rename |
| 1 | `docs/guide/mechanisms/actor-meters.md` | identity-rename |
| 2 | `docs/guide/mechanisms/aptitudes.md` | identity-rename |
| 9 | `docs/guide/mechanisms/counter-development.md` | identity-rename |
| 10 | `docs/guide/mechanisms/fog-of-war.md` | identity-rename |
| 3 | `docs/guide/mechanisms/lawn-match.md` | identity-rename |
| 1 | `docs/guide/mechanisms/layer-rail.md` | identity-rename |
| 6 | `docs/guide/mechanisms/local-control-room.md` | identity-rename |
| 1 | `docs/guide/mechanisms/map-orders.md` | identity-rename |
| 3 | `docs/guide/mechanisms/save-select.md` | identity-rename |
| 3 | `docs/guide/mechanisms/siege.md` | identity-rename |
| 2 | `docs/guide/mechanisms/species-builds.md` | identity-rename |
| 1 | `docs/guide/mechanisms/specimen-fusion.md` | identity-rename |
| 1 | `docs/guide/mechanisms/system-settings.md` | identity-rename |
| 8 | `docs/guide/mechanisms/virtual-turns.md` | identity-rename |
| 2 | `docs/guide/mechanisms/world-events.md` | identity-rename |
| 10 | `docs/guide/mechanisms/world-map.md` | identity-rename |
| 9 | `docs/guide/mechanisms/zomboss-commander.md` | identity-rename |
| 2 | `docs/guide/relics-and-builds.md` | identity-rename |
| 13 | `docs/guide/site/index.html` | identity-rename |
| 1 | `docs/guide/site/mechanisms/actor-meters.html` | identity-rename |
| 2 | `docs/guide/site/mechanisms/aptitudes.html` | identity-rename |
| 9 | `docs/guide/site/mechanisms/counter-development.html` | identity-rename |
| 10 | `docs/guide/site/mechanisms/fog-of-war.html` | identity-rename |
| 4 | `docs/guide/site/mechanisms/lawn-match.html` | identity-rename |
| 1 | `docs/guide/site/mechanisms/layer-rail.html` | identity-rename |
| 4 | `docs/guide/site/mechanisms/local-control-room.html` | identity-rename |
| 1 | `docs/guide/site/mechanisms/map-orders.html` | identity-rename |
| 3 | `docs/guide/site/mechanisms/save-select.html` | identity-rename |
| 3 | `docs/guide/site/mechanisms/siege.html` | identity-rename |
| 2 | `docs/guide/site/mechanisms/species-builds.html` | identity-rename |
| 1 | `docs/guide/site/mechanisms/specimen-fusion.html` | identity-rename |
| 1 | `docs/guide/site/mechanisms/system-settings.html` | identity-rename |
| 8 | `docs/guide/site/mechanisms/virtual-turns.html` | identity-rename |
| 2 | `docs/guide/site/mechanisms/world-events.html` | identity-rename |
| 10 | `docs/guide/site/mechanisms/world-map.html` | identity-rename |
| 12 | `docs/guide/site/mechanisms/zomboss-commander.html` | identity-rename |
| 10 | `docs/guide/the-game.md` | identity-rename |
| 2 | `docs/guide/the-lawn.md` | identity-rename |
| 3 | `docs/guide/the-loops.md` | identity-rename |
| 5 | `docs/guide/the-rift.md` | identity-rename |
| 3 | `gk-web/web/fusion-rpg-web/src/i18n/locales/en/messages.po` | identity-rename |
| 1 | `gk-web/web/fusion-rpg-web/src/i18n/locales/pseudo/messages.po` | identity-rename |
| 2 | `gk-data/packs/fusion/data/seed/passive-tree/_runs/tree-language.ledger.json` | **ip-censor T16** |
| 2 | `gk-data/packs/fusion/data/seed/passive-tree/nodes/command.json` | **ip-censor T16** |

The line-level list for any path above is in the scan JSON the gate wrote (the release step pipes
`--format json` to the runner) and in the committed `tasks/ip-censor/report.md`; this table is the
owner ledger, not a replacement for it.

**Report-only residue, deliberately not listed above.** The same scan reports **6,567** findings that
do not block a release: `code-identifier` 3,389, `deliberate-identity` 2,583,
`docs-prose-citation` 549, `registry-self` 2, and **44** hits on an enforced surface whose mark
declares no scope for it (the `pvz`/`dr-zomboss` hits in `gk-forge/tools/seedsmith/**` code comments and
identifiers that IC-1b's "in scope on player-facing surfaces only" keeps report-only — 325
surface-enforced minus the 281 enforced). They do not block by IC-3, and `spec-scan.md` §Objective
keeps attributed `docs/research/**` citations report-only on purpose. The one report-only class worth
naming is the generated/upstream material under `gk-data/packs/fusion/data/seed/creatures/**` and the item corpus, whose
real-person tokens are the subject of `tasks/ip-censor/jackson-trace.md`; whether that tree should be
a `player-prose` surface is an open owner question recorded there (§6b), not a residue item here.

## 4. What this file does not have, and why that is not a shortcut

T23's `Do` also names the program's single full-suite run (`test-fast.ps1 -AllDefault`, plus
`$PY gk-core/tools/ip-censor/tests -q` and `$SS gk-forge/tools/seedsmith/tests -q`), because the program's last
checkpoint crosses `tools/`, `data/`, `.github/` and possibly `gk-core/src/FusionRpg.Data`. **That run is
deferred, deliberately:** the checkpoint T23 gates on has not arrived — four of the five rows that
decide §9 are still blocked, so a full-suite reading now would measure a tree this program is not
finished changing, and it would compete with the lanes that can actually finish them. The readings in
hand are the ones the tool and the guards can give today, and they are recorded in §2.

## 5. What the next lane needs

1. **The fence grant** for `.github/workflows/release.yml` and
   `gk-core/tests/FusionRpg.Guard.Tests/WorkflowExitCheckTests.cs` (T12), `gk-forge/tools/seedsmith/**` (T14–T16, T18
   part 2, T19), `gk-data/packs/fusion/data/seed/passive-tree/**` (T16), `gk-data/packs/fusion/data/seed/creatures/**` + `gk-data/packs/fusion/data/generated/**`
   (T19), and `gk-core/src/FusionRpg.Data/**` + `gk-core/tests/FusionRpg.Data.Tests/**` (T19b).
2. **The owner's replacement strings** for `data/seed/ip-censor/_registry/import-renames.v1.json`
   (T18/T19/T19b — the validator is landed and tested, so this is a data change when they arrive), and
   the owner's ruling on T22's candidate source.
3. **`tasks/sessions/**`**, or a pre-created `tasks/sessions/<lane>.json`: without it
   `verify-change.ps1 -Session` cannot run at all, and this lane had to use `-AllowUnscoped`.
4. **The downloaded USPTO export** for T21's first real import round.
