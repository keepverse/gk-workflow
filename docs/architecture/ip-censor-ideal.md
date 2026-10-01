# IP censor — the ideal

> ### ⚠️ Status line vs. what shipped (checked 2026-09-20)
>
> **This document's status line is not current.** It says *"idea phase ... Not a spec. No build
> authorized."* Measured today: [ip-censor-map.md](ip-censor-map.md) reads **"Map approved by the
> owner 2026-09-19 ('approve, go'). Module specs authorized"** — **9** module specs are written at
> `docs/architecture/ip-censor/spec-<module-id>.md`, and `tasks/ip-censor-todo.md` exists with
> **0 done / 46 open**. The map's own text still gates the *build* ("no build authorized").
>
> Read this document for its reasoning and its decisions, never for its status. Verify anything
> load-bearing against the capability map, the module specs, the task list, and the code.

**Status:** idea phase, 2026-09-19. Not a spec. No build authorized. Program id: `ip-censor`.

**This doc answers one question:** *how do we detect third-party IP in this repo, and what should the
tool and the gate actually do?* It is the phase before `/spec`; it stops here.

---

## Which loop this extends

**None, and it does not invent one.** This is not a player-facing feature and it adds no loop to
[the-loops.md](../guide/the-loops.md). It is a cross-cutting **content gate** that protects the
*named content* four existing loops surface:

| Loop (`the-loops.md`) | The names this protects |
|---|---|
| **A. Level up and power** | passive-tree node names (`gk-data/packs/fusion/data/seed/passive-tree/nodes/**`) |
| **B. Creature summon and fusion** | species `displayName` / traits (`gk-data/packs/fusion/data/seed/creatures/**`) |
| **C. Item collection and progression** | unique/item names, set/charm names (`gk-data/packs/fusion/data/seed/items/**`) |
| **7. Quests and events** | delve rooms, dungeon, event copy (`gk-data/packs/fusion/data/seed/dungeon/**`) |

Stated explicitly because the skill's rule is to name a loop or escalate: a feature that adds no loop
must **say so** rather than manufacture a parallel pitch. Nothing here is a new pitch — the genre is
unchanged (RPG + empire building over a legal PvZ Fusion install).

---

## Step 0 — the principles this must not break (restated, not linked)

These are restated inline on purpose. A downstream session reads this doc, not its links.

1. **Every RPG feature lives in the RPG layer; it is never built by changing what PvZ is.** Here the
   sharpest consequence: **this repo's deliberate use of PvZ's own world — plants, zombies, Crazy
   Dave, Penny, Zomboss — *is the product*, is owner-approved, and is out of scope for censorship.**
   A blanket "strip all IP tokens" tool would delete the product's identity. The gate must know the
   difference between *the licensed/fan-work premise* and *an accidental third-party mark*.
   **⚠️ Amended 2026-09-19 (owner rulings R8–R9, [npc-story-events-ideal.md](npc-story-events-ideal.md) §10):**
   for **narrative text** the leads take original names and prose never names a species by its PvZ or
   Fusion name; existing surfaces are renamed. So Crazy Dave, Penny and Zomboss are **in** scope on the
   player-facing narrative surface (see "Narrative generation" below). Code identifiers and the
   plants/zombies premise itself stay out of scope.
2. **Generated seed data is never hand-edited — fix the generator and regenerate.** Passive-tree node
   names are generator output carrying provenance (`gk-data/packs/fusion/data/seed/passive-tree/nodes/command.json:542`
   `"promptVersion": "tree-language/3"`; `:5` `_meta.model`). Editing `"Overwatch Protocol"` by hand
   forks the corpus from its generator and the next run reverts it. The sanctioned path is a
   **generator/prompt change + regenerate**.
3. **A guardrail validates the CONTRACT and closed enums — never a population count or generated
   text** ([validation-ssot.md](validation-ssot.md)). So an IP gate asserts *envelope, join,
   uniqueness, determinism* over a registry — it must never pin "the registry has N marks" or "the
   corpus has zero hits". The registry is a **closed vocabulary** (a human edits it) so *its own*
   member list may be pinned; the **hit population** is a reading and must not be.
4. **A debug API may trigger a real operation, never fabricate its result.** Same spirit for a gate:
   a scanner may *report*, but a "smart replace" may only rewrite a token when a human authored the
   replacement — never invent a substitute name.
5. **The balance surface is data.** The registry is authored data in a registry directory (see
   Tunables) — never a `const` in tool code.

**DESIGN-GATE §5 note:** this doc is a pre-proposal artifact. It introduces no code, so no session
boundary or test run is owed; the checklist is satisfied at `/spec` time when paths exist. One item
is honestly **not** ticked: **no legal review has been done, and this is not legal advice.** See
"Open questions" and "Prior art §5".

---

## What this is, in one paragraph

The repo occasionally ships a **player-visible name that collides with a third-party mark** — usually
because an LLM naming prompt had no avoid-list. We need (a) a **census** that can list every distinct
token across the tracked tree, (b) a **scope-aware scanner** that flags a token from a curated
third-party-IP registry *only where it matters* (player-facing names, and generator prompts that
produce them — not the deliberate PvZ identity and not attributed research citations), and (c) a
**deterministic rename primitive** for the narrow case where an exact token has a human-authored
replacement. The scanner and the gate are the deliverable; the rename primitive is a proven
capability that currently exists **only as a deleted throwaway script**.

---

## What already exists — three buckets

### ✅ BUILT

| Thing | Where | What proves it |
|---|---|---|
| A repo-wide, word-boundary, case-preserving content+path rename **was proven**. | *No committed file.* Recorded only as history: a temp script at `%TEMP%\kilo\rename_vocab.py` (now **deleted**), run 2026-09-12; outcome recorded in `docs/guide/glossary.md:61` and `docs/architecture/gameplay-tiers-ideal.md:71` (commit `740920d2`, "3,914-path rename"). | The rename is done and the tree is clean; the *capability* was demonstrated, then discarded. Reading counts from that run (~25,640 replacements / 2,342 files / 1,800 paths) are **historical readings, not constants**. |
| Deny-word gate that **already enforces one banned word at three points**: prompt, model answer, emit. | `gk-forge/tools/seedsmith/seedsmith/adapters/items/combogen/grid.py:32` (`BANNED_WORD = "runeword"`), `:199-207` (`scan_for_banned_word`, case-insensitive + `r"rune[_\- ]word"`); call sites `combogen/emit.py:50-52`, `combogen/brief.py:121-125`, `workflow/graphs/item_combination.py:94-96`. | This is the **exact shape the IP gate needs** — a ban that stops outbound briefs *and* inbound answers *and* the minted id. Its word list is one internal term, not IP. |
| Scope-aware player-copy vocabulary scanner with word-boundary matching + an allow-listed dev surface set. | `gk-web/web/fusion-rpg-web/src/i18n/vocabularyGuard.ts:42-70` (`BANNED_WORDS`, `\b…\b`), `:16-37` (`ALLOW_LISTED_PREFIXES`), `:137` (`scanForBannedVocabulary`). | Tests prove the boundary discipline: `vocabularyGuard.test.ts:110,181` ("does not flag a word that merely contains a banned substring"). |
| Protected-span (comment/string) strippers — the machinery a careful renamer needs. | `gk-core/scripts/cscan.py:246` (`strip_comments_and_literals_preserving_layout`); `gk-core/scripts/guard-test-substrate.py:55-101`. | Reusable, already correct, currently used only by scanners. |
| Dry-run-by-default single-file move with namespace/using/.csproj rewiring + revert. | `gk-core/tools/FileMove/Program.cs:5-11`, `FileMover.cs:24-116`, `MovePlan.cs:49-104`; tests `gk-core/tests/FusionRpg.FileMove.Tests/FileMoverTests.cs`. | A **mover**, not a token renamer — but it is the committed precedent for safe filesystem mutation (dry-run default, refused plans). |
| Authored `nameKey` derivation (`slug(name)`), so a renamed display name deterministically re-derives its key. | `gk-forge/tools/seedsmith/seedsmith/adapters/trees/nodegen/run.py:652-682` (`_slugify`, `_derive_unique_name_key`); `adapters/items/setgen/schema.py:53-58`. | Means a rename of `name` does not require hand-editing `nameKey` — the generator owns it. |
| The provenance fields that identify generated rows. | `gk-data/packs/fusion/data/seed/passive-tree/nodes/command.json:5,542`; `gk-data/packs/fusion/data/seed/items/uniques/**` per-file `_meta`. | Lets a gate route a finding to *generator* vs *authored* file. |

### ⚠️ WIRING GAP (machinery exists and is inert — not a wall)

| Thing | Where the inert line is | What is missing |
|---|---|---|
| **The rename tool itself.** The demon→creature capability is not a committed tool: no `.ps1`/`.py` under `scripts/**` or `tools/**` mentions the token; the throwaway script is gone. | Nothing to point at — the gap is *absence of a file*. The proven logic (word boundary, case map `demon/Demon/DEMON`, protected spans `demonstrate|Demonic|Pandemonium|Enslave_Demon|<base64 hash>`, force-map for one build-cache token, `git mv` paths, `--check` on the staged tree, rehearsal on a clone) lives only in the session transcript `ses_f6b4e42f2ffeohj9WFHtlqOYQR`. | Commit the tool. Copy the runeword gate's enforcement shape and vocabularyGuard's scope/allow-list shape; re-derive the demon tool's *rules* from the transcript rather than re-inventing them. |
| **An IP avoid-list on the naming prompts.** The prompts freely invent names; a negative-clause mechanism already exists but does not mention IP. | `gk-forge/tools/seedsmith/seedsmith/adapters/trees/nodegen/brief.py:62-68` (system prompt, no IP clause), `gk-forge/tools/seedsmith/seedsmith/adapters/trees/nodegen/schema.py:71-87` (`name` is free text, "no mechanics, no number" — nothing about third-party marks); `gk-forge/tools/seedsmith/seedsmith/adapters/items/uniques/briefs.py:266-267` names "Diablo" as the style target with no avoid-list. `trees/nodegen/brief.py:157` already prints an `Avoid entirely: <list>` line. | Feed an IP avoid-list through the **already-present** `Avoid entirely` seam and add the runeword-style answer-side refusal. |
| **A gate hook point.** `scripts/verify-change.ps1` exists; no guard reads a vocabulary registry. | `scripts/guard-*.ps1` all ban code shapes, never words (verified: none matches `trademark|copyright|pokemon|…`). | A new `guard-ip-vocabulary.ps1` (does not exist yet) in the existing guard family, wired like `gk-core/scripts/guard-dal.py`. |
| **Import-time filter for the upstream almanac.** The import path exists and takes rows straight through. | `gk-core/src/FusionRpg.Server/Program.cs:1382-1401` reads `gk-data/packs/fusion/data/seed/external-reference/almanac-enrichment/pvz-fusion-almanac-3.6.1.json` and calls `store.ImportAlmanacEnrichment(rows, "pvz-fusion-almanac-3.6.1")`. | This file is *upstream data* (imported, not generated here), so "change the generator" does not apply — the honest seam is a normalization/allow-deny step at import. |

### ❌ REAL GAP (no mechanism anywhere)

| Gap | Evidence |
|---|---|
| **No third-party-IP deny-list or registry exists anywhere.** | A repo-wide search for `trademark|copyright|third-party IP|brand name|franchise` across `*.py/*.cs/*.ts/*.ps1` finds no validator; `scripts/commit-tool/policy.json:56-70` banned only AI/vendor watermarks (that file was retired with the git gate on 2026-09-19; the finding stands). The only word-ban is `runeword`, an internal collision term. |
| **No repo-wide token census.** | Token counters that exist are domain-scoped only: passive-tree node names (`gk-web/web/fusion-rpg-web/scripts/render-tree-cards.mjs:483-507`), action name similarity (`.../dedup_select/similarity.py:38-57`), aptitude families (`gk-core/scripts/audit-reader-census.py:3`). A "2,312 distinct tokens" figure is quoted as a past measurement with no committed reproducer (`characteristic_pool/curation.py:8`). |
| **Shipped third-party collisions, already live.** | `gk-data/packs/fusion/data/seed/passive-tree/nodes/command.json:537-539` — `"name": "Overwatch Protocol"` (a Blizzard mark), produced by the unguarded prompt; `:542` shows `promptVersion tree-language/3`. Also real-person references inherited from the upstream fan pack: `gk-data/packs/fusion/data/seed/external-reference/almanac-enrichment/pvz-fusion-almanac-3.6.1.json:5247,5677,5772` ("Michael Zombie", "Michael Zomboni", "Jackson Worldwide") → derived `speciesId`s `gk-data/packs/fusion/data/seed/creatures/species/_index.json:382-387` (`JacksonDriver`, `JacksonZombie`, `Jackson_a`…) and `gk-data/packs/fusion/data/seed/creatures/species/zombie/undead.json:2290` (`JacksonZombie`), `species/zombie/performer-undead.json:75,80` (`Jackson_a`, trait `moonwalking`). |
| **No clearance/decision record** — nothing states which collisions were assessed and accepted as risk. | No doc under `docs/` records a trademark assessment. `NOTICE:18-19` disclaims game content generally but does not enumerate accepted risks. |

**Not counted as IP risk (deliberate, do not "fix"):** the PvZ identity itself
(`docs/guide/the-game.md:13-17,29,39`), and the attributed prior-art corpus under `docs/research/**`
(~700+ matches, every one a sourced citation with a URL — nominative reference, not a shipped name).

---

## Prior art — with numbers, formulas, and documented failure modes

### 1. The failure mode this tool will hit first: the Scunthorpe problem

Substring/word-list filtering produces **false positives that are the dominant cost**, not a footnote.

- Named 1996 (AOL blocked the town of *Scunthorpe* because it contains a four-letter substring);
  Google SafeSearch repeated it in the early 2000s; a 2020 Twitter filter blocked discussions of
  Dominic Cummings (`cum`) from trending; an Oct-2020 filter banned the words **"bone", "pubic" and
  "stream"** at a paleontology conference. ([Wikipedia](https://en.wikipedia.org/wiki/Scunthorpe_problem),
  [Vice/Motherboard](https://www.vice.com/en/article/dyzamj/a-profanity-filter-banned-the-word-bone-at-a-paleontology-conference))
- The documented mitigation is **a whitelist of known false positives plus word-boundary
  discipline** — exactly the discipline the demon rename already used (protecting `demonstrate*`,
  `Pandemonium`, `Enslave_Demon`) and `vocabularyGuard.ts` tests for.
- **Consequence for this design:** a blanket IP filter over the whole tree would flag the product's
  own premise and every research citation. **At this repo's volume that is thousands of findings and
  the tool gets disabled** — the failure mode is abandonment, not over-censorship. Scope-awareness is
  therefore not a nicety; it is the load-bearing requirement.

### 2. "Smart replace" is the wrong shape for IP; *knock out, then clear* is the industry shape

Trademark practice splits detection into two stages with **different precision targets**
([USPTO comprehensive clearance](https://www.uspto.gov/trademarks/search/comprehensive-clearance-search-similar-trademarks),
[USPTO likelihood of confusion](https://www.uspto.gov/trademarks/search/likelihood-confusion),
[Perspire IP](https://www.perspireip.com/blog/trademark-knockout-search-guide)):

| Stage | Method | Precision target | Output |
|---|---|---|---|
| **Knockout** | exact / near-exact wording, same class, federal records | *high precision*, low recall (triage: "is it taken outright?") | pass / fail |
| **Full clearance** | phonetic + visual + **conceptual** similarity, related classes, common-law, domains, foreign registers | recall-oriented | a **report for a human**, never an auto-edit |

- The legal test is **likelihood of confusion**, decided by whether the marks are *confusingly
  similar* **and** the goods *related* — marks need not be identical; "similar in sound, appearance,
  or meaning, or … a similar commercial impression" suffices ([USPTO](https://www.uspto.gov/trademarks/search/likelihood-of-confusion)).
  A real Office Action (2026) refused `LEGENDARY SWORD 2 VALHALLA` against `VALHALLA` on that basis,
  and the examiner's stated method was **"the registrant's word could be received as the shortened
  name for applicant's mark"** ([USPTO OA PDF](https://tmng-al.uspto.gov/resting2/api/casedoc/cms/case/99470810/office-action/OfficeAction8370761.pdf)).
- Commercial tooling reports its own accuracy numbers: a 2026 test on ~500 refused applications
  surfaced the examiner's cited registration in **9 of 10** cases using 8 methods (exact,
  pseudo-mark, phonetic, visual, shared components, coordinated classes, word-level phonetic, similar
  meaning, foreign translation) ([GleanMark](https://app.gleanmark.com/knockout-search)). Cost
  benchmarks: knockout **$150–$500/mark/class**, full clearance **$500–$2,000+** ([Perspire IP](https://www.perspireip.com/blog/trademark-knockout-search-guide)).
- **Consequence:** the *detector* must emulate knockout (exact/near-exact list membership with word
  boundaries) and hand the *conceptual* question to a human. **It must never auto-rename a fuzzy
  hit** — a fuzzy match is a hypothesis about confusion, and inventing a replacement is both a
  content decision and (per principle 4) a fabrication.

### 3. What actually gets enforced in practice: prompt hygiene, not post-hoc censorship

- WIPO's own guidance is to **"advise against prompts referencing third-party business names,
  trademarks, copyright works, or specific authors/artists"** and to **"implement measures to check
  for infringements before using outputs"** ([WIPO GenAI factsheet, 2024](https://www.wipo.int/export/sites/www/about-ip/en/frontier_technologies/pdf/generative-ai-factsheet.pdf)).
- Legal commentary converges on the same operational shape: **guardrails + an approval workflow before
  publication**, screening "public-facing AI-generated materials" for "recognizable third-party IP,
  celebrity likenesses" ([Debevoise, 2026](https://www.debevoise.com/insights/publications/2026/03/practical-considerations-for-managing-ip-risk-in);
  [Saul Ewing, 2025](https://www.jdsupra.com/legalnews/best-practices-for-mitigating-2861077)).
  A Bloomberg Law piece notes the MCP direction — AI tooling querying trademark records in-workflow —
  while stressing **"human oversight is critical"**.
- **Consequence:** the highest-leverage fix is at the **generator prompt** (prevent the name from
  being authored), and the gate is the **backstop that proves the prevention held**. This matches the
  `runeword` precedent exactly, and it is the cheaper half of the program.

### 4. Fan-project reality (why this is worth doing at all)

Fan works are taken down on IP grounds regardless of being free and non-profit; the documented cases
are overwhelmingly *assets and names*, not mechanics — Nintendo's 2018 DMCA against **Pokémon
Essentials** (11-year-old tool + its wiki) and the 2024 closure of the **Relic Castle** fan-game
forum ([IGN](https://www.ign.com/articles/2018/08/29/nintendo-shuts-down-pokemon-fan-game-creation-tool),
[Ars Technica](https://arstechnica.com/gaming/2018/08/nintendo-shuts-down-tool-used-to-build-pokemon-fan-games),
[Nintendo Life](https://www.nintendolife.com/news/2024/03/pokemon-fan-game-site-relic-castle-shut-down-following-dmca-takedown-notice)).
Legal analyses stress that **"using the name of another brand is an easy case of copyright
infringement regardless of use"** and that mechanics with original names/art are the defensible part
([Game Developer](https://www.gamedeveloper.com/business/are-fan-games-fair-use-)).
This project already sits on a fan pack and already disclaims it — `NOTICE:18-19`,
`the-game.md:15` ("a fan-made Plants vs. Zombies pack, separate from EA's official titles"). The
upstream fan pack's own site publishes a DMCA policy and states it does not claim ownership of
third-party trademarks ([plantsvszombie.com/dmca-policy](https://plantsvszombie.com/dmca-policy)).

### 5. ⚠️ Explicitly unverified / out of scope

- **No clearance opinion exists for any name in this repo.** Nothing here has been assessed by
  counsel, and this document is not legal advice.
- Deeper conceptual-similarity detection (embeddings, phonetic algorithms) is *described* by vendor
  material above but **I did not benchmark any of it against this corpus** — treat §2's 9/10 figure as
  a vendor claim, not a measured property of our tool.
- Whether a curated list or a bulk trademark dataset is the right registry source is an **owner
  decision** (see Open questions), not a research finding.

---

## How to filter correctly — measured on this repo (2026-09-19)

The owner's question — *can a deterministic engine do this, and is there a library?* — has a measured
answer. **Yes, and the engine is the easy half; the hard half is scope.** Every number below was
produced in this session over **10,288 tracked scannable files / 195.6 MB**.

### 6.1 The three traps, each demonstrated

**(a) Substring replace corrupts identifiers.** The naive version of "replace `pvz` → `fusion`":

| Input | Blind substring `re.sub("pvz","fusion")` | Correct |
|---|---|---|
| `PvZ2 strategies` | `fusion2 strategies` ✗ | leave `PvZ2` (a *different* EA game) |
| `PVZRH` | `fusionRH` ✗ | leave (a proper name) |
| `02-pvz2-chinese` | `02-fusion2-chinese` ✗ | leave |

This is the Scunthorpe/Clbuttic problem (Prior art §1). **Word boundaries are the fix** — verified:
`\bpvz\b` correctly skips `PvzStats`, `PVZRH`, `pvzrh-3.9`, `PvZ2`, `02-pvz2-…` while still matching
`PvZ Fusion`, `pvz-fusion-almanac-3.6.1`, `` `pvz.*` ``, `drop.pvz.run`.

**(b) `\b` does not mean "the string ends here."** `\b` is a `\w`⇄non-`\w` transition, and `-`, `.`,
`/` are **non-word** characters — so `\bpvz\b` **matches inside** `pvz-fusion-almanac-3.6.1`,
`pvz.*` and `drop.pvz.run`. Verified. Any real filter needs a **boundary policy that names its
separators** (`[-./_\s]`), or an explicit per-alias allow/deny of separator-adjacent forms.

**(c) `\b` fails entirely on CJK neighbours.** This repo contains Chinese content. Verified:

| Text | stdlib `\bpvz\b` | `regex` UAX29 | needed |
|---|---|---|---|
| `PvZ融合版` | **no match** (false negative) | **no match** | match |
| `使用PvZ Fusion` | **no match** | **no match** | match |
| `PvZ的植物` | **no match** | **no match** | match |

`\w` treats CJK as word characters, so there is no boundary. A correct filter must define
"boundary = start/end, whitespace, punctuation, **or a script change (Han↔Latin)**".

**(d) Case/diacritic folding is not `.lower()`.** Verified: `"Pokémon".lower()` does **not** contain
`"pokemon"` (`é` ≠ `e`), so a naively folded list silently misses `Pokémon`/`POKÉMON` — and this repo
has **149** `pokémon` + **18** `pokemon` hits. Use **Unicode case folding** (and decide explicitly
whether accents are significant).

### 6.2 Two engines, benchmarked end-to-end on this repo

| Engine | Time for 195.6 MB | Notes |
|---|---|---|
| `re` alternation + Unicode lookaround | **17,038 ms** | one pass per file; simple, zero deps |
| `pyahocorasick` + own boundary post-filter | **2,046 ms** | **8.3× faster**; the automaton is *substring*, so it **still needs the same boundary filter** |

Both found the **same ~3,400 hits in 688 files**; a raw comparison showed a small delta which traced to
a **registry defect, not an engine defect** — the alias `"wow"` (matching `World of Warcraft`) also
matches ordinary exclamation, producing **142 bare-word `wow` hits** in prose. This is trap (a) again,
inside the registry: **short aliases are the primary false-positive source.**

`pyahocorasick` is already installed (`import ahocorasick` → OK; Python 3.13.12). `flashtext` is
**not** installed but `flashtext2` (Rust-backed, 1.1.0) is on PyPI and is the fastest of that family —
**do not build a trie by hand.** `regex` (2026.3.32) is installed.

### 6.3 The library answer, stated plainly

**Do not build from scratch. Buy the automaton, build the policy.** Concretely:

| Concern | Use | Why / measured |
|---|---|---|
| Multi-pattern exact matching | **`pyahocorasick`** (installed) or **`flashtext2`** | Aho-Corasick is linear in text length + matches and is the standard answer (Stanford CS166: `Θ(m+z)`; Hyperscan's own paper shows AC is the prefilter under DPI) |
| Word / script boundaries | **`regex`** (installed) for UAX#29-aware boundaries, **or** a ~20-line boundary function over `pyahocorasick` hits | stdlib `re` proved wrong on CJK (§6.1c) |
| Case/diacritic folding | `str.casefold()` (not `.lower()`) | verified `é` miss |
| Longest-match-first | automaton output ordering (AC reports every match; keep the longest at each span) | `flashtext`/`flashtext2` do this by design |
| Fuzzy / phonetic / similarity | **a bulk/cloud API at review time** (USPTO / WIPO Global Brand Database / EUIPO), never in the gate | knockout must stay **high-precision** (Prior art §2); fuzzy is a human queue |
| Trademark *data* (the registry) | curate from **USPTO / WIPO Global Brand Database (76M+ records) / EUIPO / TMview** | you do not want 76M patterns in a pre-commit hook |

**A deterministic engine is sufficient for the gate.** The measured 2 s over the whole tree means it
can run on every change; nothing about this needs a model. The only place an LLM adds value is
*proposing registry candidates* — and that output is a **human-confirmed** list, not an enforcement
path.

### 6.4 Scope is the real design problem — and the census proves it

The owner's instruction is to **"only censor the IP that already exists"** and to avoid misleading.
That splits cleanly, and the split is measurable:

| Group | Hits | Where they actually live | Verdict |
|---|---|---|---|
| **PvZ aliases** | `pvz` **4,146**, `plants vs. zombies` **88**, `plants vs zombies` **6**, `plant vs zombie` **3**, `plants versus zombies` **0** | `docs` 2,119 · `src` 782 · `tests` 516 · `tasks` 339 … | ⚠️ **Mixed.** The *product's own premise* (do not censor) and *code identifiers* (`pvz.*` intent namespace, `drop.pvz.run`) occupy the same word as the EA mark. |
| **Diablo** | **495** | `docs` 486 · `data` 5 · `src` 3 · `tools` 2 | Citations + the `runeword` collision precedent |
| **HoMM** | `homm` **143**, `might and magic` **21**, `heroes of might and magic` **18** | `docs` | Citations only |
| **Warcraft / WoW** | **167** / **31** | `docs`, prose + citations | Citations; `wow` is a false-positive trap |
| **Pokémon** | `pokémon` **149** + `pokemon` **18** | `docs` 164, `data` 1 | Citations |
| **Arknights / Genshin / Honkai** | **127 / 96 / 7** | nearly all `docs` | Citations (tuning rationale notes) |
| **Overwatch** | **43** | `docs` 39, **`data` 4** | **2 of those `data` hits are a shipped player-facing node name** (Real gap) |

**Two facts fall out of the census, and they settle the design:**

1. **The overwhelming majority of third-party IP in this repo is *attributed prior-art citation*
   inside `docs/`** — and per principle 3, that is **nominative reference, not a shipped name**. A
   filter that flags it produces the thousands-of-false-positives failure (§6.1, §1). **`docs/**` must
   be a citation scope, not an enforcement scope.**
2. **The enforcement scope is tiny and specific:** `gk-data/packs/fusion/data/seed/**` and `gk-data/packs/fusion/data/generated/**` name fields,
   `gk-forge/tools/seedsmith/**` prompts that emit them, and the hand-authored registries. The *whole* genuine
   live finding is one node name (`gk-data/packs/fusion/data/seed/passive-tree/nodes/command.json:538`) plus the
   upstream-almanac real-person family.

That is why the answer to "how do we filter correctly?" is **not** a better matching engine. It is:
**match with the automaton (cheap, solved), then decide with scope (the actual work).**

---

## The shape being proposed

**Three verbs, one registry, three enforcement points — not one "smart replace" pass.**

```
registry (authored, versioned)  ──┐
                                   ├─► 1. census   : list distinct tokens + counts (READ)
scope policy (authored)  ─────────┤   2. scan     : registry × scope → findings (READ, the GATE)
                                   └─► 3. replace  : exact token → authored replacement (the ONLY writer)
```

A **registry entry is an alias group**, not a string: one canonical mark (`pvz`) with its spellings
(`pvz`, `plants vs. zombies`, `plants vs zombies`, `plant vs zombie`, `plants versus zombies`), a
category, and a **scope**. The scanner searches the group; a finding is reported once per group, not
once per spelling (§6).

1. **`census` — list tokens.** The thing the owner asked for first. Tokenization over the tracked tree
   (excluding binaries, lockfiles, generated integrity hashes), reporting distinct tokens with counts
   and the surface category each appears on. **Read-only.** This is what makes the registry curatable
   and what the owner's own alias list must be checked against — the census above already shows
   `plants vs zombies` (6) and `plant vs zombie` (3) exist even though `plants versus zombies` does not.

2. **`scan` — the gate.** Matches registry alias groups with an **explicit boundary policy** (§6.1b/c
   — not bare `\b`), longest-match-first, case-folded, then filters by **scope policy**: which token
   categories are in scope, and on which surfaces. Emits findings with `file:line`, bucketed as
   *player-facing name* / *generator prompt* / *authored registry* / *citation (ignored)* /
   *deliberate identity (ignored)* / *code identifier (ignored — a rename would break it)*.
   **Read-only.** This is the CI gate.

3. **`replace` — the narrow writer.** The demon tool's proven contract, and nothing more: an **exact**
   token with an **authored** replacement, case-mapped, boundary-anchored, protected-span-aware,
   dry-run by default, path renames via `git mv`, `--check` on the staged tree. **A fuzzy hit never
   reaches this verb**, and **an identifier hit never reaches this verb at all** (§6.1a: renaming
   `pvz.*` or `drop.pvz.run` breaks code). For generated rows, `replace` is the *wrong* tool — the
   generator is.

**Alternatives rejected, with the reason:**

| Rejected shape | Why |
|---|---|
| One blanket "smart replace" over the whole tree | Flags the product's own PvZ premise and every research citation → thousands of false positives → the tool is disabled (Prior art §1, measured §6.4). |
| A **substring** replace | Corrupts identifiers: `PVZRH`→`fusionRH`, `PvZ2`→`fusion2`, `02-pvz2-…`→`02-fusion2-…`. Measured §6.1a. |
| Bare `\b` as the boundary | Matches *inside* `pvz-fusion-almanac-3.6.1`, `pvz.*`, `drop.pvz.run` (`-`, `.`, `/` are non-word), and **misses** `PvZ融合版` entirely (`\w` includes Han). Measured §6.1b–c. |
| `.lower()` for case folding | Misses `Pokémon`/`POKÉMON` (`é`≠`e`) — and the repo has 149 `pokémon` hits. Measured §6.1d. |
| Hand-rolling a trie / writing the automaton | `pyahocorasick` is already installed and `flashtext2` exists; measured 8.3× over a `re` alternation. Buy it. |
| A pure post-hoc censor (detect-and-rewrite only) | Violates the generated-tree rule: it forks `gk-data/packs/fusion/data/seed/**` from its generator, and the next run reverts it. WIPO/legal guidance puts the fix at the prompt (§3). |
| Fuzzy/phonetic auto-similarity as the *detector* | Knockout needs high precision; conceptual similarity is a *human* call (§2). Fuzzy output is a review queue, never an edit. |
| A registry of every trademark in a bulk dataset | 76M+ records (WIPO Global Brand Database); membership would be un-auditable and would flag the deliberate identity. The registry must be **curated and small**. |
| Aliasing short common words into the registry (`wow`, `ea`, `pop`) | Measured: bare-word `wow` = **142** prose hits; `ea` = **67**; `pop` = **221**. These are registry defects that look like engine defects. Require a minimum alias length or an explicit scope per short alias. |
| Putting the ban only in `vocabularyGuard.ts` | That guard is FE-copy-only (`*.ts/.tsx`). The collisions are in `gk-data/packs/fusion/data/seed/**` and `gk-forge/tools/seedsmith/**` prompts — outside its reach. |

---

## Narrative generation — prevent at the prompt (added 2026-09-19)

**Why this section exists.** Owner ruling, 2026-09-19, made while answering the narrative-seed
questions: *enrich the ip-censor document so generation avoids words we will need to censor.* The
same day the owner ruled that story content uses the game's **own** names — the three leads get
original names, and story prose never names a species by its PvZ or Fusion name
([npc-story-events-ideal.md](npc-story-events-ideal.md) §10, R8–R10). The narrative programs
([narrative-seed-ideal.md](narrative-seed-ideal.md)) will generate far more player-facing text than
every corpus this census measured: characters, storylets with choice labels, dialogue lines, arcs and
main-story chapters. §3 already says prevention belongs at the prompt; this section says how, for text
at that volume.

**What changes in this design:**

| # | Change | Why |
|---|---|---|
| 1 | **Scope widens to the narrative surfaces**: character names, epithets and lines; storylet names, situations, choice labels and results; arc names and premises; main-story chapters; the motif gloss registry; the names registry | These are player-facing names and prose (the "player-facing name" and "generator prompt" buckets of §The shape), in a new tree the census has not seen |
| 2 | **One registry, enforced at release.** ~~A tier-2 validator inside each generator's retry loop~~ — **withdrawn by the owner (ruling IC-3 below): blocking during generation costs more model calls than it saves.** What remains at generation time is free: a shared seedsmith helper renders the registry's in-scope alias groups into briefs as an avoid-list (no extra calls, no retries), and the token design keeps names out of prose (row 5). **The `scan` is the release gate**: it runs before any release and blocks it on a hit | Today prevention is per adapter — `adapters/items/combogen/grid.py:32` keeps its own `BANNED_WORD`. Per-adapter lists drift; one registry cannot. A hit found at release is fixed the sanctioned way: the generator's avoid-list gains the term, then the affected rows regenerate |
| 3 | **The PvZ/EA character names become registry entries in the narrative scope** — Crazy Dave, Penny, Dr. Zomboss and their spellings — in the *player-facing narrative* surface only. Code identifiers (`pvz.*`, `drop.pvz.run`) stay out of scope exactly as §6.1a requires | Owner ruling R8/R9 settles Q1b **for narrative text**: prose uses original names. The code namespace question is untouched |
| 4 | **Species catalog names are barred from narrative prose** (not from the species catalog or the UI that shows it) | Owner ruling R8's widest option. The in-loop check is the narrative-seed "no literal names in text" validator (`literal-name`, [spec-narrative-validators.md](narrative-seed/spec-narrative-validators.md) §3), which checks names-registry entries and species catalog names only; IP marks are checked at release by `scan` (IC-3). Reconciled 2026-09-19: the earlier wording had the validator read this registry, which IC-3 withdrew |
| 5 | **Structured text makes the leak structural, not probabilistic.** Narrative text refers to people and places through tokens (`{lead_antagonist}`, `{c_<id>}`) resolved from a names registry ([narrative-seed-ideal.md](narrative-seed-ideal.md) §6.5b). The model never sees a real name, so it cannot copy one; the names registry itself is the one place a name lives, and it passes `scan` before it is published | A name that appears in one registry file is one row to check; a name baked into thousands of lines is a corpus-wide census |
| 6 | **Prompts never cite prior art by name.** Briefs must not mention other games or franchises (Hades, Wildermyth, Diablo and the like) as style references | A named reference in a prompt is an invitation to borrow its names. Style is carried by the program's own exemplars and anchor lines instead |
| 7 | **Translation is a leak path too.** The motif gloss registry (all 1,586 motifs are Chinese today) and any future locale file are generated text: their outputs pass `scan` like any other generated name | Translating an upstream almanac term can surface a third-party mark the source language hid |

**What this does not change:** the three verbs (census, scan, replace), the boundary policy, the
curated-small registry, `replace` never touching generated rows, and the open questions below. Q1b is
now answered for narrative text only (row 3); its code-namespace half stays open.

---

## Tunables

**Almost none — by design.** The substance is a **closed authored vocabulary** (the registry), not a
balance surface.

| Thing | Kind | Home |
|---|---|---|
| Registry of third-party marks as **alias groups** (canonical mark + spellings + category + scope) | **Closed authored vocabulary** (a human edits it) | A registry directory with the `_registry` convention (cf. `gk-data/packs/fusion/data/seed/items/_registry/`, `gk-data/packs/fusion/data/seed/creatures/_registry/`) — versioned, and its own member list may be asserted. |
| Scope policy (which category × which surface) | Authored data | Alongside the registry. |
| **Boundary policy** (separator set, script-change rule, min alias length) | Authored data — it is tuned against findings, like a registry | Alongside the registry, **not** a `const`: §6.1b/c proved the obvious default is wrong, so this will be adjusted per finding. |
| Case folding + accent significance | Structural (`str.casefold()`) | `const` in tool code with a reason comment. |
| Fuzzy-similarity threshold (**only if** verb 2 ever gains a fuzzy mode) | A real tunable number | `gk-core/data/tuning/` if it ships — never a bare `const`. |

**Explicitly not a tunable, and not assertable:** `len(registry.hits)`, "zero findings", or the number
of tokens in the census. Per [validation-ssot.md](validation-ssot.md): the hit population is a
**reading**; the registry is a **closed vocabulary**. The gate asserts envelope, category membership,
uniqueness of a mark, determinism, and that every finding joins to a registry row.

---

## What this deliberately does not decide

- **No legal judgement.** The tool screens; a human decides. It never classifies something as
  "safe".
- **No replacement names.** Renaming `Overwatch Protocol` to something original is a *content/identity*
  decision (and, for generated rows, a *prompt* decision) — out of scope here.
- **No new loop, currency, stat, or player surface.**
- **No decision on the PvZ homonym.** Whether prose `PvZ` becomes "Fusion" is Q1b — a product-identity
  call, not an engineering one. This doc establishes only that a code identifier (`pvz.*`) is not a
  rename candidate.
- **No spec, no plan, no code.** This doc is where the phase stops.

---

## Owner rulings (2026-09-19) — all questions below answered

Answered in the narrative-seed session. The original questions are kept underneath for the reasoning
trail.

| # | Question | Ruling | Consequence |
|---|---|---|---|
| IC-1 | Which kinds of IP are in scope? | **Game and franchise marks, real-person names, company and brand names.** Film, song and book titles are **out** (common-phrase false positives). Attributed research citations stay out (the census settles it) | The registry's category enum has these three in-scope members |
| IC-1b | The `pvz` homonym | **Replace display and prose "PvZ" / "Plants vs. Zombies" with "Fusion" everywhere.** Code identifiers (`pvz.*`, `drop.pvz.run`) are untouched (§6.1a). Story text already never names it (narrative rulings R8–R9) | Joins the rename program (`npc-story-events-ideal.md` §10 R9, R12); the gate's scope policy treats `pvz` as in scope on player-facing surfaces only |
| IC-2 | Where the registry comes from | **Both: import a trademark dataset first, curated down to game-related marks; then the census plus model-proposed candidates, confirmed by a human, re-confirm it** | Two stages: `import` (dataset → curated candidate rows) then `reconfirm` (census hits and model proposals checked by a person). Every row records which stage admitted it |
| IC-3 | How hard the gate enforces | **A release gate.** The scan runs before any release and blocks the release on a hit. It does **not** block generation — *"block generation will cost more than help"* | Generation keeps only the free avoid-list in briefs (row 2 of the section above). The release checklist gains the scan |
| IC-4 | The live findings | **Fix both before release** | `Overwatch Protocol`: the tree generator's avoid-list gains the term, then that node regenerates. The `Jackson*` family: an authored import-time rename map, since upstream data cannot be regenerated. **Owner answer to the plan's gate G1 (2026-09-19): the `Jackson*` species ids are re-keyed too** — a backed-up, one-transaction, idempotent store migration (`tasks/ip-censor-todo.md` T19b) |
| IC-5 | Is the registry tracked? | **Yes, in the repo** | The release gate runs reproducibly on any clone |
| IC-6 | Short aliases | **A minimum length and an explicit scope**: an alias under 4 characters is rejected unless its entry names a narrow scope | Boundary policy rows carry the length rule; short entries must declare a scope |

## Open questions — owner decisions only (answered above; kept for the trail)

1. **Scope of "IP" — which categories are in scope at all?** Candidates: (a) third-party
   game/franchise marks (Overwatch, Diablo, HoMM, Final Fantasy), (b) real-person names/likeness
   (Jackson\*), (c) company/brand names, (d) film/song/book titles, (e) the deliberate PvZ identity,
   (f) attributed research citations. **The census settles two of these by evidence, not taste:**
   (f) is `docs`-only and is **nominative citation** — flagging it is the §6.1 abandonment failure, so
   it must be **out**; and **(e) is genuinely ambiguous**, because `pvz` is *simultaneously* the product's
   premise, an EA mark, and a code namespace (`pvz.*`, `drop.pvz.run`) — see Q1b.

1b. **⚠️ The `pvz` homonym — the one genuinely hard call.** Measured: `pvz` appears **4,146** times
   across `docs` 2,119 / `src` 782 / `tests` 516 / `tasks` 339, plus `plants vs. zombies` 88. It means
   three different things at once: **our own shorthand for the host pack** (leave), **EA's trademark**
   (the thing to consider replacing with "Fusion"), and **a code/identifier namespace** (`pvz.*`
   intents, `drop.pvz.run` tables — cannot be renamed without a code change). *Do we (i) rename
   display/prose `PvZ`→`Fusion` while leaving identifiers, (ii) leave it entirely because "Fusion" is
   already the pack's own name, or (iii) treat `pvz` as out-of-scope and enforce only unrelated marks?*
   This is the decision the whole gate's usefulness hinges on, and it is a **product identity** call.

2. **Registry provenance — where does the list come from, and who owns it?** (i) hand-curated seed
   list grown from `census` output; (ii) import a trademark dataset (USPTO / WIPO Global Brand
   Database / EUIPO / TMview) and curate **down** to a few hundred marks that relate to games; (iii)
   LLM-proposed candidates → human confirm. All three are defensible; they differ in maintenance cost
   and auditability.

3. **Enforcement point and severity.** Advisory `scan` report only, or a new guard (does not exist
   yet) that **fails** `gk-core/scripts/verify-change.py`/CI? (A blocking gate with an uncurated registry will
   be disabled within a day — this is coupled to Q2.)

4. **The live findings — fix now, or accept as risk and record?** `Overwatch Protocol`
   (`gk-data/packs/fusion/data/seed/passive-tree/nodes/command.json:537-539`) is fixable only through the tree generator
   (prompt avoid-list + regenerate). The `Jackson*` species (`species/_index.json:382-387`) trace to
   **upstream imported** data (`pvz-fusion-almanac-3.6.1.json:5247,5677,5772`) and cannot be
   "regenerated" — they need an import-time filter or an authored rename map. *Fix, defer, or
   record-as-accepted?*

5. **Does the gate's registry live in the repo (tracked) at all?** A public repo publishing a list of
   "marks we avoid" is itself a low-risk disclosure, but it is an owner call — and it interacts with
   the "keep the tool out of the tree so it cannot self-reference" trick the demon script used.

6. **Short-alias policy.** Measured false positives from aliasing common words: `wow` 142, `pop` 221,
   `ea` 67. *Set a minimum alias length, or require an explicit scope per short alias, or both?*

---

## Hand-off

**Next step: `/spec`** — a capability map for `ip-censor` plus module specs (census / registry /
scan-gate / replace / prompt-hygiene), once Q1–Q3 are answered. Q4 and Q5 can be deferred to plan
time. Do not start a tool build before Q1–Q3, because the registry scope decides the scanner's entire
shape.
