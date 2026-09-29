# SGC5-F3 — the proposed fix is not achievable in-fence: re-recording would rewrite the corpus

⚠ Location note: the brief says fragments live under `tasks/evidence-fragments/`, outside this lane's
allowed paths (`tasks/species-gear-chain-*`); this file is named to stay inside the fence.

| Criterion | Command | Result |
|---|---|---|
| the failure, reproduced | `dotnet run --project gk-forge/tools/CreatureCorpusDump -- --verify gk-data/packs/fusion/data/seed/creatures/_dump` | `FAILED self-consistency — hash mismatch: manifest declares cc322647cd0118c72d2dc80826cfe7cea7d02077a59aedfb0bb167319d38a10d, files on disk hash to 6181dc2d5393e44653b4e7b688633bc3c79b97928183eee645bce15b31c05e0a` — **EXIT 1** |
| the committed payloads are the bytes the mirror hashes | `DumpWriter.ComputeContentHash` / `preflight._compute_content_hash` | both SHA-256 the same four files in the same order, manifest excluded (`gk-forge/tools/CreatureCorpusDump/DumpWriter.cs:143`, `gk-forge/tools/seedsmith/seedsmith/adapters/creatures/preflight.py:79`) — they agree, so the DATA (the manifest's declared hash) is the stale side |
| the manifest's COUNTS are NOT stale — only its hash is | `gk-data/packs/fusion/data/seed/creatures/_dump/_manifest.json` vs the payload arrays | manifest declares `plantCount 677 zombieCount 227 baselineCount 82 recipeCount 1295`; the payload files hold exactly **677 / 227 / 82 / 1295**. So the manifest was written against a payload of the same shape but different bytes, and only `contentHash` drifted |
| no mode re-renders the manifest from the payloads on disk | `Program.cs` / `DumpWriter.cs` read | `BuildTree(payload, capturedUtc)` is the ONLY manifest producer and it takes a DB payload; `WriteToDisk` writes all five files; `VerifyCommittedTree` only re-hashes and compares. There is no `--rehash`/manifest-only path |
| re-recording from the live DB would CHANGE THE CORPUS | `dotnet run --project gk-forge/tools/CreatureCorpusDump -- <backup copy of dist rpg-hot.sqlite> --check` | `expected hash a71ff42e19f9733f1673c2c46f5555f2bf5769798f4e59ce95d2cff4c65f324d, plant=677 zombie=227 baselines=913 recipes=0` — baselines 82 → **913**, recipes 1295 → **0**. A payload rewrite, not a manifest fix |
| the tool's own author already rules that out | `gk-forge/tools/CreatureCorpusDump/Program.cs` (`--base-stats` comment) | "the four almanac/baseline/recipe payload files are a 2026-08-23 snapshot, and re-emitting them from today's database would be a large, unrelated diff nobody asked for" |
| the seedsmith mirror cannot write it either | `grep -n "write_text\\|_manifest.json" gk-forge/tools/seedsmith/seedsmith/adapters/creatures/preflight.py` | the mirror only READS (`_read_manifest`) and records a preflight report; it has no dump writer, by design ("must agree with the C# implementation") |
| hand-editing the manifest is forbidden | the generated-data rule | `_manifest.json` is `DumpWriter` output; the row itself says "⛔ Never hand-edit `_manifest.json`: it is generated" |

**Exact blocker.** The minimal correct fix is a **manifest-only rehash** — recompute `contentHash` from the
four committed payloads (`6181dc2d…`) and leave the payload bytes untouched. That needs a new mode in
`gk-forge/tools/CreatureCorpusDump/**`, which is **outside this lane's fence** (`gk-forge/tools/seedsmith/**` only, and the
tool is not under `src/`). The alternative the row proposes — re-record from a live DB — is measured above
to rewrite the corpus (baselines 82 → 913, recipes 1295 → 0) and is explicitly unwanted by the tool's own
author. So the row is blocked on either that tool change or an owner decision to re-snapshot the corpus;
the data half cannot be touched from here.

**Second, distinct finding (not named by the row).** There are TWO stalenesses, not one: the manifest is
stale relative to the committed payloads (`cc32…` vs `6181…`), and the committed payloads are stale
relative to the live game (`6181…` vs `a71f…`, with different baseline/recipe populations). The row's
cause describes only the first. The second is the creature-seed program's snapshot question — the dump is
a deliberate 2026-08-23 capture, so re-snapshotting it is an owner/content decision, not a bug fix.
