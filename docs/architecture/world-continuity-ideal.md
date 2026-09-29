# World continuity — the ideal

> ### ⚠️ Status line vs. what shipped (checked 2026-09-20)
>
> **This document's status line is not current.** It says *"idea phase ... Not a spec. No build
> authorized."* Measured today: [world-continuity-map.md](world-continuity-map.md) reads **"APPROVED
> 2026-09-19"** (owner) — module specs written the same day. **16** module specs are written at
> `docs/architecture/world-continuity/spec-<module-id>.md`. The map's own text still gates the
> *build* ("no build authorized until the plan and task list exist"); no
> `tasks/world-continuity-todo.md` exists in this tree yet.
>
> Read this document for its reasoning and its decisions, never for its status. Verify anything
> load-bearing against the capability map, the module specs, and the code.

**Status:** idea phase, 2026-09-19. Not a spec. No build authorized. **Program id:** `world-continuity`.

**Owner ruling (2026-09-19), which this program exists to carry out:**

> *"Victory doesn't end the world. The world still exists and works normally; it becomes a slow
> development phase. Then the player can advance to a new world with only limited things they can
> carry. The old world still exists and can come back; events still happen in the old world, but it
> goes to hibernate mode, so active worlds have the most active events. Maybe change the old world to
> idle gameplay."*

Follow-up rulings the same day, recorded as decisions in §9: advancing is allowed at any time; old
worlds run on the world-turn clock (hibernating) or the expedition wall clock (idle); **an old world
can fall completely**, with a later mechanism to reclaim it; **wardens return** as the way to protect
an old world; **cross-world trade routes are in v1**; each world carries one difficulty profile; each
world has **many empires**, not one enemy.

**Vocabulary rule (owner, 2026-09-19):** design text for the empire layer uses generic strategy-genre
terms — *empire*, *enemy empires*, *unit*, *legion*, *sector* — and no named characters or IP words.
The shipped enum ids stay as they are.

**Evidence base:** one inventory-and-prior-art agent (2026-09-19) plus the trade-network survey rounds;
load-bearing claims re-read against code.

---

## 1. Which loop this extends

- **Place 5 — World stage** and **Place 4 — World map**: the world you stand on, and the ones you left.
- **Place 2 — Idle expeditions**: an idle old world is idle play on the **existing expedition clock**.
- **Place 3 — Farm, hunt, defend**: an old world is ground you still hold, can lose, and can take back.
- **Place 7 — Quests and events**: old worlds keep a slower story clock.

**No fourth clock.** Hibernating worlds advance on the world-turn clock; idle worlds on the expedition
wall clock. `docs/guide/the-loops.md` gains one row saying so; the count stays three.

## 2. What this is, in the player's language

When you take a world, the war there does not stop — the world settles into a slow development phase.
Whenever you want, you can **advance**: step through to a new world, taking only what your legions
can carry. If you won the old world first, you can carry more.

The worlds you leave keep going. A world you left recently **hibernates**: nothing happens on your
screen, but each End Turn you take elsewhere counts, and when you look back you get a summary of what
changed. A world you turn over to a **warden** — a strong commander and legion stationed to hold it —
becomes **idle** play: it produces on the wall clock like an expedition, and you collect when you
visit.

Old worlds can be lost. Enemy empires keep pressing, and a poorly guarded world can fall entirely.
It is still there afterwards — hostile ground you can come back and reclaim.

Your worlds are also connected: **trade routes can run between worlds**, so a mature old world can
feed the frontier of a new one.

## 3. Principles that constrain every choice below

1. **RPG layer only; one turn engine.** Old worlds reuse the world turn engine's rules; they never get
   a parallel simulation with different rules.
2. **Never step N full worlds per End Turn.** One full `TurnEngine.Step` for the active world; old
   worlds advance **lazily** and **coarsely**, computed when visited or on a bounded budget. Anno 1800
   simulates every session in full and pays for it in late-game CPU; RimWorld players install mods to
   pause settlements they are not viewing.
3. **Leaving must never pay better than staying.** Background yield is strictly below active yield,
   and it must be collected. X4 players stay out of sectors when the out-of-sector sim is kinder.
4. **Determinism.** A coarse step is a pure closed-form function of `(world summary, seed, n)`, the
   same shape the expedition resolver already uses (`gk-core/src/FusionRpg.Core/Expeditions/ExpeditionResolver.cs:61`).
   Replay produces the same result.
5. **No hard ceilings, but bounded catch-up.** The credited catch-up window is a tunable (the existing
   `catch_up_cap` column), a structural bound, stated as such — the Melvor Idle shape (24 h credited).
6. **Loam is never traded or converted, and never crosses worlds.**
7. **Every faucet names its sink; territorial income needs territorial upkeep.** Old worlds keep paying
   upkeep; a warden is a real cost.
8. **The 500-hour test.** *"Any permanent solution to a recurring cost is eventually free"*
   (`empire-economy-ssot.md` §7). Bounded worlds used to dissolve that test; persistent worlds bring it
   back, so this program owes a new cure (§6.6).
9. **A warden must never freeze decay for free.** That is why the owner withdrew the warden on
   2026-09-13 (`docs/architecture/warden-mortality-ideal.md`: freezing `StabilityMilli` *"lets a single specimen
   zero out the chaos-decay side of the loam economy for free"*). The resumed warden lowers loss odds and
   costs upkeep; it never stops decay.
10. **One ActorHub compose; one battle engine.** A warden's strength is read from Hub output; an old
    world's contests use Θ-difference, never a private curve.

## 4. What already exists

### Built

| What | Where |
|---|---|
| A world `state` column (default `'active'`), indexed with `player_id` and `kind` | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.World.cs:32,36,206` |
| `kind` and `parent_world_id`: several worlds per save already coexist (delves are `kind='delve'`) | `RpgStore.World.cs:204-205`; `docs/architecture/decisions.md` — 'World store — delve worlds (2026-09-05)' |
| Unused wall-clock stepping columns: `mode`, `turn_period_seconds`, `catch_up_cap`, `last_advanced_utc` | `RpgStore.World.cs:25-30` |
| Save identity with several empires per save | `docs/architecture/solid-enforcement/spec-save-identity.md:77-100`; `decisions.md:80` |
| Faction kinds for many empires (`Rival`, `Clan`, …); policy lookup is plural-ready | `gk-core/src/FusionRpg.Core/World/FactionKindCatalog.cs:7-18`; `gk-core/src/FusionRpg.Core/World/Ai/FactionPolicies.cs:13-18` |
| Lazy, pure idle resolution | `ExpeditionResolver.cs:61`; `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.Expeditions.cs:73-93` |
| Bounded, single-transaction carriers (legion cargo) | `decisions.md:47` (Scoped inventory hierarchy) |
| Warden resolver (withdrawn mechanic, code still present) | `gk-core/src/FusionRpg.Core/World/Movement/WardenResolver.cs` |

### Wiring gap

| Inert | Where |
|---|---|
| No code ends a world; the only `UPDATE rpg_worlds` is the turn commit | `gk-core/src/FusionRpg.Data/Sqlite/RpgStore.WorldTurns.cs:687` |
| World creation exists only under a test endpoint | `gk-core/src/FusionRpg.Server/WorldEndpoints.cs:600-622` |
| The active world is "first active map by id", not a chosen pointer | `RpgStore.World.cs:415-428` |
| `catch_up_cap` and `turn_period_seconds` are never read | `RpgStore.World.cs:25-30` |

### Real gap

No hibernate or idle state; no coarse step; no carry rule between worlds; no world-surviving ledger
(the Multiverse-scope wonder was deferred for exactly that, `decisions.md:48`); no event budget per
world; no selected-world pointer; no reclaim mechanic.

## 5. Prior art

| Game | What it does | Lesson |
|---|---|---|
| **Anno 1800** ([Anno Union](https://www.anno-union.com/multisession-gameplay-in-anno-1800/)) | Every session simulated in parallel, in full | Late-game CPU grows with session count — do not |
| **Dwarf Fortress** ([reclaim](https://dwarffortresswiki.org/index.php/Reclaim_fortress_mode)) | A retired fort persists, takes part only in coarse world history, and can be unretired or reclaimed | The closest match. Returning to a sacked fort is accepted because the world has a history — it needs a clear "while you were away" report |
| **RimWorld** ([Workshop](https://steamcommunity.com/sharedfiles/filedetails/?id=3526657761)) | Multiple colonies = multiple full maps; players mod in pausing of unviewed settlements | Players ask for inactive worlds to be frozen or simplified |
| **Melvor Idle** ([wiki](https://wiki.melvoridle.com/w/Offline_Progression)) | Offline progress simulated, capped at 24 h | A capped credited window |
| **Against the Storm** ([wiki](https://against-the-storm.fandom.com/wiki/Blightstorm_Cycle)) | The map resets each cycle; the capital persists | The model this ruling moves away from |
| **Stellaris** ([Steam](https://steamcommunity.com/app/281990/discussions/0/357286663680577110/)) | Continue after victory as a sandbox | The post-victory slog; ours avoids it only if the old world stays useful at low attention |

**Rules taken from it:** never full-fidelity background worlds; evaluate lazily in closed form; cap the
credited window; background yield below active; coarse, rate-limited events plus a digest; losses
possible but never a silent surprise.

## 6. The shape

### 6.1 World states

A closed vocabulary on `rpg_worlds.state`:

| State | Entered when | What runs |
|---|---|---|
| `active` | The world the player selected — exactly one per save | The full `TurnEngine.Step` on End Turn; all events |
| `developing` | Victory over the world's dominant enemy empire — **automatic** | The full step still runs; remaining empires keep acting; escalation slows. The player may stay indefinitely, and **Advance** unlocks with the full carry limit |
| `hibernating` | The player advances or switches away | Lazy coarse steps on the world-turn clock; rate-limited events |
| `idle` | The player stations a **warden** there | The idle-yield resolver on the expedition wall clock, capped window; warden-defended |
| `fallen` | Enemy empires take the world's seat | Revisitable as hostile ground; reclaimable (§6.7) |

### 6.2 Advancing

- **Advance is allowed at any time.** Winning first raises the **carry limit**; advancing without a
  win carries less. Both limits are tunables.
- **Carry is cargo.** What crosses rides as legion cargo through the built, bounded, single-transaction
  cargo model — nothing is copied. Loam never crosses. World stocks cross only as cargo (amends
  `empire-resource-ssot.md` §4 rule 5 and base-defense decision 18 — they no longer "die with the map",
  because the map no longer dies; they stay map-scoped and never auto-bank).
- **Wallets and materials keep banking** as they do today.

### 6.3 Clocks and the coarse step

- **Hibernating:** each End Turn in the active world adds one pending turn to every hibernating world;
  no stepping happens then. When the player looks at the world, or on a small background budget, a
  **`CoarseStep(world, pendingTurns)`** runs once, capped by `catch_up_cap`.
- **Idle:** the expedition wall-clock pattern — the world records when it went idle, and the resolver
  pro-rates on collect, within a capped window.
- **What a coarse step computes**, per faction and never per unit: production at a background
  multiplier below 1 into warehouses, upkeep and fading, hostile spread, one Θ-difference contest per
  enemy frontier, and a digest for the turn report and notifications. The hashed world graph is written
  once per visit, not once per pending turn.

### 6.4 Wardens, resumed for old worlds

The warden mechanic was withdrawn from the loam economy because it froze decay for free. It returns
in a different job: **the defender of an old world**.

- A warden is a strong **commander with a legion** stationed on an old world. It is the entry
  condition for `idle`.
- During coarse steps and idle resolution, the warden's strength (read from `ActorHub` output) lowers
  the odds of losing frontier sectors and the seat. It **never freezes decay or production losses**.
- A warden **costs upkeep** every period and ties up the commander and the legion — they are not
  fighting in the active world.
- The withdrawn doc's reconciliation pattern (`WorldCommand`/`WardenResolver`) is reused, per its own
  instruction to re-read it before re-deriving a warden-shaped mechanic.

### 6.5 Losing an old world

Owner ruling: **an old world can fall completely.** Enemy empires keep acting through coarse steps;
without a warden, a world can lose its frontier and then its seat. The digest reports each loss as it
happens, never as a surprise wipe. A fallen world stays on the multiverse map as hostile ground.

### 6.6 A new cure for the 500-hour test

Bounded worlds used to make every permanent structure "safe, lost at map end". Persistent worlds need
a new cure:

1. The background yield multiplier stays below 1 and **decays as more worlds hibernate** — a soft cap,
   tunable.
2. Background yield lands in that world's warehouses and must be **collected** — by visiting, by
   cargo, or by a cross-world trade route (§6.8) — never straight into the wallet.
3. **Old worlds keep enemy pressure and upkeep**, so a permanent structure is never free: holding it
   needs a warden or attention, and neglect can lose it.

### 6.7 Reclaim

A later mechanism, named now so the states support it: a fallen world can be re-entered as a hostile
world and retaken, with its history kept (Dwarf Fortress reclaim). Its design is a follow-up module.

### 6.8 Cross-world trade

Owner ruling: **cross-world trade routes are in v1.** A route may join trade hubs in two worlds the
player holds. It follows trade-network's rules — located goods, throughput, loss, ledger facts — with
one extra leg: the crossing between worlds, priced and bounded like a lane. Owned by trade-network as
sub-program `rift-trade` (trade-network §11), built on this program's world states.

### 6.9 Events

The storylet engine (`npc-story-events`) gets a per-world **event budget keyed by state**: full in
`active`, reduced in `developing`, low and coarse-only in `hibernating`, maintenance-only in `idle`.
Hibernating events resolve inside `CoarseStep` from the same storylet deck — never a second deck.

### 6.10 Difficulty

Each world carries one **difficulty profile id**, recorded beside its per-world ruleset stamp. v1 ships
one default profile.

## 7. Product documents this changes

1. `docs/guide/the-game.md` — the Win/Lose table and the slogan (*"You keep who you are. You lose where
   you were."*), plus *"Ending one world and starting another is the progression loop"*.
2. `docs/guide/mechanisms/new-world-prestige.md` and its content/site copies — becomes *advancing to a
   new world*.
3. `docs/guide/the-loops.md` — one row: old worlds ride the world-turn clock (hibernating) or the
   expedition clock (idle).
4. `docs/architecture/empire-resource-ssot.md` §4 rule 5 — world stocks are map-scoped and never
   auto-bank; they cross only as cargo (new rule 5b).
5. `docs/architecture/empire-economy-ssot.md` §4 and §7 — the three-things list and the 500-hour cure
   (§6.6 here).
6. `docs/architecture/base-defense-ideal.md` decision 18.
7. `docs/architecture/trade-network-ideal.md` §2, §3, §8.6 — goods no longer die at world end.
8. `docs/architecture/world-graph-ideal.md` §1 — victory becomes a state change, in neutral wording.
9. `docs/architecture/npc-story-events-ideal.md` — the story must survive revisitable worlds.
10. `docs/architecture/decisions.md` — a row for world states and the selected-world pointer.
11. One-line mentions in the other guide pages (the-rift, features, chronicle, world-map, and others)
    and their content/site copies.
12. `docs/PRINCIPLES.md` §11.

These are changed when this program's map is approved, in the same change, never piecemeal.

## 8. Tunables

`data/tuning/world-continuity.v1.json` (proposed; the file does not exist yet): carry limit with and
without victory; background yield multiplier and its decay per hibernating world; `catch_up_cap`
(turns) and the idle credited window; warden upkeep and defence weight; event budget per state;
cross-world crossing cost and loss.

## 9. Owner decisions — closed 2026-09-19

| # | Question | Decision |
|---|---|---|
| W1 | What happens at victory? | **The world auto-enters `developing`** and keeps running |
| W2 | When can the player advance? | **At any time**; a smaller carry limit without a win |
| W3 | Which clock drives old worlds? | **Hibernating on the world-turn clock (lazy); idle on the expedition wall clock**, capped |
| W4 | How much can go wrong while away? | **An old world can fall completely**; a reclaim mechanic comes later |
| W5 | How is an old world protected? | **Wardens, resumed** — a commander and legion stationed there, costing upkeep, lowering loss odds, never freezing decay |
| W6 | Cross-world trade in v1? | **Yes** — cross-world routes (trade-network `rift-trade`) |
| W7 | Difficulty | **One difficulty profile per world**, default only in v1 |
| W8 | Enemies | **Many empires per world**; design text says *enemy empires* |

## 10. What this deliberately does not decide

The reclaim mechanic's design; exact multipliers and windows; how the multiverse map is drawn; what the
warden's commander does inside a battle beyond reading Hub output.

## 11. Next step

`/spec world-continuity`. Model-free first: the selected-world pointer and state vocabulary, then the
coarse step, then advance and carry, then wardens, then events and digest. `rift-trade` waits on the
states and on trade-network's `logistics-flow`.
