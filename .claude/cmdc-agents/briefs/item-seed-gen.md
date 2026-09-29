# Task: item-seed corpus — fix the GENERATORS, then regenerate

`ItemSeedValidator` is at **62 errors**, down from 3581. Every remaining finding was triaged as a
generator defect. Your job is the generators, not the JSON.

## The rule that decides every one of these — read it before you touch anything

`gk-data/packs/fusion/data/seed/items/**` is seedsmith OUTPUT: ~1011 of 1041 files carry `_meta.model`. The repo's hard
rule:

> Generated seed data is never hand-edited. A failing seed test is either a stale test or a
> generator defect — never a prompt to edit the emitted JSON.

Hand-editing a row forks the corpus from its generator: the next run reverts you, the ledger stops
describing the file, and the fix is invisible to every other consumer. **The only sanctioned path
is: change the generator, its tuning, or its registry, then regenerate and commit the diff.**

Registries (`**/_registry/**`) and `**/_exemplars/**` ARE authored — you may edit those by hand.

## The findings, and what each one actually means

**27 `TagAxisExclusive`** — 26 of them are `combat-posture` carrying both `defensive` and `utility`.
The axis is declared exclusive and the generator emitted two values on it.

A blanket "defensive wins" rewrite has already been **rejected**, and the reason matters: it
hand-picks an identity for 26 items from outside their own evidence, and the next generation run
reverts it. Enforce exclusivity **at emit time** — the generator must pick one value on an exclusive
axis from the item's own draw — then regenerate.

**8 content bugs** — `UniqueFrameImpossible` (4), `UniqueSetMembership` (3),
`GemAffinityNotConcrete` (1). Each one means a generator never constrained its draw. Find the
unconstrained draw and constrain it.

**6 kind/id findings** — `item-category` and `rare-name-words` ship but were never onboarded into
`KindCatalog.cs` / `naming.v1.json`. For `rare-name.head`/`tail` and
`atom.chill-punisher`/`atom.rot-punisher`: read the actual `naming.v1.json` rule first, then either
rename or widen the exemption **once**. Do not write four special cases.

**19 `MetaIncomplete`** — mostly closed already by an earlier `_meta` provenance backfill. For
anything left: **never stamp a model name that was not used.** An honestly unknown provenance beats
a fabricated `_meta.model`.

## Generation runtime

Local LM Studio at `http://localhost:1234/v1`, model `google/gemma-4-26b-a4b-qat`. This is the
owner-authorised local model — no API spend. It is already the seedsmith default in
`gk-forge/tools/seedsmith/seedsmith/pipeline/llm_caller.py`. Do not switch models.

## Rules

- One logical change per commit: generator fix + the regenerated diff + evidence + ledger line.
- Say in each commit body which generator you changed and what re-ran.
- If a generator cannot express a fix yet, **fixing the generator is the deliverable** — not a
  workaround in the data.

## Verification

- `dotnet run --project gk-forge/tools/ItemSeedValidator` (state the error count before and after)
- `$env:PYTHONPATH = "gk-forge/tools/seedsmith"; python -m pytest gk-forge/tools/seedsmith/tests -q`
- `pwsh -NoProfile -File scripts/run-guards.ps1 -Tier ci`

Note: `test_actions_description_completeness` fails pre-existing on a clean HEAD. Confirm a failure
already exists before blaming your change.

Run verification in the FOREGROUND. Never end a turn waiting on your own background job.
