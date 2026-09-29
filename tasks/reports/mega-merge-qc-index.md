# Mega-merge QC — index and verdict

**QC date:** 2026-09-24 · **Head:** features/mega-merge @ `11fe6306b` (+4 manager merges,
+2 QC fix commits) · **Method:** solo, no agents, no live game (owner charter).
**Scope covered:** recent merges (cai3, sgc-6, tvb60, item-2, 4 manager slices) + the rest
by risk: keepverse, empire, notification, strain, party-dungeon, ip-censor, world-stage,
rpg-sim, seedsmith, expeditions, web build, Data/Server full, Core group sweep, hosts.

## Per-program verdicts (each with its own report file + executed evidence)

| # | Report | Verdict |
|---|---|---|
| 1 | `mega-merge-qc-1-combat-ai.md` | GREEN + 2 routed (both fixed in fix cycles 2 & 7) |
| 2 | `mega-merge-qc-2-species-gear-chain.md` | GREEN |
| 3 | `mega-merge-qc-3-test-verification-boundary.md` | GREEN |
| 4 | `mega-merge-qc-4-item-2.md` | GREEN |
| 5 | `mega-merge-qc-5-manager-slices.md` | GREEN (4 slices re-verified on HEAD) |
| 6 | `mega-merge-qc-6-keepverse-split.md` | GREEN |
| 7 | `mega-merge-qc-7-empire-progression.md` | GREEN |
| 8 | `mega-merge-qc-8-notification-ssot.md` | GREEN |
| 9 | `mega-merge-qc-9-strain-splice-host.md` | GREEN (SSH6.8 fixed in fix cycle 8) |
| 10 | `mega-merge-qc-10-party-dungeon.md` | GREEN |
| 11 | `mega-merge-qc-11-ip-censor.md` | GREEN (T16 fixed in fix cycle 9) |
| 12 | `mega-merge-qc-12-world-stage.md` | GREEN |
| 13 | `mega-merge-qc-13-rpg-simulator.md` | GREEN after fixing 1 real drift (`3c930595d`) |
| 14 | `mega-merge-qc-14-seedsmith-corpora.md` | GREEN + 2 pre-existing routed |
| 15 | `mega-merge-qc-15-expeditions-flaky.md` | **RED, cause proven** (Almanac-window vs parallel classes; product exonerated; routed) |
| 16 | `mega-merge-qc-16-web-build.md` | GREEN |
| 17 | `mega-merge-qc-17-data-server-full.md` | GREEN (Data 1783, Server 858) |
| 18 | `mega-merge-qc-18-core-group-sweep.md` | GREEN 67/68 (Expeditions excepted, see 15) |
| 19 | `mega-merge-qc-19-hosts-builds.md` | GREEN where buildable; Injector environmental |

## Whole-tree gates

- `test-fast.ps1 -AllDefault`: red on exactly the Expeditions flakiness (QC 15) — the only red
  leg; everything else in the profile green (Core 9746, Data 1783, Server 858, E2E 293).
- `run-guards.ps1 -Tier ci`: 24/25 — sole red `doc-citations`, pre-existing D3 drift in an
  untouched spec doc, identical before/after every merge in this QC.
  **FIXED in QC fix cycle 6 (2026-09-24):** the "275 D3 / 195 HIGH" reading was almost entirely a
  false positive — an untracked, unignored machine-local `tmp/bep-verify/` deploy-staging copy
  shadowed `data/**` paths, so `endswith(ref)` matched its duplicates and every full-path citation
  went ambiguous. Excluding `tmp/` (now gitignored) drops D3 to **56, all LOW in `docs/research/`**,
  HIGH 0. `guard-doc-citations.ps1` exits 0. The residual 56 are genuine prior-art basename
  collisions in `docs/research/`, exempt from the strict gate by the audit's own rule.
- `npm run test:e2e` (commander-surface): 10/10 after the rename ripple fix.

## What this QC caught and fixed (2 commits)

- `3c930595d` — unique-actor fixture re-bless (SE4.31 empireId drift). A red no single lane could see.
- `43f7127c5`, `1ff07a9f3`, `e2ede8ae6`, `dd606368c` — the four slices were merged under the
  previous goal; this QC re-verified all four on HEAD (QC 5).

## Explicitly not covered / deferred (owner decisions on record)

- T16: **fixed in fix cycle 9** — see QC 11.
- SSH6.8: **fixed in fix cycle 8** — see QC 9.
- T12 raised-floor clause: **fixed in fix cycle 10** — the caller wire was re-landed; the reopen
  diagnosis was a test-fixture bug (the shared `WildSpecies` fixture resolved to a Sunwoven species,
  structurally excluded, so the floor was never reached). See QC 5 and
  `tasks/reports/creature-seed-rank-t12.md`.
- Injector build + live-game probes: environment has no game dir; excluded by charter.
- `test_items_adapter` noted passing; completeness-file reds pre-existing.
