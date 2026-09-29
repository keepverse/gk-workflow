# spec — `vocabulary-single-declaration`

**Module 9 of `solid-remediation`.** Register entries: **X1, X2**. Depends on `green-baseline`.

Independent of the battle chain, so it can run in parallel with it.

## Objective

Status categories and element ids are declared once. Two closed vocabularies currently have two
declarations each, and one of the pairs **disagrees on failure**.

## The defects

**X1 — status id to resist category is declared twice.** One vocabulary, two owners; they can drift, and
nothing refuses the drift.

**X2 — two element-id switches that disagree on failure.** This is the one to fix first inside the module:
one returns `""` where the other throws, so **a missed element reads as a neutral matchup with no
error**. A silent wrong answer is worse than a crash, because nothing reports it and the number looks
plausible.

Both are rule 2 — one mechanism, two owners — and both are **shares** in the ideal doc's ladder: route
the second implementation at the first, or alias it.

## Shape

For each vocabulary:

1. **One declaration.** The closed set lives in exactly one place.
2. **One failure mode.** A missing member throws, naming the member. Never `""`, never a default. This
   repo's T5 rule is explicit: a default is a number nobody chose that behaves like one somebody did.
3. **The second site calls the first**, rather than being deleted and re-derived. The mapping is content;
   re-deriving it risks changing it.

## Tests to rewrite

Any test asserting the `""` return is pinning X2 and must be restated: an unknown element **throws**.

Assert the **closed vocabulary** — the member set and its size — and say why the literal is pinned: these
are enums the code owns and a human changes, which is exactly the case where pinning a count is correct.
Do not assert how many statuses or elements any content tree happens to use; that is a population.

## Boundaries

- **Always:** one declaration, one failure mode, and the failure names the missing member
- **Ask first:** changing what a status maps to. Moving a mapping is this module; re-deciding it is a
  content change with a different owner
- **Never:** keep the lenient branch "for compatibility". That branch is the defect

## Verification

```powershell
.\scripts\verify-change.ps1 -Paths <declaration> <former second site> <tests> -Session solid-remediation-<date>
```

- [ ] One declaration per vocabulary; the former second site calls it
- [ ] An unknown element throws, naming it — asserted, not assumed
- [ ] An unknown status category throws, naming it
- [ ] `battle-responsibility-guard` green

## Success criteria

A missed element is impossible to mistake for a neutral matchup. That is X2's whole risk, and it is
silent today.
