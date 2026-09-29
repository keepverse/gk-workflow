# Anchor: species-gear-chain

Map: `docs/architecture/species-gear-chain-map.md`
Plan: `tasks/species-gear-chain-plan.md` · Todo: `tasks/species-gear-chain-todo.md`
Specs: `docs/architecture/species-gear-chain/**` — the active module per the todo row
Session: `species-gear-chain-4` (worktree `.claude/worktrees/cmdc-sgc-4`, branch `cmdc/sgc-4`) · Paths: `gk-core/src/FusionRpg.Core/Items/**`, `gk-core/src/FusionRpg.Core/Stats/**`, `gk-core/src/FusionRpg.Server/**`, `gk-core/src/FusionRpg.Data/**`, `gk-core/src/FusionRpg.Contracts/**`, `gk-web/web/fusion-rpg-web/**`, `gk-forge/tools/seedsmith/**`, `gk-data/packs/fusion/data/seed/items/**`, `gk-data/packs/fusion/data/seed/loot/**`, `gk-data/packs/fusion/data/seed/atoms/generated/**`, `gk-core/data/tuning/**`, `tests/**`, `docs/architecture/species-gear-chain/**`, `tasks/**`
Standards: `PRINCIPLES.md` + the DESIGN-GATE §1 row for every subsystem this program touches + the
  `decisions.md` locks it cites. **The lane's own session reads them at its first task** — anchor setup
  did not (writing eight subsystems' standards into this file would claim a reading that never happened).
Open rows: **4 open task blocks of 66**, measured 2026-09-22 by the todo's own block rule (the
  reconciliation's `tasks/reports/backlog-reconciliation-20260921.md` §1 method: heading marker → body closure
  phrase → column-0 `- [ ]` → `- [x]`): **T37, T55, T59, T60**. The line-level count is deliberately NOT
  published here — it is non-indicative (286 of this file's unticked lines sat inside closed blocks at the
  reconciliation, and the earlier line-level reading named **T32/T34, which are done**). Where the four stand:
  - **T37** — every in-fence item landed and proven (498 authored armour edges + the regenerated corpus, the
    runtime reader's closure, the real-corpus endpoint case, the replay/produced-instance fix); blocked on TWO
    EXTERNAL items: the `gk-forge/tools/ItemSeedValidator/**` exemption for the 498 `successorOf` rows (manager plane;
    patch `tasks/evidence-fragments/T37-validator-successor-edge-exemption.patch`) and rule 4's runtime wire
    (E9's per-atom power).
  - **T55** — TVB-owned. Both boundary-mapping lines now RESOLVE (measured: `tuning-set-topology`;
    `seed-items-corpus` + `seed-items-validator-seam`); the seedsmith boundary's 17 `UNEXPECTED FAILURE`s, the
    missing glob fallback and the cwd-portability item belong to the registry owner.
  - **T59** — routing done (2 false positives corrected, `items.v1.json` closed and re-landed after a merge
    reverted the wiring, 2 already filed). The 3 remaining dark domains are the achievements, actions and
    movement/board programs' — their todos are outside this fence.
  - **T60** — prose-only classification artefact, NOT queued work: its durability half landed with T37
    (`successorDurabilityCurrent`, `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Workbench.cs:282`, `:348`); its potential
    half needs a spec read before anyone calls it closed. Recorded open, not worked around.
  Also open and not task blocks: **RECON-F6** (a routed filer row; the metric fix is in `scripts/**`) and the
  checkpoint boxes reading "Review with owner before Phase 3/4/5" / "Ready for owner sign-off". **T57** is done
  with ONE documented fence-blocked verify box (the active record omits `gk-core/tools/tuning/**`). **T32, T38 and T49
  are closed, not queued** — re-verified at the merged tip 2026-09-22: Core.Items `~ItemUpgrade` **32 passed**;
  Core.Items `~Material|~CostClass|~CraftRisk|~Enhance` **180 passed**; Data `~MaterialSpend` **12 passed**;
  `CraftAssuranceHorizonReportTests` **5 passed**; `verify-change` on both rows' paths **EXIT 0**. No tuning value
  moved: `materials.v6` is still the latest and still the host reader (`SocketTuningFiles.Materials`),
  `craftWearPerAttemptMilli` is still 50, `craft-assurance` and `enhancement` are still v1, and
  `deployment-hierarchy` v5 differs from v4 only by T37's `upgrade` potential row.
Queue (hard edges first): **empty of unstarted in-fence rows.** The lane's next actionable work is the two
  manager-plane unlocks above (re-add `gk-core/tools/tuning/**` to `tasks/sessions/species-gear-chain-4.json`; apply the
  validator patch). T27 ran in its own lane (`sgc-2`) and is closed at the merged tip.
Next: the manager-plane pair above; otherwise report rather than invent work — every remaining block is external
  or owner-gated.
Peers:
| `strain-splice-host` | `tasks/strain-splice-host-anchor.md` | sockets, combinations, helm host | the material table |
| `seed-corpus` | `tasks/seed-corpus-anchor.md` | the generated species/gear corpus | the drop + set tables |
Drift gates: `python scripts/session-boundary-check.py` ·
  `.\scripts\verify-change.ps1 -Paths <every changed path> -Session species-gear-chain-4`
Evidence: `tasks/evidence-fragments/<task-id>.md`, one per task (`| Criterion | Command | Result | Artifact |`)
Ledger: `tasks/species-gear-chain-ledger.jsonl` — append-only run state, written only through
  `python gk-core/scripts/anchor-ledger.py tasks/species-gear-chain-ledger.jsonl ...`; `check` must exit 0
Verify: each task's own Verify line (focused filter + its guard). The full suite belongs to CC8 or this
  program's final checkpoint — never to an ordinary task.
