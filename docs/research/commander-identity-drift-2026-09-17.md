# Why the commander idea drifted — a closed enum where a population belonged

**Audit 2026-09-17.** Triggered by the owner reading a claim in `empire-progression-ideal.md` and
answering: *"this is a serious defect, we need to fix it. commander is not a enum. it is a unique
creature with named and play a role like another unique actor but it can play commander role in the
legion (the inspire of heroes of might and magic)."*

The owner is right, the drift is real, and it is precisely locatable. **The idea did not drift — the
type did.** Most of the architecture already models a commander the way the owner describes; the enum
is the outlier, not the intent.

This is a diagnosis, not a plan. No build authorized.

---

## 1. What the owner's model is

| Property | Owner's words |
|---|---|
| Identity | *"a unique creature with named"* — an actor, not a constant |
| Role | *"play a role like another unique actor but it can play commander role in the legion"* |
| Inspiration | *"the inspire of heroes of might and magic"* |
| Lawn | deployed to the empire's side, **cannot enter the lawn**, sits outside with aura buff and action skills cast into it |
| Reach | also plays in **siege, world assault, delve** |

So: a commander is a **unique actor wearing a role**, and "commander" is a hat, not a species of thing.

---

## 2. Where the drift happened — one file, one day, and it is dated

`gk-core/src/FusionRpg.Core/Commanders/CommanderId.cs`, written for `aura-skill` T9a on 2026-08-30. Its own
doc comment states the reasoning, verbatim:

> *"Deliberately not player-scoped here. **There are exactly two commanders total** (owner decision,
> 2026-08-30: **"for now only have 2 of them for lawn run"**), not one per player — Dave is the
> player's own commander, Zomboss is the opposing AI's."*

```csharp
public enum CommanderId { Dave, Zomboss }
```

**The owner said a content fact and the code recorded it as a type fact.** *"For now only have 2 of
them for lawn run"* is a statement about **how much content exists today**, scoped to **the lawn**, and
explicitly temporary (*"for now"*). All three qualifiers were dropped when it became an `enum`.

---

## 3. The rule this broke is already written down, and the repo has been burned by it before

`AGENTS.md` and `CLAUDE.md` both carry this table:

| | Closed vocabulary (the code owns it) | Derived population (content grows it) |
|---|---|---|
| Changes when | a developer edits a declaration | a seed row ships |
| Cardinality | **constant — pin it, say why** | **a reading — never pin it** |

**A commander roster is a population.** It grows when content ships — a new named commander is content,
exactly like a new species. "We have two today" is a **reading**, and the rule says never pin a reading.

The repo already learned this in the other direction and wrote the incident down: a test asserting
`len(species) == 904` guards nothing, because the day a 905th species ships the "fix" is to write 905.
`CommanderId` is that same mistake **expressed as a type instead of an assertion**, which is worse:
an assertion fails loudly and gets edited, while an enum silently makes a third commander *unspeakable*
throughout the codebase.

---

## 4. Why nobody caught it — the deferral removed the reviewer

This is the actual mechanism, and it is worth stating because it is repeatable.

**One day earlier**, `decisions.md` (Buff/debuff scope, 2026-08-29) deferred the concept:

> *"Aura skill content, **the commander concept itself (Zomboss/Crazy Dave identity, roster)**, and the
> 'join battle directly' combat-participant case … are **explicitly deferred** — this program builds
> only the scope primitive."*

**The next day**, the aura program needed an addressable key for auras, allocation and resource pools,
and `CommanderId.cs`'s own summary says exactly that narrow job:

> *"an addressable identity for a commander, distinct from every other id shape a `"dave"`/`"zomboss"`
> string already means elsewhere in this codebase."*

It was solving an **id-collision problem** (`WorldFaction.FactionId` is bare `"dave"`;
`BattleActorSetup.Key` is `"squad:N"`), not modelling an actor. And because the concept that *owned*
commanders was deferred, **there was no spec for the enum to be checked against.** The deferral removed
the very document that would have caught it.

> **The pattern to name:** a program that does not own a concept minted that concept's identity type as
> a side effect of needing a key, while the program that did own it was deferred. The placeholder then
> became the definition by default, because nothing outranked it.

---

## 5. The owner's model is already the documented model — in four places

This is the strongest evidence that the idea never drifted. Every one of these predates or ignores the
enum, and every one agrees with the owner:

| Source | What it already says |
|---|---|
| `decisions.md` — Creature progression (2026-09-08) | *"A **Commander** uses the commander progression/allocation source and likewise never falls through to empire species progression."* A progression **source**, i.e. an actor that levels. |
| `decisions.md` — Deployment hierarchy (2026-09-13) | *"A dead **unique/commander**'s assigned rolled gear … moves … into a per-place `rpg_corpse_cache` row."* Commanders are already grouped **with uniques**, carry gear, and can die. |
| `commander-surface-ideal.md` §0 | *"Detail = **same `ActorPanel`**; **role extensions per commander vs creature**."* The surface program already treats commander as an actor **with a role**. |
| `aura-skill-ideal.md` §1 | *"This is the **Heroes-of-Might-and-Magic-III** model the owner named: the commander is **not a unit on the board**, and their stats reach the fight by lifting everything they command."* The HoMM3 framing and "cannot enter the lawn" are already written. |

`AllocationScope` also already carries `Commander` as one of four summed scopes
(`commander → creatureType → aspect → uniqueCreature`, *"commander smallest, unique largest"*), so a
commander's allocation identity is already first-class.

**Nothing in the architecture says a commander is a constant. One type does.**

---

## 6. How much is actually locked — far less than the file count suggests

40 files reference `CommanderId`, which looks fatal. It is not, because **the world/legion layer never
adopted the enum.**

| Layer | Commander identity today | Open or closed |
|---|---|---|
| World map / legion | `WorldCommand.CommanderId` is a **`string`** (`WorldCommand.cs:140`); `RaiseResolver.FoundLegion` stamps it into `WorldEntity.OwnerFactionId`, also a string | **Already open** |
| Persistence | `rpg_player_commander.default_lawn_commander_id` is **`TEXT`** | **Already open** |
| Legion membership | `WorldEntityMember.InstanceId` — *"Roster specimen (`rpg_unique_actors`); null for non-player forces and guards"* | **Already a unique actor** |
| Lawn / aura / allocation | `enum CommanderId`, `ToStableId` switch, `TryParseStableId` two literals, `AllocationScopeKey` two shapes, `PlayerEmpireCommanders.ForPlayer` hardcoded array | **Closed** |

Measured: only **14 enum-typed** parameters, and **45 literal** `CommanderId.Dave` / `.Zomboss`
references (37 Dave, 8 Zomboss). The storage column is already `TEXT` and merely **validated** through
`TryParseStableId` — so the schema does not need to change; the validator does.

**The world layer already models commanders the way the owner wants. The lawn layer does not.** That
split is the whole defect, and it is why the two halves disagree.

---

## 7. What is genuinely missing (a real gap, not a wiring gap)

Sorted with the required words:

- **Built.** Unique actors with specimen progression, gear and death (`rpg_unique_actors`,
  `corpse-cache`). `AllocationScope.Commander` as a summed scope. Legion members that can *be* a roster
  specimen (`WorldEntityMember.InstanceId`). String-keyed commander ownership on the world map. An
  actor sheet designed for role extensions.
- **Wiring gap.** `rpg_player_commander` stores `TEXT` but refuses anything the enum does not name —
  one validator, not a schema change. `PlayerEmpireCommanders.ForPlayer` returns a hardcoded array
  where it could read a roster.
- **Real gap.** `WorldEntityMemberRole` is `{ Fighter, Bearer }` — **there is no `Commander` role**, so
  the owner's *"play commander role in the legion"* has no representation today. And no table makes a
  unique actor *be* a commander; `CommanderId` is the only answer to "who is a commander", which is the
  defect itself.

---

## 8. The one thing a fix must not do

Do **not** add a `commander` member to `RpgActorKinds` (`player`, `plant`, `zombie`, `species`,
`specimen`).

`CommanderIds.AllocationScopeKey` gives Dave the key `player:{playerId}` — byte-identical to the
player's own scope key — and the source says why: *"he IS the player's own commander — no new
convention needed, no data migration for existing saves."* Commander Dave and the player are **one
identity** sharing one progression row. A `commander` actor kind would fork that identity in two and
create exactly the dual-source defect `decisions.md` overturned for `BattleStatComposer`.

A commander is a **role a unique actor holds**, which is also precisely how the owner described it. The
role belongs next to `WorldEntityMemberRole`, not in the actor-kind vocabulary.

Zomboss is the live asymmetry and is already open question Q2/R1 in
`empire-progression-ideal.md`: he has an allocation key (`zomboss:{playerId}`) but **no progression
row**, so "a commander levels" is currently true for Dave only.

---

## 9. Correction to a claim I made in this session

`empire-progression-ideal.md` briefly said *"there is no commander kind and no commander level
anywhere."* The narrow fact (no `commander` in `RpgActorKinds`) is true; **"anywhere" was false** and
would have sent a downstream session looking for a subsystem that is already built. Corrected in commit
`07113c7c`, and the wrong claim was left visible there rather than silently rewritten.
