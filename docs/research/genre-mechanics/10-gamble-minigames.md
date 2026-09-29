# Gamble mini-games — research input (not a design)

> **Evidence tier:** second-tier — community wikis, guides and news posts found by web search in one
> automated research run (2026-09-18), not primary data like files 01–09. Two sources (LootCube,
> Monster Sanctuary wiki) were found by search but could not be opened. Repo citations were checked
> against the code on the same day (summoning pity `gk-core/data/tuning/summoning.v1.json`, salvage faucet
> exclusions `SalvagePolicy.cs`, craft pity threshold `CraftPityCounter.cs`).

**Status:** research, 2026-09-18. Input to a later design round. Nothing here is approved, specced, or built.
**Scope rule respected throughout:** every candidate lives in the RPG layer (items, creatures, economy).
No candidate touches the PvZ game itself. All odds/numbers below are described as tunables, never
authored values; any level-derived magnitude would go through the one power ladder
(`docs/architecture/power/ssot-power-scale.md`). Fairness guards are pity/soft caps, never hard
progression ceilings. The word used throughout is **creature** (`demon` is the legacy name).

## Summary

Genre prior art converges on a small set of shapes: a capped side-currency vendor (Kadala, Obols,
Soul Gambler), a level-scaled gold vendor (Diablo 2), a one-click corruption with irreversible
outcomes (Vaal orb), a visible hard/soft pity ladder (Genshin, this repo's own summoner), a
choice-among-gambles with a legal skip (Neow, pick-1-of-3 card rewards), a comeback-ordered shared
draft (TFT carousel), and labelled-outcome hatching with a duplicate sink (Monster Sanctuary eggs).

This repo already owns most of the machinery a gamble needs: a soul ledger with idempotent spend,
a summon roller with visible two-counter pity, a per-item craft pity counter, a three-operation
reroll menu with priced anchoring, an enhance risk ladder with a consumable-based certainty route,
a ten-rung rarity ladder with rung-keyed drop pity, wild-join intake, and a strict-loss salvage
converter. The gaps are all at the surface: there is no mystery-vendor spend, no labelled
creature-egg loop, no packaged choice-among-gambles, and no corruption-style swing outcome.

Ranked best fit first, the candidates are: (1) an oddities purveyor selling mystery items for
souls, (2) labelled stray-egg hatching for creatures, (3) a temper-streak packaged loop over the
existing reroll bench, (4) a corruption altar with bounded (non-destroying) outcomes,
(5) fateful fusion of duplicate specimens, (6) a Neow-style crossroads bargain after expeditions.

## Prior art table

Ten systems. Each row: mechanic, what feels good, what is exploitative or frustrating, source.

| # | System | Mechanic (2–3 sentences) | Feels good because | Exploitative / frustrating because | Source |
|---|---|---|---|---|---|
| 1 | Diablo 2 vendor gambling (Gheed and every town vendor) | Spend gold on an unidentified item of a chosen base type. The item's level derives from character level (roughly level −5 to +4), and quality rolls magic/rare/set/unique with unique chance around 1/2000. Gold-find gear and the gold cap shape the whole loop. | Base-type targeting gives agency inside the randomness; odds scale with your level so gambling stays relevant; gold has a real job. | A 1/2000 chase is a spreadsheet grind; the gold cap forces mule juggling; optimal play is a level-clamped gold-find build, not playing the game. | https://www.wowhead.com/diablo-2/guide/diablo-2-gambling-gold-finding-explained and https://lootcube.net/en/gambling |
| 2 | Diablo 3 Kadala (blood shards) | Rift guardians and caches pay blood shards, a capped side currency, spent at Kadala for slot-targeted mystery items (25 armor / 50 ring / 75 weapon / 100 amulet) with a flat 10% legendary chance and smart loot to your class. Shard capacity grows with solo Greater Rift clears, forcing frequent spends. | The cap converts hoarding into regular small excitements; slot targeting plus smart loot keeps misses usable; season-start level-1 gambling is beloved tech. | Weapons and amulets are priced as traps versus cube-upgrading rares; there is no agency over *which* legendary; the 10% is fully opaque in-game. | https://maxroll.gg/d3/resources/using-kadala-efficiently and https://diablo.fandom.com/wiki/Kadala |
| 3 | Diablo 4 Purveyor of Curiosities (murmuring obols) | Open-world events pay murmuring obols, an account-wide capped currency, spent per equipment slot for random-rarity gear, plus whispering keys. Obols fall out of normal play with no separate grind. | Zero-friction: the gamble rides along on play you already do; account-wide stock respects alts. | The cap reads as punitive (long-running player debate); most pulls are salvage, so the loop feels like a salvage vending machine. | https://www.charlieintel.com/diablo/diablo-4-players-divided-over-dumb-murmuring-obols-cap-329604/ |
| 4 | Path of Exile Vaal orb corruption | One click corrupts an item permanently with (on gear) four equally likely outcomes: nothing, white sockets, a new corrupted implicit, or a full reroll/brick of values. Irreversible; the item can never be crafted further. | Best story generator in ARPGs: the same click produces trophies and tragedies; the base is deterministic crafting and the orb is one bounded wild swing. | New players learn the lesson by destroying gear they cannot replace; the optimal strategy (only corrupt duplicates or finished items) is tribal knowledge. | https://timesaver.gg/blog/poe2-vaal-orb-guide and https://www.mmoexp.com/News/path-of-exile-2-vaal-orb-complete-guide-high-risk-high-reward-corruption-mechanics-explained.html |
| 5 | Last Epoch gold gambler vs soul gambler | Artem the gold gambler sells base items that roll affixes after purchase; no sets/uniques, stock refreshes for gold, item level stops scaling past 40. The endgame soul gambler inside the Soulfire Bastion takes dungeon souls, can pay uniques/sets and sealed affixes, and its stock quality scales with dungeon modifiers. | Two-tier honesty: the cheap vendor is openly a levelling tool and the expensive one is openly the endgame chase; dungeon modifiers visibly improve the stock. | The gold gambler is designed into worthlessness at endgame, which reads as dead content; the soul gambler is key-gated so dry streaks on keys feel doubly bad. | https://www.icy-veins.com/last-epoch/vendor-gambling and https://lastepoch.fandom.com/wiki/Gambling |
| 6 | Genshin Impact wish pity | 0.6% base 5-star rate, soft pity from pull 74 (+6% per pull), hard guarantee at 90; a lost 50/50 guarantees the featured unit next time, and pity plus guarantee carry across same-type banners. | The worst case is bounded and published; carry-over means no pull is ever wasted even across banners. | Monetised sunk-cost engineering: pity counting keeps paying players paying; the weapon banner runs worse terms; the guarantee *is* the spending incentive. | https://gachapity.com/guides/guide-genshin-pity/ |
| 7 | Slay the Spire Neow + card rewards | Each run opens with a choice of blessings scaled to last run's success, including risk/reward pairs (take a curse, gain a rare relic; swap your starter relic for a boss relic). Card rewards are pick-1-of-3-or-skip with a hidden pity offset that drifts from −5% toward +40% rare chance until a rare appears. | A choice among gambles plus a always-legal skip; failure still earns a consolation; the pity offset is invisible yet precisely felt over many runs. | The boss-relic swap can end a run on screen one; hidden pity cannot be planned around, only trusted. | https://slay-the-spire.fandom.com/wiki/Neow and https://slay-the-spire.fandom.com/wiki/Card_Rewards |
| 8 | TFT carousel (shared draft) | At fixed intervals all players pick one champion-plus-item bundle from a shared ring, with pick order worst-health-first as a comeback mechanic; carousel composition odds are published per set. | Deterministic catch-up: losing buys first pick; the shared pool makes denial picks a skill; everyone sees the same odds. | Contested picks feel stolen rather than earned; the single-player adaptation loses the denial dimension entirely. | https://leagueoflegends.fandom.com/wiki/Carousel_(Teamfight_Tactics) |
| 9 | Monster Sanctuary eggs | Eggs are species-labelled drops from battles and reward boxes; hatching yields that species at a level scaled to the player's team, and duplicates are donated to the monster army for progress. | Suspense without a species lottery: the label removes the worst scam shape, and duplicates have a real sink so no hatch is dead. | Hatching wide dilutes team levelling; egg storage versus hatching-now is fiddly inventory play. | https://monster-sanctuary.fandom.com/wiki/Monster_Eggs |
| 10 | Hades Charon shop + boons | Run-only gold that does not persist is spent at Charon shops on boons, healing, and rerolls of door previews; boons last the run. Unspent gold evaporates, so every shop is spend-or-lose. | Spend-or-lose forces real triage every shop; door previews plus purchasable rerolls give agency over RNG without removing it. | A shop can whiff the build you were offered three rooms ago; reroll spending can feel like paying for the game's randomness. | https://hades.fandom.com/wiki/Boons and https://rogueranker.com/charon-hades-2/ |

## Existing mechanisms

One line each, with the path that proves it.

- Summoning altar spends souls for creature pulls with **visible** pity: heirloom-rung hard pity at 25, sunwoven-rung soft ramp from 41 with hard pity at 55, and a 10-pull cultivated-or-better floor — `docs/guide/mechanisms/summoning-altar.md`, `gk-core/src/FusionRpg.Core/Creatures/SummonRoller.cs`, `gk-core/data/tuning/summoning.v1.json`.
- Craft pity is a per-(instance, affix-group) counter that **places** the container's max tier at threshold without shifting any weight — `gk-core/src/FusionRpg.Core/Items/Mutation/CraftPityCounter.cs`.
- The reroll bench offers Temper (value), Reforge (identity/tier/value with priced 2^K anchoring over prefix/suffix budgets), and Imprint (deterministic floor), blind by default with escalation capped — `docs/architecture/item/ssot-reroll.md`, `gk-core/src/FusionRpg.Core/Items/Mutation/RerollPolicy.cs`.
- Enhancement runs on per-mille success bands with downgrade peril, and boss-farmed assurance consumables can buy certainty up to 100% — `gk-core/src/FusionRpg.Core/Items/Mutation/EnhancePolicy.cs`, `docs/architecture/species-gear-chain/spec-craft-assurance.md`, `docs/architecture/item/spec-enhance-reroll.md`.
- The rarity ladder has ten rungs with count bands and tier windows; drop pity keys on rungs 70 and 90 on counted sources only, with an incidental-drop floor — `docs/architecture/item/ssot-rarity.md`, `docs/architecture/item/spec-rarity-bands.md`.
- Wild joins mint specimens from expedition outcomes with no soul charge — a second, non-gacha creature intake — `docs/guide/mechanisms/wild-joins.md`.
- Salvage is a strict-loss converter: shards return one rung below the item, and `catalyst.forge` / `catalyst.flux` have no salvage faucet at all — `gk-core/src/FusionRpg.Core/Items/Materials/SalvagePolicy.cs`.
- The material vocabulary is a closed five-class, 27-id set (souls, shard, substrate, essence, catalyst) with a fixed spend order — `gk-core/src/FusionRpg.Core/Items/Materials/MaterialCatalog.cs`.
- Drop tables carry a boss channel as an authoring fact, already used to gate assurance-consumable sourcing — `gk-core/src/FusionRpg.Core/Items/Drops/DropTableModel.cs`.
- The soul ledger is append-only with idempotent per-correlation spends and a faucet/sink table (summon, fusion, contracts, upkeep) — `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Souls.cs`, `docs/architecture/creatures/spec-soul-economy.md`.
- Economy-wide rules: every faucet names its sink, holdings-scaled income needs holdings-scaled upkeep, every stock needs two competing sinks — `docs/architecture/economy-principles.md`, `docs/architecture/empire-economy-ssot.md`.

## Candidates (ranked by fit)

### 1. Oddities purveyor (mystery-item vendor) — item gamble

The loop: a control-room vendor sells unidentified items by slot (helm, nozzle, torso…).
The player pays souls plus one `shard.{rung}` of the target band, picks a slot, and receives a
freshly generated item of that slot at the paid band — Kadala's slot targeting with Diablo 2's
visible level-scaling honesty. Generation reuses the existing drop draw against the item's own
container pool and tier window, so a vended item is provably an item the generator could have
dropped. The fairness guard is a counted-source pity on rungs 70 and 90 mirroring the drop-pity
shape, with posted per-slot odds and a pity meter on the vendor panel. Reuse:
`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Souls.cs` (spend),
`docs/architecture/item/ssot-rarity.md` (bands, windows, pity keying),
`docs/architecture/creatures/spec-soul-economy.md` (soul faucet/sink balance). Genuinely new:
the vendor surface and its stock/refresh cadence. Main risk: a cheap vendor converts drops from
events into errands — pricing must keep *found beats bought* true, which is a tuning pass, not
a mechanism.

### 2. Stray-egg hatching (labelled creature eggs) — creature gamble

The loop: expeditions and boss tables occasionally yield a species-labelled egg; the player pays
`essence.{element}` plus souls to hatch it into a specimen of that species at roster-scaled level
with a trait roll. No species lottery — the Monster Sanctuary lesson — the gamble is rarity band,
traits, and variant. Generation reuses the summon roller's band fallback, shared trait roll, and
the visible heirloom/sunwoven pity counters. The fairness guard is the same visible pity plus a
label guarantee (the egg says what hatches), and duplicates feed the existing fusion-material
expectation rather than a release valve. Reuse: `gk-core/src/FusionRpg.Core/Creatures/SummonRoller.cs`,
`gk-core/data/tuning/summoning.v1.json`, `docs/guide/mechanisms/wild-joins.md` (intake precedent).
Genuinely new: egg inventory state and hatch timing. Main risk: a third creature intake next to
altar pulls and wild joins splits the collection arc three ways and needs its faucet priced
against both.

### 3. Temper streak (packaged reroll loop) — item gamble

The loop: the workbench offers a streak mode over the existing Temper operation — commit to up to
N blind tempers on one affix at a bundled shard price, watch the values walk, stop any time and
keep the last result. It is a presentation loop, not a new operation: every step is a Temper
priced and logged as today, and the streak guarantee is the existing per-group craft pity
counter with its threshold exposed as a visible meter. The fairness guard is that counter plus
the Imprint floor as the deterministic escape. Reuse:
`gk-core/src/FusionRpg.Core/Items/Mutation/RerollPolicy.cs`,
`gk-core/src/FusionRpg.Core/Items/Mutation/CraftPityCounter.cs`,
`docs/architecture/item/ssot-reroll.md`. Genuinely new: almost nothing — a workbench mode and a
meter. Main risk: the thinnest novelty of the set; if the bench already shows pity, this may be
pure UX and should be built as UX, not as a system.

### 4. Corruption altar (bounded Vaal-style swing) — item gamble

The loop: spend `catalyst.flux` plus souls to corrupt an owned item in one irreversible click
with a posted outcome distribution — nothing happens, the affix values re-roll within their
window, or one affix tier-steps up with another stepping down. The post-operation invariant from
the reroll lane holds: the result always validates as an item the generator could have dropped.
The fairness guard is structural: **no destroy outcome** (the worst case is a worse roll, per the
reroll lane's own failure-mode analysis), posted distribution, and corruption refused on items
above a tunable enhance level so trophies cannot be accidentally staked. Reuse:
`gk-core/src/FusionRpg.Core/Items/Mutation/RerollPolicy.cs` (post-op invariant),
`gk-core/src/FusionRpg.Core/Items/Materials/MaterialCatalog.cs` (flux as the priced verb),
`docs/architecture/item/ssot-reroll.md`. Genuinely new: the outcome table and its tuning.
Main risk: without a brick outcome the Vaal thrill is muted — and adding one collides with the
repo's repair-is-the-only-destroy-path rule, so this needs an explicit owner ruling (see open
question 1).

### 5. Fateful fusion (duplicate specimens in, rung-weighted specimen out) — creature gamble

The loop: fuse two or three reserve specimens of the same rung for a single specimen at the same
rung or higher, with posted rung odds and a floor at the higher input rung — the dupe sink the
summon spec already anticipates ("reserved creatures become fusion material"). It reuses the
rarity ladder, the rung migration map, and rarity-scaled trait slots. The fairness guard is the
floor plus visible odds; pity could key on the sunwoven counter family. Reuse:
`gk-core/src/FusionRpg.Core/Creatures/SummonRoller.cs`,
`docs/architecture/item/ssot-rarity.md` (ladder semantics shared with creatures),
`docs/architecture/creatures/spec-creature-summoning.md` (dupe-valve intent). Genuinely new:
the fusion outcome table. Main risk: scope overlap — fusion is its own module's territory, and
this reads as a fusion feature wearing a gamble hat.

### 6. Crossroads bargain (post-expedition choice among wagers) — item or creature gamble

The loop: when an expedition returns, the player may stake part of the haul for a choice of
three wagers in the Neow shape — a safe take, a pick-1-of-3 mystery, and a risk/reward pair with
a written downside (fewer materials now for a rung-boosted pull). Skip is always legal and keeps
the haul. The fairness guard is the always-present safe option plus a hidden rare-offset pity in
the card-reward shape. Reuse: `docs/guide/mechanisms/wild-joins.md` (outcome intake),
`gk-core/src/FusionRpg.Core/Items/Materials/SalvagePolicy.cs` (staked materials stay strict-loss).
Genuinely new: the choice surface and the offset counter. Main risk: the most new surface for
the least reuse, and the shared-draft/catch-up dynamics that make the genre versions sing have
no single-player analogue here.

## Open questions

1. May any gamble destroy or permanently brick an item or creature, or does worst-outcome-equals-worse-roll stand everywhere (repair stays the only destroy path)?
2. Should the item vendor take souls alone, or a souls-plus-`shard.{rung}` bottleneck pair so two stocks bind on every pull?
3. Should creature eggs be species-labelled (no species lottery) or true mystery eggs (species is part of the gamble)?
4. May gambles run while a lawn session is live, or are they control-room-only like the reroll bench's match lock?
5. One shared pity counter across all gambles, or a separate visible counter per gamble?
6. May gambles pay out the top rung (almanac), or must the ceiling stay exclusive to deterministic boss/quest sources?

## Sources

- Diablo 2 gambling guide (Wowhead): https://www.wowhead.com/diablo-2/guide/diablo-2-gambling-gold-finding-explained
- Diablo 2 gambling odds/strategy (LootCube): https://lootcube.net/en/gambling
- Diablo 3 Kadala efficient use (Maxroll): https://maxroll.gg/d3/resources/using-kadala-efficiently
- Kadala mechanics and pricing (Diablo Wiki): https://diablo.fandom.com/wiki/Kadala
- Diablo 4 obols cap debate (Charlie Intel): https://www.charlieintel.com/diablo/diablo-4-players-divided-over-dumb-murmuring-obols-cap-329604/
- PoE 2 Vaal orb corruption outcomes (Timesaver): https://timesaver.gg/blog/poe2-vaal-orb-guide
- PoE 2 Vaal orb high-risk guide (MMOExp): https://www.mmoexp.com/News/path-of-exile-2-vaal-orb-complete-guide-high-risk-high-reward-corruption-mechanics-explained.html
- Last Epoch vendor gambling gold vs souls (Icy Veins): https://www.icy-veins.com/last-epoch/vendor-gambling
- Last Epoch gambling rules (Official Wiki): https://lastepoch.fandom.com/wiki/Gambling
- Genshin pity soft/hard and 50/50 (GachaPity): https://gachapity.com/guides/guide-genshin-pity/
- Slay the Spire Neow blessings: https://slay-the-spire.fandom.com/wiki/Neow
- Slay the Spire card-reward pity offset: https://slay-the-spire.fandom.com/wiki/Card_Rewards
- TFT carousel shared draft: https://leagueoflegends.fandom.com/wiki/Carousel_(Teamfight_Tactics)
- Monster Sanctuary eggs: https://monster-sanctuary.fandom.com/wiki/Monster_Eggs
- Hades boons: https://hades.fandom.com/wiki/Boons
- Hades Charon shop: https://rogueranker.com/charon-hades-2/
