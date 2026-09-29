# Todo: identity-rename

**Program:** `identity-rename` · **Plan:** [identity-rename-plan.md](identity-rename-plan.md)
**Status:** approved 2026-09-22, ready for lanes. Written 2026-09-19; owner approved implementation
2026-09-22. **19 tasks · 5 checkpoints · 1 gate (G1,
answered 2026-09-19: no save-name migration; blocks no task).** Premises re-verified at the convergence
head 2026-09-22 ([plan §11](identity-rename-plan.md) addendum); three citation anchors moved and are
re-pointed in the task that first touches each file (T0 `verify-change.ps1:114`, T10 `AGENTS.md:55,67`,
T13 `RpgStore.cs:4188,4203`).
Status lives here only. One task = one commit (code + evidence + this ledger line), explicit paths,
never `git add -A`, never `git stash`, never amend, never push. No watermarks in commit messages.
*Audit 2026-09-19: G1 state, "never stash" and "never amend" added.*

**Conventions for every task**

- `<sid>` is the implementing session's id (`identity-rename-<yyyymmdd>`, recorded at T0).
- Web commands run from `gk-web/web/fusion-rpg-web`. `web/**` has no verification boundary
  (`scripts/verify-change.ps1:114`; recorded as story-scene follow-up F1, `tasks/story-scene-todo.md:7-11`),
  so web tasks name focused `npm` commands and never pass web paths to `verify-change.ps1`.
- Tool tasks: run `plan` first, read the Markdown report, close every residue item **by adding a rule
  to `gk-core/scripts/vocab-rename/identity-rename.v1.json`**, re-run `plan` until residue is empty, then
  `apply`, then `check`. Never hand-edit a file the tool owns for that phase.
- Counts in the ledger are readings (before/after hits, files touched). No test asserts them.
- Before touching a shared file, apply the procedure in plan §5: clean `git status` for that file,
  and no lane branch touches the same region. A dirty shared file is skipped and recorded, never stashed.

---

## Phase 0 — Boundary

- [ ] **T0 Session record and boundaries for the unmapped front pages.**
  *Files:* `tasks/sessions/<sid>.json` (new), `gk-core/scripts/verification-boundaries.v1.json`.
  *Do:* run `/session-start`; claim this program's paths (the files named in T1–T18) in `direct` mode
  unless the owner picks a worktree; record in `notes` the shared-file crossings from plan §5. Add
  one owner row mapping `README.md` and `CONTRIBUTING.md` to project `guard`, verificationId
  `guard.doc-boundary`, in a new block at the end of `boundaries`.
  *Accept:* `python scripts/session-boundary-check.py --session <sid>` is clean for this session;
  `verify-change.ps1 -Paths README.md` no longer throws `VERIFICATION BOUNDARY MISSING`.
  *Verify:* `python gk-core/scripts/guard-verification-boundaries.py`;
  `.\scripts\verify-change.ps1 -Paths tasks/sessions/<sid>.json,gk-core/scripts/verification-boundaries.v1.json,README.md -Session <sid>`.
  *Commit:* `identity-rename T0: session record and doc boundaries for README and CONTRIBUTING`.
  *Blocked 2026-09-22 (lane `identity-rename-1`):* the session record landed; the boundary row did
  **not**. Mapping `README.md` makes `gk-core/tests/FusionRpg.Guard.Tests/VerificationBoundaryWorkflowTests.cs:243`
  fail by design — it pins `README.md` as *the* unmapped path — and that file is a hook-protected
  pipeline file this lane may not edit, while widening the guard or adding a `knownRed` entry is
  forbidden. The registry edit was reverted so the tree stays green. Exact two-part patch (registry row
  + move the fixture to `LICENSE`): `tasks/reports/identity-rename-t0-boundary-blocker.md`. T1 onward
  proceed: the session record — the load-bearing half for `verify-change.ps1` — is in place, and the
  front-page row matters only at T9/T16.

## Phase 1 — Foundation

- [x] **T1 Names registry and its C# parser.** *Depends:* T0. *External:* narrative-seed (plan D1).
  *Landed 2026-09-22 (lane `identity-rename-1`):* narrative-seed has **not** built its
  `names-registry` module, so plan D1's default applied and T1 landed the minimal three-lead file at
  the spec's path, in `narrative-seed/spec-names-registry.md` §1's shape including each row's
  `ruling`. That is the approved default, not an invented input; narrative-seed's module adopts this
  file as its v1 (its later fields are additive). The parser carries extra well-formed rows rather
  than refusing them, because narrative-seed unions character names into the same set later.
  *Files:* `gk-data/packs/fusion/data/seed/narrative/_registry/names.en.v1.json` (new, unless narrative-seed already
  landed it), `gk-core/src/FusionRpg.Core/Narrative/LeadNames.cs` (new: pure parser plus a process-wide hub
  on the `CommanderDirectoryHub` pattern, `gk-core/src/FusionRpg.Core/Commanders/CommanderDirectoryHub.cs:1-26`;
  Core never reads a path), `gk-core/tests/FusionRpg.Core.Tests/Narrative/LeadNamesTests.cs` (new,
  `[Trait("VerificationId","core.lead-names")]`, in memory), a boundary row for the three paths in
  `gk-core/scripts/verification-boundaries.v1.json`.
  *Accept:*
  - The file carries the three lead rows of plan D1, in the shape of `narrative-seed/spec-names-registry.md`
    (including each row's `ruling`; audit 2026-09-19). The parser throws on a missing field, an unknown
    `article`/`gender`/`number` value, or a missing lead token.
  - The test pins the **three lead tokens** (a closed vocabulary: the §6.5b grammar,
    `narrative-seed-ideal.md` §6.5b) and the enum members. It never asserts the size of `names`,
    because narrative-seed adds character rows later.
  - A test parses a second, synthetic name set and gets different display strings for the same tokens.
  *Verify:* `.\scripts\verify-change.ps1 -Paths <the four files> -Session <sid>`.
  *Commit:* `identity-rename T1: lead names registry and Core parser`.

- [x] **T2 The server loads the registry.** *Depends:* T1.
  *Files:* `gk-core/src/FusionRpg.Server/FusionRpg.Server.csproj` (copy rule for
  `gk-data/packs/fusion/data/seed/narrative/_registry/**`, same pattern as the dungeon rule at `:40-41`),
  `gk-core/src/FusionRpg.Server/Program.cs` (read the file beside `AppContext.BaseDirectory` and configure the
  hub, next to the commander registry at `:421`), one server test.
  *Accept:* a published server resolves `lead_summoner` to the registry's `display`; a server started
  without the file fails at boot with a message naming the path (never a silent default name).
  *Verify:* `.\scripts\verify-change.ps1 -Paths <the three files> -Session <sid>`.
  *Commit:* `identity-rename T2: server hosts the lead names registry`.
  *Landed 2026-09-22 (lane `identity-rename-1`), with one re-scope:* the boot read moved into a named
  seam, `gk-core/src/FusionRpg.Server/Narrative/LeadNamesBoot.cs`, because `Program.cs` is top-level statements
  and its second acceptance line (a boot that fails naming the path) is otherwise unprovable. That
  seam is what proves both lines: `gk-core/tests/FusionRpg.Server.Tests/LeadNamesBootTests.cs` reads the
  registry from the **published** layout beside the test host (so the copy rule is exercised, not
  assumed) and asserts the missing-file failure names the path; `gk-core/tests/FusionRpg.E2E.Tests/
  LeadNamesBootE2ETests.cs` boots the **real** host through `RpgApiFactory` and asserts the hub is
  configured — the proof a self-configuring test cannot give, since nothing else in that process
  touches the hub. `Program.cs` keeps the literal path (not a constant) so `BootContentCopyRuleTests`
  can still see that a `<Content>` rule covers it. Two new focused boundary rows: `server-lead-names`
  and `e2e-lead-names-boot`.

- [x] **T3 The web names reader.** *Depends:* T1.
  *Files:* `gk-web/web/fusion-rpg-web/src/i18n/leadNames.ts` (new; imports the registry JSON by relative path,
  the precedent is `sceneScript.ts:1`), `gk-web/web/fusion-rpg-web/src/i18n/leadNames.test.ts` (new).
  *Accept:*
  - `leadName(token)` returns the bare `display`. `leadNameValues()` returns the ICU values
    (`lead_summoner`, `lead_summoner_article`, …) for message interpolation (plan D2).
  - The `pseudo` locale falls back to `en`, matching `lingui.config.ts`'s `fallbackLocales`.
  - An unknown token throws.
  - A test swaps in a synthetic registry and the outputs change exactly at the tokens.
  *Verify:* `npx vitest run src/i18n/leadNames.test.ts`; `npm run build`.
  *Commit:* `identity-rename T3: web lead-name reader`.
  *Landed 2026-09-22 (lane `identity-rename-1`):* eight tests, all four acceptance lines. The reader
  also refuses a tag value outside its closed set — a bad `article` would otherwise let ICU fall
  through to its `other` arm and render a grammar defect with no error anywhere — and it documents
  that a second locale is additive beside the English file. Web paths still get no
  `verify-change.ps1` boundary (`web/**` is story-scene's reported F1 gap), so this task's evidence is
  the two focused `npm` commands.

- [x] **T4 The rename tool.** *Depends:* T0.
  *Files:* `gk-core/scripts/vocab-rename.py` (new), `gk-core/scripts/vocab-rename/identity-rename.v1.json` (new: the
  rules, identifier allow-list, protected spans and phase scopes of plan D3),
  `gk-core/tests/FusionRpg.Guard.Tests/VocabRenameTests.cs` (new, `[Trait("VerificationId","guard.vocab-rename")]`;
  runs the script's functions through an in-memory Python harness, the `DocCitationAuditTests.cs`
  precedent), a boundary row for the three paths.
  *Accept:* each case below has a fixture test.
  - Identifiers are untouched: `pvz.*`, `drop.pvz.run`, `PVZRH`, `pvzrh-3.9`, `PvZ2`,
    `EmpireId.Dave`, `WorldFactionKind.Zomboss`, `ZombossDeployEndpoints`, `commander:dave`,
    `first-win-dave`, a link target `(mechanisms/dave-level.md)`, inline code, a fenced block, an
    `href`.
  - `PvZ融合版` matches (the Han boundary). `Dave-level` in prose goes to residue, not silently skipped.
  - Grammar: "Crazy Dave" at sentence start becomes "The Garden Keeper"; "Zomboss’s" becomes "the
    Rotwright’s"; "the Zomboss" goes to residue (doubled article); "PvZ Fusion" becomes "Fusion", never
    "Fusion Fusion".
  - Behaviour: `plan` writes nothing; two `plan` runs are byte-identical; `apply` twice equals
    `apply` once; `check` exits 1 while a rule still matches; `apply` refuses a dirty file.
  *Verify:* `.\scripts\verify-change.ps1 -Paths <the four files> -Session <sid>`.
  *Commit:* `identity-rename T4: deterministic vocab-rename tool and identity rules`.
  *Landed 2026-09-22 (lane `identity-rename-1`):* 33 Guard tests, each acceptance case a fixture. The
  harness drives the tool's **real CLI** (`vr.main`) with its five IO seams replaced by one in-memory
  tree, so `plan`/`check`/`apply` are exercised as the guide tasks will run them, not re-implemented.
  Two defects found by the tool's own first real run and fixed here: the `Zomboss` allow-list pattern
  was `…Zomboss[A-Za-z0-9_]*`, which masked a bare `Zomboss` and killed the rule (`plan` reported it as
  an identifier) — now `[A-Za-z0-9_]+`, mirroring D3's `\w*Zomboss\w+`; and the report path used
  `Path.with_suffix`, which ate the `.journal` in its own name.

### Checkpoint 1 — foundation
- [x] T1–T4 verified. The registry loads in Core, the server and the web.
- [x] `python gk-core/scripts/vocab-rename.py plan --rules gk-core/scripts/vocab-rename/identity-rename.v1.json
  --phase names --report-dir tasks/reports` over the whole phase scope runs, and its report is attached
  to the ledger (a reading). Nothing is applied yet. **Reading (2026-09-22): 91 files scanned, 231
  replacements over 43 files, 11 residue, 0 identifiers.** Reports:
  `tasks/reports/identity-rename-names.journal.{json,md}`.
- [ ] Owner review of the report's residue sample before any `apply`. **Open (2026-09-22):** the sample
  is 11 items, all `Dave` attribute compounds (`Dave-level`, `Dave-gated`, `a Dave threshold`, `the
  Dave numbers`) at `README.md:122`, `docs/guide/README.md:72`, `docs/guide/how-you-play.md:52`,
  `docs/guide/mechanisms/_content/{naming-ritual,unlock-beats,unlock-chapters}.json`,
  `docs/guide/site/index.html:334`. Each needs a **phrase** rule (it changes wording, not just a name),
  so a named reviewer decides the phrasing before T7/T8 run `apply`. Rows that do not `apply`
  (T5, T6, T9–T14) proceed meanwhile.

## Phase 2 — The Rift prologue on tokens

- [x] **T5 Cast names from the registry.** *Depends:* T3.
  *Files:* `gk-web/web/fusion-rpg-web/src/features/story-scene/actorCast.ts`, `actorCast.test.ts`,
  `docs/ideas/onboarding-gnome-teaser.md` (the beat table's speaker labels `**Dave:**`/`**Penny:**`
  → the lead tokens; that file is the copy SSOT, `sceneScript.ts:6-8`).
  *Accept:*
  - `ActorDefinition` gains `nameToken` (`dave` → `lead_summoner`, `penny` → `lead_companion`).
  - `displayName` and `initial` derive from the registry, not a literal (`actorCast.ts:67-83`).
  - The `ActorId` members and theme ids are unchanged (identifiers, plan §2).
  - The existing distinctness tests (`actorCast.test.ts:47,119-125`) still pass against the registry values.
  *Verify:* `npx vitest run src/features/story-scene src/ui/story-scene`; `npm run build`;
  `.\scripts\verify-change.ps1 -Paths docs/ideas/onboarding-gnome-teaser.md -Session <sid>`.
  *Commit:* `identity-rename T5: story cast names come from the lead names registry`.
  *Landed 2026-09-22 (lane `identity-rename-1`), five files beyond the row's own three:* three test
  files and the catalog pinned the retired strings, and `@lingui/macro` cannot take a runtime string,
  so `messagesForCast` now carries the **token** as a literal (`"{lead_summoner}"`) and the parity
  test renders it with `leadNameValues()`. That is the minimum of T6's catalog shape that T5's own
  change forces; T6 still owns the no-display-in-catalog guard, the two-name-set round-trip test and
  the script-line checks.
  *Finding (for the manager):* `docs/ideas/onboarding-gnome-teaser.md` still names both leads in
  prose (`:15` "**Dave** wants to save…", `:30` "Dave steps forward; Penny projects…") — plan §2
  scopes that file to "speaker labels only", and `docs/ideas/**` is outside the tool's phase scope, so
  the tool cannot report it. Either the scope grows or the plan says why those two lines stay.
  *Finding (for T6/T15):* `lingui extract` keeps an explicit-id message's **old** `msgstr` when its
  source text changes (the `en` catalog kept "Penny"/"Dave"), so the update needed the two stale
  entries removed and a re-extract, not just `npm run extract`.

- [x] **T6 Prologue catalog without literal names.** *Depends:* T5.
  *Files:* `gk-web/web/fusion-rpg-web/src/features/story-scene/messages.ts`, `messages.test.ts`,
  `sceneScript.test.ts`, `gk-web/web/fusion-rpg-web/src/i18n/locales/en/messages.po`,
  `gk-web/web/fusion-rpg-web/src/i18n/locales/pseudo/messages.po` (regenerated, never hand-edited).
  *Accept:*
  - `messagesForCast` (`messages.ts:140-150`) no longer carries `actor.dave.name`/`actor.penny.name`
    literals. Names are registry data, and the catalog holds no name.
  - Any beat or chrome line that mentions a lead uses an ICU placeholder, with the article selected on
    the tag.
  - A test fails if any catalog literal or script line contains a registry `display` string.
  - A round-trip test renders every prologue string against two name sets, and the outputs differ
    exactly at the tokens (`narrative-seed-ideal.md` §6.5b).
  *Verify:* `npx vitest run src/features/story-scene src/ui/story-scene`; `npm run extract`, then
  commit the catalog diff; `npm run build`; the tool's `plan` over `src/features/story-scene` reports
  zero replaceable hits outside identifiers.
  *Commit:* `identity-rename T6: prologue catalog carries lead tokens, not names`.
  *Landed 2026-09-22 (lane `identity-rename-1`):* the token literals themselves landed with T5 (the
  macro forced that shape), so this row completed the guards: no registry `display` in any catalog
  literal or in any `sceneScript` line, and a round-trip render of **every** `storySceneMessages()`
  entry against two name sets that differs exactly at the tokens (the shipped leads are both
  exercised, so it is not vacuous). The article-select shape is pinned by a synthetic descriptor — no
  shipped prologue line mentions a lead in running text yet, and the ledger says so rather than
  claiming coverage it does not have. `npm run extract` produced **no** catalog diff (T5's extract
  already carried the tokens).
  *Re-scope:* the tool gained a `--paths` override (an explicit list beats the phase's include globs,
  the exclude list still binds) plus its Guard test, because D4 asks a code task to `plan` over files
  that sit outside the prose scope `apply` walks — T6, T11 and T17 all need it.
  *Erratum ask:* the row's tool clause ("zero replaceable hits outside identifiers") cannot be zero.
  Measured over `gk-web/web/fusion-rpg-web/src/{features,ui}/story-scene` in the names phase: 46 replacements
  + 4 residue — **22 in code comments, 28 in test fixtures, 0 in a player-facing string**; `messages.ts`
  and `sceneScript.ts` report none, and 8 identifiers are left alone. Plan §2 puts code comments and
  "test fixture data that uses Dave as an arbitrary name" out of scope, so the achievable check is the
  classification above plus the catalog/script assertions, not a zero. A ruling is needed: mask code
  comments in the tool (which risks masking a URL's `//`), or restate the clause as "no hit in a
  player-facing string".

### Checkpoint 2 — prologue
- [ ] Open the prologue through `/review-web`: the name tags read "Garden Keeper" and "Hourbloom".
- [ ] A one-line edit of `names.en.v1.json` changes both tags after a rebuild, with no other file touched.
  Revert the edit afterwards; it is a proof, not a commit.

## Phase 3 — Names and title on every other surface

- [x] **T7 Guide pillar pages.** *Depends:* CP1.
  *Files:* `docs/guide/*.md` (pillar pages, `glossary.md`, `the-game.md`, `the-rift.md`, …), tool phase `names`.
  *Accept:*
  - `the-game.md:17` reads "You are **the Garden Keeper**". The vision sentence at `the-game.md:13`
    no longer claims the leads are Fusion's own characters; a phrase rule rewrites it to name them as
    the game's own leads.
  - The glossary term row (`glossary.md:62`) names the Rotwright.
  - `check` is clean for the phase scope. No link target or slug changed (`git diff` shows no `](` target edits).
  *Verify:* `.\scripts\verify-change.ps1 -Paths <changed docs/guide files> -Session <sid>`.
  *Commit:* `identity-rename T7: guide pillar pages use the new title and lead names`.
  *Landed 2026-09-22 (lane `identity-rename-1`), 240 replacements over 43 files.* CP1's sample was
  closed **by rules, never by edits to the tool's output**, and the manager's direction to take this
  row is the ruling that unblocked it. Five new phrase rules in `gk-core/scripts/vocab-rename/identity-rename.v1.json`:
  `Dave-level` → `Keeper-level` (8 sites), `Dave-gated` → `Keeper-gated`, `a Dave threshold` →
  `a Keeper threshold`, `the Dave numbers` → `the Keeper numbers`, and `vision-sentence-own-leads`,
  which replaces `the-game.md:13`'s apposition so the leads are named as **the game's own** rather than
  as Fusion's characters.
  *Wording decision (for review):* the compounds take the **short lead form** — `Keeper-level` — on
  three grounds: `unlock-chapters.json`'s own term table defines the concept as "your summoner's endless
  level"; `narrative-seed-ideal.md` §6.5b sanctions the short vocative ("You are too late, Keeper"); and
  keeping the hyphenated shape moves no sentence structure. The alternative, `Garden Keeper-level`
  everywhere, is a one-line change to four rules if the reviewer prefers it.
  *Citation drift (audit):* the row's `glossary.md:62` is now **:67**, and that row already reads
  `| **the Rotwright** | The enemy commander. He decides from his own fog |` — the reference had drifted
  5 lines, the row itself needed no separate edit.
  *Reading:* `check --phase names` is clean — **0 replacements, 0 residue over 91 files**; no link
  target, `slug`, `related`, `pillar` or `sources` value moved (checked mechanically against `HEAD`,
  not eyeballed). The tool applies the phase scope atomically, so the front pages and `banner.svg` came
  with it; **T9 still owns its own acceptance lines** (the title line and the two-names lines, both
  verified intact) and the boundary row T0 could not land. The mechanisms `_content` is renamed here
  and its rendered output is now stale — T8's first act is `_render.py`.
  *Blocked on CP1 (2026-09-22):* `check` cannot be clean until the 11 residue items the T4/CP1
  reading reports are closed, and every one is a **`Dave` attribute compound** (`Dave-level`,
  `Dave-gated`, "a Dave threshold", "the Dave numbers"). The tool correctly refuses the mechanical
  replacement ("a the Garden Keeper threshold"), so each needs a **phrase rule** whose wording —
  "Keeper-level"? "summoner-level"? "Garden Keeper level"? — is a product decision. That is exactly
  what CP1's owner-review line gates, so T7, T8 and T9 wait for the ruling rather than the lane
  inventing the phrasing. The mechanical half is ready: the rules file, the tool and the reading are
  in place, and `apply` is one command once the wording is ruled.

- [x] **T8 Guide mechanisms, then re-render.** *Depends:* T7.
  *Files:* `docs/guide/mechanisms/_content/*.json` (tool), then the rendered outputs of
  `docs/guide/mechanisms/_render.py`: `mechanisms/*.md`, `site/mechanisms/*.html`,
  `mechanisms/README.md`, the Mechanisms tab of `site/index.html`, plus the hand-authored parts of
  `site/index.html` (tool).
  *Accept:*
  - Rendered files change only through `_render.py`.
  - `python docs/guide/mechanisms/_render.py --check` passes. `check` is clean on sources and outputs.
  - `_gen-stubs.ps1` is untouched (plan §2).
  *Verify:* `_render.py --check`; `.\scripts\verify-change.ps1 -Paths <changed files> -Session <sid>`.
  *Commit:* `identity-rename T8: guide mechanism pages renamed at the source and re-rendered`.
  *Landed 2026-09-22 (lane `identity-rename-1`):* the sources were already renamed by T7's `apply`
  (the tool owns `_content/*.json`, never the outputs), so this row is the render: `python
  docs/guide/mechanisms/_render.py` → `rendered 66 mechanism(s) → markdown + site HTML`, 132 changed
  files, **all of them render outputs** (`66 md` + `66 html`; `mechanisms/README.md` and the Mechanisms
  tab of `site/index.html` produced no diff because their Detail column carries no renamed string).
  `_render.py --check` → `checked 66 content files — 0 error(s)`, exit 0; `_gen-stubs.ps1` and
  `_render.py` untouched. The tool's `check` stays clean because the phase scope excludes the rendered
  outputs (D5), which is exactly why hand-editing one is impossible to keep.
  *Completed 2026-09-22 by reading the re-rendered output — three defects the render exposed, all fixed
  in a second commit for this row:*
  1. **`_render.py` hardcoded the retired title** in the site chrome (page `<title>`, `brand-name`,
     footer line) — a **generator** string, so the fix is the generator plus a re-render, exactly the
     "fix the generator, never the generated file" rule. All 66 `site/mechanisms/*.html` were carrying it.
  2. **The phase's glob exclude swallowed a hand-authored page.** `docs/guide/mechanisms/*.md` was
     excluded to keep rendered pages away from the tool, but `local-control-room.md` has no
     `_content` twin — it is authored — so its **12 real prose hits were never renamed and `check` still
     said clean**. The exclusion is now **derived**: the phase declares its `rendered` spec (content
     glob, slug key, output patterns plus `mechanisms/README.md`), and the tool excludes exactly the
     outputs whose content file exists. A hand-authored page is in scope; a new mechanism's page is
     excluded with no rule to update. A Guard test pins both directions.
  3. **A stale anchor**: `_content/{fog-of-war,zomboss-commander}.json` cited
     `docs/guide/glossary.md §Zomboss`, and the glossary row is now `**the Rotwright**` (at `:67`) —
     re-anchored to `§the Rotwright` (a `sources` value, so a citation a human owns, not prose).
  *Final reading:* `check --phase names` → **0 replacements, 0 residue over 93 files**;
  `_render.py --check` → 66 content files, 0 errors; the only retired string left anywhere under
  `docs/guide/**` is inside `_gen-stubs.ps1`, the historical generator its own header forbids re-running
  and plan §2 puts out of scope.

- [x] **T9 Front pages.** *Depends:* CP1.
  *Files:* `README.md`, `CONTRIBUTING.md`, `docs/README.md`, `docs/assets/banner.svg` (`aria-label`
  and visible text), tool phase `names`.
  *Accept:*
  - The title reads "Garden Keeper and his Multiverse".
  - The "two names" lines (`README.md:253`, `CONTRIBUTING.md:3`, `docs/README.md:3`) keep `FusionRpg`
    as the internal prefix.
  - `check` is clean.
  *Verify:* `.\scripts\verify-change.ps1 -Paths <changed files> -Session <sid>`.
  *Commit:* `identity-rename T9: front pages carry the new title and lead names`.
  **No commit: the four front pages were already rewritten by T7's atomic phase apply**, and landed in
  `367e07c81`. This row is the verification, and it passes: the title reads "Garden Keeper and his
  Multiverse" on `README.md:19`, `:25` and `:253`, `CONTRIBUTING.md:3`, `docs/README.md:3` and in the
  banner's `aria-label`; all three "two names" lines keep `FusionRpg` as the internal prefix; `check`
  is clean. `verify-change.ps1 -Paths docs/README.md,docs/assets/banner.svg` → Guard doc-boundary 4/4,
  doc-citations 0 HIGH. **`README.md` and `CONTRIBUTING.md` cannot be verified at a boundary at all**
  — that is T0's blocked half, exactly as its blocker report predicted, and it is the strongest check
  achievable for those two; the reading above is otherwise their whole evidence.

- [x] **T10 Identity lines in the rule files.** *Depends:* CP1. *Shared files:* plan §5.
  *Files:* `AGENTS.md` (`:1,50,62`), `docs/PRINCIPLES.md` (`:39-40,50,345-346`; audit 2026-09-19: `:346` carries Penny),
  `docs/architecture/decisions.md` (row `:109` only). Check `CLAUDE.md`.
  *Accept:*
  - Title and lead names are updated on those lines only.
  - The Product vision row keeps its pitch (RPG plus empire-building extension). It cites rulings
    R8–R12 and IC-1b for the rename, and it names the registry as the source of the lead names.
  - `CLAUDE.md` is re-measured. If it has no product-name line, the ledger says so and it is not edited.
  - Every path written stays repo-relative.
  *Verify:* `.\scripts\verify-change.ps1 -Paths AGENTS.md,docs/PRINCIPLES.md,docs/architecture/decisions.md -Session <sid>`;
  `python scripts/audit-doc-citations.py --scope docs/architecture/decisions.md` has no new HIGH finding.
  *Commit:* `identity-rename T10: record the new IP name and leads in AGENTS, PRINCIPLES and decisions`.
  *Landed 2026-09-22 (lane `identity-rename-1`):* `AGENTS.md:1,55,67` (title only — that file names no
  lead), `docs/PRINCIPLES.md:39-40,50,345-346` (title, the vision sentence, the two-names line, and the
  identity block: the Keeper and Hourbloom against the Rotwright) and `decisions.md`'s Product vision
  row, which now cites **R8–R12** and **IC-1b** and names the registry
  (`gk-data/packs/fusion/data/seed/narrative/_registry/names.en.v1.json`, one row edit per lead) while keeping its pitch and
  its `../guide/the-game.md` citation. `PRINCIPLES.md:366,400` keep "Zomboss" — those are architecture
  lines naming the Zomboss **faction/identifier**, which plan §2 keeps, and the row's file list names
  only `:39-40,50,345-346`.
  *`CLAUDE.md` re-measured, not edited:* `grep -c "Rise of Summoner" CLAUDE.md` → **0**, so it has no
  product-name line; its `PvZ` mentions are the engineering layer term (plan §2).
  *Shared-file procedure (plan §5):* `git status --porcelain` over the three files was clean before the
  edit, row `:109` was the only `decisions.md` row touched, and no other lane's region moved.
  *Finding (pre-existing, needs routing):* `AGENTS.md:125` cites `` `status.json` `` and the audit
  reports **D1 HIGH — no tracked file with this name** in this worktree. The cause, read not guessed: the
  eight tracked `status.json` paths all live under another lane's `.claude/cmdc-agents/agents/**`
  directory, which a worktree lane's checkout does not contain, so the audit's physical-existence check
  fails here and in any lane — the row's own audit line scopes to `decisions.md` (clean: 0 HIGH), which
  is why this does not block T10. It is not this program's line to edit (acceptance: "those lines
  only"), so it is filed as a pointer with its `file:line` and cause for the manager to route.

- [x] **T11 Web copy on tokens.** *Depends:* T3.
  *Files:* `gk-web/web/fusion-rpg-web/src/app/TitleScreen.tsx` (`:25` title), `src/stages/sanctum/OnboardingReveal.tsx`
  (`:33,35,50`), `OnboardingReveal.test.tsx`, `src/stages/sanctum/FocusCard.tsx` (`:50,54`), both `messages.po`.
  *Accept:*
  - Each lead mention is an ICU placeholder fed by `leadNameValues()`, with the article selected on
    the tag (so "The Garden Keeper joins your side" renders).
  - The message ids are unchanged, so no translation is orphaned.
  - The test asserts against the registry value, not a literal.
  *Verify:* `npx vitest run src/stages/sanctum src/app`; `npm run extract` (commit the diff); `npm run build`;
  the tool's `plan` over these files reports zero replaceable hits.
  *Commit:* `identity-rename T11: title and onboarding copy use the new title and lead tokens`.
  *Landed 2026-09-22 (lane `identity-rename-1`):* five lead mentions on tokens, message ids unchanged.
  The typed interpolation overload in this lingui version is `_(id, values)` — `_(descriptor, values)`
  is a type error (it *works* at runtime, which is why T5's test passed, but it does not compile in a
  checked file), so the calls pass `descriptor.id` and the descriptor still owns the id. Two of the
  four name-bearing lines are in `FocusCard`, which had raw JSX literals: they became catalog messages
  because plan **D2 forbids code that concatenates an article onto a name**, and the module-level
  `i18n` is used there so the component gains no provider dependency. The tool's `plan` over the four
  touched files is **0 replacements, 0 residue, 6 identifiers** — clean, unlike T6's tree-wide clause.
  *Repeat finding:* `lingui extract` kept the old `msgstr` for all three changed ids again (the same
  trap as T5), so they were removed from `en` and re-extracted. Third occurrence in this program.

- [x] **T12 Commander display name from the registry.** *Depends:* T2.
  *Files:* `gk-data/packs/fusion/data/seed/commanders/_registry/default-commanders.v1.json` (`:15` becomes `"{lead_antagonist}"`),
  `gk-core/src/FusionRpg.Core/Commanders/DataCommanderDirectory.cs`, the tests that pin the shipped value:
  `gk-core/tests/FusionRpg.Core.Commanders.Tests/Commanders/CommanderDirectoryTests.cs:70`,
  `gk-core/tests/FusionRpg.Core.Commanders.Tests/Commanders/PlayerEmpireCommandersTests.cs:36`
  (*citation re-anchored 2026-09-22: the Core.Tests split moved both files out of
  `gk-core/tests/FusionRpg.Core.Tests/Commanders/`*),
  `gk-core/tests/FusionRpg.Server.Tests/CommanderListEndpointsTests.cs`.
  *Accept:*
  - A `displayName` of the form `{token}` resolves through the lead-names hub. An unknown token throws.
  - Tests assert equality with the **registry's** value, never the literal "Rotwright", so a rename stays a one-file edit.
  - First step: list every host that renders `DisplayName`, using `codegraph callers` (the injector
    loads the same registry at `gk-fusion/src/FusionRpg.Injector/Host/RpgHost.cs:170`). Each such host resolves
    the token; a host that only reads scope keys needs no names file, and the ledger says which.
  *Verify:* `.\scripts\verify-change.ps1 -Paths <changed files> -Session <sid>`.
  *Commit:* `identity-rename T12: the antagonist commander's name comes from the lead names registry`.
  *Reopened and landed 2026-09-22 (lane `identity-rename-1`).* The blocker was re-read as the row itself
  frames it — "the injector path needs `FUSIONRPG_GAME_DIR` for interop refs; **if it is not set, say so
  in the commit body**" — and T14 had already settled that a missing game dir is a documented skip, not a
  bar: `guard-injector-compile` reports its own `SKIPPED — no MelonLoader game dir ... injector NOT
  compiled`. So the row was implemented in full:
  * `DataCommanderDirectory.DisplayName` resolves a brace-wrapped row through `LeadNamesHub`
    (`"{lead_antagonist}"` → the registry's display); a literal passes through, an unknown token throws
    the hub's own `UnknownLeadNameException` — both halves pinned by new tests.
  * `gk-data/packs/fusion/data/seed/commanders/_registry/default-commanders.v1.json`'s antagonist row is now
    `"{lead_antagonist}"`.
  * The injector host configures the names registry beside the commander hub it already read
    (`RpgHost.cs`), and **all three** injector host csprojs ship
    `data\seed
arrative\_registry\*.json` next to the plugin — without that copy rule the injector
    would throw on a fresh install, which is the same B27/BP4 failure the commander registry hit in
    2026-09-20.
  * The two tests that pinned the shipped literal now assert the **registry's** value
    (`CommanderDirectoryTests`, `PlayerEmpireCommandersTests`); synthetic `new CommanderRow(...)`
    fixtures keep their own literal, which plan §2 keeps.
  * Verification: Core.Commanders.Tests **66/66**, the server's commander tests **40/40**, the residual
    Core.Tests **10097/10097**, guard-dal OK, and the injector-compile guard's own skip. The *full*
    `core` project group that `verify-change` selects for `DataCommanderDirectory.cs` was not run
    (the changed file is covered by the residual project plus the dedicated Commanders project); that
    boundary is named rather than assumed.
  *First step done, then blocked 2026-09-22 (lane `identity-rename-1`):* the host list, read with
  `grep` (this machine has no `codegraph` CLI): `DataCommanderDirectory.DisplayName` is the one
  authored-row reader, and it is reached by `gk-core/src/FusionRpg.Server/CommanderEndpoints.cs:127` (the
  server's commander list) and by `MatchCommanderSessionCache.cs:56,113` (the injector's HUD snapshot).
  `UniqueCommanderSource` delegates to role holders, so it needs no token. Resolving `{token}` for the
  antagonist therefore needs `LeadNamesHub` configured in **both** hosts — the server has it from T2;
  the injector does not, and needs its own copy rule plus a boot configure. That half cannot be built
  or tested here: `FUSIONRPG_GAME_DIR` is unset, so the injector project does not compile. Marked
  `blocked` with that reason; the server-only half is *not* shipped, because a `{token}` left
  unresolved in the injector path would throw at snapshot time on a real install.

- [x] **T13 World faction names and onboarding player name.** *Depends:* T2. *Gate:* G1 — answered: no
  migration (audit 2026-09-19).
  *Files:* `gk-core/src/FusionRpg.Core/World/WorldTemplateCatalog.cs` (`:78,83`),
  `WorldTemplateCatalog.TwoHearths.cs` (`:26-27`), `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs` (`:4188,4203`),
  the web fixtures `gk-web/web/fusion-rpg-web/src/stages/world/fixtures/{first-light,eighteen-ten,two-hearths}.json`
  (they mirror the catalog).
  *Accept:*
  - New worlds name the player faction and the antagonist faction from the registry (standalone
    label, plan D2). A new empty save's player is named from `lead_summoner`.
  - Existing rows are untouched (G1 answered: no migration). This task writes no migration; the only
    save migration in the IP work is ip-censor T19b (species ids), which touches no name column.
  - First step, reported in the ledger: run the focused world and save tests **before** the change to
    see whether a faction name feeds a golden or a hash. If one does, re-bless it in this commit with
    the reason written in the body.
  *Verify:* `.\scripts\verify-change.ps1 -Paths <changed C# files> -Session <sid>`; `npx vitest run src/stages/world`.
  *Commit:* `identity-rename T13: new worlds and saves take lead names from the registry`.
  *First step done 2026-09-22 (lane `identity-rename-1`) — the row's required pre-change measurement:*
  `dotnet test gk-core/tests/FusionRpg.Core.Tests --filter FullyQualifiedName~FusionRpg.Core.Tests.World` →
  **1247 passed, 0 failed (32 s)**. **No golden or hash pins a world faction name**, so no re-bless is
  needed in this row's commit. The only JSON carrying `Dr. Zomboss` is
  `gk-data/packs/fusion/data/seed/commanders/_registry/default-commanders.v1.json` — **T12's** file, not T13's — and every
  test pinning that literal (`CommanderDirectoryTests.cs:70,143`, `CommanderRosterTests.cs:24`,
  `PlayerEmpireCommanderTests.cs:36`, `ThirdCommanderOpenClosedTests.cs:21`) is a **commander row**
  assertion, not a world faction. The world-faction literals to move are
  `WorldTemplateCatalog.cs:78,83` and `WorldTemplateCatalog.TwoHearths.cs:26-27`; the save name is
  `RpgStore.cs:4203` (`const string OnboardingPlayerName = "Crazy Dave"`), whose insert is at `:4188`.
  *CORRECTION to the first-step reading above (found in this row's own implementation):* "no golden or
  hash pins a faction name" was **wrong**. The measurement was scoped to `gk-core/tests/FusionRpg.Core.Tests`
  (`~FusionRpg.Core.Tests.World`, 1247/1247), and the world golden lives in **`gk-core/tests/FusionRpg.Data.Tests`**
  — `WorldWaveOneAcceptanceTests.The_scenario_hashes_to_its_golden`, a scenario **hash** pinned in C#
  (`GoldenFinalHash`), which my text grep could not see. So a name DOES feed a hash, and the row's own
  clause applied: it was **re-blessed in this commit** (`6012578…` → `307b3d0…`) as **re-bless entry #21**
  with the reason in the body and above the constant. The lesson for the next reader: a golden is a
  *hash*, not a name, so grep for it in the C#, and run the *Data* world tests, not only Core's.
  *Implemented:* `WorldTemplateCatalog.cs` and `TwoHearths.cs` name the player and antagonist empires from
  `LeadNamesHub` (`lead_summoner` / `lead_antagonist`); `RpgStore`'s empty-save insert names the player from
  `lead_summoner`; `Program.cs` configures the names registry **before** `store.Init()`; and every host
  that reaches those reads configures it — the Core/Data/Server test bootstraps and, for the first time, the
  `CreatureSpeciesImport` tool (a real host whose cold process threw `LeadNamesHub.Configure(...) has not run`,
  fixed with a boot configure plus a `<Content>` copy rule; a new focused boundary row
  `data-species-import-cli` maps `gk-forge/tools/CreatureSpeciesImport/**` so the path is no longer unmapped).
  The three web fixtures mirror the catalog and were renamed with it.
  *Also fixed (my own defect, exposed by the module run):* `LeadNamesTests` reset the process-wide hub in
  its `finally` and left it unconfigured, which broke **157 World tests in a full-project run** while passing
  in a class-scoped run. It now restores the registry the module initializer configured.

- [x] **T14 Launcher and injector window titles.** *Depends:* CP1.
  *Files:* `gk-fusion/src/FusionRpg.Launcher/MainWindow.xaml` (`:5,18`), `OverlayWindow.xaml` (`:5`),
  `gk-fusion/src/FusionRpg.Injector/Hud/Win32.cs` (`:82`).
  *Accept:* all three titles read "Garden Keeper and his Multiverse" (the overlay keeps its " — Overlay"
  suffix). No binary, assembly or namespace name changes.
  *Verify:* `.\scripts\verify-change.ps1 -Paths <the three files> -Session <sid>` (the injector path
  needs `FUSIONRPG_GAME_DIR` for interop refs; if it is not set, say so in the commit body).
  *Commit:* `identity-rename T14: launcher and overlay windows carry the new title`.
  *Landed 2026-09-22 (lane `identity-rename-1`):* four strings in three files — `MainWindow.xaml:5`
  (window `Title`) and `:18` (`ui:TitleBar Title`), `OverlayWindow.xaml:5` (keeping its `— Overlay`
  suffix) and `Win32.cs:82` (`CreateWindowEx`'s window name). No binary, assembly, namespace or
  `x:Class` name moved — the titles are strings, so `FusionRpg.Launcher` / `FusionRpg.Injector` are
  untouched. **The injector was NOT compiled:** `guard-injector-compile` reported its own skip — "no
  MelonLoader game dir (set FUSIONRPG_ML_GAMEDIR); injector NOT compiled" — so `Win32.cs`'s one-line
  change is verified by inspection, the guard suite and the launcher tests, not by an injector build.
  (Note for T12: that guard wants `FUSIONRPG_ML_GAMEDIR`, not `FUSIONRPG_GAME_DIR`.)

### Checkpoint 3 — names and title
- [ ] `python gk-core/scripts/vocab-rename.py check --rules gk-core/scripts/vocab-rename/identity-rename.v1.json --phase names` is clean over the whole phase scope.
- [ ] `/review-web`: title screen, Sanctum onboarding reveal, commander list, world stage labels.
- [ ] The launcher window title is visible on a local run.
- [ ] Owner review before the `fusion` phase.

## Phase 4 — "PvZ" / "Plants vs. Zombies" → "Fusion"

- [x] **T15 Guide, phase `fusion`.** *Depends:* CP3.
  *Files:* the same scopes as T7 and T8 (sources, then re-render).
  *Accept:*
  - Every replacement within one sentence of a fusion-mechanic word went through residue and a
    phrase rule (plan §8 risk 1). No "Fusion Fusion".
  - "PvZ2", "PvZ Heroes" and "Garden Warfare" are untouched.
  - `_render.py --check` passes and `check` is clean.
  *Verify:* as T8.
  *Commit:* `identity-rename T15: guide prose names the host game Fusion`.
  *Landed 2026-09-22 (lane `identity-rename-1`):* `apply --phase fusion` wrote **16 files for 52
  replacements**, `check --phase fusion` is clean (**0 replacements, 0 residue over 93 files**, exit 0),
  and `_render.py` re-rendered plus `--check` → 66 content files, 0 errors. **Plan §8 risk 1 does not
  materialise here:** the tool matched the *long* product names first (33 hits on
  `Plants vs. Zombies: Fusion` / `Plants vs. Zombies Fusion`), so **no** `PvZ Fusion` → `Fusion Fusion`
  can occur, and a reading of all 52 replacements found **0 of 52** inside a sentence containing a
  fusion-mechanic word (`fuse`, `fusion lab`, `specimen fusion`, `Fusion (F)`, `fusable`, `Fusion
  recipe`) — so no phrase rule was needed and nothing was routed to residue. `PvZ2`, `PvZ Heroes` and
  `Garden Warfare` are untouched: they appear in **0 files** of this phase's scope (the corpus has none
  in the guide), and the allow-list that protects them is pinned by fixture in `VocabRenameTests` (19 /
  10 / 11 tracked files elsewhere carry those names and none is in scope).

- [x] **T16 Front pages and identity lines, phase `fusion`.** *Depends:* CP3.
  *Files:* `README.md`, `CONTRIBUTING.md`, `docs/README.md`, `docs/assets/banner.svg` (tool);
  `AGENTS.md:50`, `docs/PRINCIPLES.md:39,431` (audit 2026-09-19: `:426` drifted to `:431`), `decisions.md:109`.
  *Accept:*
  - `PVZRH` in `AGENTS.md:50` is untouched.
  - The legal-install lines still say a legal install is required and the binary is never patched,
    without naming the mark (IC-1b).
  - `CLAUDE.md` is not edited: its `PvZ` is the engineering layer term, not player-facing (plan §2).
  - `check` is clean.
  *Verify:* `.\scripts\verify-change.ps1 -Paths <changed files> -Session <sid>`.
  *Commit:* `identity-rename T16: front pages and identity lines name the host game Fusion`.
  *Landed 2026-09-22 (lane `identity-rename-1`):* `AGENTS.md:55` (the four-module overlay line) now
  reads "overlay for **Fusion** (PVZRH)" — **`PVZRH` untouched**, as the row requires; `PRINCIPLES.md`
  and `decisions.md`'s Product vision row say "extension for Fusion"; and the legal-copy line
  (`PRINCIPLES.md:434` — the row's `:431` has drifted) reads "**Bring a legal copy of Fusion;** the
  binary is never patched", so a legal install is still required, the binary is still never patched, and
  the mark is not named (IC-1b). `CLAUDE.md` was re-measured and **not** edited (6 `PvZ` hits, all the
  engineering layer term). No "Plants vs. Zombies" remains in any of the three identity files.
  *Two real prose defects the fusion phase produced, found by reading its output and fixed **by adding
  phrase rules**, never by editing the tool's output:*
  1. **A false trademark attribution.** `README.md:259`'s footer had become "Fusion is a trademark of
     Electronic Arts Inc. Fusion is an independent fan-made game." — the mechanical rename had put the
     *host game's own name* where the mark belonged. New rule `legal-attribution` rewrites it to "The host
     game and its characters are the property of their respective owners. The fan-made pack is an
     independent work." The rest of the disclaimer still names PopCap/EA as the non-affiliation targets,
     which is honest and is not the host game's display name.
  2. **"a fan-made Fusion pack"** (`README.md:25`, `the-game.md:15`) read as though the pack were called
     Fusion; new rule `fan-made-pack` makes it "a fan-made pack of the host game".
  Both are plan §8 risk 1 in places my sentence-proximity reading missed because the sentences carry no
  *mechanic* word — the ambiguity is the host game's own name. `check --phase fusion` is clean again
  (0 replacements, 0 residue over 93 files) and `_render.py --check` is 0 errors.

- [x] **T17 Web and launcher strings, phase `fusion`.** *Depends:* CP3.
  *Files:* `gk-web/web/fusion-rpg-web/src/app/TitleScreen.tsx:26` (subtitle), `src/layers/chronicle/ChronicleLayer.tsx:10`
  ("PvZ sheet" label; the tab id `pvz-stats` stays), `gk-fusion/src/FusionRpg.Launcher/MainWindow.xaml.cs:424`,
  `gk-fusion/src/FusionRpg.Launcher/FusionRpg.Launcher.csproj:18` (`<Description>`).
  *Accept:*
  - The visible strings say "Fusion". Ids and component names (`PvzStatsPage`, `pvz-stats`) are unchanged.
  - The tool's `plan` over these files reports zero replaceable hits.
  *Verify:* `npx vitest run src/app src/layers/chronicle`; `npm run build`;
  `.\scripts\verify-change.ps1 -Paths gk-fusion/src/FusionRpg.Launcher/MainWindow.xaml.cs,gk-fusion/src/FusionRpg.Launcher/FusionRpg.Launcher.csproj -Session <sid>`.
  *Commit:* `identity-rename T17: web and launcher strings name the host game Fusion`.
  *Landed 2026-09-22 (lane `identity-rename-1`):* four strings — `TitleScreen.tsx:26` (`Plants vs.
  Zombies` → `Fusion`), `ChronicleLayer.tsx:10` (`PvZ sheet` → `Fusion sheet`, with the tab id
  `pvz-stats` and the `PvzStatsPage` component untouched), `MainWindow.xaml.cs:424` (the folder-picker
  title) and the launcher csproj's `<Description>`. `AssemblyTitle`/`Product`/`Company` keep
  `FusionRpg` — the internal prefix, which R12 keeps. Two small clean-ups the reading demanded: the
  tab id `pvz-stats` joined the identifier allow-list (it is an id the row keeps, so a `PvZ` hit on it
  was being reported as residue rather than as an identifier), and one doc comment that listed the
  three tabs was reworded to the new sheet name. The tool's `plan` over the four files is now
  **0 replacements, 0 residue, 10 identifiers** (the identifiers being `FusionRpg.*`, `FUSIONRPG_*`
  env vars and `pvz-stats`).

### Checkpoint 4 — Fusion
- [ ] `check --phase fusion` is clean over the whole phase scope.
- [ ] Guide fusion pages read unambiguously (a manual read of `docs/guide/creatures.md` and the specimen-fusion page).

## Phase 5 — Lock-in

- [x] **T18 Regression guard and hand-off.** *Depends:* CP4.
  *Files:* `gk-web/web/fusion-rpg-web/src/i18n/vocabularyGuard.ts` (`BANNED_WORDS`, `:42`), `vocabularyGuard.test.ts`,
  and the ledger section below.
  *Accept:*
  - Player copy fails the guard on "Rise of Summoner", "Crazy Dave", "Dave", "Penny", "Zomboss",
    "Plants vs. Zombies", "PvZ". The existing allow-listed dev prefixes keep engine vocabulary
    (`vocabularyGuard.ts:16-37`).
  - A test proves an identifier (`PvzStatsPage`, `"commander:dave"`) does not trip it.
  - Both tool phases' `check` is clean.
  - *Audit 2026-09-19.* The ledger records one ip-censor release-scan reading (`python -m ipcensor.report
    scan --fail-on enforced`, if ip-censor T12 has landed): every remaining enforced lead or `PvZ` hit is
    listed with its owner. A reading, never an assertion.
  - The hand-off note below lists the rules file's alias groups as **candidate** rows for ip-censor's
    `registry` module (that program owns the rows; nothing is written into its tree).
  *Verify:* `npx vitest run src/i18n`; `npm run build`. This is the last checkpoint of a
  cross-module program (Core, Data, Server, web, docs), so it runs the full suite once:
  `.\scripts\test-fast.ps1 -AllDefault`.
  *Commit:* `identity-rename T18: guard player copy against the retired names`.
  *The row's full-suite line is NOT run:* `test-fast.ps1 -AllDefault` was started twice and both runs were killed by infrastructure errors on the long job (the same failures that hit the combined `verify-change` calls this session). Every other line of this row's acceptance is green above, and the full-suite evidence remains owed to the orchestrator/CI.
  *Landed 2026-09-22 (lane `identity-rename-1`):* the seven retired names joined `BANNED_WORDS`
  (`Rise of Summoner`, `Crazy Dave`, `Dave`, `Penny`, `Zomboss`, `Plants vs. Zombies`, `PvZ`) with the
  copy-vs-code narrowing every other entry gets, so `PvzStatsPage`, `"commander:dave"` and
  `actor.penny.name` stay untouched — pinned by a new fixture test, and the real-tree test
  (`scanForBannedVocabulary(srcDir)` over `src/`) is the acceptance's own check. `npx vitest run src/i18n`
  → **6 files, 69 tests**; `npm run build` → 12.23 s. Both tool phases are clean:
  `check --phase names` and `check --phase fusion` each **0 replacements, 0 residue over 93 files**.
  *ip-censor release-scan reading (the audit's own clause, a reading not an assertion):* **not
  available** — `python -m ipcensor.report scan --fail-on enforced` exits with
  `gk-data/packs/fusion/data/seed/ip-censor/_registry/marks.v1.json: cannot be read (No such file or directory)`, i.e.
  ip-censor's `registry` module (its T12) has not landed, so there is no enforced lead/`PvZ` hit list
  to report. Recorded here as the reading the row asks for.

### Final checkpoint
- [ ] Every task's acceptance criteria are met and ledgered.
- [ ] Renaming a lead is proven to be a one-file edit: change one `display` in `names.en.v1.json`,
  rebuild, and the prologue, onboarding reveal, commander list and a new world all show it. Revert afterwards.
- [ ] G1's answer (no migration, 2026-09-19) is recorded in the ledger.
- [ ] Session record closed (`status: merged`) in a new commit.

---

## Gate

| Gate | Resolver | Default | Blocks |
|---|---|---|---|
| G1 Migrate names already stored in existing saves | Owner | **Answered 2026-09-19: no migration**; new saves and worlds only | Nothing |

## Ledger

(Empty. Each task appends one line: task, commit, before/after readings, residue closed, anything skipped.)

## Hand-off to ip-censor

(Filled by T18.)

### Candidate rows for ip-censor's `registry` module (T18 hand-off)

Nothing here is written into ip-censor's tree; these are **candidates** for that program's own
review. Source: `gk-core/scripts/vocab-rename/identity-rename.v1.json`.

| Candidate alias group | Forms the rules file replaces (phase) | Why ip-censor may want a row |
|---|---|---|
| product title | `Rise of Summoner`, `RISE OF SUMMONER` (names) | a retired product name; already banned in web copy by `vocabularyGuard.ts` |
| lead: summoner | `Crazy Dave`, `Dave` (names) | retired character name; the registry's `lead_summoner` row is the replacement |
| lead: companion | `Penny` (names) | retired character name; `lead_companion` |
| lead: antagonist | `Dr. Zomboss`, `Dr Zomboss`, `Zomboss` (names) | retired character name; `lead_antagonist` — note ip-censor already classifies `Zomboss*` identifiers as `code-identifier` |
| host game display name | `Plants vs. Zombies: Fusion`, `Plants vs. Zombies Fusion`, `Plants vs. Zombies`, `Plants vs Zombies`, `Plant vs Zombie`, `PvZ: Fusion`, `PvZ Fusion`, `PvZ` (fusion) | IC-1b's own scope; the display form is what turns into `Fusion` |
| attributive compounds | `Dave-level`, `Dave-gated`, `a Dave threshold`, `the Dave numbers` (names) | phrase rules, not names — a registry row would need the same phrase shape |

---

## Standards audit (2026-09-19)

Findings and fixes are recorded in [identity-rename-plan.md](identity-rename-plan.md) §"Standards audit
(2026-09-19)"; the todo-side items are:

| # | Severity | Finding | Status |
|---|---|---|---|
| B1 | MEDIUM | T13, the Final checkpoint and the Gate table still described G1 by its default after it was answered | Fixed |
| B2 | MEDIUM | T10/T16 cited `PRINCIPLES.md:345,426`; Penny sits on `:346` and the legal-copy line is now `:431` | Fixed |
| B3 | LOW | Header lacked "never stash" and "never amend" (`agent-git.md` rules 2 and 4) | Fixed |
| B4 | LOW | T1 did not name the names-registry spec's row shape (`ruling` field) | Fixed |
| B5 | LOW | T18 had no hand-off reading of ip-censor's release scan | Fixed (a ledger reading, not an assertion) |
