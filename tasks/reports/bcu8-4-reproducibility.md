# Lane `cmdc-bcu8-4` — every committed reading reproduces from its own command

The brief's rule is that the orchestrator re-runs this lane's commands and a mismatch discards the run, so
this is the lane's own integrity check: each artefact below was regenerated at `2c4f5bd4a` and compared
against the committed copy. Nothing under `data/` is written by any of them.

| artefact | command | re-run result |
|---|---|---|
| `bcu2-10-readings.json` | `PYTHONPATH=gk-forge/tools/seedsmith python tasks/reports/bcu2-10-readings.py --round 1` | **identical** (only `repoHead`) |
| `bcu2-10-readings-round-2.json` | `… --round 2` | **identical** (only `repoHead`) |
| `ISG-gap-2-per-partition.json` | `PYTHONPATH=gk-forge/tools/seedsmith python tasks/reports/bcu2-11-partition-key-map.py` | **identical** (only `repoHead`) |
| `bcu2-12-vintage-reading.json` | `python tasks/reports/bcu2-12-vintage-reading.py` | **identical** (only `repoHead`) |
| `bcu2-12-j9-progress-census.json` | `python tasks/reports/bcu2-12-j9-progress-census.py` | **identical** (only `repoHead`) |
| `bcu2-12-namegate-probe.json` | `python tasks/reports/bcu2-12-namegate-probe.py` | **identical** (only `repoHead`) |
| `bcu2-12-j10-review-gate.json` | `python tasks/reports/bcu2-12-j10-review-gate-probe.py` | **identical, byte for byte** (its temp dir is removed and absent from the recorded reasons) |
| `bcu2-13-selector-reading.json` | `python tasks/reports/bcu2-13-selector-reading.py` | **identical** (only `repoHead`) |
| `bcu2-13-attacktempo-census.json` | `python tasks/reports/bcu2-13-attacktempo-census.py` | **identical** (only `repoHead`) |
| `bcu2-12-tree-census.txt` | `PYTHONPATH=gk-forge/tools/seedsmith python -m seedsmith trees census` | **identical** |
| `bcu2-12-treebinder-check.txt` | `dotnet run --project gk-forge/tools/TreeBinder -c Release -- --check` | **identical** — with one caveat below |

## The one caveat, stated rather than left to bite a re-runner

`dotnet run` prepends **build output** when it has to rebuild, and this tree emits two warnings
(`EffectAtomCatalog.Generated.cs(219,67) CS8669`, `CaptureAction.cs(138,9) CS0162`) on a rebuild. Observed
once during this audit: the raw transcript then differed by exactly those two leading lines while its
tree-binder content was unchanged. Filtering to the lines the reading is about

```
grep -E "^tree-binder:|^  REFUSED|^STALE"
```

yields **1,162 identical lines** either way. So a re-runner comparing the raw file should either expect the
warnings or filter; nothing in the reading itself is unstable, and the same run is byte-stable when no
rebuild happens.

## What this does *not* cover

The two command **results** that are not files in this lane: `seedsmith check --family PassiveTree`
(readings are quoted in the reports, re-runnable in ~1 min) and the four `verify-change.ps1` /
guard invocations (re-run by the orchestrator directly). Both were recorded with their printed numbers in
the register and the reports rather than as transcripts.
