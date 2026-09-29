# Numeric types — overflow is RANGE, precision is a separate question

**Status: SSOT for numeric type choice.** Moved here from `CLAUDE.md` (2026-09-27) so the rule has a
document path a code comment can cite. It previously lived only in assistant config, and 458 tracked
files cited it there — including 77 under `src/` — which `scripts/audit-doc-citations.py:85`
**exempted from citation checking**, so a stale or moved rule would have gone unnoticed.

Read this when choosing a numeric type, widening arithmetic, or narrowing a conversion.

---

## The two concepts, never conflated

Owner ruling 2026-09-15 — conflating them misled every agent in this repo into a floating-point ban:

- **Overflow** = the value is bigger (or smaller) than the type can hold at all. In C#, integer
  overflow **wraps silently** unless the arithmetic is `checked` — a real defect. Floating overflow
  becomes ±Infinity.
- **Precision** = how finely a type represents values. `float`/`double` hold fractions and enormous
  values, but not every integer exactly past 2^24 (`float`) / 2^53 (`double`). That is **rounding** —
  not overflow, and not a reason to ban floating point.

**Floating-point is allowed** — for magnitudes, ratios, chances, rates, multipliers, curves, anything.
Earlier text said *"Never `float` for a magnitude"* and listed each type's *exact-integer* ceiling as
if it were an overflow threshold. That was a comprehension error, and every float ban, float
source-scan test and "integer per-mille instead of a float" rule copied from it **is void**.

## The range table

`P(Θ)` is quadratic, so magnitudes grow far. Thresholds from the shipped curve (`B=0.4`):

| Type | Largest value it holds | First `Θ` whose magnitude exceeds it | Use |
|---|---|---|---|
| `int` (whole units) | 2,147,483,647 | 103,557 | Only where a proven bound sits below that |
| `int` holding per-mille of a magnitude | 2,147,483,647 (= 2,147,483 units) | 3,213 | Avoid — the ×1000 eats the range |
| `long` | 9,223,372,036,854,775,807 | 214,748,300 | Default for integer magnitudes and counts |
| `float` | ≈3.4 × 10^38 | not reachable | Allowed |
| `double` | ≈1.8 × 10^308 | not reachable | Allowed |

## The five rules — all about range

1. **Choose a type whose range holds the value at reachable `Θ`.** For an integer magnitude
   `contentScale` can touch (hp, atk, damage, defense, item values, yields) that means `long`, not
   `int`.
2. **Widen before multiplying** — `(long)a * b`, never `(long)(a * b)`. The cast binds to the
   *result*, so the multiply has already overflowed.
3. **Integer overflow throws, never wraps.** `checked` on integer magnitude arithmetic; no silent
   `unchecked`.
4. **Narrowing is checked or reported, never silent** — `double`→`long`, `long`→`int`. Unity's own
   `int` HP/attack fields are a host limit, reported through
   `EntityStatWriter.ClampToInt32Reporting`.
5. **Integer division truncates** — in integer per-mille math, divide by 1000 last so truncation
   happens once; the product before it must still fit the range (rule 2). **Not** a rule about floats.

## Determinism is a separate note, not a ban

A `double` result that feeds a hashed or persisted golden can differ in its last bits across runtimes
— record the platform stamp ([power/ssot-power-scale.md](power/ssot-power-scale.md) §10.7).

## Audit

Run before finishing work that touches a magnitude:

```powershell
python gk-core/scripts/audit-overflow.py               # integer range: narrowing casts, int magnitudes, unchecked
python gk-core/scripts/audit-overflow.py --targets A3  # file:line list for targeted work
```

## Related

- [power/ssot-power-scale.md](power/ssot-power-scale.md) §9.4 (integer safety on the shipped curve) and
  §11 (the cap register) — **one power ladder**, `Θ` for contests and `P(Θ)` for magnitudes.
- [../contributing/testing-standard.md](../contributing/testing-standard.md) — the in-memory store
  rule that keeps a test from leaking a file handle.
- [validation-ssot.md](validation-ssot.md) — why a *population* count is a reading, never a pinned
  literal.
