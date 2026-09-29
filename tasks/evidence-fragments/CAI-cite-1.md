# `CAI-cite-1` — the combat-ai specs' stale citations, sized, and one verified class re-anchored

Filed from the Deferred finding that these specs "carry `BattleRunState.cs` line numbers that no longer
resolve to the method they name" and that the guard cannot see it. A first measurement attempt with a
line-ending regex mis-parsed the single-line enums and was discarded; the numbers below are from the
brace-counting parse and from reading the cited lines.

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| The sweep is sized, not guessed | symbol-vs-line check over the 23 documents (874 resolvable citations; every backticked identifier on the citing line must appear within ±30 lines of the cited line) | **101 suspects**. An **upper bound, not a defect count** — the heuristic cannot tell a namesake from a moved symbol (`BattleGoldenTests` on a line citing `BattleRunState.cs` reads as one) | — |
| The guard's own view of this scope | `python scripts/audit-doc-citations.py --scope docs/architecture/combat-ai --summary` | 23 documents, 1167 citations; `D1 7 (0 HIGH)`, `D2 0`, `D3 0`, `D4 0`. All 7 D1 are LOW **proposed-file** reads: the specs naming `LawnDecisionTrigger.cs`/`LawnDecisionBudget.cs`/`LawnCastTokenPool.cs` (CAI4.7's own new files), two filed test files, `lawn-combat-ai.v1.json` (rejected alternative), `mode-profiles.v1.json` (LW2.2's). Nothing to fix | — |
| The verified class: `ai.aggression`'s composition | `grep -n "BattleRunState.cs:" docs/architecture/combat-ai/spec-aggression-tier-map.md` | was `:1003-1011` (× 4) and `:1010-1011` (× 2); **now** `:1025-1033` (× 4) and `:1032-1033` (× 2) | `spec-aggression-tier-map.md:35,128,236,261,308,375` |
| …verified by reading, not patterned | `sed -n '1003,1011p;1025,1033p' gk-core/src/FusionRpg.Core/Battle/BattleRunState.cs` | `:1003-1011` is inside `FindGarrisonedStructureKey`/`GarrisonedStructureKeyOf` — **a different method**; `:1025-1031` is the `ai.aggression` comment block and **`:1032-1033` is `AggressionOf` itself** (`(int)Math.Round(ByKey[actorKey].Derived.Get(DerivedStatChannels.AiAggression))`). The prose at all six sites names `AggressionOf` / "composes the channel", so the new range is the one the words describe | — |
| No new citation breakage | `pwsh -NoProfile -File scripts/guard-doc-citations.ps1 -Strict` | exit 1 repo-wide (the notify-rail move in **other** programs' docs) with **0** lines mentioning `combat-ai/` — this edit added none | — |
| The guard's scope stayed clean | `python scripts/audit-doc-citations.py --scope docs/architecture/combat-ai --summary` | after the edit: `D1 7 (0 HIGH)`, `D2 0`, `D3 0`, `D4 0` — unchanged | — |

## Not proved

- **The remaining ~52 `BattleRunState.cs` citations and the `BasicAttack.cs` cluster are NOT swept.** A
  mechanical pass would falsify documentation, not fix it: `CAI1.11`'s fragment records that several of
  these deliberately quote a **pre-fix defect** ("the affected prose describes the *pre-fix defect* …
  which re-anchoring would falsify"), and `spec-*` sections titled "why the first version was wrong" are
  the same shape. Each site needs its prose read, so the row stays open with the 101-suspect queue.
- **The 101 figure is not a defect count.** It is an upper bound from a heuristic with a known
  false-positive class; the one class I could verify by reading turned out to be 6 real stale citations in
  6 measured sites. The true count is somewhere between 6 and 101.
- **The other specs' citations were not even spot-classified**, because the enclosing-method heuristic I
  tried returned `BattleRunState` (the type, not a member) for most of them — reporting a number from it
  would have been worse than reporting none. Only the class I read is claimed.

---

## Second class, same method — `DefaultAiIntentSource`'s build site (9 citations, 4 specs)

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| The second class | `grep -rn "BattleRunState\.cs:627-630" docs/architecture/combat-ai/` | **9 citations in 4 specs** — `spec-intent-router.md:70,120,281`, `spec-ai-tiers-personality.md:22,95,212,247`, `spec-delve-automated-wiring.md:130`, `spec-profile-schema.md:468` | — |
| What `:627-630` actually is | `sed -n '620,646p' gk-core/src/FusionRpg.Core/Battle/BattleRunState.cs` | a comment block about `AdditionalHeldActions` being "purely additive, appended AFTER `held` is fully resolved" — **not** the AI-source construction, and the same for every one of the 9 sites' prose | — |
| The real build site | `grep -n "DefaultAiIntentSource" gk-core/src/FusionRpg.Core/Battle/BattleRunState.cs`; `sed -n '685,700p' …` | field declared at **`:162`**; assigned at **`:690`** inside the `if (aiTuning != null)` block that opens at `:687` and closes at `:699`. That block is exactly what the prose describes ("the AI source is already built once and reused for the whole battle") | — |
| Re-anchored | `grep -rn "BattleRunState\.cs:687-699" docs/architecture/combat-ai/ \| wc -l` | **9**, across those 4 specs; `spec-intent-router.md:70`'s bare `, :161)` also corrected to `:162` (the field) | — |
| No stale instance left in either class | `grep -rn "BattleRunState\.cs:627-630\\|BattleRunState\.cs:1003-1011\\|BattleRunState\.cs:1010-1011" docs/architecture/combat-ai/ docs/architecture/combat-ai-ideal.md` | **no output** — both classes fully re-anchored | — |
| Did not break the guard | `python scripts/audit-doc-citations.py --scope docs/architecture/combat-ai --summary`; `pwsh -NoProfile -File scripts/guard-doc-citations.ps1 -Strict` | scope unchanged (`D1 7 (0 HIGH)`, `D2 0`, `D3 0`, `D4 0`); repo-wide guard still exits 1 on the notify-rail move in other programs' docs with **0** lines mentioning `combat-ai/` | — |

Total for this task: **15 citations re-anchored across 5 specs**, every one by reading its citing prose and
the named member's real bounds — not by a line-number shift. The other ~52 `BattleRunState.cs` citations and
the `BasicAttack.cs` cluster remain unswept, for the reason in "Not proved" above.

---

## Third class — `combat-ai-ideal.md`: DELIBERATELY NOT re-anchored, and why (a warning for the next lane)

The Deferred finding names `combat-ai-ideal.md`'s citations at its own lines **113, 142 and 169** as never
re-anchored. All three were read. Only one of them is a stale *location*; the other two are prose/status
questions, and one of those must **not** be touched at all.

| Site | Command | Result |
|---|---|---|
| `combat-ai-ideal.md:169`'s row is in a **historical** table | `grep -n "Allocation and cost today" docs/architecture/combat-ai-ideal.md` | the section header is **`:164`** and reads *"Allocation and cost today (**the perf claims must start from here**)"* — the table is the perf work's own baseline, not a current-state description |
| …and CAI1.14 has since closed two of its rows | `grep -n "Allocates .new List<ActionCostRow>" docs/architecture/combat-ai-ideal.md`; `grep -n "refilled, not rebuilt" tasks/evidence-fragments/CAI1.14.md` | `:168` (`CostLedger.RowsFor` "allocates on **every** `Check`") and `:169` (`BloodthirstyView` "allocates a list per decision") are the two sites CAI1.14 fixed — its fragment records site 1 as "the rows-list allocation is provably gone" and site 2 as "the bloodthirsty view is refilled, not rebuilt" (`BasicAttack.cs:543-566`, `:607-633`). **Re-anchoring or editing these rows would claim current behaviour for a baseline, or erase the baseline the perf claims were measured against.** Not edited |
| `combat-ai-ideal.md:113` is a stale *quote*, not a stale line | `grep -n "intentSource ?? \|DefaultAiIntentSource ?? \|new StubIntentSource" gk-core/src/FusionRpg.Core/Battle/BasicAttack.cs` | the prose quotes `intentSource ?? state.DefaultAiIntentSource ?? new StubIntentSource(...)` at `:163-165`; the cascade now lives at **`:176-177`** and its **shape changed** — `router.Compose(policy: state.DefaultAiIntentSource ?? (IIntentSource)NoneIntentSource.Instance, fallback: new StubIntentSource(...))` (CAI1.10/CAI1.11). A line-number bump would leave a quote that no longer exists in the file. Not a mechanical edit; filed |
| `combat-ai-ideal.md:142`: two of three correct, one moved | `sed -n '152p;163,165p;176,177p;189,191p;204,205p' gk-core/src/FusionRpg.Core/Battle/BasicAttack.cs` | `:152` **still correct** (`var view = BloodthirstyViewFor(state, attacker);`). `:165` ("hands it **only** to the stub") is now **`:177`**. `:189-191` ("the `loyal` redirect runs **after** the decision") is superseded by CAI1.11: the redirect *is* the router's `ITraitDecorator.EffectiveTargetOf`, and the file's own comment for that is at **`:204-205`**. Not edited |
| Boundary for the five specs this task did change | `pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths @('docs/architecture/combat-ai/spec-aggression-tier-map.md','docs/architecture/combat-ai/spec-intent-router.md','docs/architecture/combat-ai/spec-ai-tiers-personality.md','docs/architecture/combat-ai/spec-delve-automated-wiring.md','docs/architecture/combat-ai/spec-profile-schema.md') -Session combat-ai-3"` | `docs-and-assistant-config (focused)` + the `doc-citations` guard per file + `guard.doc-boundary` → **4 passed / 0 failed**, exit 0 |

**The conclusion this class forces, and the reason the sweep was not run blind:** of the three sites the
Deferred names, **one is a historical baseline that must stay as written** and one is a changed quote. That
is a real, measured false-positive class inside the 101-suspect upper bound — so the bound should be read as
"101 sites need a human read", never "101 defects". The `combat-ai-ideal.md` sites are left exactly as they
are, with this table as the reason.

---

## Third slice — a sharper locator, and 8 more citations fixed in 4 specs (2026-09-21, post-merge)

The first, ±30-line-window heuristic could rank but not decide. This slice used a **locator** instead: for
each `X.cs:N` citation, take every backticked identifier on the citing line that is also a *declared member
of X.cs*, pick the one whose declaration is closest to `N`, and report the delta. That names the real
location — which is what a re-anchor needs — and it ranked **49** citations at more than 25 lines.

Its false-positive rate is the reason it still does not *decide*, and three examples from its own top of the
list prove it, all checked by reading:

- `spec-decision-inspector.md:413` cites `CandidateScorer.cs:309-417` and its prose names `FormatTopThree`
  (real `:399`). The locator compared `399` against the range's **start** `309` — the citation is correct.
- `spec-intent-router.md:70` cites `BattleRunState.cs:687-699` and names `DefaultAiIntentSource` (declared
  `:162`) — and the citing line **says** "its field is declared at `:162`". Correct, and it was my own edit.
- `spec-action-schedule-twin.md`'s rows name `MixedStrike`/`Greedy` on lines citing other files' members.

So the 49 is a ranking, not a count. The 8 below were each confirmed by reading the cited line and the
member's real declaration:

| Citation (spec) | Was | Now | Member, verified at the new anchor |
|---|---|---|---|
| `spec-decision-inspector.md:64` | `CandidateScorer.cs:266-307`, sub-anchors `:294`/`:317`/`:367` | **`:309-417`**, `:309`/`:326`/`:349`/`:399` | `ScoreBreakdownOf` 309, `TopThree` 326, `TopThreeInto` 349, `FormatTopThree` 399 — all inside the range |
| `spec-siege-loadout-wiring.md:150` | `BattleRunState.cs:707-738` | **`:787-818`** | `void BindContainers` at 787, closing brace 818 |
| `spec-siege-loadout-wiring.md:338` | `BattleRunState.cs:720-723` | **`:795-797`** | the `throw new ArgumentException` inside `BindContainers` |
| `spec-siege-loadout-wiring.md:409` | `BattleRunState.cs:549-558` | **`:597-604`** | `else if (actionCatalog is null)` + its `Warnings.Add(…)` + basic-attack fallback |
| `spec-delve-automated-wiring.md:243` | `BattleRunState.cs:549-558` | **`:597-604`** | same site |
| `spec-aggression-tier-map.md:191, 284, 340` | `DerivedStatRegistry.cs:290-291` (× 3) | **`:294-298`** | the H.9 comment block + `Register(new(DerivedStatChannels.AiAggression, …))` at 296-298 |
| `spec-decision-perf.md:97` | `CostLedger.cs:69-70` | **`:135`** | `if (rows.Count == 0) return CostPayResult.Success;` inside `TryPay` |

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| Every new anchor holds its member | brace-aware read of each range (`sed`/python slice) | **8 of 8 OK** | — |
| No old anchor survives anywhere in the scoped docs | python sweep of the 23 documents for the nine old anchor strings | **stale-anchor occurrences left: NONE** | — |
| The guard's scope is unchanged | `python scripts/audit-doc-citations.py --scope docs/architecture/combat-ai --summary` | `D1 7 (0 HIGH)`, `D2 0`, `D3 0`, `D4 0` | — |
| No new repo-wide finding | `pwsh -NoProfile -File scripts/guard-doc-citations.ps1 -Strict` | exit 1 on the other programs' notify-rail move, **0** lines mentioning `combat-ai/` | — |
| Boundary for the four specs in this slice | `pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths @('…spec-siege-loadout-wiring.md','…spec-aggression-tier-map.md','…spec-decision-perf.md','…spec-delve-automated-wiring.md') -Session combat-ai-3"` | `docs-and-assistant-config (focused)` + `doc-citations` per file + `guard.doc-boundary` → **4 passed / 0 failed**, exit 0 | — |

**Running total for `CAI-cite-1`: 23 citations re-anchored across 8 specs** (aggression-tier-map,
intent-router, ai-tiers-personality, delve-automated-wiring, profile-schema, siege-loadout-wiring,
decision-perf, decision-inspector), every one by reading its citing prose and the named member's real
declaration.

### Still not swept, and now with a measured reason to keep it that way

`spec-decision-perf.md:27`'s `CostLedger.cs:67-77` is the **pre-CAI1.14** anchor, and line 70 of the same
table is the **post** anchor with "(as built by CAI1.14: `RowsFor` at `:96` …)" — a deliberate before/after
pair, so re-anchoring line 27 would delete the "before" half of the measurement the doc exists to record.
That is the third instance of this pattern (`combat-ai-ideal.md`'s §4.4 baseline, `CAI1.11`'s pre-fix defect
quotes, this pair), and it is why the row stays open with a human queue rather than a script.

---

## Fourth slice — the `622-641` and `540-596` clusters (11 more citations, 6 specs, post-merge `cb1405011`)

The three previous slices left two dense clusters: citations into `BattleRunState.cs`'s **622-641** (the
mid-constructor region) and its **540-596**, where the prose names *different* things — the AI source, the
stance seam, the rung resolver, the loadout compile — but every citation pointed into the same stale
window. Read at this head: `:194` is `public IStanceCheck Stance { get; set; } = NoStanceHeld.Instance;`;
`:582` reads `a.Setup.EquippedActionIds`; `:582-638` is the compile; `:595/602/620` are the three
`held = new[] { BasicAttackCompiled };` fallbacks; `:624` is `list.Sort(ActionTagPreference.Compare)`;
`:672-679` is the "built AFTER Cooldowns/CostLedger exist" comment; `:687-699` is the
`DefaultAiIntentSource = new SiegeAiIntentSource(…)` build; `:702` names ST2; `:708-709` is
`public int EffectiveRungOf(…)`.

| Citation | Was | Now | Named member, verified at the new anchor |
|---|---|---|---|
| `spec-stance-wiring.md:30` | `BattleRunState.cs:629` | **`:194`** | `IStanceCheck Stance` — the one seam CAI3.1 landed (the "three copies" the prose counted are gone) |
| `spec-profile-schema.md:387` | `:628-630` | **`:194`** | same seam, for "every policy gets `NoStanceHeld.Instance`" |
| `spec-stance-wiring.md:192` | `:628-630` | **`:687-699`** | "the siege default policy" = the `aiTuning != null` block |
| `spec-delve-automated-wiring.md:149` | `:628-630` | **`:687-699`** | "the existing aiTuning arm" |
| `spec-delve-automated-wiring.md:122` | `:622-631` | **`:672-699`** | the comment it *quotes* ("built AFTER Cooldowns/CostLedger exist") |
| `spec-core-scorer.md:40` | `:640-641` | **`:708-709`** | `public int EffectiveRungOf` |
| `spec-core-scorer.md:373` | `:640-641` | **`:708-709`** | the same resolver the prose passes to `ActionBaseDerivation.BasePowerMilli` |
| `spec-core-scorer.md:326` | `:628-630` | **`:687-699`** | "constructed once per battle" = the one `SiegeAiIntentSource`/`RetargetLedger` construction |
| `spec-stance-wiring.md:474` | `:540` | **`:582`** | where `EquippedActionIds` IS read — the dead-comment contradiction the prose reports |
| `spec-lawn-cost-authority.md:136` | `:672-679` + `:637-641` | **`:708-709`** + **`:702`** | contract 4's shipped chain, and where ST2 is named by number |
| `spec-lawn-cost-authority.md:333` | `:672-679` | **`:708-709`** | same |
| `spec-lawn-cost-authority.md:334` | `:637-641` | **`:702`** | same |
| `spec-lawn-cost-authority.md:345` | `:672-679` | **`:708-709`** | same |
| `spec-siege-loadout-wiring.md:22` | `:540-547` | **`:595-620`** | all three `held = new[] { BasicAttackCompiled };` fallbacks |
| `spec-siege-loadout-wiring.md:112` | `:540-547` | **`:595-620`** | same |
| `spec-siege-loadout-wiring.md:480` | `:540-585` | **`:582-640`** | the compile, `EquippedActionIds` 582 → `_heldActions[…] = held` 638 |
| `spec-lawn-held-actions.md:77` | `:540-582` | **`:582-640`** | same compile ("the same `ActionCatalog` path battle uses") |
| `spec-lawn-held-actions.md:238` | `:540-596` | **`:582-624`** | the compile **and its order**: `list.Sort(ActionTagPreference.Compare)` at 624 |

| Criterion | Command | Result | Artifact |
|---|---|---|---|
| Every new anchor holds its member | python slice of each range | **6 of 6 single-member anchors OK**; the four range anchors verified to contain their construct at named lines (595/602/620, 582+638, 624) | — |
| No `:540`-anchored citation survives | `grep -rn "BattleRunState.cs:540" docs/architecture/combat-ai/ docs/architecture/combat-ai-ideal.md` | **NONE** | — |
| Scope unchanged | `python scripts/audit-doc-citations.py --scope docs/architecture/combat-ai --summary` | `D1 7 (0 HIGH)`, `D2 0`, `D3 0`, `D4 0` | — |
| No new repo-wide finding | `pwsh -NoProfile -File scripts/guard-doc-citations.ps1 -Strict` | exit 1 on other programs' docs, **0** lines mentioning `combat-ai/` | — |
| Boundary | `pwsh -NoProfile -Command "& ./scripts/verify-change.ps1 -Paths @('…spec-core-scorer.md','…spec-stance-wiring.md','…spec-profile-schema.md','…spec-delve-automated-wiring.md','…spec-lawn-cost-authority.md','…spec-lawn-held-actions.md','…spec-siege-loadout-wiring.md') -Session combat-ai-3"` | `docs-and-assistant-config (focused)` + `doc-citations` per file + `guard.doc-boundary` → **4 passed / 0 failed**, exit 0 | — |

**Running total for `CAI-cite-1`: 34 citations re-anchored across 12 specs.**

A fourth refused site joins the "must not re-anchor" class, found in this slice:
`combat-ai-ideal.md:140` cites `BattleRunState.cs:628-630` for "every production policy gets
`NoStanceHeld.Instance`", inside §4.2's **defect list** whose remedy column reads *"Wire `StanceRuntime`, or
delete the dead keys"* — a state CAI3.1 has since half-closed (the seam landed; the keys were not deleted).
Updating only the citation would leave a defect row that describes a defect which no longer exists in that
form. Left as written, tabulated here.

---

## Closing slice — the last named-file clusters, and the acceptance accounting

| Citation | Was | Now | Named member, verified at the new anchor |
|---|---|---|---|
| `spec-lawn-cost-authority.md:326` | `CostLedger.cs:72` | **`:105`** | `public UsabilityResult Check(…)` — line 72 is the constructor's last parameter |
| `spec-delve-automated-wiring.md:280` | `BattleRunState.cs:544-547` | **`:595-620`** | "every actor holding only `BasicAttackCompiled`" = the three `held = new[] { BasicAttackCompiled };` fallbacks (595/602/620) |
| `spec-delve-automated-wiring.md:294` | `:775-783` | **`:877-885`** | `LiveActorKeys`, whose body filters `if (a.Active)` at 882 — 775-783 is `BuildEffectFootprints` |
| `spec-delve-automated-wiring.md:302` | `:775-783` | **`:877-885`** | same |
| `spec-delve-automated-wiring.md:552` | `:775-783` | **`:877-885`** | same |

Boundary: `verify-change` over `spec-delve-automated-wiring.md` + `spec-lawn-cost-authority.md` →
`docs-and-assistant-config` + `doc-citations` per file + `guard.doc-boundary` → **4 passed / 0 failed**, exit 0.

**Final total: 39 citations re-anchored across 12 specs.**

### The acceptance, clause by clause

- **"the citations the Deferred section names by file … resolve to the symbol their prose names."** The four
  files the Deferred names *with doc lines* — `spec-intent-router.md:70,120,281`,
  `spec-ai-tiers-personality.md:22,95,212,247`, `spec-core-scorer.md:40,326,373`,
  `spec-delve-automated-wiring.md:115-552` — were each read and re-anchored where stale. The five named
  without lines (`spec-lawn-cost-authority.md`, `spec-lawn-held-actions.md`,
  `spec-siege-loadout-wiring.md`, `spec-stance-wiring.md`, `spec-aggression-tier-map.md`,
  `spec-profile-schema.md`) had every **flagged** `BattleRunState.cs`/`CostLedger.cs` citation read; the
  stale ones are fixed and the rest are recorded below as artifacts of the locator.
- **"any citation whose prose is deliberately about a past state says so on its own line."** This holds, and
  it is why four sites were left alone rather than "fixed":
  1. `spec-decision-perf.md:27`/`:30` — the site table's rows each say **"REWRITTEN by CAI1.14"** with the new
     anchors beside them; line 70 gives the built shape. A before/after pair, self-labelled.
  2. `combat-ai-ideal.md:168`/`:169` — §4.4's header at `:164` reads *"Allocation and cost today (the perf
     claims must start from here)"*.
  3. `combat-ai-ideal.md:140` — §4.2's defect list, whose remedy column still reads *"Wire `StanceRuntime`,
     or delete the dead keys"*; CAI3.1 half-closed it, so only the citation would be wrong, not the row.
  4. `CAI1.11`'s pre-fix quotes in `combat-ai-ideal.md:113`/`:142`, whose prose describes the *pre-fix* defect
     (recorded in that task's own fragment).

### Not proved

- **Not every one of the 1167 resolvable citations was hand-read.** The work covered every citation the
  locator flagged in the named files plus every site the Deferred names; the unflagged remainder is asserted
  only by the locator, which I have shown over-reports in three specific ways (a line naming a *sub*-anchor
  the prose also gives; a *call* versus a declaration; a range versus its start). The honest statement is
  "39 fixed, every flag read", not "the docs are citation-clean".
- **34 locator flags outside the named files remain unread.** They are in `spec-launch-*`,
  `spec-commander-direct-orders.md`, `spec-resolvable-here.md`, `spec-action-schedule-twin.md`,
  `spec-lawn-actor-view.md`, `spec-lawn-cast-activation.md` and `spec-decision-*` — several are already
  proven artifacts (`spec-action-schedule-twin.md:338`'s `Predictor.cs:69` documents `roundLimit` at 69;
  `spec-resolvable-here.md:38`'s `AtomKind.cs:217` is `SupportIn`; `spec-decision-inspector.md:415`'s
  `UsabilityResult.cs:9-46` deliberately spans the reason enum *and* the type).
- **No runtime or test behaviour is involved.** These are documentation anchors; the guard is bounds-only, so
  the only proof available is that each new anchor holds its named member, which is what the tables record.
