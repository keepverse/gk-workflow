# BCU2.12 — the family's own distribution census at `24ed0df3e`, and the precondition behind it

Lane `cmdc/bcu8-4`. Instrument: `python -m seedsmith trees census` — "print the passive-tree
distribution, not an aggregate (task P0.1, `tasks/passive-tree-repair-plan.md` §1)". Model-free, reads
the committed plan + nodes + `gk-data/packs/fusion/data/generated/passive-tree`'s bound reports, writes nothing (full output
saved as `tasks/reports/bcu2-12-tree-census.txt`).

## The head-line numbers

```
trees=42  expected=1680  bound=560  refused=1120  unaccounted=0  overall=33.3%
boundWithPricedAtoms=250  boundWithoutPricedAtoms=310  pricedAtoms=344  unspentBudgetShareMilli=62230
boundWithReadableAtoms=0  unreadableBoundNodes=560  readableAtoms=0  readable=0.0% of bound
```

| cut | reading |
|---|---|
| bound by class | magnitude **419/840 (49.8%)** · mechanism **141/840 (16.7%)** — *"mechanism is the deep-tier payoff; a collapse here empties tiers 8-10"* |
| bound by category | status 344/960 (35.8%) · primary 171/480 (35.6%) · elemental 45/240 (18.7%) |
| priced atoms by kind | `stat.modify` **344** — *"NOT read by the resolver (dropped silently)"* · `stat.derived` **0** |
| per-tree completeness | best `might` 26/40, worst `spark` 1/40; **no tree at 40/40** |
| plan nodes not yet generated (class E) | exactly one — `wither: skill.wither-def-t9-n1` |
| provenance vintage | `mixed` 20 trees · `stale` 22 trees; **1,066 records not the current vintage** |

## What is *not* new here (do not re-file it)

The `DEFECT: no 'stat.derived' atom bound — every bound node contributes zero even though the bind rate
looks healthy` line is the census instrument's own wording for a defect the repair program already holds:
`tasks/passive-tree-repair-todo.md:42` (*"resolver reads only `stat.derived`, so the tree still
contributes nothing in play. That is P4.3."*), `:381`, `:416-417` (`stat.derived: 0` beside the resolver's
guard `Resolve/TreeAtomSource.BoundAtomsFor`: `if (atom.KindId != "stat.derived") continue;`), and `:499`
(**BLOCKED**: *"no bound magnitude atom resolves live — `stat.modify` awaits P11 (gated), `stat.derived`
awaits module 2 (no session)"*). The same split is BCU8.8's erratum on the resolver side. This report adds
the **reading at this head**, nothing else about it.

## What is new, and why it belongs in BCU2.12's row

1. **A numeric baseline for the blocked repair rows** — 560/1680 bound with **readable 0.0%** — so the
   repair's own acceptance has a BEFORE with a date and a command, and so a claim that the bind rate
   "looks healthy" can be checked against the reading that says it buys nothing.
2. **The class-E node reconciles two independent readings.** My metric census reported one
   `MechanismRamp` GAP (`wither:defensive:t9`, 2 mechanism nodes where the ramp names 3); J13's 2026-09-10
   table named three missing mechanism nodes; the instrument names the single remaining one exactly —
   `skill.wither-def-t9-n1` — and classifies it **class E, not a defect** (the language stage simply has
   not generated it). Nothing to repair there; it is the J13 regeneration's work.
3. **The vintage reading is corroborated, with the instrument's own explanation.** The 1,066 records the
   census counts as "not the current vintage" are exactly the 1,066 nodes my
   [bcu2-12-vintage-reading.py](bcu2-12-vintage-reading.py) found carrying **no** `promptVersion` field,
   and the instrument states the consequence I inferred: *"a fresh `trees generate` re-rolls them, and the
   document stamp cannot see it (per-node provenance is authoritative)"* — i.e. J13's third acceptance
   clause cannot be judged from `_provenance.promptVersion` alone.

## The ordering dependency this puts on BCU2.12

The row's acceptance is the three generation-vintage metrics (ExclusionRate / NameCollision /
NearDuplicate) and the plan/`--check` half. This instrument shows an additional precondition: **getting
those three into target still leaves `readable = 0.0% of bound`**, and a corpus that binds but cannot be
read contributes nothing in play — the repo's own rule that a mechanism no production host reaches is not
done. So BCU2.12's `Landing` should not be declared on the three metrics alone; the bound/readable state
is the repair program's `P4.3`/P11/module-2 gate and belongs beside it.
