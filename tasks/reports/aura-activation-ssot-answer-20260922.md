# Answer: do bindings become the SSOT for aura activation? (aura-skill §3.3 / §10.1)

**Date:** 2026-09-22 · **Session:** `arch-d-20260922` · **Mode:** worktree · **Status of this doc:**
**recommendation, not a decision.** The owner asked the question; this doc answers it from code and asks
for confirmation. **Nothing here is implemented, and no todo row is ticked.**

**Question, verbatim from the spec** (`docs/architecture/aura-skill/spec-aura-binding-producer.md:337`):

> **§3.3 — do bindings become the SSOT for activation, or does activation get its own table?**
> Recommended: bindings. Blocks only the seeding line, not BP2.

**The owner's follow-up** (`tasks/backlog-clear-todo.md`, §3.3/§10.1 clearing item): *"did they
contradict? if not why don't we follow the original spec?"*

**Answer.** They did not contradict it, and **the recommendation is still the right call — followed or
not, G2 is still open and §9's criterion 4 is still unmet.** The landed work (BP2/BP3) built the part
the spec explicitly allowed it to build and left the one line the spec reserved for the owner. Follow
the original spec: **bindings become the source of truth for activation.**

---

## 1. What the spec recommends, and why

`spec-aura-binding-producer.md:165-181` (§3.3) recommends that `AuraRuntime` **seed its active set from
the durable bindings on first resolve instead of starting empty** — "two states collapse into one, and
the desync class stops existing rather than being managed". It names one alternative (persist active
ids in their own table, bindings derived) and marks the whole thing ⛔ ask-first "because it changes
`AuraRuntime`'s contract", adding: *"**This decision does not block BP2** — it blocks only the seeding
line."*

The gap it closes is **G2** (`:113-120`): active auras are RAM-only (`AuraRuntimeEndpoints.cs:31`'s
process-local dictionary; no `active_aura` column anywhere in `FusionRpg.Data`), while bindings are
durable rows — so a server restart leaves durable bindings "for auras the runtime no longer believes
are active … a desync with no symptom until someone reads two sources and gets two answers."

Spec §9 criterion 4 states the closure condition plainly (`:293-294`): *"Activation and bindings cannot
disagree after a server restart (G2 closed, **either shape**)."*

## 2. What actually landed (BP2/BP3, 2026-09-20)

Read at `15baa1454`, not from the evidence fragment:

| Fact | Evidence |
|---|---|
| The reconcile exists, is pure, and is **declarative** | `gk-core/src/FusionRpg.Core/Effects/Atoms/AuraBindingPlan.cs:38-76` — `Compute(activeAuraIds, existingBindings)` returns `{ToBind, ToWithdraw}` |
| **The active set is an input, and bindings are the output** | `AuraBindingPlan.cs:34-36` — *"`activeAuraIds` is the runtime's own post-eviction set … this function never re-derives activation, it only reconciles durable rows **to match it**"*; `:70` `toBind = active.Where(id => !byAura.ContainsKey(id))` |
| The producer writes from the runtime's set | `gk-core/src/FusionRpg.Server/AuraBindingProducer.cs:49-65` — `SyncAsync(long, activeAuraIds)` → `AuraBindingPlan.Compute(activeAuraIds, existing)` |
| Both callers pass `runtime.ActiveAuraIds` | `gk-core/src/FusionRpg.Server/AuraRuntimeEndpoints.cs:96` (`/enable`) and `:118` (`/disable`) |
| **No boot caller, and no other caller at all** | `grep -rn "SyncAsync\|AuraBindingProducer" src/` → only those two sites |
| `AuraRuntime` still starts empty and has no seed path | `gk-core/src/FusionRpg.Core/Actions/Aura/AuraRuntime.cs:25-29` — the only constructor builds a fresh empty `AuraActiveSet`; `gk-core/src/FusionRpg.Core/Actions/Aura/AuraActiveSet.cs:17,19-24` — a `List<string>`, no persistence |
| Production constructs it in exactly one place, unseeded | `AuraRuntimeEndpoints.cs:39-42` — `Runtimes.GetOrAdd(playerId, pid => new AuraRuntime(max, isEquipped))` |
| Its own doc comment records the RAM-only design as intentional | `AuraRuntimeEndpoints.cs:12-15` — *"process-local by design (`AuraRuntime`/`AuraActiveSet` hold no persistence themselves … matching this program's own T15 finding, 'active state does not persist (RAM only)')"* |
| No test covers the restart case | `grep -rn restart tests/**/*Aura*` → the only hit is a SQLite autoincrement-id note (`AuraRuntimeEndpointsTests.cs:30`) |

So the landed direction is **runtime set → durable bindings**. That is the reverse of §3.3's
recommendation, and it is **not** §3.3's named alternative either: nothing durable holds the active
ids. The spec's own words for that state are the criterion it sets: *"a third place the same fact
lives"* is the alternative's cost; here the fact lives in **exactly one** place — a process-lifetime
dictionary — which is the G2 desync itself, unchanged.

## 3. So: contradiction, or the permitted half?

**Permitted half.** §3.3's ⛔ line says BP2 "may build the producer against either shape; the reconcile
in §3.2 is identical under both", and the reconcile it points at (`:146-163`) is exactly what landed.
BP1's own record says so (`tasks/backlog-clear-todo.md:36-38`): the §3.3/§10 questions *"stay open and
ask-first, and per the plan's own text they 'block only the seeding line, not BP2.'"*

**Why it was not followed:** nobody answered the ask. The answer is not "the code took a different
path and won" — it is "the code took the path the spec left open, and the one line the spec reserved
was never ruled on". Following the original spec now requires **no rework of BP2/BP3**: the reconcile
is direction-agnostic at its call site, because the active set arrives as a parameter.

## 4. Why bindings-as-SSOT is still the recommendation

1. **It is the only shape that closes G2 without a new table.** §3.5 forbids the producer introducing
   *"No new durable runtime table. E6: ICD clocks, stacks, counters stay in RAM"* (`:205-206`). §3.3's
   alternative **is** a new durable table, so the alternative is in tension with the module's own §3.5
   boundary while the recommendation is not.
2. **The landed code reduces the change to one seeding line.** `AuraBindingPlan.Compute` already takes
   the active set as an argument and both endpoints already read `runtime.ActiveAuraIds`, so seeding at
   construction makes the durable bindings the recovery source with no change to the reconcile, the
   producer, the push, or either endpoint's response shape.
3. **The read the seed needs already exists.** The projection "`aura`-sourced bindings for this player →
   aura ids" is `AuraBindingProducer.SyncAsync:53-63`'s own loop over `store.ListBindings(owner)`
   (`gk-core/src/FusionRpg.Data/Sqlite/RpgStore.AtomInstances.cs:447`), filtered by `Source == "aura"` and
   mapped through `AuraContentCatalog.AuraIdForContainer`. It should be **extracted once and shared**
   with the seed rather than written twice — a second copy of that projection is the kind of parallel
   path §2.15 of `docs/DESIGN-GATE.md` refuses.
4. **The restart symptom is real and unguarded today.** After a restart: `Runtimes` is empty →
   `AuraRuntime.ActiveAuraIds` is `[]` → nothing re-reconciles at boot (no caller) → the durable
   `aura` bindings survive and still resolve through the reader path. `/api/aura-runtime/{id}` would
   report `activeAuraIds: []` while the aura is in fact applied. That is one fact, two answers, and the
   second one is wrong.

## 5. What the recommendation would change, if confirmed

Stated so the owner can size it, not to authorise it:

| Piece | What changes | Layer |
|---|---|---|
| `AuraRuntime` | gains a seed path (a constructor/factory parameter or an explicit `Seed(IEnumerable<string>)`), contract-visible — which is why §3.3 is ask-first | Core |
| `AuraRuntimeEndpoints.ResolveRuntime` | reads the durable `aura` bindings for the player and seeds the runtime on first construction; one read, at the moment the runtime is created | Server |
| The binding→aura-id projection | extracted from `AuraBindingProducer.SyncAsync` and shared, never copied | Server (or `FusionRpg.Data` if the read moves) |
| `AuraBindingPlan` / `SyncAsync` / both endpoint response shapes | **unchanged** | — |
| Tests | a restart-shaped test: durable `aura` binding present, fresh runtime, the aura is active without `/enable`; and the falsifier that an `aura` binding belonging to another player (or of another `source`) does not seed | Server |

**Ownership and status:** this is `aura-skill`'s remaining line, and the row below is filed in its todo.
No task exists for it yet and none should be written until the owner confirms the shape.

## 6. What this doc does not decide

- It does not re-open §3.3 as a question; it answers the owner's actual question ("did they contradict
  and why don't we follow it") and restates the spec's own recommendation as the answer.
- It does not design the seed's error behaviour (e.g. a `source == "aura"` binding whose container is
  no longer authored) — that belongs to the task, and it should mirror `SyncAsync`'s existing
  refusal-not-failure rule (`AuraBindingProducer.cs:41-43`).
- It does not touch §10's second question (`board.start` as a second reconcile trigger), which
  `spec-aura-binding-producer.md:340-343` already answers "not proposed" with its reason on record.

## 7. Open question for the owner

**One:** confirm §3.3's recommendation — **bindings become the SSOT for activation** (the seed), rather
than adding a durable active-aura table. Default if unanswered: keep the recommendation on record and
leave the seeding line unticked; G2 and §9.4 stay open and are named as such in the owning todo.
