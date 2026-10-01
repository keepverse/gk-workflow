# Spec: `band-reader`

**Program:** [empire-seed](../empire-seed-map.md) · **Module id:** `band-reader` · **Map row:** 2 ·
**Wave:** 0 · **Ideal id:** I2
**Depends on:** — · **Model calls:** none
**Status:** spec phase, 2026-09-19. Map approved by the owner 2026-09-19. No build authorized until this
spec is approved.

---

## 1. Objective

One C# reader for every world-family seed file, and one resolver that turns a seed's declared ordinal
into a number from a `gk-core/data/tuning/` band table. Both live in Core, and neither ever touches the file
system: the **host** reads the seed files and the tuning and injects them. `StructureCatalog` is the
first consumer. The legion catalogs (`legion-bands`) are the second. No family writes its own reader
after this.

**Done means:**
- `StructureCorpus` parses host-injected text through the shared reader.
- `Bands.MaterialTierOf`'s hardcoded ladder is gone, and the ladder lives in the tuning file alone.
- A VALIDATED field outside its registry is a load rejection that names the family, the field and the
  value.
- The resolved `StructureCatalog.All` is unchanged. This module is a refactor.

## 2. Scope and non-goals

**In scope.** The seed-file reader, the ordinal-to-band resolver, the closed-vocabulary validator, the
host injection in `Program.cs` and in the three test bootstraps, retiring `Bands.cs`, and the structure
role registry the C# side validates against.

**Not in scope.**
- Moving any structure number out of `magnitudes`. That is `structure-bands`, which consumes this
  module.
- Widening any vocabulary (`exchange-role`).
- Absorbing `ConcreteSpeciesSeedReader`
  (`gk-core/src/FusionRpg.Core/Creatures/Generation/ConcreteSpeciesSeedReader.cs:25`). That reader handles
  GENERATED concrete output. This one handles DERIVED magnitudes resolved at load. They are two
  ownership levels (`item/seed-contract.md` §2), and two readers for them is not a SOLID fork.
- Any roll. Structures and legion equipment never roll. The one roll SDK stays `Instantiator`
  (`gk-core/src/FusionRpg.Core/Effects/Atoms/Instantiator.cs:92`).

## 3. Current state (verified 2026-09-19)

| Bucket | What | Evidence |
|---|---|---|
| Built | The shared seed file shape `{"kind","_meta","entries"}`, one kind-specific C# reader | `gk-core/src/FusionRpg.Core/World/StructureSeed/StructureCorpus.cs:88-107` |
| Built | Loud per-field parse errors (`StructureCorpusLoadException`) | `gk-core/src/FusionRpg.Core/World/StructureSeed/StructureCorpus.cs:71-75`, `:173-197` |
| Built | Catalog validation discipline | `gk-core/src/FusionRpg.Core/World/StructureCatalog.cs:350-430` |
| Built | Closed C# vocabularies for three VALIDATED fields: `SlotKind`, `AcquisitionPath`, `RarityLadder.RungIds` | `gk-core/src/FusionRpg.Core/World/SlotTypeCatalog.cs:7`; `gk-core/src/FusionRpg.Core/World/Siege/Obstacles.cs:48`; `gk-core/src/FusionRpg.Core/Items/RarityLadder.cs:19` |
| Built | The tier ladder in tuning | `gk-core/data/tuning/structure-seed.v1.json:17` |
| Wiring gap | `StructureCorpus.Load` calls `Directory.EnumerateFiles` and `File.ReadAllText` inside Core (tunables-ssot T8: *"Core never reads the file"*) | `gk-core/src/FusionRpg.Core/World/StructureSeed/StructureCorpus.cs:91-95`; host call `gk-core/src/FusionRpg.Server/Program.cs:223-225` |
| Wiring gap | `Bands.MaterialTierOf` hardcodes `rubble/timber/stone → 1/2/3` beside `bands.tierLadder`. Only tests call it | `gk-core/src/FusionRpg.Core/World/Bands.cs:20-28`; callers `gk-core/tests/FusionRpg.Core.Tests/World/StructureCatalogImportTests.cs:249-254` |
| Wiring gap | No C# code loads `structure-seed.v1.json`. Its only readers are Python (grep this session) | `gk-forge/tools/seedsmith/seedsmith/adapters/structures/planner.py:178`; `gk-forge/tools/seedsmith/seedsmith/adapters/structures/metrics.py:265` |
| Wiring gap | `role` is a free string in C#. The closed list exists only in Python | `gk-core/src/FusionRpg.Core/World/StructureSeed/StructureCorpus.cs:119`; `gk-forge/tools/seedsmith/seedsmith/adapters/structures/anchor/schema.py:41` |
| Wiring gap | The C# walk recurses into every directory, `_exemplars/` included. The Python loader marks `_exemplars/` as non-corpus. After `world-exemplars` lands, C# would load exemplars as catalog rows | `gk-core/src/FusionRpg.Core/World/StructureSeed/StructureCorpus.cs:93`; `gk-forge/tools/seedsmith/seedsmith/corpus/model.py:188` |
| Real gap | The shared reader, the resolver, the role registry | — |

## 4. Principles as they bind this module

- **The balance surface is data** (tunables-ssot T1, T5). A band value lives in `gk-core/data/tuning/`. A missing
  band row is a load rejection naming it, never a default.
- **Core never reads a file** (tunables-ssot T8). The host enumerates and reads files, and Core parses
  strings.
- **Range-safe numbers** (`PRINCIPLES.md` §5). A resolved integer magnitude is `long`, arithmetic is
  `checked`, and narrowing into a shipped `int` field is `checked((int)v)`, which throws and never wraps.
  Floating point is allowed where a family declares a real-valued band. No structure band needs one
  today.
- **Seed → concrete → per-player.** A structure's numbers are deterministic and shared by every player,
  as species stats are. Nothing here is a per-player roll.
- **No model.** This module makes zero calls, and the generation rules do not bind it.

## 5. Design

### 5.1 Namespace and types

`src/FusionRpg.Core/Seeds/` (neutral, because structures are only the first family):

```csharp
public sealed record SeedSource(string RelativePath, string Json);             // host-built, Core-parsed

public sealed record SeedEntry(string Kind, string RelativePath, string Id, JsonElement Data);

public static class SeedFileReader
{
    // Parses every source whose top level is {"kind": <kind>, "entries": [...]}; skips any other JSON
    // (same rule as seedsmith Corpus.load, corpus/model.py:183-186); skips any source whose first path
    // segment is "_exemplars" (corpus/model.py:188). Orders by (RelativePath, Id) ordinal, so the
    // host's enumeration order cannot change the result.
    public static IReadOnlyList<SeedEntry> Read(IEnumerable<SeedSource> sources, string kind);
}

public sealed record ClosedVocabulary(string Name, IReadOnlySet<string> Members);

public sealed record BandTable(string Axis, IReadOnlyDictionary<string, long> ValueByOrdinal);

public sealed class SeedBandResolver
{
    public SeedBandResolver(string family, IReadOnlyDictionary<string, BandTable> tables,
                            IReadOnlyDictionary<string, ClosedVocabulary> vocabularies);
    public long Resolve(string axis, string ordinal, string entryId);       // throws SeedBandException
    public string RequireMember(string vocabulary, string value, string entryId); // throws SeedBandException
}

public sealed class SeedBandException : Exception   // "{family}/{entryId}: {field} '{value}' ..."
```

- **`Resolve`** throws when the axis has no table, and when the ordinal has no row. The message names
  the family, the entry, the axis and the ordinal.
- **`RequireMember`** throws for a value outside its vocabulary.
- The resolver holds no state beyond what it was constructed with. Two resolvers built from equal inputs
  resolve identically.

### 5.2 The structure family on it

- **`StructureCorpus.Parse(IEnumerable<SeedSource>)`** replaces `Load(string root)`. It calls
  `SeedFileReader.Read(sources, "structure-anchor")`, then the existing per-field parse, now reading from
  `SeedEntry.Data`. `StructureCorpusLoadException` keeps its message shape, carrying the relative path.
- **VALIDATED fields checked at parse** through `RequireMember`: `role` against the role registry
  (§5.3); `requiredSlotKind` against `Enum.GetNames<SlotKind>()` — and, when present, every entry of
  `requiredSlotKinds` the same way (round 5 B1; first entry equals `requiredSlotKind`, no duplicates,
  `empire-seed` `trade-structure-rows` §5.4 item 3); `acquisitionPaths` against
  `AcquisitionPath` (case-insensitive, matching `gk-core/src/FusionRpg.Core/World/StructureCatalog.cs:310`); and
  `rarity` against `RarityLadder.RungIds`. `rarity` is not parsed into `StructureCorpusRow` today. It is
  added as a field so it can be validated.
- **`StructureSeedTuning`**, parsed by `StructureSeedTuningLoader.Parse(string json)`, carries the
  `bands` block as `BandTable`s. The tier ladder becomes a `materialTier` band table in the next published
  `structure-seed` version (`{"rubble":1,"timber":2,"stone":3}`, published through
  `gk-core/tools/tuning/publish.py --add-key`). `bands.tierLadder` stays as the ordered axis for the Python
  planner, and a test asserts that the band table's keys equal `tierLadder` (one list, two readers).
- **`Bands.cs` is deleted.** Its two tests move to the resolver over the published table.
- **Nothing in `StructureCatalog.ToStructureDef` changes** in this module. `magnitudes` stay
  authoritative until `structure-bands`.

### 5.3 The role registry: one list, read by both languages

`data/seed/structures/_registry/roles.v1.json` is a hand-authored registry (`**/_registry/**` is an
authored path). It holds the ten role ids in declared order, each with its description. The existing
role descriptions (`gk-forge/tools/seedsmith/seedsmith/adapters/structures/anchor/descriptions.py:21-24`) move
into it. `schema.ROLE` builds its tuple from this file. The C# host injects it as a `ClosedVocabulary`.
There are no longer two lists to keep in sync. The next reviewed widening is one row plus a registry
version bump (`exchange-role`).

### 5.4 Host injection

`gk-core/src/FusionRpg.Server/Program.cs:223-225` enumerates `gk-data/packs/fusion/data/seed/structures/**/*.json` under
`AppContext.BaseDirectory` and builds `SeedSource`s with repository-style relative paths (forward
slashes). It reads `data/tuning/structure-seed.v{n}.json` and the role registry, and calls
`StructureCatalog.Configure(StructureCorpus.Parse(sources), tuning, roles)`. The three test bootstraps do
the same through one shared test helper, so the forty-plus temporary-corpus tests do not each re-derive
it:
- `gk-core/tests/FusionRpg.Core.Tests/World/StructureCatalogTestBootstrap.cs`
- `gk-core/tests/FusionRpg.Data.Tests/StructureCatalogTestBootstrap.cs`
- `gk-core/tests/FusionRpg.Server.Tests/PowerAndAptitudeTuningTestBootstrap.cs`

The count is a reading: 63 `StructureCorpus.Load` call sites across `tests/` this session. The publish
copy rule that places `gk-data/packs/fusion/data/seed/structures` next to the exe
(`gk-core/src/FusionRpg.Server/FusionRpg.Server.csproj`) also copies `_registry/`.

## 6. Tunables

| File | Key | Unit | Change |
|---|---|---|---|
| `data/tuning/structure-seed.v{n+1}.json` | `bands.materialTier.{rubble,timber,stone}` | tier index (unitless ordinal → `StructurePolicy` tier key) | new, values copied from `gk-core/src/FusionRpg.Core/World/Bands.cs:22-24` |

No value changes (T7: a refactor never lands with a rebalance).

## 7. Commands

```powershell
python gk-core/tools/tuning/publish.py structure-seed --add-key "bands:materialTier={\"rubble\":1,\"timber\":2,\"stone\":3}" --label "band-reader: tier ladder single source"
.\scripts\verify-change.ps1 -Paths <every changed C# and test file> -Session <build-session-id>
python gk-core/scripts/audit-overflow.py --targets A3
python gk-core/scripts/audit-magic-numbers.py --summary
```

## 8. Structure

```
src/FusionRpg.Core/Seeds/SeedFileReader.cs          new
src/FusionRpg.Core/Seeds/SeedBandResolver.cs        new (BandTable, ClosedVocabulary, SeedBandException)
gk-core/src/FusionRpg.Core/World/StructureSeed/StructureCorpus.cs      Parse(sources); no File/Directory call
src/FusionRpg.Core/World/StructureSeed/StructureSeedTuning.cs  new loader
gk-core/src/FusionRpg.Core/World/StructureCatalog.cs        Configure(corpus, tuning, roles)
gk-core/src/FusionRpg.Core/World/Bands.cs                   deleted
gk-core/src/FusionRpg.Server/Program.cs                     host enumeration and injection
data/seed/structures/_registry/roles.v1.json        new, hand-authored
gk-forge/tools/seedsmith/seedsmith/adapters/structures/anchor/schema.py   ROLE read from the registry
tests/FusionRpg.Core.Tests/Seeds/SeedBandResolverTests.cs        new
tests/... three bootstraps + a shared SeedSourceFixture helper
```

## 9. Acceptance (contract level)

1. **No file access on the seed path.** `src/FusionRpg.Core/Seeds/**` and
   `gk-core/src/FusionRpg.Core/World/StructureSeed/**` contain no `File.` and no `Directory.` token. A source-scan
   test asserts it.
2. **Unknown ordinal, missing band.** Resolving an ordinal absent from its table, or an axis with no
   table, throws `SeedBandException` naming the family, the entry, the axis and the ordinal.
3. **Registry rejection.** A corpus row whose `role`, `requiredSlotKind`, `acquisitionPaths` member or
   `rarity` is outside its vocabulary fails `Parse` with the field and the value named.
4. **Order independence.** Shuffling the `SeedSource` list produces an identical `StructureCorpus.Rows`
   sequence. The test runs both orders.
5. **Exemplars are never rows.** A source under `_exemplars/` with `kind: structure-anchor` is absent
   from `Rows`.
6. **One ladder.** The `materialTier` table's key set equals `bands.tierLadder`, and `Bands.cs` does not
   exist.
7. **Byte-identical catalog.** `StructureCatalog.All`, serialized field by field in id order, hashes the
   same before and after this module. This is the same harness `structure-bands` reuses (§10).
8. **Range.** `Resolve` returns `long`. Narrowing into an `int` `StructureDef` field goes through
   `checked`, and a test feeds `long.MaxValue` and expects `OverflowException`.
9. **Role vocabulary pin.** Ten roles in the registry, and Python `ROLE` equals the C# vocabulary. This
   is a closed vocabulary the code owns, and an eleventh role is the reviewed change `exchange-role`
   makes.

## 10. Test plan and verification boundary

| Test (project) | Criterion |
|---|---|
| `SeedBandResolverTests` (Core.Tests) | 2, 8 |
| `SeedFileReaderTests.Shuffle_is_order_independent`, `.Exemplars_are_skipped` (Core.Tests) | 4, 5 |
| `StructureCorpusParseTests.Unknown_role_is_rejected` and siblings (Core.Tests) | 3 |
| `SeedPathNoFileAccessTests` (Guard.Tests, source scan) | 1 |
| `StructureCatalogSnapshotTests.Catalog_hash_is_unchanged` (Core.Tests) | 7. It serializes every `StructureDef` property by reflection, so a new property cannot be silently left out. Before any code changes, the first task writes that serialization of the pre-change catalog to `tests/FusionRpg.Core.Tests/World/_snapshots/structure-catalog.json`. The test compares the live serialization to it byte for byte. That is a refactor guard for `band-reader` and `structure-bands` only. It is **deleted at the close of `structure-bands`**, because after that the corpus grows by design, and a snapshot that has to be regenerated whenever content ships is a population pin under another name (`validation-ssot.md` §3) |
| `test_structure_anchor_contract.py` (pytest) | 9, Python side |

**Verification boundary.** The C# paths map to `core-fallback` / `core-tests-fallback`
(`gk-core/scripts/verification-boundaries.v1.json:132-141`, `:179-188`), `gk-core/src/FusionRpg.Server/**` (`:1058`) and
`gk-core/tests/FusionRpg.Data.Tests/**` (`:491`). Run
`.\scripts\verify-change.ps1 -Paths <changed> -Session <id>`. The change spans Core, Data and Server test
projects, which is point 2 of AGENTS.md's "Verification boundary", so the full suite is also run once at
this module's close. **Gap:** `data/seed/structures/_registry/**`, `data/tuning/structure-seed.*` and
`gk-forge/tools/seedsmith/**` are unmapped (`gk-core/scripts/verify-change.py:771` throws). The owner of the fix is
`test-verification-boundary` `python-test-lane`. Until then, the Python side runs
`$env:PYTHONPATH = "gk-forge/tools/seedsmith"; python -m pytest gk-forge/tools/seedsmith/tests/test_structure_anchor_contract.py -q`.

## 11. Hard edges

- **Every test that reaches `StructureCatalog`** goes through a bootstrap. The signature change to
  `Configure` touches all three bootstraps and every temporary-corpus test. Land the shared helper first,
  then migrate call sites mechanically in one change.
- **A new rule with a guard:** "Core never reads a file on the seed path" (criterion 1) needs a row in
  `gk-core/scripts/enforcement-registry.v1.json` in the same change.
- **Server publish layout.** `_registry/` must be copied next to the exe, or the server fails at startup.
  That is loud, which is correct, but the csproj copy rule has to change in the same commit.

## 12. Dependencies

- Upstream: none.
- Downstream: `structure-bands` (all structure numbers), `exchange-role` (role registry widening),
  `legion-seed-contract` and `legion-bands` (the legion family's reader and tables).
- Cross-map: `legion-build-map.md` names this as *"the one seed-plus-bands reader for every world
  family"* (its §3 table). No module there may write a second one.

## 13. Open questions

None. The namespace (`FusionRpg.Core.Seeds`), which the map left as a spec-time choice, is decided here
by the principle that the reader is family-neutral.

## 14. DESIGN-GATE §5 checklist

```
[x] Subsystems: Core world catalog, structure seed reader, Server composition root, tuning.
[~] Session boundary: this spec is inside trade-network-idea-20260919's paths. The build session declares src/,
    tests/, data/ paths itself.
[x] Read this session: DESIGN-GATE rows for tunables, numeric magnitudes, seedsmith; tunables-ssot §2-§3;
    PRINCIPLES §5-§7; validation-ssot; item/seed-contract §1-§3.
[x] decisions.md: no lock on the seed reader. The Keepverse split (map §9 item 4) moves paths, not shape.
[x] Every claim cites file:line.
[x] audit-doc-citations: no HIGH finding for this file.
[x] Verified against code: StructureCorpus.Load, Bands callers (grep), Program.cs host call, RarityLadder.
[x] Read the surrounding section of T5/T7/T8 before quoting.
[~] Tested constraints: grep-verified the callers, the File use and the absence of C# structure-seed readers.
    The catalog hash harness is a build-time test.
[x] No §2 invariant contradicted. Closes invariant 12 (T8) for the seed path.
[x] Corrections propagated: _exemplars recursion is a new finding, recorded here and for world-exemplars.
[x] No population pin. The one pin is the closed role vocabulary, with its reason.
[x] No event-refreshed cache: the catalog is load-time and host-configured.
[x] Order independence is an explicit criterion (4).
[x] No actor magnitude.
[x] SOLID: one reader, one resolver. Bands.cs duplicate retired; no parallel reader.
[x] New rule "Core never reads a file on the seed path" owes an enforcement-registry row (§11).
[x] Round 5 (2026-09-20): B1 — requiredSlotKinds validated at parse beside requiredSlotKind.
```
