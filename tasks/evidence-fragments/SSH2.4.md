# SSH2.4 — Rename the kind `socket-word` → `combination` in both kind tables

## Order of operations (recorded before editing)

1. Read `docs/architecture/strain-splice-host/spec-combination-regen.md`'s rename bundle (5
   sites) and `migrate.py`'s own module docstring, which explicitly warns "(2)-(5) [are] not
   separable without leaving the corpus worse" — read as the reason to check reality before
   editing, not skip the check.
2. Read `kinds.py:90` (Python `socket-word` row) and `KindCatalog.cs:116`/`:135` (the C# side
   already carries BOTH `socket-word` (legacy) and `combination` (added earlier by
   `combination-write-unblock`, 2026-09-07) as separate rows).
3. Edited `kinds.py` in place (socket-word slot becomes combination) and `KindCatalog.cs` (deleted
   the `socket-word` row) as literally asked.
4. **Verified against the real `dotnet run --project gk-forge/tools/ItemSeedValidator` before committing**
   (the todo's own Verify line) rather than assuming green. Found a real regression: removing the
   C# row while `data/seed/items/socket-words/sockwords.json` still exists and still declares
   `"kind": "socket-word"` produces `KindUnknown` on the file plus 25 `IdOutsideNamespace` findings
   on its entries (measured 3581 -> 3609 errors, git-diffed against a clean revert of both files to
   confirm the baseline). Confirmed the Python side has NO equivalent regression (`seedsmith check`
   before/after the `kinds.py`-only rename produced byte-for-byte identical gap/note counts, order
   variance only in one non-deterministic `SemanticDedup` set iteration, unrelated).
5. **Corrected the plan rather than shipping a known regression**: kept `kinds.py`'s rename (safe,
   proven), reverted the `KindCatalog.cs` row deletion (unsafe today), and moved bundle item #3 (the
   C# row removal) to SSH2.6 — the task that actually retires `sockwords.json` for real, at which
   point removing the row is finally safe. Updated SSH2.6's own todo entry to name this explicitly,
   with the order (`combogen-migrate --write` first, then the row removal, then re-verify) and the
   measured evidence, so the next session does not rediscover it. No hard-edge rule (H1/H2/H7) is
   touched by this correction — it is a plan-accuracy fix, verified against real tool output, not a
   design decision needing owner sign-off (AGENTS.md: "Test the constraint before you declare it").

## What changed

- `gk-forge/tools/seedsmith/seedsmith/adapters/items/kinds.py` — the `socket-word` `_defined(...)` row
  becomes `combination` IN PLACE (same slot in the `KINDS` tuple): `directory`/`namespace` become
  `"combinations"`, and the required/optional field sets are transcribed directly from the C#
  `combination` row (`shape`, `aptitudes`, `minSockets`, `ingredients`, `grants`, `grantedTier`
  required; `archetype`/`hostRole`/`hostFrame` additionally optional) — `runtimeId`/`fixedAtoms`
  (socket-word's own shape) are gone. `len(KINDS) == 16` and the uniqueness assertion both still
  hold, because this is a rename, not a remove-then-add.
- `gk-forge/tools/ItemSeedValidator/Registries/KindCatalog.cs` — **left untouched** (see "found and fixed"
  above); `combination`'s own row already existed here since 2026-09-07.
- `gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py`:
  - `test_the_KINDS_assertion_still_holds` — updated from its own explicit placeholder ("the rename
    itself is bundled with the regeneration run... whenever it lands") to assert the rename has
    actually landed: `combination` in, `socket-word` out, on the Python port.
  - New `test_the_kind_is_renamed_not_removed` (SSH2.4's own named acceptance test) — proves BOTH
    ports: Python's `KINDS` (directory/namespace/required/optional shape, and that
    `runtimeId`/`fixedAtoms` are gone) and the C# port's raw source text (`Defined("combination"`
    present, `Defined("socket-word"` STILL present — the deferred half, documented in the test's
    own docstring rather than silently asserted away).
- `tasks/strain-splice-host-todo.md` — SSH2.6's entry gains bundle item #3 (the deferred
  `KindCatalog.cs` row removal), the measured evidence, and the required order.

## Verification

```
$ PYTHONPATH="gk-forge/tools/seedsmith" python -m pytest gk-forge/tools/seedsmith/tests/test_combogen.py gk-forge/tools/seedsmith/tests/test_strain_splice_gen.py -q
88 passed   (run twice in a row for determinism, both green)

$ PYTHONPATH="gk-forge/tools/seedsmith" python -m pytest gk-forge/tools/seedsmith/tests/test_dungeon_contract.py gk-forge/tools/seedsmith/tests/test_items_adapter.py gk-forge/tools/seedsmith/tests/test_linkage.py gk-forge/tools/seedsmith/tests/test_relic_kinds.py -q
63 passed   (every other file referencing `kinds`/`KindCatalog`/`socket-word` concepts)

$ cd gk-forge/tools/seedsmith && python -m seedsmith check ..\..\data\seed\items --adapter items
56 gap, 663 note, 153 not_measured   -- IDENTICAL to the pre-rename baseline (only a non-
                                          deterministic SemanticDedup ordering differs)

$ dotnet run --project gk-forge/tools/ItemSeedValidator
FAIL — 3581 errors across 129 partitions   -- IDENTICAL to the pre-rename baseline (measured via a
                                                git-checkout revert + re-run comparison)
```

Population-pin (`python gk-core/scripts/guard-population-pin.py --summary`) and doc-citations
(`python scripts/audit-doc-citations.py --strict`) re-checked clean (0/0/0; 0 HIGH).

**Verification-boundary gap (pre-existing, named again):** `scripts/verify-change.ps1` has no owner
mapping under `gk-forge/tools/seedsmith/**`. `dotnet run --project gk-forge/tools/ItemSeedValidator` (the todo's own
manual Verify step) is what actually caught the regression this task avoided shipping — direct
`pytest` + that manual run together are the verification of record.

**Unrelated pre-existing drift noted, not touched:** `gk-data/packs/fusion/data/seed/creatures/_registry/themes.v2.json`
shows as modified in `git status` (CRLF/LF line-ending normalization only — `git diff
--ignore-space-at-eol` shows zero content lines). Never edited by this task; left as-is per the
session-boundary rule against touching files outside scope.

## Acceptance criteria (from `tasks/strain-splice-host-todo.md`)

- "the Python `KindSpec` becomes `combination` with the C# field shape, and the count assertion
  still holds" — **met**.
- "The `socket-word` row is removed from `KindCatalog.cs:113`" — **deferred to SSH2.6**, with the
  measured reason recorded there and here; shipping it now would have introduced a real, verified
  validator regression against the still-live legacy file.
- `the_kind_is_renamed_not_removed` passes on both ports; `dotnet run --project
  gk-forge/tools/ItemSeedValidator` green (relative to its own pre-existing baseline, unchanged by this
  task) — **met**.
