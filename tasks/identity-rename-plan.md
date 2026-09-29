# Plan: identity-rename — "Garden Keeper and his Multiverse" and the three leads

**Status: approved 2026-09-22, ready for lanes.** Plan written 2026-09-19; owner approved implementation
2026-09-22. No task started. Premises re-verified against the convergence head 2026-09-22 — see
[§11 Addendum](#11-addendum-2026-09-22--premise-verification-against-the-convergence-head).
Task list: [identity-rename-todo.md](identity-rename-todo.md).
Program id: `identity-rename`. This is the "follow-up rename program" named by owner ruling R9
(`docs/architecture/npc-story-events-ideal.md` §10 R9) and joined by R12 (§10 R12) and IC-1b
(`docs/architecture/ip-censor-ideal.md:438`). It is also the **execute** half that
`docs/architecture/ip-censor-map.md:17-25` leaves to "a separate program" and names as this program
for the character names and the `pvz` prose homonym.

---

## 1. What the owner ruled (2026-09-19) — the input, not reopened here

| Ruling | Content | Source |
|---|---|---|
| R8 | Story text uses the game's own names. Names are **parameters** | `npc-story-events-ideal.md` §10 R8 |
| R9 | Rename everywhere: the Rift prologue, the player guide, the product-vision wording. Code identifiers (`pvz.*`) untouched. The `decisions.md` row changes in this program's own change | `npc-story-events-ideal.md` §10 R9 |
| R11 | Crazy Dave → **the Garden Keeper**; Penny → **Hourbloom**; Dr. Zomboss → **the Rotwright** | `npc-story-events-ideal.md` §10 R11 |
| R12 | **"Garden Keeper and his Multiverse"** replaces "Rise of Summoner" as the player-facing title. `FusionRpg.*` names, namespaces, binaries, env vars and release-zip internals are untouched | `npc-story-events-ideal.md` §10 R12; `AGENTS.md:62-63` |
| IC-1b | Display and prose "PvZ" / "Plants vs. Zombies" → "Fusion" everywhere player-facing. Code identifiers (`pvz.*`, `drop.pvz.run`) untouched | `ip-censor-ideal.md:438` |
| §6.5b | Lead names are tokens (`{lead_summoner}`, `{lead_companion}`, `{lead_antagonist}`) resolved from a per-locale names registry with closed feature tags. **A rename is one edit to one file** | `docs/architecture/narrative-seed-ideal.md` §6.5b |

The pitch does not change. `decisions.md:109` and `docs/guide/the-game.md:11` say the product is an RPG
plus empire-building extension for the Fusion host game; after this program they say the same thing
under the new title with the new lead names. DESIGN-GATE's Product-vision row
(`docs/DESIGN-GATE.md:31`) forbids re-pitching the genre, and no task here does.

---

## 2. Scope

### In scope (player-facing)

| Surface | Files | What changes |
|---|---|---|
| Rift prologue | `gk-web/web/fusion-rpg-web/src/features/story-scene/actorCast.ts`, `messages.ts`, `sceneScript.ts`, `gk-web/web/fusion-rpg-web/src/i18n/locales/{en,pseudo}/messages.po`, the copy SSOT `docs/ideas/onboarding-gnome-teaser.md` (speaker labels only) | Actor names come from the names registry; no literal lead name in any beat, name tag or catalog |
| Other web copy | `src/app/TitleScreen.tsx:25-26`, `src/stages/sanctum/OnboardingReveal.tsx:33,35,50`, `src/stages/sanctum/FocusCard.tsx:50,54`, `src/layers/chronicle/ChronicleLayer.tsx:10` (all under `gk-web/web/fusion-rpg-web/`) | Title, lead names (via tokens), "PvZ sheet" label |
| Server-emitted display names | `gk-data/packs/fusion/data/seed/commanders/_registry/default-commanders.v1.json:15`, `gk-core/src/FusionRpg.Core/World/WorldTemplateCatalog.cs:78,83`, `WorldTemplateCatalog.TwoHearths.cs:26-27`, `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs:4188,4203` | Resolve lead names from the names registry instead of literals |
| Launcher and injector chrome | `gk-fusion/src/FusionRpg.Launcher/MainWindow.xaml:5,18`, `OverlayWindow.xaml:5`, `MainWindow.xaml.cs:424`, `FusionRpg.Launcher.csproj:18`, `gk-fusion/src/FusionRpg.Injector/Hud/Win32.cs:82` | Window titles, the folder-picker title, the assembly description |
| Player guide | `docs/guide/**` (pillar pages, `mechanisms/_content/*.json` then re-rendered outputs, `site/**`) | Title, lead names, PvZ → Fusion |
| Repo front pages | `README.md`, `CONTRIBUTING.md`, `docs/README.md`, `docs/assets/banner.svg` | Title, lead names, PvZ → Fusion |
| Identity statements in rule files | `AGENTS.md:1,55,67`, `docs/PRINCIPLES.md:39-40,50,345-346,431`, `docs/architecture/decisions.md:109` (Product vision row only) | Product-name and product-vision lines only. *Audit 2026-09-19: `:426` had drifted to `:431` (the legal-copy line) and `:345` continues on `:346` (Penny).* *Addendum 2026-09-22: `AGENTS.md` moved to `:1,55,67`.* |

`CLAUDE.md` carries **no** product-name line today (`git grep -c "Rise of Summoner" -- CLAUDE.md` → 0).
Its ten `pvz`/`PvZ` hits are the engineering term for the host-game foundation layer (the RPG-layer
rule), not player-facing prose. T10 re-measures and records that; it does not edit CLAUDE.md unless a
product-name line has appeared by then.

### Out of scope, stated so no task drifts into it

- **Code identifiers:** `pvz.*`, `drop.pvz.run`, `PVZRH`, `pvzrh-3.9`, `PvZ2`, `EmpireId.Dave`,
  `WorldFactionKind.Zomboss`, `Zomboss*`/`*Zomboss*` types (`ZombossDeployEndpoints`, …),
  `commander:dave`, `commander:zomboss`, `first-win-dave`, theme ids `actor-dave`/`actor-penny`, the
  story-scene `ActorId` members `"dave"`/`"penny"`, file names and slugs such as
  `docs/guide/mechanisms/dave-level.md`, env vars `FUSIONRPG_*`, `FusionRpg.*`. Renaming any of these
  is a code rename with its own cost (`ip-censor-map.md:26-27`), not part of R9/R12.
- **Engineering docs:** `docs/architecture/**` (except the one `decisions.md` row), `docs/research/**`,
  `docs/design/*.html` mockups, `tasks/**`, code comments. R8 already tells readers of the ideals to
  read "Dave/Penny/Zomboss" as the lead role (`npc-story-events-ideal.md` §10 R8).
- **Generated trees** (`gk-data/packs/fusion/data/seed/items/**`, `gk-data/packs/fusion/data/generated/**`, …): a lead or mark in generated
  output is fixed by the generator (CLAUDE.md generated-seed rule) and caught by ip-censor's release
  gate (IC-3), not by this program.
- **Test fixture data** that uses "Dave"/"Crazy Dave" as an arbitrary name (e.g. the world AI tests'
  `Name = "Dave"` factions). Only tests that pin a **shipped** value change.
- **`docs/guide/mechanisms/_gen-stubs.ps1`** — a historical one-shot generator its own header forbids
  re-running (`_gen-stubs.ps1:1-3`). Not a surface.
- The third-party-IP registry and release gate: `ip-censor`'s program.

---

## 3. Baseline — readings, not constants

Measured 2026-09-19 with `git grep -o -P <pattern> -- <scope> | wc -l`. Every task re-measures before it
starts and records its own before/after in the todo ledger; none of these numbers is asserted anywhere.

| Scope | "Rise of Summoner" | "Crazy Dave" | `\bDave` | `\bPenny\b` | "Zomboss" | "Plants vs.? Zombies" |
|---|---|---|---|---|---|---|
| `docs/guide` | 293 | 8 | 274 | 3 | 183 | 51 |
| `README.md` | 5 | 2 | 6 | 2 | 9 | 15 |
| `AGENTS.md` | 3 | 0 | 0 | 0 | 0 | 1 |
| `docs/PRINCIPLES.md` | 2 | 2 | 3 | 2 | 5 | 2 |
| `gk-fusion/src/FusionRpg.Launcher` | 3 | 0 | 0 | 0 | 0 | 2 |
| `gk-web/web/fusion-rpg-web/src` | 1 | 41 | 89 | 43 | 7 | 1 |

Most web hits are tests, comments and identifiers; the player-facing web strings are the
ones listed in §2. Most server "Zomboss" hits are identifiers; the player-facing server strings are the six
in §2.

---

## 4. Architecture decisions

### D1 — The names registry comes first, and this program needs only its minimal core

The registry is `gk-data/packs/fusion/data/seed/narrative/_registry/names.en.v1.json` (path fixed by
`narrative-seed-ideal.md` §6.5b). It is **owned by narrative-seed**, as its module 9 `names-registry`
(`docs/architecture/narrative-seed-map.md` module table). That map keeps it a separate module precisely
because this program consumes it directly (`narrative-seed-map.md` §"Why these boundaries"). It depends on
narrative-seed's module 8 `token-grammar`. *Audit 2026-09-19:* that map is **approved** (its `:3`) and
[spec-names-registry.md](../docs/architecture/narrative-seed/spec-names-registry.md) is written; both
modules are unbuilt. The spec is now the file contract this program reads: the three lead rows below
match it, plus a `ruling` field (`"R11"`) on each row that T1's parser accepts and T1's file carries.

This program needs only the three lead rows. The minimal contract:

```json
{
  "schemaVersion": 1,
  "locale": "en",
  "names": {
    "lead_summoner":   { "display": "Garden Keeper", "article": "definite", "gender": "male",   "number": "singular" },
    "lead_companion":  { "display": "Hourbloom",     "article": "none",     "gender": "neuter", "number": "singular" },
    "lead_antagonist": { "display": "Rotwright",     "article": "definite", "gender": "male",   "number": "singular" }
  }
}
```

- `display` is the bare name. The article is a closed tag, never part of the string, because
  `narrative-seed-ideal.md` §6.5b puts the article in the message, not the registry.
- `article`, `gender`, `number` are closed enums. A missing or unknown value **throws** at load.
- **Default, not a gate:** if `names-registry` has not landed when T1 starts, T1 lands
  this minimal file at that path, and narrative-seed's `names-registry` spec adopts it as its v1 (its later fields are
  additive; a breaking change publishes `v2` and moves this program's three readers in the same
  change). If narrative-seed has landed first, T1 adds only the C# parser and uses its file. Either way
  there is one file.

### D2 — One presentation rule for a lead name

- **In a sentence**, the message owns the article through ICU `select` on the registry's `article`
  tag (`{lead_summoner_article, select, definite {The } other {}}{lead_summoner}`). No code
  concatenates an article onto a name.
- **As a standalone label** (story name tag, commander list, world faction label, the player's default
  name) the label is the bare `display`: "Garden Keeper", "Hourbloom", "Rotwright".

This is a presentation default, reversible in one helper per stack (TS and C#). It follows the ideal's
vocative example ("You are too late, Keeper" drops the article, `narrative-seed-ideal.md` §6.5b).

### D3 — Bulk prose goes through a committed, deterministic rename tool — never hand edits

No rename tool is committed today. The demon→creature rename's script was a `%TEMP%` file that is now
deleted (`ip-censor-ideal.md:85,97`). This program commits one: `gk-core/scripts/vocab-rename.py`, with its
rules in `gk-core/scripts/vocab-rename/identity-rename.v1.json`. It implements the `replace` contract that
`ip-censor-ideal.md:342-348` specifies, and the owner's standing rule for bulk work: a deterministic
tool does the work, and agents fix its residue by changing its rules, never its output.

| Property | Rule |
|---|---|
| **Dry run by default** | `plan` writes a report (JSON + Markdown: file, line, before, after, rule id) and changes nothing. Only `apply` writes. |
| **Deterministic** | Input files come from `git ls-files` for the phase's include globs, sorted. Rules apply longest-match-first in a fixed order. Two `plan` runs over the same tree produce byte-identical reports. |
| **Idempotent** | `apply` followed by `apply` changes nothing. `check` exits 1 if any rule still matches in scope. |
| **Exact case** | Lead names and the title match case-sensitively (proper nouns). An all-caps form is its own rule (`RISE OF SUMMONER` → `GARDEN KEEPER AND HIS MULTIVERSE`). Case folding is used only by `census`. |
| **Boundary policy, named** | A match needs a non-identifier neighbour on both sides: `(?<![A-Za-z0-9_])` and `(?![A-Za-z0-9_])`. That is ASCII-scoped on purpose: a Han neighbour counts as a boundary, which fixes the `PvZ融合版` miss that `\b` has (`ip-censor-ideal.md:232-240`). A neighbour from `[-./:_]` followed by an identifier character (`pvz.*`, `commander:dave`, `drop.pvz.run`, prose `Dave-level`) is **never replaced**: an allow-listed form is reported as `identifier`, any other form goes to residue, so a prose compound is never skipped silently. A `.` followed by whitespace or end of line is punctuation, not a separator. |
| **Protected spans** | Never rewritten: fenced code blocks, inline code, Markdown link targets and reference definitions, URLs, HTML attributes other than `content`/`alt`/`title`/`aria-label`, JSON keys, and JSON values of the `_content` identifier fields (`slug`, `related`, `sources`, `pillar`), `{token}` braces. |
| **Identifier allow-list** | A regex list in the rules file (`EmpireId\.\w+`, `WorldFactionKind\.\w+`, `\w*Zomboss\w+`, `PVZRH`, `pvzrh-[\d.]+`, `PvZ ?2`, `PvZ Heroes`, `Garden Warfare`, `FusionRpg\.\w+`, `FUSIONRPG_\w+`, …). A hit inside an allow-listed span is reported as `identifier` and never replaced. |
| **Grammar rules** | Possessive `’s`/`'s` is kept. A lead name replacing at sentence start, after a heading marker or at a table-cell start takes a capital `The`. A replacement that would produce a doubled article (`the the Rotwright`) or `Fusion Fusion` is **not applied**: it goes to residue. |
| **Refuses dirty files** | `apply` refuses to write any file with uncommitted changes (`git status --porcelain`) and lists it as residue. That keeps it from ever writing over another session's work. |
| **Residue is closed by rules** | An unhandled context (an attributive "Zomboss fortress", a compound "Dave-level", a bold glossary term, a sentence whose meaning changes) goes to residue. An agent closes it by adding a phrase rule to the rules file, then re-runs `plan`. A residue item is closed only when a re-run no longer emits it and emits nothing new. |
| **Engine** | Python stdlib `re`. At a handful of patterns over about 300 files it needs no automaton, and it adds no dependency that no lockfile declares (`ip-censor-map.md:152`). |

**The rules, in order (longest first).** Phase `names`:

| Match | Replace | Notes |
|---|---|---|
| `Rise of Summoner` / `RISE OF SUMMONER` | `Garden Keeper and his Multiverse` / all-caps form | Title |
| `Crazy Dave` | `the Garden Keeper` | Sentence-start `The` |
| `Dr. Zomboss`, `Dr Zomboss` | `the Rotwright` | |
| `Zomboss` | `the Rotwright` | Allow-list protects `ZombossDeploy…` and the other identifiers |
| `Dave` | `the Garden Keeper` | Exact case; `dave` identifiers never match |
| `Penny` | `Hourbloom` | No article |

Phase `fusion` (runs only after the `names` phase is applied and its residue is empty):

| Match | Replace |
|---|---|
| `Plants vs. Zombies: Fusion`, `Plants vs. Zombies Fusion`, `PvZ: Fusion`, `PvZ Fusion` | `Fusion` |
| `Plants vs. Zombies`, `Plants vs Zombies`, `Plant vs Zombie` | `Fusion` |
| `PvZ` (display form only; identifiers are allow-listed) | `Fusion` |

### D4 — What the tool does, and what stays a code task

The tool rewrites **prose trees**: `docs/guide/**` sources, `README.md`, `CONTRIBUTING.md`,
`docs/README.md`, `docs/assets/banner.svg`. Code and catalog changes (TS messages that gain ICU
placeholders, C# readers, XAML titles) are ordinary code tasks with tests, because they change
structure, not only words. After each code task, the tool's read-only `plan` over that task's files
must report **zero replaceable hits outside identifiers**. That is the proof the code task missed
nothing.

### D5 — Rendered guide pages are regenerated, never rewritten

`docs/guide/mechanisms/_render.py:1-12` writes `mechanisms/<slug>.md`, `site/mechanisms/<slug>.html`,
the Detail column of `mechanisms/README.md` and the Mechanisms tab of `site/index.html` from
`mechanisms/_content/*.json`. The tool's guide phases therefore **exclude** those outputs, rewrite
`_content/*.json` and the hand-authored pages, then run `python docs/guide/mechanisms/_render.py` and
`--check`. Editing a rendered file would be reverted by the next render. It is the same rule as the
generated-seed rule.

### D6 — Persisted names in existing saves are not migrated (gate G1, answered)

**Owner, 2026-09-19: G1 answered — no migration of names already stored in saves.** *Audit
2026-09-19:* this line previously read "the plan was approved with G1 at its default", which
contradicted the status line ("awaiting owner approval"); only the G1 answer is on record here.
**This program owns no save migration.** The one save migration across the IP work is ip-censor T19b
(the `Jackson*` species ids, `tasks/ip-censor-todo.md` Phase 6); it re-keys species ids only and never
touches `players.name` or stored faction names, and this program never touches a species id.

`RpgStore.cs:4203` writes the onboarding player name into the `players` row once, on an empty boot (the
SQL parameter is `:4188`; *addendum 2026-09-22 — this section cited `:4032`, which is now a JSON number
helper*).
World creation stores faction names from `WorldTemplateCatalog`. After T13, **new** saves and
new worlds get the registry names. **Existing** rows keep what they stored. Rewriting stored rows in
the owner's real save would be the one irreversible step in this program. It is gate **G1** (§7),
answered "no migration", and no task waits on it.

### D7 — Verification per surface (a known boundary gap is reported, not worked around)

`scripts/verify-change.ps1:114` throws `VERIFICATION BOUNDARY MISSING` for an unmapped path.
Measured on 2026-09-19: `docs/**`, `AGENTS.md`, `CLAUDE.md` map to `guard.doc-boundary`; `tasks/**`
maps to the session-boundary guard; `gk-fusion/src/FusionRpg.Launcher/**` and `gk-fusion/src/FusionRpg.Injector/**` are
mapped. **`README.md`, `CONTRIBUTING.md`, `web/**` and `gk-data/packs/fusion/data/seed/narrative/**` are not.** T0 adds
owner rows for `README.md` and `CONTRIBUTING.md`; T1 and T4 add the rows for their own new files in
the same commit that creates them. `web/**` stays
unmapped: the story-scene program already recorded that as a boundary defect
(`tasks/story-scene-todo.md:7-11`). Web tasks therefore name their focused `npm` commands directly
(`AGENTS.md` Web section): `npx vitest run <files>`, `npm run build`, `npm run extract`.

---

## 5. Shared files — who else owns them and how each is coordinated

Measured from `tasks/sessions/*.json` on 2026-09-19 (active records only). Mode matters: a
**worktree** lane meets this program only at its merge; a **direct** session shares this working tree.

| File | Also claimed by | Mode | Coordination |
|---|---|---|---|
| `docs/architecture/decisions.md` | `keepverse-split`; summoner-convergence lanes B, C, D | direct; worktrees | Edit only row `:109`. Before editing: `git status --porcelain -- <file>` must be clean (the tool refuses otherwise), and `git diff <merge-base>..<lane-branch> -- <file>` must not touch that row. If the file is dirty, T10 moves on and records the item as residue. It is never stashed. |
| `docs/PRINCIPLES.md` | `keepverse-split`, `trade-network-idea-20260919`; lanes B, D | direct; worktrees | Same procedure; edit only the identity lines `:39-40,50,345,426` |
| `gk-core/scripts/verification-boundaries.v1.json` | `keepverse-split`; lanes A2, B, C, D | direct; worktrees | Add new owner rows in one contiguous block at the end of `boundaries`, away from `keepverse-roots`' region (before `core-tests-fallback`, per its record). Run `gk-core/scripts/guard-verification-boundaries.py` |
| `gk-data/packs/fusion/data/seed/narrative/_registry/names.en.v1.json` | narrative-seed `names-registry` (owner of the file); lanes C, D (broad globs) | not yet claimed; worktrees | D1 default. If a narrative-seed session record claims the path when T1 starts, T1 uses its file and adds only the parser |
| `gk-data/packs/fusion/data/seed/commanders/_registry/default-commanders.v1.json`, `WorldTemplateCatalog*.cs`, `RpgStore.cs` | lanes B, C, D (broad globs) | worktrees | Region check at merge (`session-boundary.md` §5); the edits are single lines |
| `web/.../story-scene/**`, `OnboardingReveal.tsx`, `TitleScreen.tsx`, `locales/*.po` | lanes C, D (A2 for `.po`) | worktrees | `.po` files are regenerated by `npm run extract`, never hand-merged. On a merge conflict, re-run `extract` on the merged tree |
| `docs/guide/**`, `docs/ideas/onboarding-gnome-teaser.md`, `README.md`, `AGENTS.md` | lanes B, D (broad globs) | worktrees | The tool refuses dirty files. A tool pass is re-runnable, so a conflict at merge is fixed by re-running `apply` on the merged tree, not by hand |
| `tasks/identity-rename-*.md` | `narrative-programs-spec-20260919` (this plan's author) | direct | The implementing session claims them in its own record at T0 |

`AGENTS.md` and `CLAUDE.md` are tracked assistant config: every path written into them stays
repo-relative.

**Keepverse migration.** `tasks/keepverse-split-plan.md:233` gate GM ("start migration") moves this
tree into the Keepverse sub-repos. This program's edits are ordinary source commits the migration tool
carries along. If GM opens before this program closes, the unfinished tasks retarget their include
globs in the rules file; no task depends on a path that the move renames.

---

## 6. Phases and task index

Full task detail, acceptance criteria and verification: [identity-rename-todo.md](identity-rename-todo.md).
One commit per task (code, evidence and the ledger line together), explicit paths, no push.

**Phase 0 — Boundary**
- T0 Session record; verification boundaries for `README.md` and `CONTRIBUTING.md`

**Phase 1 — Foundation: names registry and the tool**
- T1 Names registry (the three leads) and its C# parser in Core
- T2 The server loads the registry (copy rule, hub configuration)
- T3 The TS names reader for the web
- T4 The rename tool (`plan`/`apply`/`check`), its rules and Guard tests
- **Checkpoint 1**

**Phase 2 — The Rift prologue on tokens**
- T5 Cast names from the registry (actorCast, name tag, teaser speaker labels)
- T6 Prologue catalog: no literal names, round-trip render test, extract
- **Checkpoint 2**

**Phase 3 — Names and title on every other surface**
- T7 Guide pillar pages (tool, phase `names`)
- T8 Guide mechanisms: `_content` (tool), then re-render
- T9 Front pages: README, CONTRIBUTING, docs/README, banner (tool)
- T10 Identity lines: AGENTS.md, PRINCIPLES.md, the decisions.md Product vision row
- T11 Web copy: title and onboarding lines on tokens
- T12 Commander display name from the registry
- T13 World faction names and the onboarding player name from the registry
- T14 Launcher and injector window titles
- **Checkpoint 3**

**Phase 4 — "PvZ" / "Plants vs. Zombies" → "Fusion"**
- T15 Guide (tool, phase `fusion`, then re-render)
- T16 Front pages and identity lines
- T17 Web and launcher strings
- **Checkpoint 4**

**Phase 5 — Lock-in**
- T18 Regression guard on web player copy, full-scope `check`, hand-off to ip-censor
- **Final checkpoint**

19 tasks (T0–T18), 5 checkpoints, 1 gate (G1, which blocks no task).

**Order rationale.** The registry and the tool are foundations every later task reads (D1, D3). The
prologue goes second because it is the one surface R9 names first, and it proves the token path end to
end on the smallest scope. Names before "Fusion" because the `fusion` phase creates a new ambiguity
(the host game's name against the fusion mechanic, §8 risk 1), and reviewing it on a tree whose names
already settled keeps each residue list about one thing.

**Parallel work.** After Checkpoint 1: T5–T6 and T11 (web), T7–T10 (docs) and T12–T14 (C#) touch
disjoint files and can run in separate lanes. T15–T17 need Checkpoint 3.

---

## 7. Gates

| Gate | Blocks | Why it is a gate | Resolver | Default if unanswered |
|---|---|---|---|---|
| **G1** Migrate names already stored in existing saves (`players.name` = "Crazy Dave" from onboarding; world faction names stored at world creation) | Nothing in this plan | A rewrite of stored rows in the owner's real save cannot be undone without a backup | Owner | **Answered 2026-09-19: no migration.** New saves and worlds show the registry names; existing rows keep their stored names. No migration task exists. *Audit 2026-09-19: gate closed.* |

There are no other gates. Approval of this plan is the ordinary plan review, not a gate.

---

## 8. Risks

| Risk | Impact | Mitigation |
|---|---|---|
| 1. "Fusion" becomes ambiguous: the host game's name and the specimen-fusion mechanic (the guide already has to say the rail key "is this lab — not the host game's product name") | Medium: confusing prose on the guide's fusion pages | The `fusion` phase sends every replacement within one sentence of a fusion-mechanic word (`fuse`, `fusion lab`, `specimen fusion`, `Fusion (F)`) to residue. An agent resolves each one with a phrase rule (for example "the Fusion host game") |
| 2. Mechanical grammar errors (doubled article, lowercase `the` at sentence start, attributive "the Rotwright fortress") | Medium: visible prose defects across about 300 files | Grammar rules plus residue (D3). T4's fixtures cover each case. Every guide task reviews its Markdown report before `apply` |
| 3. A shared file is dirty from a direct-mode session (keepverse-split, trade-network) when a task reaches it | Low: that one file waits | The tool refuses dirty files (D3). The task commits everything else and records the file as residue. It re-runs later; nothing is stashed |
| 4. Rendered guide outputs are edited instead of their `_content` source | Medium: the next render silently reverts the rename | D5: the outputs are excluded from the tool's include globs, and `_render.py --check` runs in T8 and T15 |

---

## 9. External dependencies

| Dependency | Needed by | Status 2026-09-19 | If not ready |
|---|---|---|---|
| narrative-seed — module `names-registry` (`narrative-seed-map.md` row 9), after `token-grammar` | T1 | Map approved 2026-09-19, spec written (`spec-names-registry.md`); unbuilt (audit 2026-09-19) | D1 default: T1 lands the minimal three-lead file, and narrative-seed adopts it |
| ip-censor — `scan` as the release gate | T18 hand-off only | Map **approved** 2026-09-19 (`ip-censor-map.md:3`); plan awaiting approval (`tasks/ip-censor-plan.md`). *Audit 2026-09-19: status corrected* | T18 writes its alias list as candidate rows in the hand-off note; ip-censor T22 admits them. ip-censor's release gate (its T12) reports every player-facing lead or `PvZ` hit left before this program's Phases 3–4 land, so a release is blocked until then (IC-3, by design). ip-censor classifies source-code roots as `code-identifier` (its plan D10), so the identifiers this program keeps never block a release, and player literals in code are proven by this program's `check` and T18 guard |
| story-scene — owns the prologue code | T5, T6 | Approved program (`tasks/story-scene-todo.md:5`) | T5/T6 are content changes inside its contract (closed `ActorId` set unchanged, message ids stable). No story-scene task is reopened |
| npc-story-events R2 — the antagonist speaks | Not needed | `ActorId` widening is that program's reviewed change (`npc-story-events-ideal.md` §10 R2) | T1 still ships `lead_antagonist`, because the server surfaces (T12, T13) need it |

---

## 10. DESIGN-GATE §5 checklist

```
[x] Subsystems: story-scene (web), i18n, player guide, commanders, world templates, onboarding save, launcher.
[ ] Session boundary recorded: NOT YET. This plan was written under narrative-programs-spec-20260919,
    whose paths include only the two plan files. The implementing session records its own boundary at T0.
[x] Read this session: the §1 Product vision row docs (the-game.md, decisions.md:109), ip-censor-ideal
    §6 and rulings, narrative-seed-ideal §6.5b, npc-story-events-ideal §10, session-boundary.md,
    agent-git.md, the glossary and gameplay-tiers rename precedent.
[x] decisions.md checked: row :109 is the Product vision row R9 names. No lock forbids the rename.
[x] Every factual claim cites file:line.
[x] audit-doc-citations run on this file (result in the hand-off).
[x] Verified against code: story-scene files, commander registry, WorldTemplateCatalog, RpgStore
    onboarding name, verify-change boundary gap, _render.py outputs.
[x] Surrounding sections read for every quoted rule (R8-R12 rows, IC-1b row, §6.1, §6.5b).
[ ] Constraints tested: whether a world-template faction-name change moves a golden is NOT tested
    here. T13's first step runs the focused world tests and reports it.
[x] No §2 invariant contradicted: no new composer, no Funnel/Writer change, no magnitude.
[x] No assertion pins a population: the registry test pins the three lead tokens, a closed vocabulary
    of the §6.5b grammar. The whole registry's size is never asserted.
[x] No event-refreshed cache introduced.
[x] No ordering assumption in play.
```

---

## Standards audit (2026-09-19)

Independent adversarial audit against owner rulings R8–R12 (`npc-story-events-ideal.md` §10), IC-1b,
G1 (answered: no save-name migration), the planning standard, `agent-git.md`, `session-boundary.md`,
the AGENTS.md verification boundary and `testing-standard.md`. Fixed items are marked *Audit
2026-09-19* in place.

| # | Severity | Finding | Status |
|---|---|---|---|
| B1 | MEDIUM | D6 said "the plan was approved with G1 at its default" while the status line says "awaiting owner approval"; the gate table still offered a default | Fixed: D6 and §7 record only the G1 answer; approval status left as the status line says |
| B2 | MEDIUM | Migration ownership against ip-censor's T19b (the `Jackson*` id re-key) was not stated | Fixed: D6 — this program owns no save migration; T19b is the only one and touches no name column |
| B3 | MEDIUM | Cross-plan ordering: the ip-censor release gate stays red until Phases 3–4 land, and a path-based classifier could have made this program's kept identifiers block every release | Fixed: §9 ip-censor row (classifier contract: ip-censor plan D10) |
| B4 | MEDIUM | Citation drift after same-day amendments: `npc-story-events-ideal.md:654,658,659,661,663` (rows now at `:666-675`), `narrative-seed-ideal.md:412-441,428,437-447,444-447`, `narrative-seed-map.md:207,208,229-231`, `PRINCIPLES.md:426` (now `:431`), `verify-change.ps1:95` (now `:118`) | Fixed: cited by ruling id, section or module row, which do not drift |
| B5 | MEDIUM | D1 said narrative-seed's map was awaiting approval; it is approved and `spec-names-registry.md` defines the file with a `ruling` field D1's contract lacked | Fixed: D1, §9 |
| B6 | LOW | ip-censor status in §9 was stale (map approved) | Fixed |
| B7 | LOW | The lead pairs appear in this program's rules file and in ip-censor's `replacements.v1.json` | Deferred: the rules file drives prose rewrites, the ip-censor file only drives suggestions; recorded in the ip-censor plan audit (A8) |

Verified against code this session (sample): `AGENTS.md:1,50,62-63`; `PRINCIPLES.md:39-40,50,345-346,431`;
`decisions.md:109`; `RpgStore.cs:4032`; `WorldTemplateCatalog.cs:78,83`; `WorldTemplateCatalog.TwoHearths.cs:26`;
`RpgHost.cs:170`; `gk-core/src/FusionRpg.Server/Program.cs:421` (the 2026-09-19 reading — the boot-registries
block has since moved; the path is given per the citation audit's D3); `FusionRpg.Server.csproj:40`; `TitleScreen.tsx:25-26`;
`MainWindow.xaml.cs:424`; `FusionRpg.Launcher.csproj:18`; `Win32.cs:82`; `vocabularyGuard.ts:42`.
Boundary claims re-measured with `verify-change.ps1 -PlanOnly -AllowUnscoped`: `README.md`,
`CONTRIBUTING.md`, `web/**` throw `VERIFICATION BOUNDARY MISSING` (T0 maps the first two;
`web/**` is story-scene F1); `docs/assets/banner.svg` → `docs-and-assistant-config`;
`gk-data/packs/fusion/data/seed/commanders/**` → `commander-directory`; launcher and injector paths map to their fallbacks.

**Proposed enforcement-registry row** (added by the implementing session at T18; this audit edits no
shared file): `retired-lead-names-in-player-copy` — source `tasks/identity-rename-plan.md` §1 (R9, R11,
R12, IC-1b); `guards: []`; `unguardableReason`: "enforced by the web vocabulary guard test
(`vocabularyGuard.test.ts`) and `vocab-rename.py check`, not a guard script".

**Verification-boundary asks:** `README.md`, `CONTRIBUTING.md` (T0), `gk-data/packs/fusion/data/seed/narrative/**` (T1),
`gk-core/scripts/vocab-rename*` (T4) — all mapped by this program in the task that creates or first edits them;
`web/**` stays the reported story-scene F1 defect.

---

## 11. Addendum (2026-09-22) — premise verification against the convergence head

Verified at `15baa1454` (worktree `cmdc-arch-d`, session `arch-d-20260922`) before the status line moved to
"approved, ready for lanes". Method: open each cited line, re-run the boundary probe, and count the two
registries. Nothing in this addendum reopens an approved decision; it records what holds and what moved.

### Verified clean — no task changes

| Premise | Evidence at this head |
|---|---|
| D1's default applies: the names registry does not exist, its spec does | `gk-data/packs/fusion/data/seed/narrative/` absent (no `_registry/`); `docs/architecture/narrative-seed/spec-names-registry.md` present; map row 9 at `narrative-seed-map.md:212` names the same path and rows |
| D3's "no rename tool is committed today" | `gk-core/scripts/vocab-rename*` absent |
| D5's two guide files | `docs/guide/mechanisms/_render.py` and `_gen-stubs.ps1` both present |
| T1's registry path: the plan's §5 "not yet claimed" is now **stale** | `tasks/sessions/strain-splice-host-20260922.json` (worktree, `active`) lists `gk-data/packs/fusion/data/seed/**/_registry/**`, which covers `gk-data/packs/fusion/data/seed/narrative/_registry/`. D1's default still holds (the file does not exist), and a worktree lane meets this program only at merge, so T1 proceeds; §5's row is corrected here: the coordination is the same region check, and no other active record claims `gk-data/packs/fusion/data/seed/narrative/**` literally |
| Every web surface literal | `TitleScreen.tsx:25` `Rise of Summoner`, `:26` `Plants vs. Zombies`; `ChronicleLayer.tsx:10` `"PvZ sheet"` |
| Every server/catalog literal | `default-commanders.v1.json:15` `"Dr. Zomboss"`; `WorldTemplateCatalog.cs:78` `Name = "Dave"`, `:83` `Name = "Dr. Zomboss"`; `WorldTemplateCatalog.TwoHearths.cs:26-27` the same two |
| Every launcher/injector literal | `MainWindow.xaml:5` and `:18` `"Rise of Summoner"`; `MainWindow.xaml.cs:424` the folder-picker title; `FusionRpg.Launcher.csproj:18` the description; `Win32.cs:82` the overlay window title |
| Identity lines | `decisions.md:109` Product vision row; `PRINCIPLES.md:39-40,50,345-346,431`; `AGENTS.md:1` |
| `CLAUDE.md` carries no product-name line | `git grep -c "Rise of Summoner" -- CLAUDE.md` → no match |
| T18's guard anchor | `vocabularyGuard.ts:42` is still `const BANNED_WORDS = [` |
| Boundary facts D7 relies on | `README.md` **unmapped**; `CONTRIBUTING.md` **unmapped**; `web/**/TitleScreen.tsx` **unmapped**; `gk-data/packs/fusion/data/seed/commanders/_registry/default-commanders.v1.json` → `commander-directory` (module); `docs/assets/banner.svg` → `docs-and-assistant-config` (focused); `gk-fusion/src/FusionRpg.Launcher/**` → `launcher-fallback` + `launcher-source-guards`; `gk-fusion/src/FusionRpg.Injector/**` → `injector-fallback` |

### Drift — citations only, no task changes

The 2026-09-19 audit already replaced the drift-prone ruling citations with ruling ids. Three anchors moved
since and are re-pointed here; every one is a same-file line move, not a premise change.

| Cited as | At this head | Affects |
|---|---|---|
| `RpgStore.cs:4032` (D6, §2, §5) | `RpgStore.cs:4203` — `const string OnboardingPlayerName = "Crazy Dave"`; the `players` insert's `$name` parameter is `:4188` | D6's reasoning is unchanged; T13's *Files* line should read `:4188,4203` |
| `AGENTS.md:1,50,62` (§2, T10) | `:1`, `:55`, `:67` | T10's *Files* line |
| `scripts/verify-change.ps1:118` (D7, todo conventions) | `:114` — the `VERIFICATION BOUNDARY MISSING` throw | T0/T4/T18 verify lines; cosmetic |
| §5's shared-file row for `gk-data/packs/fusion/data/seed/narrative/_registry/names.en.v1.json` | "not yet claimed" → `strain-splice-host-20260922` claims `gk-data/packs/fusion/data/seed/**/_registry/**` (worktree) | T1 applies the §5 clean-or-skip/region check; the write itself is unaffected |

`gk-data/packs/fusion/data/seed/commanders/_registry/default-commanders.v1.json` resolves at the path the plan names (§2
and §5 both use the plural directory; measured with `verify-change.ps1 -PlanOnly`). No other cited path
moved.

### Not re-measured here

§3's baseline table is a set of 2026-09-19 readings and every task re-measures its own; the addendum does
not restate them, and no test asserts them. T13's world-template golden question (the one untested constraint
in §10) is still T13's first step.

### Verdict

Premises hold. The three drifts are citation anchors inside files the tasks already name, so they are fixed in
the task that first touches each file (T10, T13, T0) rather than by re-issuing the plan. **Status set to
"approved 2026-09-22, ready for lanes".**
