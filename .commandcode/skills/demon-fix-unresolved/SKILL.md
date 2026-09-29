---
name: demon-fix-unresolved
description: Deterministically resolve demon anchors stuck at "unresolved" after a classification run — threatBand and rarity (derived from a real signal) and, since 2026-09-07, aptitudePrimary too (an invented flat default, since no real signal exists for it). Use after reading DemonQualityReport's unresolved-rate finding, when you want to close the remainder without spending more model calls — never automatically. elementPrimary is the one field still with no fallback of either kind.
---

# demon-fix-unresolved

**This is a fix STEP, not part of classification.** It never runs automatically during
`start`/`resume`/`rerun` — a human reads the audit, decides the remaining unresolved rate is worth
closing deterministically, and runs this on demand. It makes zero model calls.

## Two different kinds of fallback, and why

Four fields can end up `"unresolved"` after a genuine 3-way vote split: `elementPrimary`,
`aptitudePrimary`, `rarity`, `threatBand`. Three now have a fallback — but not the same *kind* of
fallback, and the difference matters:

| Field | Fallback signal? | Kind | Verdict |
|---|---|---|---|
| `threatBand` | `data/tuning/demon-threat.v1.json`'s own `inferredDefaultRung` — already committed, already the sanctioned answer for "no reliable signal," just never wired to this specific case before | **Derived** | **Yes — deterministic fix applies** |
| `rarity` | Falls back to the SAME species' own `threatBand` (real or itself just defaulted, same pass) via `data/tuning/demon-rarity-power-fallback.v1.json`'s rank-preserving correspondence — stronger species land on rarer rungs, reusing `demon-threat.v1.json`'s own already-validated power banding rather than inventing a second curve | **Derived** | **Yes — deterministic fix applies (Phase H)** |
| `aptitudePrimary` | Measured directly (2026-09-07), not assumed: of the 151 species with a computable power score AND a resolved aptitude, a one-way ANOVA of score-by-aptitude comes back at **F≈1.34 — noise, not separation** — and 10 of the 11 real unresolved species have no computable score at all to feed a classifier with. **No real signal exists to derive from, at all.** | **Invented** | **Yes — a flat default applies (Phase I), on explicit owner direction that this is fine for a game-invented mechanism when a real derivation genuinely doesn't exist** |
| `elementPrimary` | Purely thematic/lore, zero numeric anchor of any kind; currently moot anyway (0/840 unresolved as of 2026-09-07) | — | No fallback of either kind |

`rarity`'s own prompt description (`descriptions.py`) still tells the model "never conflate this
with threatBand" — that instruction is about keeping the model's OWN real judgment independent of
perceived danger during a REAL classification, and stays correct. It is a different, narrower
concern from what a deterministic fallback may do once voting has already failed to produce a
judgment at all — see `resolve_unresolved_rarity`'s own docstring in
`tools/seedsmith/seedsmith/adapters/demons/anchor/derive.py`.

`aptitudePrimary`'s fallback is intentionally NOT dressed up as a derivation anywhere — the tuning
file's own `_note`, the function's own docstring, and this doc all say plainly that
`demon-aptitude-fallback.v1.json`'s `inferredDefaultAptitude` (`"Onslaught"`, picked because it is
already the single most common aptitude in the real corpus — 332/840, 395‰) is an invented
convention, not a calculation. **Do not extend a fallback to `elementPrimary`** unless a real
signal or an explicit owner decision to invent one is made first — silently assuming one exists is
the failure mode this whole investigation was built to avoid.

## When to use

After any classification/self-heal pass, once `DemonQualityReport`'s own Section 1 (`Unresolved
rate per voted field`) shows a count you want closed without another LLM run. Typical flow:

```powershell
cd gk-forge/tools/seedsmith

# 1. See what would change, before touching anything
python -m seedsmith demons run fix-unresolved --dry-run

# 2. Apply it for real
python -m seedsmith demons run fix-unresolved

# 3. Re-measure
cd ../..
dotnet run --project tools/DemonQualityReport
```

## What it does, precisely

For every real anchor: `threatBand` first, then (using that same pass's own resulting
`threatBand`) `rarity`, then — independently, nothing chains into it — `aptitudePrimary`:

- `threatBand` resolves to `demon-threat.v1.json`'s `inferredDefaultRung`'s own rung id (currently
  `raider`, rung 4) — the SAME value already sanctioned for "no computable score at all," reused
  for "the vote genuinely never converged," the same underlying situation (no reliable signal).
- `rarity` resolves to whatever `demon-rarity-power-fallback.v1.json` names for that species'
  (possibly just-fixed) `threatBand` rung — a table, never a formula. If `threatBand` has no value
  at all (missing, not merely the "unresolved" sentinel), `rarity` correctly stays `"unresolved"`.
- `aptitudePrimary` resolves to `demon-aptitude-fallback.v1.json`'s flat
  `inferredDefaultAptitude` — no other field feeds it, because nothing correlates strongly enough
  to be worth reading. `posture`/`pure` (both functions of `aptitudePrimary`) are recomputed in the
  same write so they never go stale relative to the fixed value.
- Each fixed field's `_provenance.confidence[field]` is stamped `"deterministic-fallback"` — never
  `"high"` or `"split"` — so nothing downstream (a report, a human, another tool) can mistake this
  for a real LLM judgment. If you ever see that string in an anchor, that field's value came from
  this fix step, not a classification pass.
- Leaves `dumpHash`/every other field/every other pipeline's own provenance untouched — this fix
  never re-reads the corpus dump and never claims a pipeline ran that didn't.
- Idempotent — running it twice in a row does nothing the second time (nothing left to fix).

It never touches `elementPrimary` — stays `"unresolved"` and visible in the next
`DemonQualityReport` if it ever becomes non-zero, which is the honest, correct outcome when no
fallback of either kind exists.

## Real result, 2026-09-04 (threatBand)

10 real species (`Jalakelp`, `DoomChomper`, `SwordStar`, `DoomBlover`, `IceBean`, `MagnetDoom`,
`UltimateTorch`, `HypnoQueen`, `HypnoTorch`, `CherryTorch`) had `threatBand: "unresolved"` after the
E1/E2 self-heal pass. All 10 resolved to `raider` — which also happened to be the one `threatBand`
value the corpus had NEVER used at all (`DemonQualityReport`'s Section 2 flagged `raider` as
unused), so this closed two findings from the same audit at once.

## Real result, 2026-09-07 (rarity, Phase H, then aptitude, Phase I)

By the time rarity's fallback was built, the live corpus already showed **0/840 unresolved
`rarity`** (the 15/840 open as of Phase E on 2026-09-04 had since been closed by later work,
verified live via `DemonQualityReport` before shipping — `--dry-run` correctly reported "0
field-fixes"). It shipped anyway as standing infrastructure for the next corpus expansion.

`aptitudePrimary` was different: 11/840 (13‰) were genuinely still open, and this time the fix
landed on real work. Applied for real the same day: `Tower_iceGloom`, `ZombieEndoFlame`,
`AllPeater`, `NutTorch`, `BloverPot`, `EnumValue265`, `EnumValue267`, `Extract_single`, `Refrash`,
`EnumValue268`, `SnorkleZombie` — all 11 resolved to `Onslaught`. `DemonQualityReport`'s "Unresolved
rate per voted field" section is now **completely empty** — for the first time, every voted field
across all 840 species is resolved, by a real classification or an honestly-labeled deterministic
fallback. Re-running the fix confirms idempotency (0 field-fixes the second time).
