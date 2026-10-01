# Spec: narrative-text

Status: **DRAFT for owner review, 2026-09-19. Spec phase; no build authorized.** Every `file:line` below was
opened in this session.

Module `narrative-text`, row 11 of the [npc-story-events map](../npc-story-events-map.md) (`:217`), wave 1 (Owner ruling 2026-09-19 (round 4): moved from wave 2 so `delve-live-rooms` shows keyed text in wave 1). Depends on
`narrative-vocabulary`. Reads narrative-seed's `token-grammar` and `names-registry` (`narrative-seed-map.md:207-208`)
and the keyed text of storylets, characters and spine chapters. Consumed by `scene-script-loader`,
`storylet-card`, `quest-log-layer` and every server read model that carries story text. Draft decision row **NS5**
(`npc-story-events-map.md:403`). Session record: `tasks/sessions/narrative-programs-spec2-20260919.json`.

## Objective

Render structured story text: entity tokens resolved from the **names registry** and the cast, ICU `select` on the
registry's closed feature tags, the closed semantic markup rendered by the presentation layer, and the **lingui
codegen bridge** that turns every keyed seed string into a literal `msg({ id, message })` descriptor — committed,
drift-checked, and loaded in its own chunk. There is one translation system (lingui) and one names registry.

Success looks like: a fixture storylet renders against two different names registries and the outputs differ
exactly at the tokens; no display name ever travels from the server; `npm run extract` and the generator's
`--check` are clean in CI; the narrative catalog is not in the entry chunk.

## Locked anchors

- **Names are tokens** (R8–R11; map principle 16, `:124-126`; `narrative-seed-ideal.md` §6.5b, `:412-482`): literal
  text, entity tokens, closed semantic markup; a rename is one registry edit.
- **Lingui needs compile-time literals**: *"`msg({ message: someRuntimeString })` is a hard error"*
  (`gk-web/web/fusion-rpg-web/src/features/story-scene/messages.ts:13-19`). The runtime path that does work is a descriptor
  id with values: `i18n._(RIFT_PROLOGUE_PROGRESS.id, { position, total })`
  (`gk-web/web/fusion-rpg-web/src/ui/story-scene/StorySceneHost.tsx:98-101`).
- **The bridge is codegen** (`narrative-seed-ideal.md` §6.8, `:546-554`): seed keys become lingui ids; the generated
  module is committed and drift-checked; the catalog loads in its own chunk.
- **All player text goes through lingui** (story-scene decision S4, `docs/architecture/story-scene-map.md:306`).
- **Buy before build**: lingui already renders ICU placeholders and `select`; no new library
  (`narrative-seed-ideal.md:481-482`).
- **Generated-file precedent**: `gk-web/web/fusion-rpg-web/scripts/gen-tokens.mjs` generates a committed file and its
  `--check` mode, run by the test suite, fails on drift (`gen-tokens.mjs:1-9`). CI already fails when the extracted
  catalog is stale (`.github/workflows/ci.yml:434-444`).

## Design

### 1. The grammar (read; owned by `token-grammar`)

| Part | Members | Resolved from |
|---|---|---|
| lead tokens | `{lead_summoner}`, `{lead_companion}`, `{lead_antagonist}` | names registry rows (R11: the Garden Keeper, Hourbloom, the Rotwright) |
| character tokens | `{c_<slug>}`, `{c_<slug>_epithet}` — `<slug>` is `slug_for(characterId)`, the id body with `.`/`-` → `_` (`narrative-seed/spec-token-grammar.md` §3; Audit 2026-09-19: was `c_<characterId>`, which ICU cannot parse) | the character seed's keyed `name` / `epithet` (`narrative-seed-ideal.md:358`) |
| forms and pronouns | `_start`, `_bare`; `_subj`, `_obj`, `_poss` on a lead or character token (`spec-token-grammar.md` §3) | expanded to ICU `select` by `expand` at generation; the runtime supplies the arguments below |
| role tokens | `{role_<roleId>}` | the storylet's cast (`spec-cast-resolver.md` §6), then as a lead or character token |
| bound placeholders | `{place}`, `{supply}`, `{reward}`, `{cost}` | the cast's `EntityRef`s; `{reward}`/`{cost}` from `choice-resolution` |
| semantic markup | `<em>`, `<whisper>`, `<shout>`, `<pause/>` at first ship | the renderer's component table |
| feature tags | `gender`, `number`, `article` (closed enums) | the registry row or the character seed |

Feature values reach a message as extra ICU values. Audit 2026-09-19: `token-grammar` §5 now fixes the spelling —
for every lead or character token `T` the runtime supplies exactly `T`, `T_article`, `T_gender`, `T_number` (its test
`expanded_arguments_are_closed`); the renderer builds those four from the names-registry row or the character seed's
`grammar`, and the registry's `display` never carries an article (`spec-names-registry.md` §1).

### 2. What the server sends — references, never names

Server read models carry a `NarrativeTextDto`:

```csharp
namespace FusionRpg.Contracts;

public sealed class NarrativeTextDto
{
    [JsonPropertyName("key")]    public string Key { get; set; } = "";                 // the seed text key = lingui id
    [JsonPropertyName("tokens")] public Dictionary<string, TokenRefDto> Tokens { get; set; } = new();
}

public sealed class TokenRefDto
{
    [JsonPropertyName("kind")]   public string Kind { get; set; } = "";    // lead | character | character-epithet | sector-slot | delve-domain | homeworld | supply | magnitude
    [JsonPropertyName("id")]     public string Id { get; set; } = "";
    [JsonPropertyName("amount")] public long? Amount { get; set; }        // magnitude only: a resolved P(Θ) amount
    [JsonPropertyName("unit")]   public string? Unit { get; set; }        // magnitude only: the stock id (souls, essence, ...)
}
```

`StoryTextBinder.Bind(TextRef text, StoryletCast cast)` (new, Core) produces the token map for one text field: every
token the text uses is bound, or binding fails naming it. `role_<id>` is replaced by what the role was cast to; a
magnitude keeps its number (`long`, because `P(Θ)` magnitudes outgrow `int` at reachable Θ, CLAUDE.md range table).
**No display string crosses the wire**, so the server cannot leak a name and a rename never needs a server change.

### 3. Load-time validation (C#)

`TokenGrammar.Validate(TextRef, declaredRoles, knownCharacterIds)` (new, Core) runs from the storylet, character and
spine loaders:
- every `{...}` is a closed-grammar token; no stray or unbalanced brace;
- every `role_<id>` is declared in the storylet's `roles[]` (`storylet.role-undeclared`, `spec-storylet-contract.md` §5);
- every `c_<slug>` maps back, through `slug_for`, to a character in the corpus (Audit 2026-09-19);
- every markup tag is in the closed set and balanced;
- no ASCII digit (`storylet.digit-in-text`).
The names-registry literal-name check and the round-trip render are narrative-seed's validators
(`narrative-seed-map.md:211`); the runtime repeats token closure only, because an unresolvable token is a runtime
failure while a literal name is a content-quality defect caught at generation.

### 4. The codegen bridge

`web/fusion-rpg-web/scripts/gen-narrative-messages.mjs` (new):

1. reads every keyed text field under `gk-data/packs/fusion/data/seed/narrative/` (storylets, characters, spine chapters, arcs) **and**
   the keyed `name`/`flavor` of the repaired legacy Delve events under `gk-data/packs/fusion/data/seed/dungeon/events/` — Owner ruling
   2026-09-19 (round 4): narrative-seed's wave-0 `dungeon-generator-repair` regenerates the contaminated legacy events
   clean and gives their name and flavor text keys (`docs/architecture/item/seed-contract.md` §6: key and string
   authored together), so the live Delve shows clean, keyed legacy text from day one through this bridge; wave 6's
   `delve-event-regen` later replaces them with storylets. A legacy row without a key is a generation refusal naming
   the file, never an unkeyed string on screen;
2. emits `web/fusion-rpg-web/src/features/narrative/generated/narrativeMessages.generated.ts` (new): one literal
   `msg({ id: "<key>", message: "<text>" })` per key, sorted by key, with a do-not-edit header naming the script;
3. refuses two seeds emitting one key with different text (a changed string is a new key, `narrative-seed-ideal.md:387-388`);
4. `--check` regenerates in memory and fails if the committed file differs.

The generated module is a normal lingui source file, so `npm run extract` picks up every descriptor. Lingui gets a
**second catalog** for it in `gk-web/web/fusion-rpg-web/lingui.config.ts` (today one catalog, `src/i18n/locales/{locale}/messages`
over `src`): `src/i18n/locales/{locale}/narrative`, including only `src/features/narrative/generated`, and the main
catalog excludes that folder. The narrative module and catalog are loaded with a dynamic `import()` the first time a
narrative surface mounts, so they never enter the entry chunk; `npm run check:bundle` proves it. A large catalog is a
splitting problem, never a reason to drop lingui (CLAUDE.md buy-before-build).

CI needs no new step: the existing extract step fails when `src/i18n/locales` drifts (`ci.yml:434-444`), and the
generator's `--check` runs inside `npm test` (the `gen-tokens` precedent).

### 5. Rendering (web)

```ts
// web/fusion-rpg-web/src/features/narrative/renderNarrative.tsx (new)
export function useNarrativeText(text: NarrativeTextDto): React.ReactNode;
```

1. Resolve each `TokenRefDto` to a display string and its feature values:
   - `lead` → `names.<locale>.v1.json` row (imported as JSON, the precedent `sceneScript.ts:1` sets for tuning data);
   - `character` / `character-epithet` → the character's own name key rendered through lingui;
   - `sector-slot`, `delve-domain`, `homeworld`, `supply` → that entity's existing display path (a resolver table keyed
     by `kind`; an unknown kind throws, never renders a raw id);
   - `magnitude` → lingui's ICU number formatting plus the stock's display name.
2. Call lingui with the text's key and the value map (`i18n._(key, values)` — the id-plus-values form the host already
   uses, `StorySceneHost.tsx:98-101`), rendering markup through lingui's rich-text components with a component per
   closed tag. The build task starts with a probe, as `messages.ts:13-19` did for literals, confirming that named tags
   compile through the extractor; if lingui accepts only numbered tags, the generator maps each closed tag name to a
   fixed index from the same table the renderer reads.
3. Markup names meaning; the presentation layer owns style (`narrative-seed-ideal.md:425`).

A missing key throws in development and renders lingui's own fallback id in production — never a raw seed string.

### 6. Caches

Two static caches, loaded once per page: the names registry (a JSON import, fixed at build) and the narrative lingui
catalog (loaded on first narrative surface). Their full trigger set (DESIGN-GATE §2.16): a build (new registry, new
catalog), and a **locale change**, which must reload the narrative catalog for the new locale and re-resolve lead
names from the new registry file — the locale switch is the key-set edge, and it gets its own test. No runtime event
mutates either.

## Data shapes

- Wire: `NarrativeTextDto`, `TokenRefDto` (`gk-core/src/FusionRpg.Contracts/NarrativeTextDtos.cs`, new).
- Seed/registry: read only (`names.en.v1.json`, token grammar, keyed text).
- Web: the generated module and the second lingui catalog.

## Numeric types

`TokenRefDto.Amount` is `long?`: a reward or cost is a `P(Θ)` magnitude, and integer magnitudes are `long` (CLAUDE.md
numeric rules). The web formats it with `Intl`/ICU; a value beyond `Number.MAX_SAFE_INTEGER` is serialized as a string
by the contract (the build task confirms the serializer setting and tests the boundary).

## SOLID notes

- **S:** one translation system (lingui); one names registry; one binder for every text field.
- **O:** a new token kind is a grammar row plus one resolver arm.
- **D:** server read models depend on `StoryTextBinder`; the web depends on `useNarrativeText`; neither knows names.
- No second i18n path and no second name filter (IP clearance is `ip-censor`'s release gate, IC-3).

## Commands

```powershell
.\scripts\verify-change.ps1 -Paths @('gk-core/src/FusionRpg.Core/Narrative/Text/TokenGrammar.cs','gk-core/src/FusionRpg.Core/Narrative/Text/StoryTextBinder.cs','gk-core/tests/FusionRpg.Core.Tests/Narrative/Text/NarrativeTextTests.cs') -Session <session-id>
cd gk-web/web/fusion-rpg-web
node scripts/gen-narrative-messages.mjs --check
npx vitest run src/features/narrative
npm run extract ; npm run build ; npm run check:bundle
```

`web/**` has no entry in `gk-core/scripts/verification-boundaries.v1.json` (`verify-change.py` throws for it,
`gk-core/scripts/verify-change.py:771`); web verification is the npm commands above until a web boundary exists.

## Structure

```
gk-core/src/FusionRpg.Core/Narrative/Text/TokenGrammar.cs              (new)
gk-core/src/FusionRpg.Core/Narrative/Text/StoryTextBinder.cs           (new)
gk-core/src/FusionRpg.Contracts/NarrativeTextDtos.cs                   (new)
web/fusion-rpg-web/scripts/gen-narrative-messages.mjs          (new)
web/fusion-rpg-web/src/features/narrative/generated/narrativeMessages.generated.ts   (new, generated)
web/fusion-rpg-web/src/features/narrative/namesRegistry.ts      (new)
web/fusion-rpg-web/src/features/narrative/renderNarrative.tsx   (new)
web/fusion-rpg-web/src/features/narrative/narrativeText.test.ts (new)
gk-web/web/fusion-rpg-web/lingui.config.ts                              (edited: second catalog)
gk-web/web/fusion-rpg-web/src/i18n/locales/{en,pseudo}/narrative.*     (new, extracted)
gk-core/tests/FusionRpg.Core.Tests/Narrative/Text/NarrativeTextTests.cs  (new)
```

## Testing strategy

- **Two name sets (web):** each fixture message renders with the real `names.en.v1.json` and with a test registry of
  different names; the two outputs differ exactly at token positions (a diff over rendered strings).
- **No literal names (web):** no display string of the test registry appears in any rendered output that does not
  use its token.
- **Select on features:** a fixture message using `article` renders "The Rotwright" sentence-initially and
  "the Rotwright" mid-sentence from the registry's tags, not string surgery.
- **Binder (C#):** every token in a fixture storylet is bound from a fixture cast; an unbound token fails naming it;
  `role_<id>` resolves through the cast; magnitudes carry `long`.
- **Grammar (C#):** unknown token, stray brace, undeclared role, unknown character, unbalanced markup and a digit
  each reject with their rule id.
- **Codegen:** `--check` passes on the committed file and fails after a fixture seed's text changes; two seeds with one
  key and different text fail generation; output is sorted and stable across runs.
- **Chunking:** `npm run check:bundle` passes with the narrative module present; the entry chunk contains no key from
  the generated module.
- **Locale switch (cache trigger):** switching `en` → `pseudo` reloads the narrative catalog and re-resolves lead
  names; a test asserts the rendered text changes on the switch without a page reload.
- **No population:** no test counts keys or messages in the committed corpus.

## Success criteria

1. Story text reaches the player only through lingui, with tokens resolved on the web. 2. The server sends
references, never names. 3. The generated module and catalogs are committed and drift-checked. 4. The narrative
catalog is its own chunk. 5. Renaming a lead is one registry edit with no code change (proven by the two-name-set test).

## Boundaries

- **Always:** keys as lingui ids; references on the wire; markup as meaning.
- **Ask first:** a new markup tag or feature enum (a `token-grammar` change); a second locale's registry file.
- **Never:** `msg()` with a runtime string; a display name in a seed, DTO or C# literal; HTML or styling in markup; a
  second translation path; an in-loop IP filter.

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| `NarrativeTextDto`, `TokenRefDto`, `StoryTextBinder.Bind` | every server read model with story text (`quest-log-contract`, hosts' DTOs) |
| `TokenGrammar.Validate` | storylet, character and spine loaders |
| `useNarrativeText`, the generated descriptors, the narrative catalog loader | `scene-script-loader`, `storylet-card`, `quest-log-layer` |

## Contradictions found (report; not fixed here)

1. **Token spelling inside narrative-seed.** `narrative-seed-ideal.md:390` lists placeholders `{role.<id>}` and
   `{sector}`; its own §6.5b (`:424`) and this map (`:217`) use `{role_<roleId>}` and `{place}`. This spec follows
   §6.5b; `token-grammar` should retire the §6.5 spelling. Reconciled 2026-09-19: the ideal's §6.5 now uses the
   token-grammar spelling.
2. **Feature tags on characters.** §6.5 requires *"everything that fills a slot"* to carry feature tags
   (`narrative-seed-ideal.md:396-398`), but the character contract's field table (`:352-360`) has none. A character
   token cannot select on gender without them; filed on `narrative-contract`/`character-vocab`. Reconciled 2026-09-19:
   `narrative-seed/spec-narrative-contract.md` §6 carries a VALIDATED `grammar` field
   (`{gender, number, article, epithetArticle}`, closed enums from `spec-names-registry.md` §1), and the ideal's
   character table now lists it.

## Open questions

None for the owner. (The ideal §9 left the localization mechanism to spec; `narrative-seed-ideal.md` §6.8 chose
codegen, and this spec implements that choice.)

## Design-gate checklist

```
[x] Subsystems: i18n/lingui, story-scene (consumer), narrative seeds (text), web bundle, contracts DTOs.
[x] Session boundary recorded (narrative-programs-spec2-20260919).
[x] Read this session: narrative-seed §6.5, §6.5b, §6.8; story-scene-map S3/S4; messages.ts; StorySceneHost.tsx;
    lingui.config.ts; package.json scripts; gen-tokens.mjs; ci.yml i18n step.
[x] Every claim cites file:line.
[x] Buy before build: lingui only; splitting, not deletion, for size.
[x] Caches: two static caches with the full trigger set incl. the locale-switch key-set edge, each tested.
[x] No population pinned. No actor number. Magnitudes typed long on the wire.
[x] No parallel path: one translation system, one registry.
[ ] Registry row: none proposed; the drift checks are CI/test steps. (Audit 2026-09-19: rows proposed below.)
```

## Standards audit (2026-09-19)

| # | Severity | Finding | Status |
|---|---|---|---|
| 1 | high | Round-4 owner ruling: players never see a blank Delve event. The bridge read only `gk-data/packs/fusion/data/seed/narrative/`, so the repaired, keyed legacy events `delve-live-rooms` now shows had no path into lingui | **Fixed:** the bridge also reads the repaired legacy events' keys; an unkeyed legacy row refuses generation |
| 2 | medium | Character tokens were written `{c_<characterId>}`; the grammar is `{c_<slug>}` via `slug_for`, because ICU argument names cannot contain `.` or `-` (`spec-token-grammar.md` §3) | **Fixed** |
| 3 | medium | "This spec does not choose that spelling" for feature arguments — token-grammar §5 has since fixed them (`T_article`, `T_gender`, `T_number`); forms and pronouns were not listed | **Fixed** |
| 4 | medium | Two wire text shapes exist in the program: `NarrativeTextDto` here and `TextRefDto(Key, Tokens: string→string)` in `spec-quest-log-contract.md` §2 and `spec-expedition-lead-host.md` — a parallel text path (SOLID S), and the string map cannot carry a `magnitude` amount | **Closed — Alignment 2026-09-20:** both specs now use `NarrativeTextDto`; `TextRefDto` is withdrawn. `delve-live-rooms` already did |
| 5 | low | Map citations one line early (`:216`, `:402`) | **Fixed** |

Checked and clean: one translation system (lingui), buy-before-build (no new library), the catalog in its own chunk
(split, never drop), `long` magnitudes on the wire, static caches with the locale-switch key-set edge tested,
no population pin, no display string on the wire.

**Proposed enforcement-registry rows:** `ns5-names-are-tokens` — no names-registry display string literal in any
seed text field, C# or TS source outside the registry; guard: the two-name-set render test plus narrative-seed's
`narrative-validators` literal-name rule. `ns-one-narrative-text-dto` — one wire shape for story text; guard: a
Contracts reflection test that no DTO other than `NarrativeTextDto` carries a `key` + token map. **Verification-boundary
ask:** a web boundary for `web/fusion-rpg-web/src/features/narrative/**` and `scripts/gen-narrative-messages.mjs`
(today `verify-change.py` throws for `web/**`).
