---
name: seedsmith
description: >-
  Operate the Seedsmith content-generation and seed-corpus health toolkit (gk-forge/tools/seedsmith).
  Prefer `items fill` / `.env` defaults for resume-and-fill; use when validating corpora,
  running generation pipelines, or configuring local LLM (LM Studio). Triggered by /seedsmith.
---

# Seedsmith — Corpus Health & Generation Runbook

`seedsmith` is the offline content-generation, measurement, and validation toolkit for Rise of Summoner, located in `gk-forge/tools/seedsmith`.

**Agent default:** configure `tools/seedsmith/.env`, then use the one-liners in §1. Do **not** retype `--endpoint`, `--out-dir`, or `--allow-production-tree` on every call when `.env` already has them.

---

## 1. Operator one-liners (start here)

```powershell
cd gk-forge/tools/seedsmith

# Resume / fill missing item subjects across all kinds (write implied)
# Always bound the first live run — unbounded set/charm/combination need --limit or --full
python -m seedsmith items fill --limit 1 --max-partitions 1 --count 1 --batch-size 1 --dry-run
python -m seedsmith items fill --limit 1 --max-partitions 1 --count 1 --batch-size 1

# Single kind (still needs --write; endpoint/out-dir come from .env)
python -m seedsmith items generate --kind set --write
python -m seedsmith items generate --kind material --write

# Health
python -m seedsmith check gk-data/packs/fusion/data/seed/items --adapter items
python -m seedsmith items validate --deps

# Demons (long runs — preflight first)
python -m seedsmith demons preflight
python -m seedsmith demons run status
```

### Agentic decision tree

1. **Inspect** — `items fill --dry-run` or `items generate --kind X` (no `--write`).
2. **Validate deps** when touching combinations / recipes — `items validate --deps`.
3. **Fill / resume** — `items fill` (or single-kind `--write`). Re-run is resume-safe via `RunLedger`.
4. **Measure** — `check` / `report`.
5. **Never** invent magnitudes (LLM = identity only). **Never** `--ignore-ledger` / `--overwrite all` unless the owner asked.

---

## 2. `.env` contract (truthful)

File: `tools/seedsmith/.env` (gitignored). Copy from `.env.example`.

| Key | Purpose |
|---|---|
| `SEEDSMITH_LLM_ENDPOINT` | Live chat-completions URL (LM Studio default works) |
| `SEEDSMITH_LLM_MODEL` | Model id from `/v1/models` |
| `SEEDSMITH_LLM_TIMEOUT` / `_ATTEMPTS` / `_RETRY_DELAY` / `_MAX_HEAL` / `_MAX_TOKENS` | Transport / heal |
| `SEEDSMITH_ALLOW_PRODUCTION_TREE` | `1` → allow writes under `gk-data/packs/fusion/data/seed/items/` and default out-dirs |
| `SEEDSMITH_ITEMS_OUT_DIR` | Optional override for set/charm/combination out-dir |

Resolution order for LLM keys: built-in defaults → `seedsmith.toml` → `.env` (wins). CLI `--endpoint` / `--model` win over `.env` when non-empty.

`load_config()` finds `.env` as: explicit path → **CWD** `.env` → **`tools/seedsmith/.env`** (so repo-root runs still work).

After this setup, these are enough:

```powershell
python -m seedsmith items generate --kind set --write
python -m seedsmith items fill
```

`--write` stays explicit on `generate` (safety). `fill` implies write.

---

## 3. Quick Start & Execution

```powershell
cd gk-forge/tools/seedsmith
python -m seedsmith <command> [options]

# Or from repo root:
$env:PYTHONPATH = "gk-forge/tools/seedsmith"
python -m seedsmith <command> [options]
```

### Run Tests
```powershell
python -m pytest gk-forge/tools/seedsmith/tests/test_cli.py -v
python -m pytest gk-forge/tools/seedsmith/tests/test_items_fill_ux.py -q
```

---

## 4. Command Cheatsheet

| Task | Command |
|---|---|
| **Fill all item kinds (resume, smoke)** | `python -m seedsmith items fill --limit 1 --max-partitions 1 --count 1 --batch-size 1` |
| **Fill plan only** | `python -m seedsmith items fill --limit 1 --max-partitions 1 --dry-run` |
| **Fill unbounded (explicit)** | `python -m seedsmith items fill --full` |
| **Fill overnight (resume-safe)** | `python -m seedsmith items fill --full --continue-on-error` then re-run until EXIT=0 |
| **Fill subset** | `python -m seedsmith items fill --kinds set,charm --limit 1` |
| **Health Check (Items)** | `python -m seedsmith check gk-data/packs/fusion/data/seed/items --adapter items` |
| **Health Check (Actions)** | `python -m seedsmith check gk-data/packs/fusion/data/seed/actions --adapter actions` |
| **Health Check (Demons)** | `python -m seedsmith check data/seed/demons --adapter demons` |
| **CI Gate Mode** | `python -m seedsmith check gk-data/packs/fusion/data/seed/items --adapter items --gate` |
| **Full Health Report** | `python -m seedsmith report --corpus gk-data/packs/fusion/data/seed/items --adapter items` |
| **Demon Preflight** | `python -m seedsmith demons preflight` |
| **Demon Status / Resume** | `python -m seedsmith demons run status` / `… run resume` |
| **Generate Sets** | `python -m seedsmith items generate --kind set --write` |
| **Passive Tree Gen** | `python -m seedsmith trees generate --tree might --write --workers 4` |

---

## 5. Item kinds (11) — what `fill` does

| Kind | Selectors | Fill behavior |
|---|---|---|
| `affix-family` | `--group` + `--affix-kind` | Discovers `g-*.json` × legal kinds; skips partitions with no free `(channel, op)` |
| `material` | none | Closed issuable corpus + ledger |
| `gem` | `--slot` (+ fill `--count` → gemgen batch) | Discovers `gems/gN.json`; skips `toGenerate=0` |
| `consumable` | optional `--theme`/`--slot` | Reconcile-only on fill (mint needs `--theme` on generate) |
| `enhancement-milestone` | none | Default draw count + ledger |
| `base-type` | `--role` `--frame` `--band` | Discovers existing `frame-role-band.json` only |
| `set` | `--population` | **species then build** steps; ledger resume; production out-dir from `.env` |
| `charm` | `--population` | species only; ledger resume |
| `recipe` | none | `--write --backfill` reconcile; under `--full` elevated `--count` unless set |
| `combination` | `--shape` strain/splice | Both shapes; blocked/escalate terminal ledger; production out-dir from `.env` |
| `drop-table` | `--slot` | Discovers `drop-tables/dN.json` |

`unique` is **not** a generate kind (hand-authored).

Resume = re-invoke the same kind / `items fill` again. There is no separate `items resume` verb — `RunLedger` skips done subjects.

---

## 6. Core Operational Workflows

### Workflow 1: Inspect Corpus Health & Fix Gaps
1. `python -m seedsmith check gk-data/packs/fusion/data/seed/<domain> --adapter <domain>`
2. Interpret `[GAP]` / `[NOTE]` / `[NOT_MEASURED]`.
3. Add `--gate` for CI-shaped exit codes.
Detailed guide: [references/core_and_metrics.md](references/core_and_metrics.md).

### Workflow 2: Fill / resume items (preferred)
```powershell
# Small-batch smoke first (dependency order is built in; --limit required for set/charm/combo)
python -m seedsmith items fill --limit 1 --max-partitions 1 --count 1 --batch-size 1 --dry-run
python -m seedsmith items validate --deps
python -m seedsmith items fill --limit 1 --max-partitions 1 --count 1 --batch-size 1
python -m seedsmith check gk-data/packs/fusion/data/seed/items --adapter items
# Overnight / full corpus (re-run until EXIT=0; escalate is ledgered and advances):
python -m seedsmith items fill --full --dry-run
python -m seedsmith items fill --full --continue-on-error
```

### Workflow 3: Single-kind generate (after `.env`)
```powershell
python -m seedsmith items generate --kind set --population species --limit 5 --write
python -m seedsmith items generate --kind combination --shape strain --write
```

### Workflow 4: Demon Anchor Classification & Effect Generation
1. `python -m seedsmith demons preflight`
2. Motifs / threat / power-parse as needed
3. `python -m seedsmith demons run start --all --workers 4` then `run status` / `run resume`
4. `python -m seedsmith demons generate --kind commander-effect --workers 2`
Detailed guide: [references/demons_pipeline.md](references/demons_pipeline.md).

### Workflow 5: Passive Tree Planning & Generation
```powershell
python -m seedsmith trees plan --manifest --emit
python -m seedsmith trees generate --tree might --dry-run
python -m seedsmith trees generate --all --write --workers 4
```
Detailed guide: [references/trees_structures_dungeon.md](references/trees_structures_dungeon.md).

### Workflow 6: Actions 15-stage pipeline
See [references/actions_pipeline.md](references/actions_pipeline.md) — still staged adapters, not `items fill`.

---

## 7. Invariants & Rules of Engagement

1. **LLMs Write Identity; Deterministic Code Writes Magnitude.**
2. **Small Batches First** — `--dry-run` / `--limit 5` before full populations; `items fill --dry-run` before `items fill`.
3. **Seeds vs. Concrete** — seeds are offline enums/structure; runtime `Instantiator` rolls per player.
4. **No Git Write Commands.**

---

## Subsystem References
- [Architecture & Setup](references/architecture_and_setup.md)
- [Core Commands & Metrics](references/core_and_metrics.md)
- [Demons Pipeline](references/demons_pipeline.md)
- [Actions 15-Stage Pipeline](references/actions_pipeline.md)
- [Items & Effects Pipeline](references/items_effects_pipeline.md)
- [Passive Trees, Structures & Dungeon](references/trees_structures_dungeon.md)
