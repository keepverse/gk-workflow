# CV.2 — golden re-bless register

Register: `tasks/summoner-convergence-todo.md` → "Golden re-bless register (CV.2, H1 order)".

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| every H1 mover listed with cause and hash, in H1 order | `git log --oneline --diff-filter=M -- '*Golden*' '*golden*' \| head -n 3` | `a10cd2f95` (merge bookkeeping), `eceb08f1a` SP6.1 (the layer re-bless), `17a15a7d4` SP6.0 (H7 publish) — plus `AE1.5` outside that glob, found by `git show` | the register table, rows 1–6 |
| `AE1.5` moved the battle goldens in its own commit | `git show --stat --format= 04b8daa0 \| grep -cE "Golden\|golden\|trace"` | 5 (BattleGoldenTests + 4 trace fixtures) | register row 3 |
| `SP6.1` is the layer re-bless and carries its artifact | `git show --stat --format= eceb08f1 \| grep -c baseline-goldens` | 1 | register row 5 |
| the two earliest movers recorded a no-move instead of a silent pass | `git show --stat --format= 75553de4 a4fc08d2` | both touch only `tasks/evidence-fragments/ST2.3.md` / `ST1.3.md`, the ledger and the session record — no golden file | `tasks/evidence-fragments/ST2.3.md`, `ST1.3.md` |
| `SP1.2` C1 is a defect correction, not a re-bless | `git show --stat --format= 283ab83b` | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs` + its test bootstrap; no golden | register row 4 |
| no re-bless landed out of order (so none is reverted) | dates vs H1 sequence: `ST2.3`/`ST1.3` 2026-09-18 → `AE1.5` 2026-09-19 → `SP1.2` fix 2026-09-19 → `SP6.1` 2026-09-20 | monotone in H1's order | this fragment |
| the two H7 publishes are not read as causeless golden moves | `git show --stat --format= 17a15a7d 243b2aa6` | `SP6.0` publishes `read.layerWeightMilliByScope` with its reader switch; `SE1.4` publishes `aptitudes.v9` through `publish.py` removal ops — both recorded as publishes under the register | register note |
| the still-unlanded H1 rows are registered as pending, not as moved | `tasks/empire-progression-todo.md` rows `EP4.18`, `EP2.7`, `EP2.13`+`EP2.14` | open (wave D / wave 2 not built) | register rows 6 and the independent table |
