# species-gear-chain — the brief's "26 open task blocks / 263 workable", decomposed (2026-09-23, lane sgc-6)

| Reading | Command | Result |
|---|---|---|
| the manager's census, run here | `python .claude/cmdc-agents/scripts/convergence-census.py` | `species-gear-chain 25 blocks 0 wip 240 residue 0 nested` at the first reading, **`24 blocks 0 wip 240 residue` mid-lane** (after this lane ticked four of T37's verify boxes), **`25 blocks 0 wip 241 residue` at the very end** (this lane then ADDED two filed rows, `SGC5-F7` and `SGC5-F8`, each contributing one column-0 `- [ ]` row) — a block is *one column-0 `- [ ]` row* (the script's own header says so) |
| the todo's own block rule (heading marker → body `CLOSED <date>` phrase → column-0 `- [ ]`) | scan of `tasks/species-gear-chain-todo.md` | **40 blocks carry unticked column-0 boxes** (a shipped task's boxes are its original contract); of those, **2 are OPEN** |
| the open set | same scan | **T37** (12 unticked boxes at the first reading, **8 re-run at the end of this lane** — this lane ticked 4 of T37's 5 verify boxes) and **T55** (8, unchanged). **T57** is closed by its body phrase (`✅ **CLOSED 2026-09-21 (lane sgc-4).**`) and carries one fence-blocked verify box inside a closed block |

⚠ **Both figures above moved because THIS LANE moved them** (`f41dd5e12` + `1561a9774` measured T37's
verify block, so its unticked column-0 rows went 12 → 8 and the census fell 25 → 24; then `a6d932c3b` +
`7325edd55` filed two rows of its own, taking it back to **25 / 241**). Recorded rather than silently
updated: a figure this lane published, then invalidated by its own work — in either direction — is exactly
the kind that must be re-measured rather than left standing. The OPEN BLOCK set never moved: 2.

So the census's 25 (and the brief's 26) is the line-level artifact RECON-F6 already names: a shipped task
carries 6–10 permanently-unchecked acceptance boxes, so a line count both overstates and misleads. The
block-level truth at this tip is **2**, and neither is workable in-fence:

* **T37** — every in-fence item landed and proven (498 authored armour edges, the regenerated corpus, the
  runtime reader's closure, the real-corpus endpoint case, the replay/produced-instance fix). Open on TWO
  external lines: the `gk-forge/tools/ItemSeedValidator/**` exemption for the 498 `successorOf` rows (DENIED PATH,
  manager plane, ready patch at `tasks/evidence-fragments/T37-validator-successor-edge-exemption.patch`)
  and rule 4's runtime wire, which waits on item module 24 (`equipment-activation`, P7.3/P7.4) — another
  program's unbuilt rows.
* **T55** — `gk-core/scripts/verification-boundaries.v1.json` disposition. Re-measured here: all **191**
  `gk-core/data/tuning/*.json` files resolve to an owner (0 unmapped), so box 1's first half holds; its second half
  ("mapped on day one") needs a glob fallback the row itself calls an anti-pattern, or a guard change —
  and `gk-core/scripts/guard-verification-boundaries.py` is pipeline-guarded. Box 2's nine red seedsmith rows are
  cross-program: **six were SGC5-F1 (fixed and green in this lane, commit `2b99dd4d2`)**, two are SGC5-F2
  (premise false — see `tasks/species-gear-chain-sgc6-f2.md`), one is SGC5-F3 (the committed creature dump,
  out of this fence).

**Conclusion for the lane's step 3 ("the remaining workable rows"):** there is no in-fence unstarted
workable row left. The two owner-ruled rows were the program's blocking edge, and they were the right first
target: SGC5-F1 is done; SGC5-F2 needs an erratum because its ruled mechanism cannot exist.
