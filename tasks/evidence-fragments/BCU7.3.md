# BCU7.3 — gui-lego P2/P3/P4, all already done

Live-verified via SanctumStage.tsx: CreaturesLayer, RelicsLayer, CommandersLayer, FusionLayer,
PactsLayer, ExpeditionsLayer, AlmanacLayer, ChronicleLayer all real, lazy-loaded, wired. Remaining
Actor tabs (Status/Elements/Kit via CatalogTabs.tsx, Paths via PathsTab.tsx) also real.

Corrected both menu-refactor-queue.md's priority table and gui-lego-todo.md's mirrored bullets,
which independently carried the same stale claims. Only P4 · Notices / P4 · Builds stay genuinely
open (unchanged, already correctly gated).

```
$ python scripts/audit-doc-citations.py --scope docs/architecture/gui-lego/menu-refactor-queue.md --strict
0 HIGH
$ python scripts/audit-doc-citations.py --scope tasks/gui-lego-todo.md --strict
0 HIGH
```
