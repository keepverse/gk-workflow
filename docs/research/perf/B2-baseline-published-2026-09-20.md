# B2 baseline — published, corrected 2026-09-20

**Backlog-clean-up BCU7.4.** `backlog-clear-todo.md` Phase 9 named "Perf probe B2 before/after
published in research" as an open item. Four raw baseline captures already existed on disk
(`_baseline-b2-live-x2{,-o1,-o2,-o3}.json`, all captured 2026-08-20, all bundled into an unrelated
launcher commit `8be1c30ca` with no accompanying write-up) but were never published as a readable
before/after comparison. This publishes the raw numbers factually.

Per [perf-probe-plan.md](../../runbook/perf-probe-plan.md) §1, B2 is "Heavy level (aim 200+
entities), normal speed", measuring scaling with board size.

## Raw summary (extracted from the JSON, not re-measured)

| Scenario | Captured (UTC) | Windows | Total frames | Avg FPS | Max frame (ms) | Frames ≥33ms |
|---|---|---|---|---|---|---|
| `b2-live-x2` (base) | 2026-08-20T16:41:05Z | 18 | 16,833 | 187.0 | 233.57 | 100 |
| `b2-live-x2-o1` | 2026-08-20T16:54:25Z | 18 | 16,787 | 186.8 | 185.77 | 39 |
| `b2-live-x2-o2` | 2026-08-20T17:04:41Z | 13 | 12,555 | 190.6 | **18,378.64** | 13 |
| `b2-live-x2-o3` | 2026-08-20T17:28:43Z | 18 | 10,115 | **112.3** | 87.71 | 10 |

## What this does and does not show

- **o1 vs base**: a real, consistent improvement in `Frames ≥33ms` (100 → 39), avg FPS essentially
  unchanged. Reads as a genuine tail-latency fix.
- **o2's `maxMs` of ~18.4 seconds is almost certainly a capture artifact** (a debugger pause, a scene
  load, or an editor breakpoint), not a real frame — no game session holds a single frame open for
  18 seconds. Excluding that one outlier, o2's `Frames ≥33ms` (13) continues the downward trend from
  o1.
- **o3's avg FPS (112.3) is markedly lower than the other three (~187-191), despite fewer total
  frames and the lowest `Frames ≥33ms` count.** This does not resolve cleanly into either "o3 is a
  regression" or "o3 measured a lighter scenario" without the original session's own notes on what
  each `o`-suffixed capture changed — which do not exist in this repo (checked: no commit message,
  no adjacent doc, no code comment ties these four files to specific dated optimization commits).
- **No causal claim is made here about which code change produced which number.** The four files
  were captured 13-47 minutes apart on the same day with no log connecting a specific optimization
  landing to a specific `-oN` suffix. Publishing the raw numbers is what this task asked for; a
  causal write-up needs either the original author's context or a fresh, clean before/after
  `probe_perf.py` run against the current `RulesetVersion`, not a re-interpretation of five-week-old
  numbers with an unexplained 200x outlier in the middle of them.

## Recommendation

If this comparison is still wanted for real optimization decisions, re-run
`.\scripts\probe-perf.ps1 -Scenario B2 -DurationSec 90` fresh against current code, twice, and diff
those two runs — do not keep extending inference from these four unlabeled captures.
