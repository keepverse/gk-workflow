# Spec: `naming-grammar-repair` (item-seedgen module 13)

Parent: [item-seedgen-map.md](../item-seedgen-map.md) · Sibling module it is modelled on:
[`spec-fill-runner.md`](spec-fill-runner.md) · Grammar + collision SSOT it must never restate:
[`ssot-affixes.md`](../item/ssot-affixes.md) §4.12, `gk-data/packs/fusion/data/seed/items/_registry/naming.v1.json`, and
the C# that actually enforces both (`gk-forge/tools/ItemSeedValidator/Checks/NamingCheck.cs`,
`gk-forge/tools/ItemSeedValidator/Naming/NameNormalizer.cs`).

**Status:** written 2026-09-20 by `backlog-clean-up` BCU8.7. **The module's code already shipped**
(`d401f446`, `750b0dfd`, 2026-09-20) — this spec documents that code, names the one missing wire, and is
the acceptance for closing it. §6 is the open half.

---

## 0. The defect this module exists for

Item identity text is model-authored, and nothing in the generation pipeline stated the naming grammar
to the model: every brief said "a short display name". `naming_grammar.py`'s own docstring records the
result — **1125** `NameGrammarViolation`/`PossessiveForbidden`/`InventedConnective`/`PluralForbidden`/
`GeneratedOnlyNamePattern` findings on one real `ItemSeedValidator` run, almost all of them fixed
authoring rules that had never been said out loud.

Stating the rules in future briefs (`naming_grammar.py`, `NAMING_GRAMMAR_RULES`) stops the growth. It
does not repair what already shipped. **Generating seed is never hand-edited** (AGENTS.md hard rule,
enforced by `gk-core/scripts/guard-generated-seed.py`), so the repair must itself be a generator: a pass whose
authority is the validator and whose output is written by code.

## 1. Scope

| In scope | Out of scope |
|---|---|
| The persisted `name` field of every kind `NamingCheck.cs` applies the grammar to | `nameKey` / `iconKey` / `flavorKey` / any gameplay field — **no cross-field consistency check exists for those**, confirmed by reading `NamingCheck.cs` |
| Plan + prompt + validate + write + dry-run, driven by real validator findings | The grammar itself (`ssot-affixes.md` §4.12 / `naming.v1.json`), the validator, or the collision `name_repair` pass |
| A CLI verb that a human or an agent runs | Rewriting the 811-row backlog by hand — forbidden |

**A count is a reading, never a constant.** "1125" and "811" are measurements from two dates, not
acceptance numbers; the acceptance is "the validator reports 0 for these six codes", whenever that is
reached.

## 2. The C# validator is the only authority

`findings()` (`naming_grammar_repair.py:61-87`) shells out to
`dotnet run --project gk-forge/tools/ItemSeedValidator -- <root> --findings-json --codes=…` and parses the JSON
payload. It raises `RepairRefused` (`:40-42`) when the tool cannot run rather than planning against a
guessed list. `NAMING_GRAMMAR_CODES` (`:34-38`) is the closed set this pass may fix:
`NameGrammarViolation`, `PossessiveForbidden`, `InventedConnective`, `PluralForbidden`,
`GeneratedOnlyNamePattern`, `FusionNotDecomposable`.

**Nothing here re-implements the grammar in Python.** The same rule `name_repair.py` states for the
collision normalizer applies verbatim: a second implementation would be a second authority, and the two
would drift on exactly the shapes nobody tests. The rule codes are produced by
`NamingCheck.cs:146,157,164,168,184,250`.

## 3. The loop

```
findings()    real validator, six codes            :61
   ↓
plan()        one repair per failing entry, deduped across every code that entry failed :97
   ↓
brief()       one prompt per entry; embeds NAMING_GRAMMAR_RULES; names the refusal reasons :143
   ↓
run_batch()   injected caller(prompt, schema); bounded per-row retry (max_attempts=5)  :183
   ↓
validate_answer()  non-empty, changed, and not already present anywhere in the corpus :165
   ↓
apply()       writes ONLY `name`; atomic LF write; write=False = report only          :218
```

Rules that are load-bearing, each with the reason it exists:

- **Dedupe by entry, not by finding.** One name can fail several codes at once (`Kirov's Tethered
  Husk` is `NameGrammarViolation` + `PossessiveForbidden` + `InventedConnective`); three prompts for one
  name would produce three answers competing for the same field.
- **A refusal is data.** `brief()` re-states every previously refused candidate and asks for a different
  one; `run_batch()` retries the row up to `max_attempts` and reports the row in `failed` if it never
  lands, so one stubborn row never discards the batch.
- **A transport failure is not a row failure.** `run_batch()` reports it and moves on (`:206-210`)
  rather than blaming the name.
- **`validate_answer()` checks the whole corpus, not the file.** `_current_names()` (`:245`) reads every
  non-`_`-prefixed `**/*.json` outside `_runs`/`_exemplars`. A replacement that duplicates a name in an
  unrelated file is refused here — the failure mode observed live, where a candidate collided with an
  *untouched* entry and `NamingCheck.cs` attached the error to whichever file the scan reached second.
- **Only `name` is written.** `apply()` (`:236`) assigns `row["name"]` and nothing else; the
  atomic temp-file + `os.replace` write (`:262-271`) uses `newline="\n"` so a Windows run cannot flip
  the corpus's line endings.
- **`write=False` is the default.** The pass is dry-run-first by contract; a write also has to clear the
  production-tree gate (`--allow-production-tree`).

## 4. Structure

| File | State |
|---|---|
| `gk-forge/tools/seedsmith/seedsmith/adapters/items/naming_grammar.py` | **built** — `NAMING_GRAMMAR_RULES`, the three legal shapes (A adjective-base, B base-of-concept, C fused pair), and the four hard rules (no possessive, no plural head noun, `of` the only connective, never shapes A+B combined). Shared verbatim into every authoring brief (`setgen`, `charmgen`, `basetypegen`, `droptablegen`, `combogen`, `affixfamgen`, `gemgen` all import it). |
| `gk-forge/tools/seedsmith/seedsmith/adapters/items/naming_grammar_repair.py` | **built** — 272 lines, §3's loop. |
| `gk-forge/tools/seedsmith/tests/test_naming_grammar_repair.py` | **built** — 13 tests: plan dedupe/skip, the three `validate_answer` refusals, name-only apply, the four `run_batch` paths (clean / retry-with-refusal / exhausted / transport), and two text guards on `NAMING_GRAMMAR_RULES`. |
| a `seedsmith items` verb | ⛔ **missing** — see §6. |

## 5. Testing strategy

- **Unit (shipped).** The 13 tests above, against a fake `caller`; no live endpoint, no corpus writes.
- **CLI (required with the wire).** A verb test that (a) plans against a planted finding on a scratch
  copy, (b) `--dry-run` writes nothing and exits with a report, (c) `--write --answers` writes only the
  `name` field, and (d) production-tree writes are refused without the gate.
- **Corpus (the run itself).** `ItemSeedValidator` for the six codes is the before/after reading. Never
  a pinned count.

## 6. ⛔ The wiring gap — the module is not done

`rg -n "naming_grammar_repair" gk-forge/tools/seedsmith/seedsmith/report/cli.py` returns **no hits**: no
`seedsmith items …` verb reaches this module. Its only importer today is its own test file, and the real
corpus batches were driven by an **uncommitted** driver script — `750b0dfd`'s own message says so
("the still-uncommitted driver script now re-runs the real validator across NameCollision + every
naming-grammar code after every apply").

By this repo's own rule, a mechanism no production host reaches is not done, and an uncommitted driver
is not a host. The wire is small and has a working sibling: `items repair-names`
(`gk-forge/tools/seedsmith/seedsmith/report/cli.py:895-985`, parser `:3109`) already does dry-run / `--write` /
`--answers` / `--endpoint` / `--allow-production-tree` for the *collision* pass. The naming-grammar pass
needs the same shape with
`findings()`/`plan()`/`run_batch()`/`apply()` behind it instead of `collision_groups()`.

**Owner:** the `items` verb surface belongs to **`seedsmith-cli-ux`**; the corpus run itself is
**`item-seed-regen`**. A row for each is open in
[`tasks/seedsmith-generated-seed-repair-todo.md`](../../../tasks/seedsmith-generated-seed-repair-todo.md)
under the follow-up this spec closes. Until the verb exists, the eight-hundred-odd remaining rows can
only be repaired by a script nobody committed — which is the defect, not the fix.

## 7. Boundaries (always / ask first / never)

- **Always:** the validator is the authority; a repair writes only `name`; dry-run is the default; a
  refused answer is re-prompted, never accepted or silently dropped.
- **Ask first:** a new item kind for `NamingCheck` to cover; a change to `NAMING_GRAMMAR_RULES` (it is
  shared by every brief — `combogen`'s `spells_the_count` guard refuses a brief that risks disagreeing
  with a schema count, and this text is shared into that brief).
- **Never:** hand-edit a generated `name`; write `nameKey`/`iconKey`/`flavorKey`; re-implement the
  grammar or the normalizer in Python; leave a row that exhausted retries half-written.

## 8. Success criteria

1. A committed `seedsmith items` verb reaches the pass; no uncommitted driver is required (the §6 wire).
2. `ItemSeedValidator` reports 0 for the six codes, reached through that verb — a reading, not a pinned
   count, and with zero hand-edits (`guard-generated-seed.py` stays green).
3. A repaired name is unique corpus-wide and legal by `NamingCheck.cs`'s own verdict, not by this
   module's opinion of it.
