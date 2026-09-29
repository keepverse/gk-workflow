# S5 — Combat-AI prior art (shipped games, GDC / Game AI Pro)

Research date 2026-09-20. Every bullet carries a source URL. **[unverified]** = only a search-engine summary, a forum post, or my own recollection backed it; I could not open a primary page. Several wikis (Fandom, the LoL wiki, Nexters support) blocked direct fetches, so their numbers come from search-result excerpts. Those are marked **[snippet]**.
Primary texts that I read in full: Dill, *Dual-Utility Reasoning* (Game AI Pro 2, ch. 3), Lewis, *Choosing Effective Utility-Based Considerations* (Game AI Pro 3, ch. 13, the Guild Wars 2: Heart of Thorns AI) and the Mark & Dill GDC 2010 slides.

## Summary (the 6 most decision-relevant findings)

1. **Auto-battlers trigger casts from a resource that fills on attacks, not from timers.** TFT gives 5/7/10 mana per attack by role plus a damage-taken term. Dota Auto Chess casts at 100 mana, and a normal unit gains at most 10 per attack, which means about 10 attacks per cast. Idle Heroes gives 50 energy per basic attack against a 100 cap. Hero Wars and AFK Arena use 1000 energy. The owner's "cast every N basic attacks" rule is this same shape with integer counters, so it is cheap and deterministic.
2. **After a cast, a lock and an overflow rule are standard.** TFT does not gain mana for 1 s after a cast, and since Set 12 excess mana carries over up to one cast (the old reset-to-0 wasted it). Idle Heroes turns energy above 100 into bonus skill damage at 1:1. A counter trigger needs an explicit carry-over or overflow policy.
3. **Player-configurable AI converges on one shape: an ordered list of (target selector, condition, action) rows, evaluated top-down on each decision tick, with the first match winning.** FF12 has 2 to 12 gambit slots and re-evaluates from the top every turn. Dragon Age: Origins starts with 2 tactics slots and adds 1 at levels 3, 6, 10, 15, 20, 25 and 30, plus the Combat Tactics skill. Pillars of Eternity 2 differs: it picks each instruction by **weighted random over priority**. The existing stub AI ("first usable action in a static preference order") is already the gambit core. Profiles only need to supply the list.
4. **Utility AI in shipped games is a data-driven list of scored decisions ("DSEs") shared across archetypes.** Guild Wars 2: Heart of Thorns normalises each consideration to 0..1, passes it through a response curve, multiplies the results, and **stops early at the first 0**, with cheap checks ordered first. It uses runtime (`y=1-x^6`) and cooldown (`y=x^5`) curves against repetition and a commitment bonus against oscillation. Designers built more than 100 reusable behaviour patterns and assembled an NPC's AI in about 7 minutes. This is the "shared core + data profile" architecture in production.
5. **Dual utility (rank, then weight) gives designer-controlled tiers plus bounded randomness.** Pick the highest *rank* tier, drop options below a percentage of the best weight, then take a weighted random among the rest. Zoo Tycoon 2 used ranks 0, about 5, 98–102 and 1,000,000 (death). The same algorithm fits all four modes. Only deterministic modes need the RNG seeded.
6. **Scale comes from budgeting and LOD, not from a smarter per-agent brain.** AC Unity capped **40 real AIs** out of a 10,000-NPC crowd. Doom 2016 limits simultaneous attackers with **attack tokens**. Planetary Annihilation's sim runs at 10 ticks/s. Age of Empires kept 1,500 units in deterministic lockstep with 200 ms command turns. Unreal behaviour trees are event-driven rather than re-evaluated every frame. For about 300 zombies and N actors, the decision should run only for RPG actors, only when a trigger fires, and against a per-frame cast budget.

---

## 1. Player-configurable / profiled party AI

**FF12 Gambits**
- Each character starts with **2 gambit slots**. Licenses add +1 each, **up to 10 more, for 12 in total**. [snippet] https://gamefaqs.gamespot.com/ps2/459841-final-fantasy-xii/faqs/79737/appendix-g-gambits-and-quickenings · https://ff12sector.com/ff12_gambit_license_guide.php
- A gambit is a **target (Ally/Foe/Self) plus a condition** (for example "Ally: HP < 70%" or "Foe: nearest") **plus an action**. It is an if/then. The list is **re-evaluated from the top each time the character gets a new turn**, and the first gambit that is satisfiable fires. [snippet] https://billpringle.com/games/ffxii_gambits.html · https://jegged.com/Games/Final-Fantasy-XII/Gambits/
- The selector and the condition are one merged token. There is no AND between two conditions, so complex logic needs stacked rows. [unverified, from genre knowledge. The fused "target+condition" token is visible in the list above.]
- Design intent (Hiroaki Kato): combat had to "progress seamlessly in real time", and controlling everything by hand "might be too fast-paced", so they adopted gambits. It grew out of FF4's hidden monster AI scripts. https://blog.playstation.com/2017/07/07/extended-play-how-final-fantasy-xiis-gambit-created-one-of-the-most-distinct-rpgs-ever/
- The best-known criticism is that **"the game plays itself"**. Defenders call it "a puzzle game disguised as combat". https://icicledisaster.com/final-fantasy-xii-review/ · https://www.resetera.com/threads/i-really-dont-get-why-the-gambit-system-of-final-fantasy-xii-was-so-reviled-considering-how-it-pretty-much-solved-the-drawbacks-of-partner-ais.152253/
- Slots and gambit conditions are **progression rewards** (bought or found). The AI's expressiveness is itself something the player unlocks. https://www.thegamer.com/final-fantasy-12-complete-guide-gambits/

**Dragon Age: Origins tactics**
- Characters start with **2 tactics slots at level 1 and gain 1 at levels 3, 6, 10, 15, 20, 25 and 30**. The Combat Tactics skill adds more. Mods reach 25–40 slots. [snippet] https://dragonage.fandom.com/wiki/Tactics_(Origins) · https://dragonage.fandom.com/wiki/Combat_Tactics · https://www.nexusmods.com/dragonage/mods/5357
- **Dragon Age: Inquisition cut the system** down to per-ability preferred/disabled flags plus a **mana/stamina reserve threshold**: below the threshold the companion won't use an ability. Players complained, and the cut is linked to the 8-ability bar. https://screenrant.com/set-behaviors-tactics-dragon-age-inquisition/ · https://www.gamepressure.com/dragonageiii/the-battlefield/z36c6d · https://gamefaqs.gamespot.com/boards/718650-dragon-age-inquisition/79546584
- Veilguard removed direct companion control altogether. https://www.techradar.com/gaming/consoles-pc/dragon-age-the-veilguard-has-removed-the-tactical-camera-and-wont-let-you-control-your-companions

**Pillars of Eternity 2: Deadfire AI behaviours**
- Each script row is a **Conditional + Action + Target type + Target priority** (the rule for choosing among valid targets). https://www.gamepressure.com/pillars-of-eternity-2/partys-ai/z1ae65 · https://steamcommunity.com/sharedfiles/filedetails/?id=1392162466
- Instructions are **picked by weighted random using their priority**, so a higher priority is picked more often. This is non-deterministic, unlike FF12's strict top-down order. [snippet from the official wiki] https://pillarsofeternity.fandom.com/wiki/AI_behaviors
- Scripts are saved as files (`Saved Games\Pillars of Eternity II\CustomAIBehaviors\`) and shared. Mods add conditions, which shows the shipped condition vocabulary felt too small. https://www.nexusmods.com/pillarsofeternity2/mods/88 · https://www.nexusmods.com/pillarsofeternity2/mods/426

**Pathfinder: Wrath of the Righteous (a counter-example)**
- There is effectively no companion caster AI. Casters use cantrips until you give an explicit spell order, then return to cantrips. The reason given is that per-rest spells "can't be spammed". Players still report "suicidal" actions with AI off. [forum, unverified] https://steamcommunity.com/app/1184370/discussions/0/3044985412466352795/

**The Division (profiles on top of a shared behaviour tree)**
- 36 enemy types across 5 factions share **9 core archetypes** (Assault, Rusher, Tank, Sniper, Thrower, Support, Heavy, Leader, Controller). An **AI profile** adjusts 8 attributes: reaction time, movement speed, group behaviour, cover use, **skill usage**, stagger resistance, health and accuracy. https://www.gamedeveloper.com/design/enemy-ai-design-in-tom-clancy-s-the-division · https://media.gdcvault.com/gdc2016/Presentations/Dunstan_Philip_BlendingAutonomyAnd.pdf

## 2. Auto-cast skill triggers (auto-battlers, idle, TD)

**Teamfight Tactics** [snippet. The LoL wiki blocked the fetch.]
- Mana per attack depends on role: **10 for Assassin/Marksman/Fighter, 7 for Caster, 5 for Tank** (current role system. Older sets gave a flat 10.)
- Damage taken gives **1% of pre-mitigation plus 7% of post-mitigation** damage as mana. Tanks get 1% plus 3%, **capped at 42.5 per instance**.
  https://wiki.leagueoflegends.com/en-us/TFT:Mana · https://leagueoflegends.fandom.com/wiki/Mana_(Teamfight_Tactics)
- **Mana lock**: a champion gains no mana for about 1 s after casting, and some champions are locked longer. https://wiki.leagueoflegends.com/en-us/Template:Tip_data/Tft_mana-lock · https://tftraits.com/cast-timelines/
- **Overflow** (Set 12 onward): excess mana carries over up to one cast, for example 50/60 + 20 gives 10/60 after the cast. Before Set 12 the reset to 0 wasted it, which made extra mana "actively detrimental". https://x.com/tftguidesgg/status/1813204106170736792 · https://steffnstuff.com/posts/shallow-dip-tft-bis-qol/

**Dota Auto Chess** [snippet]
- A unit **tries to cast at 100 mana**.
- Attack mana for Shaman/Warlock/Mage/Priest is damage dealt ÷ 2.5, capped at 20. For every other unit it is **capped at 10**, so a normal unit needs **about 10 attacks per cast**.
- Damage taken gives damage ÷ 5 as mana, capped at 50.
  https://dotaautochess.fandom.com/wiki/Mana

**Hero Wars** [snippet]
- The ultimate costs **1000 energy**. Titans also need 1000. Totems need 3000.
- Energy gains are fractions of the bar:
  - each basic attack or skill use: **+10%**
  - each 1% of max HP lost: **+1%**
  - a kill: **+30% bonus**, so 40% total on the killing hit
  - a **dodge** grants the energy the hit would have given
  https://support-hwa.nexters.com/hc/en-us/articles/12581439931666-Energy-Generation-in-Combat · https://hero-wars.fandom.com/wiki/Energy · https://www.herowarscentral.com/hero-energy

**AFK Arena** [snippet]
- The ultimate is ready at **1000 energy** and fires automatically in Auto mode.
- Energy comes from attacking (a fixed amount per hit, "regardless of damage"), from taking damage, and **+200 per kill**. I could not verify the exact per-hit number.
  https://afk-arena.fandom.com/wiki/Energy · https://afk.guide/game-mechanics/

**Idle Heroes** [snippet]
- Heroes **start at 50 energy** and the active skill fires at 100.
- A **basic attack gives +50**, so the active skill comes every 2 attacks.
- Being hit gives +10, or +20 on a crit.
- **Energy above 100 turns into +1% skill damage per point**, a spend-overflow rule.
  https://idle-agents.fandom.com/wiki/Agents:_Descriptions. [unverified. The snippet came from a page about another game and quotes the Idle Heroes rules.]

**Vampire Survivors (pure cooldown auto-fire)**
- Every weapon fires on its own cooldown with no decision layer.
- Empty Tome gives **−8% cooldown per level, −40% at max** (about 1.67× fire rate). Cooldown reduction stacks additively, with a **hard cap of −90%** (10× rate).
  https://vampire.survivors.wiki/w/Cooldown · https://vampire.survivors.wiki/w/Empty_Tome · https://rogueranker.com/empty-tome-vampire-survivors/

**Kingdom Rush heroes (the closest analogue to lawn TD)**
- Heroes **cast active abilities automatically** and "spam them as much as they can" as soon as the cooldown is up. The player's job is **positioning**, according to the developer.
- If an ability is interrupted while it is being performed, it still goes on cooldown.
  https://steamcommunity.com/app/246420/discussions/0/630802343953076323 · https://kingdomrushtd.fandom.com/wiki/Hero_Spell

**Legends of Idleon**
- Attack talents on the skill bar are auto-used when Auto is on or while the player is away.
- AFK gains count only active attack talents, damage and speed. Mana-triggered talents and cooldown reduction are **not** counted. This suggests offline kills are computed from a model rather than simulated per cast. [forum/guide, unverified]
  https://www.slythergames.com/2021/05/13/legends-of-idleon-how-to-use-skills/ · https://steamcommunity.com/app/1476970/discussions/0/3073118388432603978/

**Dota 2 bot API (utility inside a shipped game)**
- Each bot mode returns a **desire from 0 to 1** from `GetDesire()`, and the highest desire becomes the active mode.
- `AbilityUsageThink` and `ItemUsageThink` run **every frame, whatever the mode**, so ability use is a separate layer from movement and mode choice.
  https://pastebin.com/R0ra6Xwi (mirror of developer.valvesoftware.com/wiki/Dota_Bot_Scripting)

## 3. Utility AI, behaviour trees and GOAP; shared core + data profiles

**Mark & Dill, GDC 2010, "Improving AI Decision Modeling Through Utility Theory"**
- Pipeline: raw input → **response curve** (linear, quadratic, **logistic** with shift and threshold variants) → normalise to 0..1 → combine → select.
- There are three selection rules: **highest score, weighted random over all, or weighted random over the top n**.
- Named considerations: tuning (a constant from data), range, **"inertia consideration adds utility to the current choice so we don't change without a good reason"**, random noise, ammo, and veto (boolean). The recommended combination is **sum of base scores × final multipliers**, where a multiplier of 0 is a veto. Advice: "start as simple as possible, extend only when necessary".
  https://media.gdcvault.com/gdc10/slides/MarkDill_ImprovingAIUtilityTheory.pdf · https://www.gdcvault.com/play/1012410/Improving-AI-Decision-Modeling-Through

**Dill, "Dual-Utility Reasoning" (Game AI Pro 2, ch. 3)**
- **Absolute utility** means taking the max. Its weakness is that it is predictable.
- **Relative utility** means weighted random, `P(o) = U(o)/ΣU`. Its weakness is that it sometimes picks a stupid low-weight option. Squaring weights or screening them out is "a balancing act… hard to maintain".
- Dual utility gives each option a **rank** and a **weight**. The algorithm is:
  1. Drop options with weight ≤ 0 (the veto).
  2. Keep only the highest rank.
  3. Drop options whose weight is below a **configurable percentage of the best weight** (set per decision).
  4. Take a weighted random among what remains.
- In Zoo Tycoon 2, needs ran at **rank 0**, context behaviours (in a tree) at **about 5**, scripted show sequences at **98–102** (driven by a small FSM) and die at **1,000,000**.
  https://www.gameaipro.com/GameAIPro2/GameAIPro2_Chapter03_Dual-Utility_Reasoning.pdf

**Lewis, "Choosing Effective Utility-Based Considerations" (Game AI Pro 3, ch. 13), the Guild Wars 2: Heart of Thorns AI built on Dave Mark's IAUS**
- It is data-driven. Each archetype or "species" gets a **set of decisions (DSEs)**, all DSEs are scored every think cycle, and the **best-scoring one wins**.
- Scoring: each consideration's raw input is normalised with **bookends** (for example 0–100 m), passed through a response curve and **multiplied** into the total.
- **Any consideration that scores 0 ends scoring for that DSE immediately.** Cheap switches go first and the expensive line-of-sight raycast goes last. Lewis calls this ordering "a large part of what made the HoT AI sufficiently performant".
- Standard curves: **runtime `y = 1 − x^6`** caps how long a decision can repeat back-to-back, and **cooldown `y = x^5`** stays near 0 until the end of the cooldown. They stop "evade forever, can't be hit" loops and flip-flopping between decisions. A danger-map curve is `y = 1 − (x−1)^4`.
- **Skill DSEs are premade consideration sets reused across many skills**, a charge attack for example: busy and rooted switches, a distance curve peaking at medium range, "too many allies already on this target" from the influence map, own health, facing and line of sight. Pathing to every target was **skipped as too expensive**.
- **Oscillation** is a named failure. The listed mitigations are a **commitment bonus** on the last choice, per-decision weights (a score of 3–4 instead of 1) and runtime/cooldown considerations. Lewis warns that these only *move* the oscillation zone. **The real fix is to add a distinguishing consideration**, and failing that, to reshape the curves. Build slider tooling for tuning.
- Scale of reuse: **more than 100 predefined behaviour patterns**, mixed into new creatures "in a handful of minutes" (about 7 minutes per NPC package in the GDC 2015 talk).
  https://www.gameaipro.com/GameAIPro3/GameAIPro3_Chapter13_Choosing_Effective_Utility-Based_Considerations.pdf · https://www.gdcvault.com/play/1021848/Building-a-Better-Centaur-AI · https://www.gamedeveloper.com/programming/learn-to-make-games-smarter-at-the-gdc-2015-ai-summit

**IAUS compensation factor**
- Multiplying many considerations drags scores down: 0.9^9 = 0.387. This unfairly penalises decisions that have more considerations. Mark's **compensation factor** corrects each score for the number of considerations. The formula is not in the sources I could open.
- A commonly quoted form is `mod = 1 − 1/n; makeUp = (1 − s)·mod; s' = s + makeUp·s`. **[unverified]**
  https://zenn.dev/sanmal/articles/9ed9989c11b7eb?locale=en · https://www.gameai.com/iaus.php

**Behaviour trees, utility and GOAP**
- The Game AI Pro overview says behaviour trees balance ease of implementation and visualisation well but are **"poor at modeling analog concepts such as uncertainty over multiple valid options"**, which is where utility fits. https://www.gameaipro.com/GameAIPro/GameAIPro_Chapter04_Behavior_Selection_Algorithms.pdf
- F.E.A.R. used GOAP: an FSM with only **3 states (Goto, Animate, UseSmartObject)** plus an A* planner over actions with a **per-action cost** and procedural preconditions. It is powerful but heavy, and a poor fit for 300 agents. https://www.gamedevs.org/uploads/three-states-plan-ai-of-fear.pdf
- The Division used a behaviour tree with archetype profiles (see §1). https://gdcvault.com/play/1023382/AI-Behavior-Editing-and-Debugging

## 4. Performance patterns for many agents

- **Hard cap on "real" AIs.** AC Unity ran **40 real AIs and 120 high-res models** inside a crowd of about 10,000. NPCs switch between LoRes Bulk (over 40 m away), Autonomous Bulk and Puppet Bulk LODs through pooling. https://gdcvault.com/play/1022411/Massive-Crowd-on-Assassin-s · https://archive.org/details/GDC2015Cournoyer
- **Token or slot budget for expensive actions.** In Doom 2016 each attack type has a limited pool of tokens. A demon requests one, releases it after the attack, and can **steal** one if it has a better chance. Token counts differ per difficulty. Doomworld reports the pool occasionally "breaks", meaning leaks when a token is not released. https://www.gamedeveloper.com/design/cyber-demons-the-ai-of-doom-2016- · https://www.doomworld.com/forum/topic/134214-the-attack-token-system-in-doom-eternal-breaks-occasionally-for-no-reason-at-all/
- **Event-driven rather than polled.** Unreal behaviour trees do not re-run from the root each frame. Decorators observe blackboard keys and abort running branches ("Observer Aborts") only when a value changes. The catch is that preemption happens only where aborts are configured. https://dev.epicgames.com/documentation/en-us/unreal-engine/behavior-tree-in-unreal-engine---overview · https://www.behaviortrees.com/learn/behavior-trees-in-unreal-engine/
- **Reduced think rate.** Planetary Annihilation's sim runs at **10 ticks/s**, and AI search intervals are set in ticks (for example 0.5 s). https://planetaryannihilation.wiki.gg/wiki/Unit_Properties
- **Unreal Mass** LOD processors tick far entities at a lower frequency. https://github.com/Megafunk/MassSample
- **AI LOD as architecture.** Dave Mark's GDC 2013 talk "Architecture Tricks: Managing Behaviors in Time, Space, and Depth". [One search summary attributed LOD numbers to "Rafael Isla"; I could not verify that.] https://www.gdcvault.com/play/1018040/Architecture-Tricks-Managing-Behaviors-in
- **The cheapest scoring is early-out ordering** (HoT, §3). The Heart of Thorns rewrite also "used significantly less processing time" than the earlier AI. https://www.gamedeveloper.com/programming/learn-to-make-games-smarter-at-the-gdc-2015-ai-summit
- **Round-robin time-slicing.** When the frame's AI slice runs out, the remaining agents get their turn next frame. [patent-level source only, unverified as a shipped-game number] https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/8095496
- **Determinism and lockstep.** Age of Empires synchronised **1,500 units, 8 players** by running an identical simulation on every machine from the same commands. Command turns were **about 200 ms**, separate from render frames. https://www.gamedeveloper.com/programming/1500-archers-on-a-28-8-network-programming-in-age-of-empires-and-beyond
- **Floating-point determinism.** It holds with the same binary and instruction set, strict FP (`/fp:strict`), no reordering optimisations and no transcendental functions. It is not reliable across compilers or architectures. Gas Powered Games and Pandemic shipped it that way. https://gafferongames.com/post/floating_point_determinism/
- Taken together: replay goldens need the same binary, a seeded RNG and a fixed evaluation order. Integer counters for triggers avoid the floating-point question entirely.

## 5. Resource-spend policies

- **A reserve threshold is the minimum viable policy.** Dragon Age: Inquisition's behaviour screen sets a mana/stamina threshold below which a companion won't use abilities. https://www.gamepressure.com/dragonageiii/the-battlefield/z36c6d
- **Spend on ready is what TD heroes do.** Kingdom Rush heroes cast as soon as the cooldown is up, and positioning is the player's skill. https://steamcommunity.com/app/246420/discussions/0/630802343953076323
- **Spam and waste is the main complaint about gacha auto modes.** Examples:
  - ultimates used "right away even though they barely have utility" (Honkai: Star Rail)
  - ultimates fired "on cooldown for no reason… no targets in range… as the last unit" (Girls' Frontline 2)
  - shields and buffs cast one turn before the fight ends
  Players treat auto mode as a farming tool, not as a pilot for hard content.
  https://www.digitaltrends.com/gaming/honkai-star-rail-auto-battle/ · https://steamcommunity.com/app/3308670/discussions/0/595145072449741254 · https://ultimategacha.com/chaos-zero-nightmare-auto-mode-ai-behavior-when-to-use/
- **Hoarding is the opposite failure.** Pathfinder: Wrath of the Righteous companions never spend per-rest spells without an order. [forum] https://steamcommunity.com/app/1184370/discussions/0/3044985412466352795/
- **Overflow policy.** Pre-Set-12 TFT wasted excess mana and players felt it. The fixes shipped so far are carry-over capped at one cast (TFT) and converting overflow to damage (Idle Heroes). A "cast on the Nth attack" counter has the same edge case: what to do when the cast is blocked (no target, silenced). The options are to hold at N or to reset. https://x.com/tftguidesgg/status/1813204106170736792
- **Post-cast lock.** TFT's lock of about 1 s stops mana gained *during* the cast animation from queueing an immediate second cast. https://wiki.leagueoflegends.com/en-us/Template:Tip_data/Tft_mana-lock
- **Cooldown sync.** Units that start a fight together on equal timers or counters cast in the same frame. That creates a CPU and VFX spike and one burst window. The usual fixes are a random or stagger initial offset (a seeded one in deterministic modes) and a cast-token budget per frame. [engineering practice, unverified as a documented shipped incident. Doom tokens are the closest documented relative.]
- **Last-target waste.** An AoE or ultimate fired at a single dying enemy. Common fixes are a minimum-targets or minimum-remaining-HP consideration (as in HoT's "allies already on target" consideration), or "hold if the combat will end". https://ultimategacha.com/chaos-zero-nightmare-auto-mode-ai-behavior-when-to-use/

---

## Failure modes catalogue

| Mechanic | Failure | Fix | Source |
|---|---|---|---|
| Ordered rule list (gambits) | "Game plays itself"; the player is left with no in-fight agency | Treat configuration as the gameplay; keep manual override; gate slots and conditions behind progression | icicledisaster.com FF12 review; ff12sector license guide |
| Ordered rule list | No AND between conditions; logic gets stacked across rows | Allow a compound condition (target selector + 1..k predicates) | [unverified] genre knowledge |
| Tactics cut down to toggles (DA:I) | Players lose control; the AI is "dumb" | Keep at least a reserve threshold and preferred/disabled flags per ability | gamefaqs DA:I; screenrant |
| Weighted-random picking (PoE2, relative utility) | Sometimes picks an absurd low-weight option; non-deterministic | Dual utility: rank tier first, weight cut-off as a % of the best, then random; seed the RNG | Dill GAP2 ch. 3; PoE wiki |
| Absolute max-utility | Predictable; ties oscillate | Commitment/inertia bonus; add a distinguishing consideration; runtime/cooldown curves | Lewis GAP3 ch. 13; Mark & Dill 2010 |
| Utility oscillation | Ping-pong between two close decisions | Commitment bonus only moves the zone; add a consideration, reshape curves, slider tooling | Lewis GAP3 ch. 13 |
| Repeating a valid decision | "Evades constantly, impossible to hit" | Runtime curve `1−x^6` plus cooldown curve `x^5` | Lewis GAP3 ch. 13 |
| Multiplied considerations | Score shrinks with the number of considerations (0.9^9 = 0.39) | Compensation factor, or add base scores and multiply only by vetoes/multipliers | zenn IAUS article; Mark & Dill 2010 |
| Expensive checks | Raycasts and pathing for every candidate | Early-out at 0; cheap checks first; skip pathing | Lewis GAP3 ch. 13 |
| Auto ultimate | Cast on cooldown with no targets, on the last enemy, or buffs right before victory | Minimum-target, remaining-HP and fight-ending considerations | digitaltrends HSR; GFL2 Steam thread; ultimategacha |
| Per-rest resources | AI hoards and never casts | Reserve threshold instead of a ban; spend above the reserve | Pathfinder WotR Steam thread |
| Mana on cast | Overflow wasted (pre-Set-12 TFT) | Carry over up to one cast, or convert overflow to power | tftguidesgg; Idle Heroes snippet |
| Resource gain during the cast | Immediate double cast | Post-cast lock (TFT about 1 s) | LoL wiki mana-lock |
| Everyone acts at once | Burst spike; unreadable chaos | Attack/cast tokens with a per-difficulty pool; steal only when better | Doom 2016 gamedeveloper |
| Token pool | Token not returned, so the pool drains | Release on death, interrupt and timeout | Doomworld thread |
| Per-frame re-evaluation of every agent | CPU cost grows with agent count | Event-driven re-evaluation, lower tick rate, LOD, hard cap on "real" AIs | Unreal BT docs; PA wiki; AC Unity GDC 2015 |
| Floating-point in the sim | Desync and replay drift across builds or CPUs | Same binary + strict FP, or integers; seeded RNG; fixed order | Gaffer on Games; AoE 1500 Archers |

## Implications for a shared core + per-mode profile design

1. **Keep the stub's shape as the core.** An ordered, gated action list with first-match selection *is* FF12/DA:O gambits, and it is the cheapest and most deterministic form. Add utility only as an optional scorer inside a tier, not as the default.
2. **Make the core dual-utility in shape: (rank, weight, veto) per candidate.** A strict ordered list is the special case where every candidate has a distinct rank and the tie-break is "first". A PoE2-style weighted pick is the case of one rank with a seeded RNG. One algorithm covers all four profiles.
3. **Put triggers outside the decision core.** "Cast every N basic attacks" or "every T seconds" is an integer *eligibility gate*, like Idle Heroes' 50 per attack against 100 and Dota Auto Chess's roughly 10 attacks. The core runs only when a gate opens (event-driven), never per zombie per frame.
4. **Specify overflow and lock for the trigger explicitly:** carry-over up to one cast, a post-cast lock, and behaviour when the cast is blocked (hold at N, or reset). Each of these is a tunable per profile.
5. **For the lawn, add a per-frame cast budget.** Use a Doom-style token pool (maximum casts per frame or per window) plus a seeded initial counter offset per actor to break sync spikes. Release tokens on death and interrupt.
6. **Put the reserve threshold in every profile** (the DA:I minimum). The owner's "dumb AI spends while available" is `reserve = 0`. Battle and dungeon profiles can raise it or add "save for ultimate".
7. **Include waste considerations in the default consideration set:** minimum targets in the AoE, target not about to die, fight not about to end. These are the most-cited complaints about auto modes.
8. **Build anti-repeat into the core, not the profiles:** a commitment bonus for continuous modes and runtime/cooldown gates. Fix oscillation by adding a consideration, not by stacking bonuses.
9. **Order considerations cheap-first and stop at the first 0.** Range and cooldown checks come before any target scan. On the lawn, candidate targets come from a per-frame cache, never from a per-decision scan (this matches the repo's own perf audit finding).
10. **Profiles are data**: a list of decision templates, weights or ranks, curve parameters, reserve, trigger (N attacks or T ms), think rate and budget. HoT (100+ reusable patterns) and The Division (9 archetypes, an 8-attribute profile) show this scales. It maps onto a seed/tuning file rather than code.
11. **Think rate per mode.** Battle and ATB: once per actor turn, which is the FF12 "re-evaluate on new turn" rule. Lawn: on trigger events only. Siege: a lower fixed tick (PA-style 10 Hz) or event-driven. Dungeon: per turn/tick plus an immediate re-evaluation when the player issues an order.
12. **Deterministic modes:** a seeded RNG owned by the battle, a stable candidate order, and integer or strict math for scores that affect choices. Floating-point scores are fine within one binary. Goldens pin behaviour, not cross-platform bits.
13. **Player steering (dungeon) is a rank override.** A player order is a top-rank candidate (Zoo Tycoon's scripted 98–102 tier) that ends on completion or timeout. Autonomous choices resume below it. This avoids a second decision system.
14. **Siege structures and obstacles are extra target selectors and considerations** (reachability as a cheap proxy, like HoT's line of sight instead of pathing), not a separate AI.
15. **Treat "the AI plays itself" as a design choice:** expose slots and conditions as progression (FF12/DA:O) if player-configured AI is wanted later. The core already supports it, because a profile is an ordered list.
