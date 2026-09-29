# S2 — the topology classes as versioned data (loader + resolver + validator)

Task: `species-gear-chain` T27 `setClass` half, lane `sgc-2`, queue step S2 ·
spec: `docs/architecture/species-gear-chain/spec-set-species-binding.md` rev 2 § The set-planning system

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| The class numbers are versioned data, no magnitude in code | `grep -n "memberRoleMin\|bonusTierCeiling\|memberRoleSet\|resolutionOrder" gk-core/data/tuning/set-topology.v1.json` | exit=0 :: 4 hits (`resolutionOrder` + the three class rows) | `gk-core/data/tuning/set-topology.v1.json` |
| No balance number in the module | `python gk-core/scripts/audit-magic-numbers.py --summary` | `TOTAL 0 0 0 0 0`; the only numerals in `topology.py` are the `0`/`1` bounds and `parents[6]` | `gk-forge/tools/seedsmith/seedsmith/adapters/items/setgen/topology.py` |
| Loader parses, validates the structure, and refuses a missing key rather than defaulting | `PYTHONPATH=gk-forge/tools/seedsmith python -m pytest gk-forge/tools/seedsmith/tests/test_set_topology.py -q` | exit=0 :: **33 passed in 0.56s** | `gk-forge/tools/seedsmith/tests/test_set_topology.py` |
| The ladder is most-restrictive-first, no default, no fallback | same run | 6 roles/3 tiers → `family`; 6 roles/4 tiers → `general`; 10 roles `(2,10)` → `unique-species`; 12 roles and 10 roles `(2,4,6)` → `family`; 5 thresholds → refused naming all three classes | idem |
| `memberRoleCount` counts DISTINCT roles, not member rows | same run | 8 rows over 2 frames = 4 roles → `general`; a duplicate role row never inflates the count | idem |
| Every shipped entry resolves and satisfies its own class — closure, not a count | same run | `test_every_shipped_set_entry_resolves_to_exactly_one_class` and `..._satisfies_its_own_class_template` pass | idem |
| The mandatory first threshold is read from its owning domain, never copied | same run | default == `set-charm-gen.v1.json` `setShape.mandatoryThresholdPieces`; `mandatoryThresholdPieces`/`setShape` are absent as keys from the topology file | idem |
| Shipped tally — printed as a READING, never asserted | `PYTHONPATH=gk-forge/tools/seedsmith python -m pytest gk-forge/tools/seedsmith/tests/test_set_topology.py -q -s -k tally` | `unique-species 0 · family 4 · general 906`; by theme prefix `creature {general: 844}`, `build {general: 36}`, `theme {general: 26, family: 4}` | spec § The shipped corpus is re-planned onto the ladder |
| Path-owned boundary for the mapped paths | `.\scripts\verify-change.ps1 -Paths gk-forge/tools/seedsmith/seedsmith/adapters/items/setgen/topology.py,gk-forge/tools/seedsmith/tests/test_set_topology.py,docs/architecture/species-gear-chain/spec-set-species-binding.md,tasks/sessions/sgc-2.json -Session sgc-2` | exit=1 :: 3 failed, 1100 passed, 3783 subtests — **all three failures are in the pre-S2 baseline** (`sgc-2-S1.md`: 21 failed / 4115 passed) and none touches set topology | T55 |
| Path-owned boundary for the new tuning file | `.\scripts\verify-change.ps1 -Paths gk-core/data/tuning/set-topology.v1.json -Session sgc-2` | **fail** :: `VERIFICATION BOUNDARY MISSING: gk-core/data/tuning/set-topology.v1.json`; the registry is `scripts/**`, outside this lane's fence, so it is filed not edited | T55 |
| Session boundary is clean for this lane | `python scripts/session-boundary-check.py` | exit=0 :: DRIFT names only two pre-existing records (`docs-citations-1`, `warden-freeze-fix-20260919`) | `tasks/sessions/sgc-2.json` |

## Not proved

- No C# reader: the resolver is seedsmith-side, so `dotnet test`/`ItemSeedValidator` bear on S4's
  corpus rather than on this module.
- **A green `verify-change` for any `gk-forge/tools/seedsmith/**` path is unreachable today** — three
  pre-existing failures are absent from `knownRed` (T55). Diagnosed at the selected boundary, not
  retried broadly.
- `gk-core/data/tuning/set-topology.v1.json` cannot be verified through `verify-change` until T55 lands.
