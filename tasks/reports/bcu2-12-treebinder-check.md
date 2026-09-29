# BCU2.12 — `tree-binder --check` at `d37024804`: the `--check` clause is green, the verdict is unreachable

Lane `cmdc/bcu8-4`. J9's Verify line is *"`--check` green; the reverse index reports no cross-namespace
reference"*. This runs the check the build section names
(`dotnet run --project gk-forge/tools/TreeBinder -- --check`, model-free, writes nothing in check mode) and reads
its verdicts. Full transcript: `tasks/reports/bcu2-12-treebinder-check.txt`.

## `--check` itself: green

```
dotnet run --project gk-forge/tools/TreeBinder -c Release -- --check
→ exit 0, 0 lines matching /^STALE/
```

So the committed `gk-data/packs/fusion/data/generated/passive-tree/*.json` **are** byte-identical to a fresh binder run —
`gk-forge/tools/TreeBinder/Program.cs:131-141` compares every output and prints `STALE <path> does not match a fresh
regeneration from <seed>` for a mismatch, then returns `1` if any did. That closes the determinism half of
J9's Verify line. It says nothing about health: the same run prints the verdicts below.

## The verdicts: 42/42 `Fail`, 1120 refusals, **0 deliberate holes**

| refusal class | count |
|---|---:|
| `affix '…' does not exist in the shipped seed content` | **612** (49 distinct ids) |
| `… channel is a pool reference (…)` — `spec-channel-pool.md §3.2/§3.4` | **507** |
| `affixIds must be 1..3, got 0 (R6)` | 1 — `skill.wither-def-t9-n1` (the class-E node the census names) |
| `(deliberate hole)` | **0** |

Top missing affixes: `atom.elpw-attune` 69 · `atom.elpw-overflow` 59 · `atom.elpw-pierce` 49 ·
`atom.sust-grit` 42 · `atom.death-glean` 36 · `atom.sust-callus` 29 · `atom.elpw-focus` 28 ·
`atom.swiftness` 26.

## Re-running this (and the one thing that can differ)

The tree-binder content below the build output is stable: regenerated at `2c4f5bd4a`, the transcript's
`grep -E "^tree-binder:|^  REFUSED|^STALE"` lines are **1,162 identical lines**. What can differ is the
*preamble* — `dotnet run` prepends build output when it has to rebuild, and this tree emits two warnings on
a rebuild (`EffectAtomCatalog.Generated.cs(219,67) CS8669`, `CaptureAction.cs(138,9) CS0162`) — so a
re-runner comparing the raw file should either expect those two lines or filter as above. See
[bcu8-4-reproducibility.md](bcu8-4-reproducibility.md) for the same check over every reading this lane
committed.

## What is new: the pass bar cannot be reached by authoring content

`gk-core/src/FusionRpg.Core/PassiveTree/Binding/BinderRunReport.cs:60`:

```csharp
var verdict = refused.Any(r => !r.DeliberateHole) ? RunVerdict.Fail : RunVerdict.Pass;
```

A tree passes only when **every** refusal is a deliberate hole — and this run marks zero. 507 of the 1,120
refusals are the binder *correctly* declining a channel that resolves later:
`docs/architecture/effect-atom/spec-channel-pool.md:8` — *"count and per-member weights, resolved to a
concrete channel **at roll time, per player**"* — and `:33-34` — *"seedsmith emits a seed, the runtime rolls
the concrete object per player. A pre-multiplied cartesian is a second roll implemented at authoring time"*.
So no amount of affix authoring turns such a node into a priced one, and `verdict=Pass` stays unreachable
for any tree that picks a pool channel until either

- (a) the verdict rule learns to treat a roll-time pool refusal as deferred rather than failed (i.e. those
  refusals become deliberate holes), or
- (b) the plan stops picking pool channels for bake-time nodes.

That is a semantics ruling (binder verdict vs node authoring), not a lane's change — and it matters because
BCU2.12's acceptance is measured on this corpus: the repair plan's `G6` bar (*"`does not exist` refusals drop
to **0** *by expansion, not by exclusion*"*, `tasks/passive-tree-repair-plan.md:387`) would close the 612 and
leave the 507 untouched.

## The baseline delta (a reading, not a conclusion)

`tasks/passive-tree-repair-plan.md:39-45` recorded:

```
trees=42  expected=1680  bound=266  refused=1414  unaccounted=0  overall=15.8%
refusal buckets:    affixNotGenerated 1356  ·  opMore 54  ·  other 4
```

At this head the same instrument reads **bound 560 · refused 1120 · overall 33.3%**, with
`affixNotGenerated` **612** and a **pool-reference class of 507 that the plan's buckets do not name**. So
the bind rate has roughly doubled and the remaining refusal mass has changed shape — the second-largest
class is now one that expansion cannot address by construction.
