# BCU2.12 — the name gate is correct; the key-suffix path is what hides the duplicate

Lane `cmdc/bcu8-4`, head `5a64f47ca`. Supersedes the "narrowed to two mechanisms" section of
[bcu2-12-namecollision-finding.md](bcu2-12-namecollision-finding.md), which named a `nameKey`-vs-`name`
re-gate and the codex/finalize write as the two candidates. Two model-free probes now exclude both and
pin the mechanism to one shape. Nothing under `data/` is written by either probe.

## Probe 1 — the gate refuses a duplicate name (so "the check is not wired" is false)

`python tasks/reports/bcu2-12-namegate-probe.py`

| probe | result |
|---|---|
| `build_response_gate(..., taken_names=["Kinetic Recirculation"])` over a draft named `Kinetic Recirculation` | **refused**: *"field 'name' ('Kinetic Recirculation') is already used by another commander effect — this one needs a distinct name"* |
| the same draft against an unrelated taken name (control) | passes |
| `_derive_unique_name_key("Kinetic Recirculation", {"tree.node.kinetic-recirculation"})` | **`tree.node.kinetic-recirculation-2`** — the key is suffixed, the **name is untouched** |

So `name_collision` **is** reached from node generation, exactly as `build_response_gate`'s docstring
claims (`nodegen/run.py:170-192`, the check at `:249`). The codex candidate is dead too: the codex stage
deals in `codexSummary` sentences and never mints node names (`species/generate_codex.py`,
`_j9_batch_run.py:100-137`).

## The mechanism the fingerprint points at

The ledger's 12 accepts of `Kinetic Recirculation` are byte-identical names with keys
`tree.node.defensive-deep-mechanism-kinetic-recirculation`, then `-2`, `-4`, `-5`, `-6`, `-8`, `-9`,
`-10`, `-11`, `-12`, `-13`, **`-13` again** — i.e. a suffix sequence, minted by
`_derive_unique_name_key` (`nodegen/run.py:703-724`, called at **`:909`**). That function exists so the
persisted key is "collision-free by construction, never by hoping the model gets it right" — **about
keys only**. It takes the *accepted name*, derives the key, and can always make the key unique, so a
duplicate **name** that gets past the gate is silently absorbed into a distinct key. The metric compares
names (`metrics/passive_tree.py:1008`), which is why the corpus reports it and nothing in the pipeline
did.

## Where a duplicate can still be persisted, after the closure

`nodegen/run.py:1141-1179` closes the **same-batch** race explicitly: the generation-time gates run
against a snapshot taken before a parallel batch, so two subjects in one batch can pick the same name —
and at record time a colliding *key* is re-derived while a colliding *name* makes the outcome
**`unresolved`** (*"gate 21: a colliding name is re-prompted, never persisted"*). So a persisted
duplicate needs one of:

1. an accept from **before** gate 21 (2026-09-11) or before the closure, or
2. a **cross-invocation** collision the closure's per-invocation live sets cannot see.

The dates separate them: the shared-tree node files that hold the name are `might`, `vigor`, `precision`
— all last written **2026-09-07**, i.e. candidate 1 — while `shatter` (index 1472) and the four
species-side holders (`AbyssSwordStar` 2026-09-21, `AllPeater`, `ArmedGargantuar`, and `BigGatling`,
which has no node file at all) are **post-closure**, i.e. candidate 2. Candidate 2 is the one still
open, and the species path is where it sits: the driver runs one species per invocation against a shared
ledger (`_j9_batch_run.py:32`), so any ordering in which a species' `run_language_stage` seeds from the
ledger before another subject's accept of the same name is visible produces exactly this fingerprint.

## What would settle it (and why it is not this lane's)

One controlled species run against the shared ledger, with the shared trees already holding the name —
a model call, so the manager's. The code it would exercise is `gk-forge/tools/seedsmith/**`, outside this lane's
fence. What this lane contributes is the narrowing: the gate works, the codex path cannot be the cause,
and the suffixing path is what turns a raced duplicate into a persisted one — so the fix is either to
make the name claim race-proof across invocations (or serialise it) or to treat "the key had to be
suffixed **and** the name collides" as the hard defect it is.
