# Seedsmith: Architecture & Environment Setup

`seedsmith` is the offline Python application (`gk-forge/tools/seedsmith`) that owns the health of every seed corpus in Rise of Summoner. It validates content against closed schemas, measures gaps and distributional imbalance, and deterministically plans work orders for LLM-driven generation pipelines.

---

## 1. Core Principles

Seedsmith is built around five core architectural invariants:

### P1 — The LLM writes identity; deterministic code writes magnitude
A language model authors identity, theme, naming, and flavour. It **never** chooses numbers. Base stats, tier magnitudes, drop rates, costs, curves, and scaling formulas are resolved deterministically by code from rung bands, role budget weights, and the rarity ladder (`ssot-rarity.md`, `ssot-power-scale.md`).

### P2 — A metric without a declared target is an opinion
Expected distributions and counts are defined declaratively in `budget` and tuning files (`gk-core/data/tuning/`). Every metric measures *actual vs. declared*.

### P3 — Closed-loop vs. open-loop metrics
- **Closed-loop metrics** can verify their own fixes by machine (e.g. "every item in kind X has flavour text"). A passing run requires all closed-loop metrics to pass.
- **Open-loop metrics** identify issues that require human or advisory review (e.g. "flavour is repetitive or generic"). Open-loop metrics produce review queues and never contribute to an automatic gate pass.

### P4 — The plan is deterministic
Findings $\rightarrow$ work orders is a pure function: which partitions to author, in what dependency order, with which constraints. Models never plan their own work.

### P5 — Domain knowledge lives in adapters
The core engine (`seedsmith.corpus`, `seedsmith.budget`, `seedsmith.metrics`, `seedsmith.report`, `seedsmith.planner`) is domain-agnostic. All game-specific structures live in domain adapters (`adapters/items`, `adapters/demons`, `adapters/actions`, `adapters/dungeon`, etc.).

---

## 2. Environment & Installation

### Requirements
- Python `>= 3.11` (Python 3.13 tested)
- Dependencies declared in `gk-forge/tools/seedsmith/pyproject.toml` (`jieba==0.42.1`, `langgraph==1.2.11`, `pytest==9.0.2`).

### Running Seedsmith
Seedsmith can be executed either from within `gk-forge/tools/seedsmith` or from the repository root:

```powershell
# From gk-forge/tools/seedsmith:
cd gk-forge/tools/seedsmith
python -m seedsmith <command> [options]

# From repo root (setting PYTHONPATH):
$env:PYTHONPATH = "gk-forge/tools/seedsmith"
python -m seedsmith <command> [options]
```

### Running the Test Suite
```powershell
cd gk-forge/tools/seedsmith
python -m pytest tests/test_cli.py -v
python -m pytest tests/ -q
```

---

## 3. Local Model Configuration (`.env`)

Seedsmith connects to local OpenAI-compatible model endpoints (such as LM Studio).

Copy `.env.example` → `tools/seedsmith/.env`. Resolution for LLM keys:

1. Built-in `LlmCallerConfig` defaults  
2. `seedsmith.toml` `[pipeline.llm_caller]`  
3. `.env` (wins)

`load_config()` looks for `.env` at CWD first, then `tools/seedsmith/.env` (so repo-root runs still find the machine file). CLI `--endpoint` / `--model` override `.env` when non-empty.

```ini
# tools/seedsmith/.env

SEEDSMITH_LLM_ENDPOINT=http://localhost:1234/v1/chat/completions
SEEDSMITH_LLM_MODEL=google/gemma-4-26b-a4b-qat
SEEDSMITH_LLM_TIMEOUT=420
SEEDSMITH_LLM_ATTEMPTS=2
SEEDSMITH_LLM_RETRY_DELAY=3
SEEDSMITH_LLM_MAX_HEAL=3
SEEDSMITH_LLM_MAX_TOKENS=16384

# items generate / items fill — production writes without retyping flags
SEEDSMITH_ALLOW_PRODUCTION_TREE=1
# SEEDSMITH_ITEMS_OUT_DIR=   # optional; unset = sets/ / charms/ / combinations/
```

With that file, these are enough:

```powershell
python -m seedsmith items generate --kind set --write --limit 5
python -m seedsmith items fill --limit 1 --max-partitions 1 --count 1 --batch-size 1 --dry-run
python -m seedsmith items fill --limit 1 --max-partitions 1 --count 1 --batch-size 1
```

---

## 4. Exit Codes Contract

Seedsmith CLI commands return strict exit codes relied upon by CI and scripts:

| Code | Name | Meaning |
|:---:|---|---|
| `0` | `EXIT_CLEAN` | Clean run. No findings at `GAP` severity (or under `--gate`, no gaps from promoted gating metrics). |
| `1` | `EXIT_GAP` | One or more findings at `GAP` severity found. |
| `2` | `EXIT_CANNOT_RUN` | Fatal configuration error: unreadable corpus root, missing required file, or unknown adapter. |
| `3` | `EXIT_REFUSED` | Planner or runner refused an invalid, unresolvable, or unpromoted work order. |

---

## 5. Directory Layout & Conventions

```text
gk-forge/tools/seedsmith/
├── seedsmith/
│   ├── adapters/            # Domain adapters: actions, demons, dungeon, effects, items, structures, trees
│   ├── briefkit/            # Brief generation from deterministic work orders
│   ├── budget/              # Declarative target distributions and cell counts
│   ├── corpus/              # Generic seed folder loader and graph model
│   ├── metrics/             # Coverage, linkage, balance, distribution, dedup checks
│   ├── numerics/            # Band evaluation and battle ruleset progression
│   ├── pipeline/            # Transport caller, schema validation, self-healing, staleness tracking
│   ├── planner/             # Deterministic findings -> work orders
│   ├── report/              # CLI interface and formatters
│   ├── sampling/            # Deterministic sampling for open-loop review
│   └── workflow/            # LangGraph workflow runners and state graphs
├── tests/                   # Extensive test suite (130+ test modules)
├── pyproject.toml           # Package metadata and dependencies
└── .env.example             # Template for local model runner
```
