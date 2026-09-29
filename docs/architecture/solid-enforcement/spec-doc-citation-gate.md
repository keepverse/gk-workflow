# Spec: `doc-citation-gate`

**Program:** [`solid-enforcement`](../solid-enforcement-map.md) · **Wave 3** · depends on:
`guard-runner`.

## Objective

`scripts/audit-doc-citations.py` shipped on 2026-09-18 (`6f0d1b62`) as **report-only by design**:
*"--strict exists for a later CI adoption, once the noise floor is known and the backlog is down."*
Ruling 2 makes that later adoption this module. Clear the backlog, add the one systemic check the
audits found by hand, and gate.

Why it belongs in a SOLID program: `DESIGN-GATE.md` is the repo's single source of truth for *how
design decisions are grounded*, and its first rule is *"read → verify against code → propose"*. A
citation that doesn't resolve is a broken link in that chain. The costliest form, a **stale
negative** (*"X has zero production callers"*), licenses rebuilding working code. That is how the
2026-08-29 aura session lost an hour.

## Design

### Backlog, measured 2026-09-18 after the day's cleanup

| Code | Meaning | Count | Gating after this module |
|---|---|---|---|
| **D1** | cited file does not exist | **217 HIGH** (540 total; the rest are LOW: prior-art/research, or a line-less proposal in a forward-looking doc naming a file that never existed) | yes (HIGH) |
| **D2** | cited line past end of file | 32 HIGH (38 total) | yes (HIGH) |
| **D3** | a line-numbered citation to an ambiguous basename (e.g. bare `Program.cs`, which many files share), so it cannot be checked | 284 LOW | **yes.** See the debate |
| **D4** | *new:* an ideal doc whose own map says approved/authorized/in use, while its status line says it isn't, and it carries no status banner | measure at build (≈ 0 after `572695b6` added 21 banners) | yes |

The largest clusters, measured **before** exemption 6 changed the D1 classification, were
`docs/architecture` root (74), `world-stage/` (28), `seedsmith/` (24), `item/` (24),
`world-map-runtime/` (22) and `story-scene/` (20). Re-measure with `--summary` at build time, and
size the SE3.8–SE3.12 batches from that reading, not this one.

### The fix for each finding, in order of preference

1. **The code moved:** point the citation at the successor `file:line`, **verified by opening it**.
   Never infer the new line.
2. **The code was replaced wholesale** and the passage describes what *was*: keep the citation and
   add a `<!-- citations-historical: <what changed, and where it went> -->` marker. The audit already
   honours it (`99a288d1`), and it is the honest form for a survey of replaced code.
3. **The claim itself is now false:** correct the claim in prose, leaving the old text visible (the
   repo's correction convention). A marker cannot fix a wrong fact.
4. **D3:** replace the bare basename with its repository path (`Program.cs:402` →
   `gk-core/src/FusionRpg.Server/Program.cs:402`), **after confirming which of the same-named files the
   passage meant.** When the passage cannot say, the citation is recorded as unverifiable in prose,
   never guessed.

### D4 — the status-line check

For each `docs/architecture/<p>-ideal.md` whose `<p>-map.md` status line matches
`approved|authorized|in use|complete` (case-insensitive), fail if the ideal's first 15 lines match
`no build authorized|not a spec|nothing specced|nothing built|no spec, no plan` **and** the file does
not contain the banner heading `Status line vs. what shipped`. This is the systemic finding of the
2026-09-18 gap survey, where 21 ideals contradicted their own maps. It is mechanical by nature, so
it belongs in the audit rather than in the next audit round.

### Gating

`--strict` fails on HIGH (D1/D2) plus D3 plus D4. The registry row goes `ci` / `backlog` →
`doc-citation-gate` when the module starts, and `ci` / `gating` when `--strict` exits 0 on the tree.
`docs/research/**` and prior-art sections stay LOW and non-gating, by the audit's existing exemption
3. Those cite *other* projects' files, which this repo cannot resolve.

## Commands

```powershell
python scripts/audit-doc-citations.py --summary
python scripts/audit-doc-citations.py --targets D1        # bare file:line list for a work batch
python scripts/audit-doc-citations.py --scope docs/architecture/item
python scripts/audit-doc-citations.py --strict             # the gate
```

## Project structure

| Path | Change |
|---|---|
| `scripts/audit-doc-citations.py` | D3 promoted (non-research); D4 added; docstring updated |
| `scripts/audit-doc-citations.py` | the checker itself, called with `--strict`; the thin `.ps1` wrapper that used to front it was retired 2026-09-26 and the runner now dispatches the `.py` directly |
| ~150 docs under `docs/**` | fixes per the preference order |
| `gk-forge/tools/seedsmith/tests/test_audit_doc_citations.py` (or a Guard.Tests equivalent) | **new**: D1–D4 falsifiers and the exemptions |
| `gk-core/scripts/enforcement-registry.v1.json` | guard row |

## Testing strategy

- **Falsifiers on in-memory markdown:** a dead file fails D1. A line past EOF fails D2. The same line
  under a `citations-historical` marker passes. The same line whose text says "deleted" passes. A
  bare basename with two tracked files sharing that name (e.g. two files named `Program.cs`) fails D3. An ideal plus approved map
  without the banner fails D4, and with the banner it passes.
- **Batch discipline:** each backlog batch is one directory. Its commit states the before/after count
  for that scope and names any claim that was **corrected** rather than repointed. That is the
  information a reviewer needs, and it is what separates this from a find-and-replace.

## Boundaries

- **Always:** open the successor before repointing. Correct false claims in prose.
- **Ask first:** extending exemption 3 beyond prior-art sections and `docs/research/`.
- **Never:** guess a line number. Never use a marker to hide a claim that is now false.

## Success criteria

- [ ] `audit-doc-citations.py --strict` exits 0 on the tree.
- [ ] D3 and D4 implemented with falsifiers.
- [ ] Guard gating in CI through the runner.
- [ ] Every corrected (not merely repointed) claim is listed in its batch's commit body.

## Self-audit — the debate

**Objection: "D3 is LOW by the audit's own design. Promoting it contradicts the tool."** The tool
made it LOW because it *cannot check* it, not because it is fine. By the tool's own first principle,
"a citation nobody can open is not evidence", an uncheckable line number is exactly that. The fix is
mechanical and makes the citation both checkable and clearer to a human. It stays exempt in
`docs/research/`, where same-named files often belong to other projects.

**Objection: "~530 fixes (217 + 32 + 284) across ~150 docs is a documentation marathon in a SOLID program."** The
alternatives are permanent report-only (ruled out) or an allowlist of known-bad citations (ruled out).
It parallelises by directory, and the gap survey showed the cost of *not* doing it: an agent
spending 30 minutes rediscovering what this script finds in two seconds, on documents the design gate
tells every session to read.

**Objection: "D5, closed-vocabulary counts stated in prose (the '12 kinds' class), was the other big
finding. Why not here?"** A regex over prose for "N kinds" or "N attach points" has no reliable
anchor, and the same sentence shape appears in history sections that are *correctly* stale (every
correction written on 2026-09-18 quotes the old count on purpose). **No rule was prototyped.** That
is a judgement from the shape of the prose, not a measured false-positive rate, and it is stated as
such. It stays out, recorded here. The real protection is `population-pin` P2 (one pin per vocabulary, at its owner) plus
`vocabulary-mirror`, which remove the *code-side* drift that the prose was copying.

## Gaps found and closed while writing

- **Two defects in the audit itself, found by running it on this program's own documents** (fixed on
  2026-09-18, before this spec was committed):
  1. **It could not see a new doc.** It listed tracked files only, and reported "0 documents" for
     this program's uncommitted specs. That is exactly when `DESIGN-GATE.md` §5 says to run it. It
     now includes untracked, non-ignored files.
  2. **It would have failed every spec.** Specs, maps, plans and todos name the files they propose to
     create, and 87 citations in this program's own docs were proposals. **Exemption 6** makes a
     missing file LOW in a forward-looking doc, but only when **no line is cited** and **git history
     shows the file never existed.** The history condition came from measuring the first draft of the
     rule, whose comment claimed rot was "overwhelmingly line-numbered". It was not: 58 of 262
     line-less misses were deleted files, 14 of them in `spec-world-map-gaps.md`. With the history
     check, all 58 are HIGH again and every real proposal stays LOW.

- **A defect in the previous module's own evidence:** commit `99a288d1` reported `world-stage-ideal.md`
  10 → 0. It was actually 5, because the audit's line-level exemption didn't see a table header.
  Fixed on 2026-09-18 by marking each row, and recorded in the commit that lands this spec. The lesson
  is carried into the batch discipline above: **re-run the scope after the edit, and quote that
  output, never the intent.**
- **D4 was going to be a new script.** It belongs in the audit that already owns doc hygiene, so it
  was added as a code, not a new tool.
- **The audit had no `.ps1` entry point,** and the runner's catalog is keyed to scripts. The thin
  wrapper keeps one invocation convention.
