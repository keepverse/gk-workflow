# Spec: `replay-identity` (combat-ai module 8)

**Program:** [combat-ai](../combat-ai-map.md) · **Ideal:** [combat-ai-ideal.md](../combat-ai-ideal.md) §7 ·
**Depends on:** `profile-schema` (module 2) · **Unblocks:** `delve-automated-wiring` (13),
`auto-policy-switch` (14) · **Status:** **part built** (CAI2.1, 2026-09-20; `CAI2.2`'s Server source half landed 2026-09-23, lane `cai2`): the Core third is in (`CombatAiProfileIdentity` + `ICombatAiProfileSource`), and so is the Server's version-addressed source (`Server/CombatAiProfileFiles.cs`, 8 tests) — but that source has **no production caller**, and the pin resolution it exists for reads `entry.CombatAiProfile`, which needs the nullable `combat_ai_profile` column in `gk-core/src/FusionRpg.Data/**` (outside every combat-ai lane's fence). The Data third is therefore the whole remainder. See `:69`.

## Objective

A web match records what it resolved against so it can be re-resolved: `WebMatchService.cs:125-128`
stamps `EngineVersion`, `RulesetVersion`, `RngAlgoVersion`, `BattleEnvironment.Stamp` and
`ComputeContentHash().ToCompact()` onto `rpg_web_match_log`. **That stamp has a hole exactly the shape
of this program.** `ComputeContentHash` hashes database tables only — `ContentHashRegistry.For(schemaVersion)`
then one `TableDigestUnlocked` per covered table (`RpgStore.ContentHash.cs:21-42`), and a table that
does not exist throws rather than hashing empty (`:48-55`). Nothing in that sweep can see
`gk-core/data/tuning/*`, because a tuning file is not a table.

The hole is only harmless while automated decisions are not policy-driven. They are not recorded:
`DecisionTrace` holds `DecisionSource.Player` and `DecisionSource.Timeout` and nothing else
(`DecisionTrace.cs:5-20`), and `InteractiveIntentSource.ResumeReplayThenLive` replays that human
prefix and then goes live (`InteractiveIntentSource.cs:110-127`), handing every un-steered actor to
the `_fallback` policy — so **automated decisions are re-derived, never replayed**. Both correlation
replay paths re-run `BattleEngine.Resolve` over the stored setup (`WebMatchService.cs:136-151` and
`:208-223`) and return the newly computed report, and the delve resumes the same way
(`DelveBattleSessionManager.cs:267-322`). Publish `combat-ai.v{n+1}` and every one of those silently
produces a *different* battle from the same `(setup, seed)`. `AUDIT.md` M3 names this; ideal §7 rules
it: **the profile version joins the match stamp, and a match pins its profile at start.**

This module ships the identity record and the version-addressed pin, and nothing else. **It changes no
decision and moves no golden** — after it lands, every battle still resolves through today's default
policy, and the new column is a provenance field that only becomes load-bearing when
`auto-policy-switch` (14) flips that default. That ordering is the point: landing 14 first would write
`RulesetVersion` 6 rows with no profile stamp, and those rows are on disk forever.

## Tech stack

`FusionRpg.Core` (the stamp + comparison reuse, no I/O), `FusionRpg.Data` (one nullable column on
`rpg_web_match_log`, SQL stays inside the DAL), `FusionRpg.Server` (three call sites stamp it, two
replay paths read it). No new dependency, no new tuning file, no new package.

## Commands

```powershell
dotnet test gk-core/tests/FusionRpg.Core.Tests  --filter "FullyQualifiedName~ContentHash|CombatAiProfileStamp"
dotnet test gk-core/tests/FusionRpg.Data.Tests  --filter "FullyQualifiedName~WebMatch"
dotnet test gk-core/tests/FusionRpg.Server.Tests --filter "FullyQualifiedName~WebMatch|Sweep|Delve"
dotnet test gk-core/tests/FusionRpg.Core.Tests  --filter "FullyQualifiedName~BattleGolden"   # must be UNCHANGED
python gk-core/scripts/guard-dal.py
python gk-core/scripts/guard-test-substrate.py
.\scripts\verify-change.ps1 -Paths <changed files> -Session backlog-clean-up-20260920
```

No `publish.py` invocation: this module adds no tunable.

## Project structure

| What | Where |
|---|---|
| Version-addressed profile lookup + the stamp builder | `gk-core/src/FusionRpg.Core/Actions/Ai/CombatAiProfileIdentity.cs` (new; **built by CAI2.1 in lane `combat-ai-2`, 2026-09-20** — takes the shipped `CombatAiTuning`, which already carries `Version` + `Profiles`, instead of declaring a second `CombatAiProfileSet` wrapper with the same two fields) |
| The host-side source that can hand back an *older* published profile set | `gk-core/src/FusionRpg.Core/Actions/Ai/ICombatAiProfileSource.cs` (new; **built by CAI2.1**, same session) |
| Server host implementation (reads every `data/tuning/combat-ai.v*.json`) | `gk-core/src/FusionRpg.Server/CombatAiProfileFiles.cs` (new — **landed by `CAI2.2`, lane `cai2`, 2026-09-23**; 8 tests. It still has no production caller, and the pin resolution that would use it needs the denied `Data` column) |
| The stamp carrier and its comparison — **reused, not re-declared** | `gk-core/src/FusionRpg.Core/Effects/Atoms/ContentHashStamp.cs` (existing, unchanged) |
| Column migration | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.cs` — one `EnsureColumn` beside `:821` |
| Log row + append + select | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WebMatches.cs:7-19,28-68,203-229` |
| Fresh + replay stamping and reading | `gk-core/src/FusionRpg.Server/WebMatchService.cs:125-128,136-151,197-200,208-223` |
| Boot-sweep refusal | `gk-core/src/FusionRpg.Server/WebMatchService.cs:246-290` |
| Delve start/resume | `gk-core/src/FusionRpg.Server/DelveBattleSessionManager.cs:200-204,267-295` |
| Tests | `gk-core/tests/FusionRpg.Core.Tests/Actions/Ai/CombatAiProfileIdentityTests.cs` (**built by CAI2.1**), `gk-core/tests/FusionRpg.Data.Tests/WebMatchLogProfileStampTests.cs` and `tests/FusionRpg.Server.Tests/WebMatchProfilePinTests.cs` (**unbuilt** — the Data third is CAI2.1's, the Server pin tests are CAI2.2's) (the latter two not yet; see the Status line) |

**Status, 2026-09-20 (lane `combat-ai-2`).** The **Core third is built** (`CombatAiProfileIdentity`, `ICombatAiProfileSource`, 11 tests including the reflection coverage pin). The **Data third** (the `combat_ai_profile` column and `RpgStore.WebMatches.cs`) and the **Server third** (`CombatAiProfileFiles`, the three stamping sites, the pin resolution, the boot-sweep guard) are unbuilt and filed against their owning paths in `tasks/combat-ai-todo.md` "Deferred / named follow-ups" — they need paths that lane does not own. **CAI2.2 sits entirely behind the Server third** and is filed, not attempted.

## The shape

### 1. The stamp reuses `ContentHashStamp`; it does not fork it

`ContentHashStamp` is already a part-agnostic `(SchemaVersion, Hash, IReadOnlyDictionary<string,string>)`
with a durable compact form `v{n}|{hash}|{part}={digest},…` and a `TryParse` (`ContentHashStamp.cs:16-64`).
`ContentHashComparison.Compare` is already the exact decision procedure this module needs
(`ContentHashStamp.cs:106-149`):

- a null or empty stored stamp is a **Match**, *"rows written before this module existed carry no stamp,
  and refusing them would strand crash-recovery work that predates the feature"* (`:102-104`);
- same version, different hash → **Mismatch**, naming which parts differ (`:118-129`);
- the covered *set* changed → **RegistryChanged**, explicitly **not** a refusal (`:76-80`, `:132-148`);
- unparseable → **Unreadable**, refused, *"unverifiable is not proven"* (`:82-83`).

Writing a second stamp type with those same four verdicts is the mechanism fork this repo's SOLID rule
bans (`CLAUDE.md` "SOLID is binding"; `battle-engine-ssot.md` §5 Q4 *"never re-implements it"*). So the
profile stamp **is** a `ContentHashStamp` whose `SchemaVersion` is the published `combat-ai.v{n}`
version and whose parts are profile ids:

```csharp
// gk-core/src/FusionRpg.Core/Actions/Ai/CombatAiProfileIdentity.cs (new)
public static class CombatAiProfileIdentity
{
    /// <summary>The identity of one published profile set: the tuning version, the combined digest,
    /// and a per-profile digest so a replay refusal can name WHICH profile moved. Pure — the caller
    /// hands over an already-parsed set (profile-schema owns the parser); this reads no file and no
    /// clock, so the stamp is a function of the document alone.</summary>
    public static ContentHashStamp StampOf(CombatAiProfileSet set);   // CombatAiProfileSet: module 2

    /// <summary>Compare a stored compact stamp with the set a replay is about to use. Delegates
    /// verbatim to ContentHashComparison.Compare — same four verdicts, same pre-field NULL rule.</summary>
    public static ContentHashComparison Compare(string? storedCompact, ContentHashStamp current)
        => ContentHashComparison.Compare(storedCompact, current);
}
```

Digest construction must be **order-independent**: profile ids are sorted ordinal before combining, the
same discipline `ToCompact` already applies (`ContentHashStamp.cs:30-32`) and `ComputeContentHash`
applies over its table list.

### 2. The pin is loaded, not merely compared

Comparing is enough for the boot sweep, which refuses rather than re-resolves. It is **not** enough for
the two replay paths, because they must still return the battle that happened. `publish.py` keeps every
version on disk as its own file — `gk-core/data/tuning/` holds `aptitudes.v1.json` … `aptitudes.v8.json` today —
so the profile set a stamp names is recoverable:

```csharp
// gk-core/src/FusionRpg.Core/Actions/Ai/ICombatAiProfileSource.cs (new)
public interface ICombatAiProfileSource
{
    /// <summary>The set a FRESH match resolves under, and whose stamp it records.</summary>
    CombatAiProfileSet Current { get; }

    /// <summary>The set a PINNED match resolves under. Null means the host cannot supply that
    /// version — a refusal, never a silent fall back to Current: re-resolving a pinned match on a
    /// newer profile is the exact defect this module exists to close.</summary>
    CombatAiProfileSet? ForVersion(int tuningVersion);
}
```

`CombatAiProfileFiles` (Server) implements it by loading every `combat-ai.v*.json` in the tuning
directory at startup — the host does the file reading, Core stays I/O-free (`tunables-ssot.md` §7.2,
the same split `spec-mode-profile.md` uses for `mode-profiles.v1.json` — that file does not exist yet either; its owner is `lawn-tuning-profile`).

**Resolution order at a replay**, in each of the two `if (!created)` branches
(`WebMatchService.cs:129-165`, `:201-235`) and in `DelveBattleSessionManager.Resume` (`:267-295`):

1. `entry.CombatAiProfile` is NULL → resolve under today's default policy (see §3). No refusal.
2. It parses, and `ForVersion(stamp.SchemaVersion)` returns a set whose own stamp **equals** the stored
   hash → resolve under that set. This is the pin.
3. It parses, `ForVersion` returns a set, and the hashes differ → the published file was edited in
   place under the same version number. Refuse: `profile.mismatch`. (Hand-editing a published `v{n}` is
   already banned — `tunables-ssot.md`, `CLAUDE.md` "Generated seed data is never hand-edited"; this
   turns the ban into a detection.)
4. `ForVersion` returns null → refuse: `profile.unavailable:v{n}`.
5. Unparseable → refuse: `profile.unreadable`.

Refusal shape matches the existing `correlation.mismatch` return already used by both branches
(`WebMatchService.cs:132`, `:210`): `(false, "<reason>", null)`. `DelveBattleSessionManager.Resume`
already returns `null` for an unreplayable row (`:274`, `:291` *"an absent/incomplete trace refuses,
never re-resolves blind"*) — the same return, with the reason logged, is the consistent answer there.

**The boot sweep** (`WebMatchService.cs:246-290`) gets a fifth guard, placed after the content-hash
check and written in the same shape: a `ShouldRefuse` verdict calls `MarkWebMatchSweepRefused` with the
reason, which is terminal by design (`:252-256` — an unmarked refusal would be re-listed every boot and
crowd the `ORDER BY id ASC LIMIT n` window). The sweep does **not** attempt a pinned re-resolve: it
already refuses anything it cannot reproduce exactly.

### 3. Rows stamped before the field existed

A NULL `combat_ai_profile` means *"this match resolved before combat-ai profiles existed"*, which is
`StubIntentSource` and the pre-14 default chain `intentSource ?? state.DefaultAiIntentSource ?? new
StubIntentSource(...)` (`BasicAttack.cs:175-180`). It never means "the current profile". Two periods,
and both are safe:

| Period | Row | Replay |
|---|---|---|
| Before module 14 | `RulesetVersion` 5, profile NULL | Re-derives under the same stub default it originally used — behaviourally identical, so nothing is refused. Matches `ContentHashComparison.Compare`'s own pre-field rule verbatim. |
| After module 14 | `RulesetVersion` 6, profile stamped | Pinned per §2. |
| After module 14, legacy row | `RulesetVersion` 5, profile NULL | Already refused by the **existing** version guard (`WebMatchService.cs:259-268`) before the profile is ever consulted. |

**The invariant this yields, and it is asserted rather than assumed:** a row with
`RulesetVersion >= 6` and a NULL `combat_ai_profile` is impossible by construction — it would be a
profiled match that forgot to stamp. A test refuses that pairing, and the write path makes it
unreachable by stamping in the same `AppendWebMatchLog` call that writes the version.

### 4. Storage

One nullable `TEXT` column, following `profile_id`'s own precedent verbatim (`RpgStore.cs:815-821`,
including that the `EnsureColumn` must sit **after** `rpg_web_match_log`'s own `CREATE` — `:803-805`
records why):

```csharp
// combat-ai `replay-identity`: the combat-ai profile set a match resolved under, so a replay can
// resolve under the SAME set instead of whatever was published since. NULL means "this match
// predates combat-ai profiles" — the pre-14 stub default — never "use the current profile".
EnsureColumn(db, "rpg_web_match_log", "combat_ai_profile", "TEXT");
```

`WebMatchLogEntry` gains `string? CombatAiProfile = null` as a trailing optional positional after
`ProfileId` (`RpgStore.WebMatches.cs:19`); `AppendWebMatchLog` gains `string? combatAiProfile = null`
after `profileId` (`:31`) so every existing caller compiles unchanged; `SelectLog` gains the column
(`:203-208`) and `MapLog` reads index 16 (`:220-229`).

**`combat_ai_profile` is not `profile_id`.** `profile_id` carries a `BattleModeProfile` id — the
timeline mode (`BattleModeProfileCatalog.DelveId` at `DelveBattleSessionManager.cs:204`;
`BattleModeProfile.cs:185-189` holds the five ids). Overloading it would fuse the turn model with the
decision policy. Two columns, two vocabularies, stated here because the name collision is the obvious
mistake.

### 5. Stamping sites

Three, all already calling `AppendWebMatchLog` and all gaining one named argument:

- `WebMatchService.cs:125-128` — ad-hoc web match.
- `WebMatchService.cs:197-200` — planned match (the expedition-collect path,
  `ExpeditionEndpoints.cs:136`).
- `DelveBattleSessionManager.cs:200-204` — delve room fight, beside the existing `profileId:`.

Siege has no row to stamp: `DistrictAssaultResolver` never calls `AppendWebMatchLog` (the only two
callers in `src/` are the ones above), because a district assault resolves inside a world turn from
`(setup, seed)` and persists no match log. **Stated as a named gap, not a silent exemption:** siege
replay identity belongs to whatever world-turn record acquires one, and it is out of this module's
scope. Today it is unreachable — siege already runs a profiled policy whose tuning is published the
same way, so the exposure is identical in kind and is recorded here rather than being discovered later.

### 6. What this module deliberately does not do

It does **not** put the stamp on `BattleReport`. `BattleReport.ContentHash` reaches the report
(`WebMatchService.cs:411`) and is blanked before hashing precisely so a content addition never looks
like a determinism break (`BattleGoldenTests.cs:145-175`, the `Hash` helper blanks four provenance
fields). Adding a fifth field would move the four golden constants for a provenance reason, which
violates the one-cause rule (map §Load-bearing rules 7 / H1). If a later module wants it on the report,
it blanks it in `Hash` in the same change and says so — that is a decision for that module, not this one.

## Tunables

**None.** This module adds no key to any `gk-core/data/tuning/*.json` and publishes no `v{n+1}`. It *reads* the
version number of `data/tuning/combat-ai.v{n}.json`, which `profile-schema` (module 2) owns and
publishes through `gk-core/tools/tuning/publish.py`.

Two constants are involved and neither is a balance number:

| Constant | Where | Class |
|---|---|---|
| `ContentHashStamp.TableDigestHexLength = 16` | `ContentHashStamp.cs:22` (existing, reused) | **Structural** — a log-row size bound, already commented *"long enough that a collision is not a concern"*. Not re-declared here. |
| The compact form's `v{n}\|hash\|parts` grammar | `ContentHashStamp.cs:28-33` (existing, reused) | **Structural** — a durable wire format. Changing it invalidates stamps already in the database, the same warning `BattleEnvironment`'s own comment carries (`BattleModels.cs:667-669`). |

## Code style

- The reason a column exists lives in the comment beside its `EnsureColumn`, as every neighbour does
  (`RpgStore.cs:803-821`) — including what NULL means, because that is the field's hardest rule.
- Refusal strings are lowercase dotted tokens matching the existing `correlation.missing` /
  `correlation.mismatch` / `battle.<reason>` family (`WebMatchService.cs:101`, `:132`;
  `ExpeditionEndpoints.cs:138`).
- A refusal is logged to `Console.Error` with the match key and the reason before it is marked, exactly
  as the four existing sweep guards do (`WebMatchService.cs:265`, `:275`, `:285`).
- Core takes parsed data, never a path; hosts read files (`tunables-ssot.md` §7.2).
- `string.Equals(..., StringComparison.Ordinal)` for every id and digest comparison — never culture.

## Testing strategy

Contract and closed vocabulary only (`validation-ssot.md`; DESIGN-GATE §3 rule 7).

**Core — `CombatAiProfileIdentityTests`**
- ✅ `StampOf` round-trips through `ToCompact` / `TryParse` with every profile id preserved.
- ✅ Determinism: the same set stamps identically twice, and a set whose profiles are supplied in a
  different order stamps identically (order-independence is the property, not an ordering).
- ✅ One changed weight in one profile → `Mismatch`, and the reason **names that profile id**.
- ✅ A profile id **added** → `RegistryChanged`, and `ShouldRefuse` is false. A new place×role profile
  must not strand every match logged before it.
- ✅ A null or empty stored stamp → `Match` with `ShouldRefuse` false.
- ✅ A corrupted compact string → `Unreadable` with `ShouldRefuse` true.
- ❌ Never assert how many profiles a set has, or any weight's value. Both are readings that grow with
  content; the vocabulary of *selectors, conditions, tiers and personality axes* is module 2's and 3's
  closed list to pin, not this module's population.

**Data — `WebMatchLogProfileStampTests`** (in memory; `testing-standard.md`, `guard-test-substrate.py`)
- ✅ `AppendWebMatchLog` with no `combatAiProfile` writes a row whose `CombatAiProfile` is null — the
  compile-compatibility property every existing caller relies on.
- ✅ A stamped row round-trips through `TryGetWebMatchLog` and `ListUnresolvedWebMatches` byte-for-byte.
- ✅ `EnsureColumn` is idempotent: opening an existing database twice adds the column once and preserves
  pre-existing rows with NULL.

**Server — `WebMatchProfilePinTests`**
- ✅ Fresh match: the row is stamped with `Current`'s stamp.
- ✅ Replay under an unchanged profile set resolves and returns `"replay"` — the no-op property.
- ✅ Replay after a `v{n+1}` publish resolves under the **pinned** `v{n}` set, and the returned report
  is byte-identical to the fresh one. This is the module's whole proof.
- ✅ Replay whose pinned version the source cannot supply returns `(false, "profile.unavailable:v{n}", null)`
  and **never** falls back to `Current`.
- ✅ Replay whose pinned version exists but whose published file was edited in place returns
  `profile.mismatch`.
- ✅ Boot sweep refuses a profile mismatch **terminally** (`sweep_refused` is set, and the row leaves the
  unresolved window on the next call) — the same assertion shape the version and platform guards have.
- ✅ **Order-independent** (DESIGN-GATE §5): a delve row resumed *before* any publish and a delve row
  resumed *after* one are separate criteria, and both are tested. `DelveBattleSessionManager.Resume`
  and the `StartSession` rehydrate branch (`:216-232`) are two reachable entries into the same pin and
  each has its own test — the second is the one an acceptance criterion would otherwise skip.
- ✅ A row with `RulesetVersion >= 6` and a NULL profile stamp is unreachable from the write path.

**Goldens**
- ✅ `BattleGoldenTests` is **untouched and unchanged**. If a golden moves, this module is wrong — it is
  the acceptance, not something to re-bless. The report carries no new field (§6), so this holds by
  construction and is asserted rather than argued.

## Boundaries

**Always**
- Reuse `ContentHashStamp` / `ContentHashComparison`. One stamp mechanism.
- Treat NULL as "predates the feature", exactly as the content stamp and the platform stamp already do.
- Refuse loudly and terminally rather than resolve under a profile the match did not use.
- Keep Core file-free; the host loads and injects.
- Keep SQL inside `FusionRpg.Data` (`guard-dal.py`).

**Ask first**
- Putting the stamp on `BattleReport` (it moves four golden constants; §6).
- Any change to `ContentHashStamp`'s compact grammar (it invalidates stamps already on disk).
- Pruning old `combat-ai.v*.json` files from `gk-core/data/tuning/` — that is what makes a pin unresolvable.

**Never**
- Declare a second stamp/verdict type with the same four verdicts.
- Overload `profile_id` (it is the `BattleModeProfile` id).
- Fall back to the current profile when a pinned one is missing.
- Hand-edit a published `combat-ai.v{n}.json`; publish `v{n+1}` through `gk-core/tools/tuning/publish.py`.
- Add the tuning document to `ContentHashRegistry` — that registry hashes tables, and a missing table
  is a hard throw (`RpgStore.ContentHash.cs:48-55`). A file is not a table.

## battle-engine-ssot §5 — the six answers

1. **Which responsibility (§3)?** Responsibility **19, determinism and seeded RNG streams** — replay
   identity is that property's record. Not a new responsibility; the closed register is untouched.
2. **Decide or resolve (§3c)?** **Neither.** It is provenance *about* the deciding side. It never enters
   `IIntentSource.TryDeclare` and never changes what the engine resolves. §3c's own test applies: *"a
   recorded battle replays by substituting a trace source for the live AI and getting an identical
   report"* — automated decisions have no trace, so their identity must come from the policy's version.
3. **Mechanism or loop?** **Mechanism** — one stamp, one comparison, one pin, shared by every mode that
   persists a match. The per-mode part is only *where* the row is written.
4. **Which implementation does it extend?** `ContentHashStamp` / `ContentHashComparison`
   (`ContentHashStamp.cs:16-149`) and the existing `rpg_web_match_log` stamp columns
   (`RpgStore.cs:803-821`). By calling, never by copying.
5. **Does every mode get it?** Every mode that logs a match: ad-hoc web battle, expedition collect,
   delve session. Siege does not log one (`DistrictAssaultResolver` never calls `AppendWebMatchLog`) and
   is named as a gap in §5 above rather than excused. The lawn has no replay identity at all and is
   outside this module by construction.
6. **Deterministic and seeded?** Yes. `StampOf` is a pure function of the parsed document — no clock, no
   RNG, no ambient state, ordinal ordering. It draws from no seeded stream because it makes no choice.

## Success criteria

1. `rpg_web_match_log.combat_ai_profile` exists, is nullable, and is idempotently added on an existing
   database.
2. All three `AppendWebMatchLog` call sites stamp it; no existing caller signature broke.
3. Both `WebMatchService` correlation-replay branches and both delve resume entries resolve under the
   **pinned** set and return a report byte-identical to the fresh resolve, across a `v{n+1}` publish.
4. A pinned version the host cannot supply, a same-version hash mismatch, and an unreadable stamp each
   refuse with a named reason; none falls back to the current profile.
5. The boot sweep marks a profile refusal terminally, in the same shape as the four existing guards.
6. A NULL stamp replays exactly as today, and `RulesetVersion >= 6` with a NULL stamp is unreachable.
7. **`BattleGoldenTests` unchanged**, all four constants untouched.
8. `guard-dal.py` and `guard-test-substrate.py` green; `verify-change.ps1` clean for the changed paths.

## Open questions

1. **`ContentHashStamp.TableDigests` is named for tables, and this module puts profile ids in it.**
   Options: (a) reuse as-is and let the property name read oddly for one of its two callers;
   (b) rename to a part-neutral `PartDigests` with `TableDigests` kept as an obsolete alias, touching
   every existing content-hash consumer; (c) fork a second type. **Recommended default: (a) now.** (c)
   is the SOLID defect this spec exists to avoid, and (b) is a cross-module rename that would put two
   causes in one commit. Revisit (b) as its own cosmetic change once a second non-table consumer exists.
2. **How many published `combat-ai.v*.json` files a host must keep loaded.** Options: (a) all of them
   (today's tuning directory already holds eight `aptitudes` versions, so the cost is bounded and small);
   (b) a retention window, with older pins refused. **Recommended default: (a)**, because a refused
   replay of a real expedition collect is a player-visible failure and disk is not the constraint.
   Revisit only if the file count becomes a measured startup cost.
3. *(Cross-module note, outside this module's responsibility.)* Siege has no persisted match row, so it
   has no replay identity of any kind today — not for the profile, and not for the content hash or the
   platform stamp either. Recorded here because this module's evidence found it; it belongs to whichever
   module gives a world turn a durable battle record, not to `replay-identity`.

## Design gate checklist (DESIGN-GATE §5)

```
[x] Subsystems identified: battle engine (determinism), data schema, server replay/sweep, tunables.
[x] Session boundary: backlog-clean-up-20260920, combat-ai /spec run; this session wrote only
    docs/architecture/combat-ai/spec-*.md (four files), edited nothing else, ran no git mutation.
[x] Read this session: combat-ai-map.md, combat-ai-ideal.md rev 3 (D1-D6), research/combat-ai/AUDIT.md,
    S1-battle-core.md, battle-engine-ssot.md (§2, §3c, §5), DESIGN-GATE.md §1+§5, decisions.md rows
    43-44, CLAUDE.md + AGENTS.md hard rules.
[x] decisions.md checked: row 44 (next RulesetVersion bump trigger + predicted-delta writeup) and
    row 43 (Battle time model, determinism = (setup, seed, decision-trace)) both govern this module.
[x] Every factual claim cites file:line; every cited file was opened this session.
[~] audit-doc-citations.py reports no HIGH finding for this file -- run after writing; new files are
    marked "(new; does not exist yet)".
[x] Verified against CODE: ComputeContentHash covers tables only, DecisionTrace holds Player/Timeout
    only, both replay branches re-resolve, profile_id is the BattleModeProfile id.
[x] Read the surrounding section of every rule quoted (battle-engine-ssot §3c, §5; DESIGN-GATE §1 rows
    "Anything that changes what happens in a BATTLE" and "Data / SQL / schema").
[~] Constraints tested, not assumed: the "no golden moves" claim is argued from construction (the
    report gains no field, and BattleGoldenTests.Hash serialises the report) and is listed as the
    module's own acceptance to RUN, not as a completed measurement -- this session ran no suite
    (spec-only lane, no builds).
[x] Nothing contradicts a §2 invariant. Invariant 6 (SQL only in FusionRpg.Data) and 12 (balance
    surface is data) are honoured; this module adds no tunable.
[x] Corrections propagated: none needed -- no existing doc claim was found wrong. The siege
    no-match-row gap is recorded in §5 and in Open questions 3 rather than left implicit.
[x] No assertion pins a derived population, item total, generated text, or per-cycle outcome. The
    testing section bans asserting profile counts and weight values explicitly.
[x] §2.16 event-refreshed cache: this module introduces none. The host's version->set map is built
    once at startup from immutable published files and is never invalidated mid-process; a version
    absent from it is a refusal, not a stale read.
[x] No acceptance criterion fixes an ordering that can vary: the delve pin is tested through BOTH
    Resume and the StartSession rehydrate branch, and the publish-before / publish-after replay pair
    is stated as order-independent.
[x] Produces/consumes no actor combat or derived magnitude -- no ActorHub interaction at all.
[x] Extends no SOLID-violating path: it reuses the one stamp mechanism rather than forking a second.
[x] New rule has a guard: the pin is enforced by tests, and the DAL boundary by guard-dal.py. No new
    rule needs a registry row -- this module adds a field and a refusal, not a repo-wide policy.
```
