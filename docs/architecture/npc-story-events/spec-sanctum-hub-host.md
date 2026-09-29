# Spec: sanctum-hub-host

Status: **DRAFT for owner review, 2026-09-19. Spec phase; no build authorized.** Every `file:line` below was
opened in this session.

Module `sanctum-hub-host`, row 21 of the [npc-story-events map](../npc-story-events-map.md) (`:226`), wave 4. Depends
on `scene-script-loader` (data-driven scenes played by `StorySceneHost`), `character-registry` (who is at home) and
`storylet-selection` (which conversation). Gate **G4** hub clause (`npc-story-events-map.md:299`: *"A hub conversation
plays once per character per return"*). Session record: `tasks/sessions/narrative-programs-spec2-20260919.json`.

## Objective

The homeworld is where story plays between outings. After an outing, on entering the Sanctum, **Hourbloom, the
companions and any visitors** each have at most **one conversation per return**, reacting to how the outing went (a
wipe, a win, a lost sector), played through `StorySceneHost`. This module also holds the onboarding slot **"first
character met"**, which it asks of the first-session spec rather than editing it.

Success looks like: with the game closed, a fixture save that closes a delve as wiped and then enters the Sanctum gets
one conversation from Hourbloom that reads the wipe; entering again without another outing gets none; two companions
present each get at most one; no conversation starts while a lawn match is running or a layer is open.

## Locked anchors

- **Homeworld** (ideal §6.6 Homeworld row, `npc-story-events-ideal.md`): *"Hub conversations with Hourbloom,
  companions and visitors … one conversation per character per return, and characters react to how the outing went"*;
  Hades' return to the House (ideal §4.1, `:226`).
- **The pacing bound is structural**: `SelectionBounds.ConversationsPerCharacterPerReturn = 1`
  (`spec-narrative-vocabulary.md` §4, *"the Hades rule the hub host is built on"*).
- **Scenes play through `StorySceneHost` only** (map principle 15, `:121-123`); the Sanctum already triggers the Rift
  prologue through the `scene-trigger` seam: `isSceneEligible(RIFT_PROLOGUE_TRIGGER, stories, { noLayerOpen })`
  (`gk-web/web/fusion-rpg-web/src/stages/sanctum/SanctumStage.tsx:86-98`), which requires a server row marked eligible and no
  open layer, and can only narrow (`gk-web/web/fusion-rpg-web/src/features/story-scene/sceneTrigger.ts:50-74`).
- **The frozen Rift contract** (`rift-prologue` / version `1`) is untouched (`spec-story-ledger.md` §1).
- **Lawn never mid-match** (ideal §6.6 Lawn row, `:457`; map principle 1, `:74-77`).
- **Onboarding checkpoints** are the one shipped ordered milestone gate (`gk-core/src/FusionRpg.Core/Onboarding/OnboardingCheckpointEvaluator.cs:6-13`);
  the first-session sequence belongs to `docs/architecture/standalone/spec-first-session-progression.md` (map `:190`,
  `:326`) — asked, not edited.
- **Homeworld Θ is danger 0** (`spec-host-content-theta.md` §3); **the homeworld pays no resources directly**
  (`spec-outcome-routing.md` §3). Owner ruling 2026-09-20: a save quest a conversation offers is paid on completion by
  **taking** one `expedition-tier` roll of the save's next collect (`spec-quest-sources.md` §6) — out of what an
  expedition already pays, never an added roll; the homeworld itself has no budget line.

## Design

### 1. What a "return" is

A **return** is the first entry into the Sanctum after at least one **outing fact** newer than the previous return.
Outing facts are durable records other programs already commit:

| Outing | Durable record |
|---|---|
| a world turn ended | a `rpg_world_turn_log` row for the player's **active** world (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:41-50`); a world-continuity coarse catch-up of a dormant world is not an outing (Audit 2026-09-19: the player did not play it) |
| a delve closed | the delve's final state (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Delve.cs:81`, `CloseDelve` `:762`) |
| an expedition collected | the expedition's `Collected`/`Recalled` state (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs:743-755`) |
| a web battle or lawn run finished | the match log (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs:726`) |

`SanctumReturns.Record(playerId)` (Server, new), called by the Sanctum's entry route (§4), checks for an outing record
newer than the last `sanctum.returned` fact and, if one exists, appends `sanctum.returned` (save scope, source
`return:{playerId}:{newestOutingRef}`, attrs `{outings: [...refs]}`). The **`sanctum.return` host clock** is the count
of `sanctum.returned` facts. A lawn match in progress is not an outing until its record is written, so a conversation
can never start mid-match: the pulse is Sanctum entry, and the Sanctum is not the lawn.

`sanctum.returned` is a new `StoryFactKind` member (a reviewed addition; `spec-narrative-vocabulary.md` §3 lists the
fact kinds and names which modules may add them — filed there).

### 2. Who is home

At a return, the **present** characters are:

1. `lead_companion` (Hourbloom) — always (`spec-character-registry.md` §1, lead rows);
2. save-scoped `companion` characters with fate `Present` (`spec-cast-resolver.md` §2);
3. **visitors** — non-enemy characters with a `met` fact whose fate is `Present` and for whom an eligible `sanctum.hub`
   storylet casts (Alignment 2026-09-20: a character seed has no `hosts` field — `narrative-seed/spec-narrative-contract.md`
   §6 — so "hosts include `sanctum.hub`" is read off the storylets, not the character), capped per return by the
   structural bound `SelectionBounds.VisitorsPerReturn = 1` (added with this module; a hub that fills with every
   character met stops being a conversation).

Enemy-role characters are never present: the antagonist's voice reaches the hub only as a faction-level scene
(`counter-doctrine`, `spine-progress`), never as a personal conversation (R13 rule 3).

### 3. Selecting conversations

For each present character, in the order above, take **at most one** conversation, the first of these that exists
(Alignment 2026-09-20: the seed shapes are narrative-seed's — `spec-storylet-vocab.md` §3.1 and
`spec-character-vocab.md` §5–§6; no hub-only seed kind exists or is needed):

1. **A due spine scene** (Hourbloom only): `scene.due.*` flag (`spec-outcome-routing.md` §5), the spine tier.
2. **A `sanctum.hub` storylet** — an ordinary storylet whose `hosts` include `sanctum.hub`, asked of
   `storylet-selection` with the character bound into its required role `speaker` (`cast-resolver`); priority tier
   (consequences, first-seen teaching storylets, `spec-storylet-selection.md` §4), then the pool.
3. **The character's homecoming line** — an `ally` character (Hourbloom, companions) says its `lines[]` entry for
   the return's **outing context** and its current band, played as a one-line scene; a visitor's fallback is its
   `greet` line for its band. The outing context is classified from this return's outing facts, most serious first:
   `return-wiped` (`delve.wiped`, `siege.failed`), `return-lost` (`sector.lost`), `return-won` (a delve closed
   `Extracted`, a `chapter.reached` or a world won, a quest completed), else `return-quiet`. A band with no `return-*`
   pair (`wary`, `hostile`) falls back to `greet`.

This is how a conversation **reacts to the outing** without any storylet predicate over outing facts: the reaction
is data on the character seed, chosen by a closed rule here. The earlier "`this-return` facts exposed to predicates"
had no seed condition that could name them and is withdrawn (Alignment 2026-09-20).

- **Fire chance**: `firing.sanctum.hub = 1000/0` — a character at home always has something to say: a storylet if
  one is eligible, else its line.
- **Cooldowns** on the `sanctum.return` clock (`cooldown.perStorylet/perKind.sanctum.return`).

The result is an ordered **conversation queue** of at most `1 + companions + visitors` entries.

### 4. Delivery — through the scene trigger, never around it

```text
POST /api/narrative/{playerId}/sanctum/enter      -> records a return if due; returns the conversation queue
POST /api/narrative/{playerId}/sanctum/conversations/{offerRef}/answer   -> ChoiceAnswerService (storylet choices)
```

Each queue entry is either:

- a **scene** (a data-driven scene script, `scene-script-loader`) — a spine scene, or a **line scene** built from a
  character's homecoming or `greet` line (`spec-scene-script-loader.md` §2, Alignment 2026-09-20): exposed through the
  same ledger shape `isSceneEligible` reads — a `StoryLedgerEntry` with `eligible: true` for that scene id and revision —
  so the FE's existing trigger seam decides *when* it opens (no layer open; the Rift prologue first when it is due); or
- a **storylet with choices** (talk verbs: `interact`, `persuade`, `threaten`, `leave`): shown on the storylet card
  (`storylet-card`, FE wave 6), answered through the answer route.

The SanctumStage change is one call: on mount, `POST …/sanctum/enter` and pass its scene rows into the same
`isSceneEligible` evaluation it already runs for the Rift prologue (`SanctumStage.tsx:86-98`), one scene at a time, the
Rift prologue first. The FE never decides eligibility (`sceneTrigger.ts:54-56`: *"`when` can only narrow"*).
Skipping a scene (`StorySceneHost`'s unconditional skip) acknowledges it — a `scene.acknowledged` fact
(`spec-story-ledger.md` §1) — so a skipped conversation is spent for this return, never nagged again.

**Idempotent entry.** `…/sanctum/enter` twice for one return returns the same queue (the return fact dedupes; the
queue is derived from the return's `seq`), minus conversations already acknowledged or answered.

### 5. The onboarding slot

The first-session spec owns the reveal sequence. This module **asks it for one slot**, "first character met", and
provides the fact that fills it: the save's first `met` fact about any non-lead character. The ask, filed on
`spec-first-session-progression.md`: *"after checkpoint X, the next return queues Hourbloom's introduction of the first
character met"*. Until that spec answers, the hub runs with no onboarding special case (the first `met` simply makes
that character a visitor), which is correct behaviour, not a gap in this module.

### 6. Budget

`SanctumHostBudget : IHostBudget` — no loot source, souls 0, spendable stocks none (`spec-outcome-routing.md` §3).
Conversations grant access — relations, flags, quests, a join — never resources. `offer:{stock}` on `sanctum.hub` is a
preflight refusal (`sanctum.no-spend`, added with this module).

## Data shapes

- New fact kind `sanctum.returned` (filed on `narrative-vocabulary`).
- Structural consts added to `SelectionBounds`: `VisitorsPerReturn = 1` (with its reason comment).
- Routes above; the scene rows reuse the onboarding story-entry shape the FE already reads
  (`OnboardingStoryDto` projection, `gk-core/src/FusionRpg.Server/OnboardingEndpoints.cs:34-45`).

## Numeric types

| Quantity | Type | Why |
|---|---|---|
| `sanctum.return` clock | `long` | a count of returns over a save's life |
| queue length | `int` | bounded by the structural consts |

## SOLID notes

- **S:** the host decides when (a return) and who is present; selection decides which conversation; story-scene plays it.
- **O:** new conversations are seed data on `sanctum.hub`; new outing kinds are one reader row.
- **L:** the Rift prologue path is unchanged; hub scenes enter the same seam as one more eligible row.
- **D:** the FE depends on the scene-trigger seam and the entry route, never on narrative internals.
- One scene player, one trigger seam, one storylet engine.

## Commands

```powershell
.\scripts\verify-change.ps1 -Paths @('src/FusionRpg.Server/Narrative/SanctumReturns.cs','src/FusionRpg.Server/Narrative/SanctumHub.cs','gk-web/web/fusion-rpg-web/src/stages/sanctum/SanctumStage.tsx','tests/FusionRpg.Server.Tests/Narrative/SanctumHubTests.cs') -Session <session-id>
dotnet test tests\FusionRpg.Server.Tests --filter "FullyQualifiedName~SanctumHub|FullyQualifiedName~Onboarding"
cd gk-web/web/fusion-rpg-web; npm test -- sceneTrigger SanctumStage
```

## Structure

```
src/FusionRpg.Server/Narrative/SanctumReturns.cs        (new: return detection, sanctum.returned)
src/FusionRpg.Server/Narrative/SanctumHub.cs            (new: presence, per-character selection, queue)
src/FusionRpg.Server/Narrative/NarrativeEndpoints.cs    (edited: sanctum/enter, conversation answer)
src/FusionRpg.Core/Narrative/Hosts/SanctumHostBudget.cs (new)
gk-core/src/FusionRpg.Core/Narrative/Vocabulary/SelectionBounds.cs (edited: VisitorsPerReturn)
gk-web/web/fusion-rpg-web/src/stages/sanctum/SanctumStage.tsx  (edited: call enter, feed scene rows to isSceneEligible)
tests/FusionRpg.Server.Tests/Narrative/SanctumHubTests.cs   (new; in-memory store)
```

## Testing strategy

Game closed; in-memory store; fixture corpus and scenes.

- **Once per character per return:** two companions and Hourbloom present → at most one conversation each; entering
  again with no new outing → an empty queue.
- **Return detection:** a closed delve, a committed world turn and a collected expedition each make the next entry a
  return; entering with none is not a return. Outing then entry, and two outings then one entry, both give one return.
- **Reaction (Alignment 2026-09-20):** with no eligible hub storylet, a fixture `delve.wiped` fact from this return
  makes Hourbloom say its `return-wiped` line for its band; a `sector.lost` plus an extraction in one return picks
  `return-wiped`/`return-lost` over `return-won` (most serious first); a `wary` companion falls back to `greet`.
- **Skip spends it:** acknowledging a hub scene removes it from the queue; a re-entry does not re-offer it.
- **Rift first:** when the Rift prologue is eligible, the hub scene rows are evaluated after it (FE unit test through
  `isSceneEligible` with both rows).
- **Never mid-match / never over a layer:** with a lawn run in progress (no match record yet) no return is recorded;
  with a layer open `isSceneEligible` stays false (existing seam behaviour, re-asserted).
- **No enemy at home:** an enemy-role character with a `met`-less encounter is never present.
- **No spend:** `offer:{stock}` on `sanctum.hub` fails preflight; no hub plan contains a loot or soul step.
- **Idempotent entry:** two `enter` calls for one return return the same queue.

## Success criteria

1. One conversation per character per return, proven with the game closed. 2. Conversations react to the outing's
facts. 3. Scenes play through `StorySceneHost` via the existing trigger seam; the Rift contract is untouched. 4. No
conversation mid-match or over a layer. 5. The onboarding slot is filed on the first-session spec, not written here.
(G4 hub clause.)

## Boundaries

- **Always:** detect returns from durable outing records; go through the scene-trigger seam; one conversation per
  character per return.
- **Ask first:** more than one visitor per return; a conversation that pays a resource.
- **Never:** a second scene player or trigger; edit the first-session sequence; play anything during a lawn match;
  give an enemy a personal conversation.

## Interface exposed to dependents

| Member | Consumer |
|---|---|
| `POST …/sanctum/enter` → queue | `SanctumStage` (FE) |
| `sanctum.returned` facts, `sanctum.return` clock | `storylet-selection` (cooldowns), `spine-progress`, `narrative-readings` |
| the "first character met" fact | `spec-first-session-progression.md` (filed ask) |

## Contradictions found (report; not fixed here)

1. **No fact records a return.** `spec-narrative-vocabulary.md` §3 listed 22 `StoryFactKind` members and a
   `sanctum.return` clock (`HostClockKind.SanctumReturn`), but no fact from which that clock is counted. This spec adds
   `sanctum.returned`; filed on `narrative-vocabulary`. Alignment 2026-09-20: now listed there (§3).
2. **No seed shape for hub conversations — resolved (Alignment 2026-09-20).** The seed side defined no hub
   conversation (`spec-scene-script-loader.md` §1). narrative-seed now carries the `sanctum.hub` host row
   (`narrative-seed/spec-storylet-vocab.md` §3.1) and four `return-*` line contexts as `ally` pairs
   (`narrative-seed/spec-character-vocab.md` §5–§6); §3 above reads exactly those.

## Open questions

None for the owner.

## Design-gate checklist

```
[x] Subsystems: homeworld stage (trigger only), story-scene (consumer), onboarding (asked), characters, story ledger.
[x] Session boundary recorded (narrative-programs-spec2-20260919).
[x] Read this session: map rows 12, 21, G4, :190, :326; ideal §4.1 (Hades), §6.6; DESIGN-GATE §1 UI and Standalone rows;
    sibling specs narrative-vocabulary, story-ledger, character-registry, cast-resolver, outcome-routing; code:
    SanctumStage, sceneTrigger, OnboardingCheckpointEvaluator, OnboardingEndpoints, outing record tables.
[x] Every claim cites file:line.
[x] No population pinned.
[x] No cache; the queue is derived per return.
[x] Order: outing/entry orders and Rift-first ordering specified and tested.
[x] Actor numbers: none.
[x] No parallel path: one scene player and trigger seam.
[ ] Registry row: none new.
```

## Standards audit (2026-09-19)

Independent adversarial review against DESIGN-GATE §1 (UI row — GG-1 layers, `StorySceneHost` scoped exemption;
Standalone; Economy rows), §2 (1, 2, 9, 15, 16), §3, §5; R13 rule 3; round-3/round-4 rulings.

| # | Severity | Finding | Status |
|---|---|---|---|
| 1 | MEDIUM | "The homeworld pays no resources" vs save quests offered here that pay a roll on completion (`spec-quest-sources.md` §6) | **Fixed in text** (Locked anchors). **Resolved — Owner ruling 2026-09-20:** the roll is taken out of a collect's existing tier rolls; no faucet |
| 2 | LOW | A coarse catch-up of a dormant world writes world-continuity records; counted as an "outing", it would queue reactions to turns the player never played (round 4) | **Fixed** (§1 table): active-world full-step turns only |

Checked and holding: one conversation per character per return (structural bound, commented); enemy-role characters
never present (R13 rule 3); scenes only through the existing scene-trigger seam and `StorySceneHost`; nothing
mid-match or over an open layer; the onboarding slot asked of the first-session spec, not edited; the FE query path
is rebuilt per return (no event-refreshed cache introduced).

**Registry row:** none new. **Boundary ask:** `src/FusionRpg.Server/Narrative/SanctumReturns.cs` (new), `SanctumHub.cs` (new) →
`FusionRpg.Server.Tests` filter `SanctumHub`; `gk-web/web/fusion-rpg-web/src/stages/sanctum/SanctumStage.tsx` keeps its
vitest mapping.

## Cross-lane alignment (2026-09-20)

Alignment 2026-09-20: this host needed a seed shape the seed side did not define. Chosen as the smallest change
consistent with ideal §6.6 and the character lines contract: conversations with choices are ordinary storylets on
the new `sanctum.hub` host row; the reaction to the outing is the character's `return-*` line (four new line contexts,
`ally` pairs), played as a one-line scene. §2 no longer reads a `hosts` field off character seeds (they have none),
and §3's outing reaction is a closed classification here instead of storylet predicates no seed could write.
