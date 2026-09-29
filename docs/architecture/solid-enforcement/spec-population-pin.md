# Spec: `population-pin`

**Program:** [`solid-enforcement`](../solid-enforcement-map.md) · **Wave 3** · depends on:
`guard-runner`.

## Objective

`CLAUDE.md` hard rule: *"A guardrail validates the CONTRACT, never a population count or generated
text."* A closed vocabulary's size **is** the contract, so pin it. A derived population's size is a
**reading**, so never pin it. The rule records two incidents, one in each direction (2026-08-24 tore
out a correct canary; 2026-09-11 replaced `84` with `904`). Nothing enforces either direction, and
the measurements show the rule is broken today:

| Where | Literal count assertions ≥ 10 in tests that read committed content | Of which ≥ 50 |
|---|---|---|
| C# (`tests/**`) | **205** in 90 files | 42 |
| Python (`gk-forge/tools/seedsmith/tests/**`) | **69** in 28 files | — |

They include **`904`** (the species roster, `test_tree_species_roster.py`: the incident, recurring),
`775` fusion recipes, `125` affix families plus per-tag counts (`test_nodegen_vocab.py`), and one
closed-vocabulary count (`269` registered derived channels) **pinned in six separate files**.

A number alone cannot tell a scan which kind of count it is: `10` is the ten-rung rarity ladder
(closed), and `125` is today's affix families (population). So this module makes the **author
declare it**, and the guard checks the declaration (map decision D4: markers over heuristics).

## Design

### The rules

**P1 — a count pin must declare what it pins.** In a test that reads committed content (it touches
`data/{seed,generated,tuning}`, locates the repo root, or loads a registry or catalog), a literal count
assertion with a literal ≥ `minLiteral` must carry a marker on the same line or the line above:

```csharp
// pin: closed-vocabulary DerivedStatRegistry.AllRegistered — a new channel is a reviewed change
Assert.Equal(268, registry.AllRegistered.Count);

// pin: immutable gk-core/data/tuning/aptitudes.v8.json — a published version never changes
Assert.Equal(526, v8.Edges.Count);
```

```python
# pin: closed-vocabulary ActionTag — owner ActionEnums.cs
```

Exactly **two marker kinds** exist, and the set is closed:

- `closed-vocabulary <Owner>`: the owner symbol or file where the vocabulary is declared.
- `immutable <path>`: a published, never-edited file, where the count is a property of that exact
  version. It is legitimate **because `tuning-immutability` makes it true**, and only for a path under
  `gk-core/data/tuning/` naming a specific `v<n>`.

An unmarked pin is a population pin. The fix is **never** to add a marker to it. It is to rewrite it
as the contract (`CLAUDE.md`'s own worked example: *"Assert `len(catalog) == records_on_disk`,
`Σ memberships == assigned`, ids unique, every join closes … Print the scale; never assert it."*).

**P2 — pin a closed vocabulary once, at its owner.** Two `closed-vocabulary` markers naming the same
owner, each beside a numeric literal, fail. Every other site asserts *equality with the owner*
(`Assert.Equal(DerivedStatRegistry.AllRegistered.Count, surface.Rows.Count)`). This removes the
six-fold `269`, and with it, five of the six edits `retire-atk` would otherwise need.

**P3 — the marker names something real.** `closed-vocabulary <Owner>` must resolve to a symbol or
file that exists; `immutable <path>` must be a tracked `gk-core/data/tuning/<d>.v<n>.json`.

### The threshold

`minLiteral` defaults to **10**. It is a precision knob with a written reason, not a balance number.
Measured on content-reading C# tests (2026-09-18): **502** count assertions below 10, dominated by
`0`–`3` (367 sites). Those are emptiness and singleton contract checks such as
`Assert.Equal(0, errors.Count)`, which *are* contract assertions. The next largest value is `6`
(52 sites), which matches the six resources and six elements. **These were not individually
classified**, so the threshold is a stated trade-off, not a proven boundary: a population smaller
than 10 escapes the guard. The script's comment records this measurement and the trade-off. It lives
in the guard as a commented structural `const`.

### The guard: `gk-core/scripts/guard-population-pin.py` (+ `.ps1` wrapper)

One script scans both C# (`Assert.Equal(<int>, <expr>{.Count|.Length|.Count()})`) and Python
(`assertEqual(len(...), <int>)`, `assertEqual(x.count, <int>)`, both argument orders). It reports
`file:line`, the literal, and which rule failed, and `--targets P1` prints a bare file:line list for
backlog work, matching `audit-magic-numbers.py`'s conventions.

### Clearing the backlog (green-first)

274 sites. **Each one gets one of three dispositions, recorded by the change itself:**

1. **Closed vocabulary pinned at its owner:** add a `closed-vocabulary` marker. At most one per owner.
2. **A closed-vocabulary duplicate:** rewrite as equality with the owner (P2).
3. **A population:** rewrite to contract assertions and print the scale.

Tasks are split by test project and folder, so each is S or M, and the ≥ 50 sites go first because
they are almost all population or duplicate pins. `904`, `775` and `125` are dispositions 3.

### Registry

A new guard row: `ci` / `backlog` → `population-pin` until 0 findings, then `ci` / `gating`.
Invariant row `claude-contract-not-population` → `population-pin`.

## Commands

```powershell
python gk-core/scripts/guard-population-pin.py --summary
python gk-core/scripts/guard-population-pin.py --targets P1
.\scripts\run-guards.ps1 -Only population-pin
```

## Project structure

| Path | Change |
|---|---|
| `gk-core/scripts/guard-population-pin.py`, `.ps1` | **new** |
| `gk-forge/tools/seedsmith/tests/test_guard_population_pin.py` | **new** (falsifiers) |
| ~118 test files across `tests/**` and `gk-forge/tools/seedsmith/tests/**` | marker or rewrite, per site |
| `docs/architecture/validation-ssot.md` | a section documenting the two marker kinds |
| `gk-core/scripts/enforcement-registry.v1.json` | rows |

## Testing strategy

- **Falsifiers** on in-memory source text: an unmarked `Assert.Equal(904, species.Count)` in a test
  containing `gk-data/packs/fusion/data/seed` fails P1. The same line in a pure-fixture test (no content read) passes. Two
  `closed-vocabulary X` pins fail P2. A marker naming a nonexistent owner fails P3.
  `immutable data/tuning/foo.json` (no version) fails P3.
- **Every rewritten population test must still fail when its contract breaks.** For each disposition-3
  rewrite, the commit body records the mutation tried (e.g. a duplicated id, a dangling join) and
  confirms the new assertion caught it. A rewrite that asserts nothing is worse than the pin it
  replaced.

## Boundaries

- **Always:** rewrite a population pin to the contract. Pin a closed vocabulary once, at its owner.
- **Ask first:** a third marker kind, or moving `minLiteral`.
- **Never:** mark a population pin to silence the guard. Never bump a pinned reading.

## Success criteria

- [ ] P1–P3 enforced across C# and Python, and each has falsifiers.
- [ ] All 274 measured sites dispositioned. `904`, `775` and `125` rewritten as contracts; `269`
      pinned once.
- [ ] The guard gates in CI. `validation-ssot.md` documents the markers.

## Self-audit — the debate

**Objection: "A marker is a way to launder a population pin."** Only if nobody reviews it, and the
marker makes review possible: it names an owner, and P3 checks the owner exists. A
`closed-vocabulary SpeciesCatalog` marker on `904` would be visibly false in review, because a
species catalog is not a closed vocabulary. Without the marker, the same pin is invisible among 274
others. The alternative, a guard that guesses from the number, is exactly the heuristic that fails
on `10`.

**Objection: "`immutable` pins are readings too."** A count taken from a *mutable* file is a reading.
A count taken from a file that can never change (a published tuning version, which
`tuning-immutability` now enforces) is a fact about an artefact, and it stays true for as long as the
file exists. That is why the kind requires a versioned tuning path and nothing else.

**Objection: "274 sites is a lot for one module."** It is the largest backlog in the program. But
almost all of it is mechanical (disposition 1 is a comment line), and the ruling is green-first. The
plan splits it into project-sized tasks that can run in parallel. The alternative, a known-red
allowlist, was explicitly ruled out.

## Gaps found and closed while writing

- **The raw count (258) included fixture tests** that never read committed content. Narrowing to
  content-reading tests (205) removed noise without losing a population pin, because a population is
  by definition committed content.
- **Python was missing** from the first draft, and it holds the `904` recurrence. It is in scope.
- **The same closed-vocabulary pin in six files** is not a population defect, and P1 alone would have
  accepted all six with markers. P2 exists because of that measurement.
- **Disposition 3 can produce hollow tests.** The mutation-check requirement guards the rewrite
  itself.
