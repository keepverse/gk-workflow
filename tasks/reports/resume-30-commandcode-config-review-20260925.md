# Resume 30 — `.commandcode` tracked-configuration review

**Lane:** read-only review. **Base:** boundary commit `67f16a23be82ec513ab5a9cb542dadb0ff3f0d16` (adds
only this evidence bundle and this lane's session record). **Product comparison base:** `6d77888cc`.
**Date:** 2026-09-25. **Program:** `multi-agent-runners`.

This lane reviewed three dirty `.commandcode` paths as **tracked configuration for review**, per the
owner's decision. It changed no source path, added no ignore rule, deleted nothing, committed nothing
and merged nothing. The one file it wrote is this report.

## 1. The three source paths, as captured

Source of truth is the evidence bundle, not the main checkout. The MANIFEST's recorded SHA-256 for
each source path and my independent `Get-FileHash` of the bundle copy are **identical**, which proves
the bundle is byte-for-byte the main-checkout file at capture time.

| Source path | SHA-256 (source **and** bundle copy) | Bundle file | Tracked? | Ignored? |
|---|---|---|---|---|
| `.commandcode/settings.json` | `4CB9784F1025E84C8FE9827BA47545A1AD9772EF3D1A8643F3E1EDA654C02FAA` | `settings.json` | **untracked** | **not ignored** |
| `.commandcode/taste/taste/taste.md` | `1DBDCD9A3C9B5111EC5F5C3F01DC64789E81CD5214CE4915E922E610ABC1D14F` | `taste.md` | **TRACKED** | not ignored |
| `.commandcode/taste/workflow/taste.md` | `9F36148D37A22571A353D510106F01E0458694236D1DA132A4D91B785B4CF9EB` | `workflow-taste.md` | **untracked** | **not ignored** |

Two corrections to the MANIFEST's "current checkout state" column, both proved in this worktree:

- The MANIFEST records `taste.md` as **modified**. It is more than that: the file is **already
  tracked** (in the index since `b979e4966`, "add agents stuffs"), so the main-checkout edit is an
  8-line **append to a committed file**, not a new untracked file. It is not orphaned state.
- **No `.commandcode` path is ignored anywhere.** `.gitignore` has no `commandcode` rule at all
  (its assistant-runtime rules cover `.claude/vendor/`, `.claude/settings.local.json`,
  `.claude/worktrees/`, `.kilo/worktrees/`, `.kilo/sessions/`, `.claude/cmdc-agents/agents/`, and the
  two runtime JSONL ledgers — lines 85–91, 169, 173–178). Consequence: the two untracked files are
  **untracked but not ignored**, so they surface in every `git status` as permanent `??` noise. That
  is the real cost of leaving them undecided.

## 2. What the three files actually contain

`.commandcode/settings.json` (11 lines) is a **permission allow-list**, nothing else:

```json
{ "permissions": { "allow": ["Shell(show:*)", "Shell(worktree:*)", "powershell"],
                   "deny": [], "defaultMode": "default" } }
```

Three allow entries, one of them an **unbounded wildcard** (`Shell(show:*)`), against an **empty deny
list**. `defaultMode` is `"default"`, *not* a bypass mode — so the file is not itself a bypass grant.

The two `taste.md` files are **machine-written per-user preference profiles**: a heading plus
confidence-scored bullet lines about how one person likes to work. `taste.md` is 21 lines; the
committed version is 13, and the pending change is a **pure append of 8 lines** (a pure
`@@ -13,0 +14,8 @@` diff — no line edited, none removed). `workflow-taste.md` is 6 lines of the same
shape.

## 3. Repo conventions these files would land in

- **Assistant config is tracked by policy.** `AGENTS.md` lists `AGENTS.md`, `CLAUDE.md`, `.kilo/`,
  `.claude/`, `.cursor/`, `.agents/`, `.mcp.json` as tracked, and requires every committed path there be
  **portable** — `${workspaceFolder}` or repo-relative, never a drive letter.
- **Tracked config is portable and identity-free, not security posture.** The tracked
  `.claude/settings.json` carries only an `attribution` block with `commit`, `pr` and `sessionUrl`
  deliberately blanked — the "no watermarks" rule applied to config. `.cursor/mcp.json` uses
  `${workspaceFolder}`; `.kilo/kilo.json` uses a repo-relative command. **No tracked file in this
  repo carries a tool permission allow-list.** `.commandcode/settings.json` would be the first.
- **The tool's own convention puts machine-local state outside the repo.** `.commandcode/import-report.md`
  records its machine-local state landing at `~/.commandcode/AGENTS.md` and `~/.commandcode/mcp.json`,
  while repo-level `.commandcode/` holds only portable imported artifacts (26 skills/commands/agents).
  `settings.json` is machine-local state by that convention.
- **Durable knowledge does not live in assistant config.** `.claude/README.md:108` states: *"Never let
  a fact exist only inside `.claude/`"* — durable knowledge goes in committed `docs/`, and the skill is
  the procedure that loads it. A `taste.md` is knowledge, and it exists **only** inside
  `.commandcode/`. This is the one place the tracked decision cuts against a written repo rule, and it
  is already the status quo (`taste/taste.md` has been tracked since `b979e4966`).
- **Per-runtime copies are expected to drift** and are edited in the same change
  (`.claude/README.md:106`, `:108`). A second tracked `taste` domain deepens that maintenance surface.

## 4. The decisive mechanical finding: who owns these paths

This is the part that settles the patch, and it is proved, not inferred. Resolving each path through
the repo's own registry (`Resolve-Owner` over the 449 owner boundaries in
`gk-core/scripts/verification-boundaries.v1.json#docs-and-assistant-config`, whose `paths`
array lists `.commandcode/**/*.md`):

```
.commandcode/settings.json                                 => UNMAPPED
.commandcode/taste/taste/taste.md                          => docs-and-assistant-config  (specificity 100020)
.commandcode/taste/workflow/taste.md                       => docs-and-assistant-config  (specificity 100020)
```

And the unmapped result is **deliberate, not an oversight**. The pattern-shape contract in
`scripts/lib/VerificationBoundaries.ps1:54` says `dir/**/*.md` matches "only the Markdown files under
`dir/`" because "assistant-config trees (`.claude/`, `.agents/`, `.commandcode/`) also hold scripts,
which must stay unmapped rather than inherit a docs-only boundary". `.commandcode` is also **not** in
`$Script:EnforcedRoots` (`scripts/lib/VerificationBoundaries.ps1:46` — only `gk-core/data/tuning/**`,
`gk-core/tests/fixtures/**`, `gk-data/packs/fusion/data/generated/**`, `gk-data/packs/fusion/data/seed/**`), so the registry guard would not fail over
an unmapped `.commandcode` file; but `verify-change.ps1 -Paths .commandcode/settings.json` would
report `(unmapped)`, and `AGENTS.md` calls an unmapped production path a verification-boundary
defect.

So the three files are **not one question**. They are two, and the answers differ:

- Both `taste.md` files are **already inside** a verification boundary that owns
  `.commandcode/**/*.md`, whose `verificationId` is `guard.doc-boundary` and whose project is `guard`.
  Tracking them requires **no registry change** and no new guard.
- `settings.json` is **outside every boundary by design**. Tracking it would create a committed,
  permission-bearing file that no boundary can verify.

Gate status for the tracked option, run per-file as `docs/contributing/creative-mode.md:454` requires:
both `taste.md` copies and the committed `taste/taste/taste.md` return **0 HIGH, exit 0**.

## 5. Secrets, machine-local paths, watermarks, permissions

A pattern scan over the three bundle files:

| Check | `settings.json` | `taste.md` | `workflow-taste.md` |
|---|---|---|---|
| Drive-letter paths (`X:\`) | 0 | 0 | 0 |
| `/Users/`, `/home/` paths | 0 | 0 | 0 |
| `~/` paths | 0 | 0 | 0 |
| Token-ish keys (api key/secret/token/password/bearer/`sk-…`) | 0 | 0 | 0 |
| Watermark tokens (co-authored-by / generated-by / AI-generated / vendor model names) | 0 | 0 | 0 |
| Non-ASCII | 0 | 4 (all U+2014 em dash) | 0 |
| Line endings | LF only | LF only | LF only |

**No secrets. No machine-local paths. No watermarks. Nothing needs redacting** — the only non-ASCII
is four em dashes, and the committed version already uses them. The only genuine hazard is not content
but **posture**: an unbounded `Shell(show:*)` wildcard with an empty deny list (R1 below).

## 6. Ownership — is it clear enough for a named tooling/configuration owner?

**Partly. There is a fallback owner and no specific one.**

- `.github/CODEOWNERS` ends with a catch-all `* @letuhao`, so every path — including all of
  `.commandcode/**` — already has a **named human owner**. Nothing is unowned.
- But there is **no specific entry** for assistant/tooling config, and **no decision-register entry**:
  `docs/architecture/decisions.md` (205 lines) contains **zero** occurrences of `commandcode`,
  `assistant config`, `taste`, or `settings.json`. So nothing in the architecture lock file records
  *why* assistant config is tracked, or whether `taste` belongs there.
- `.claude/README.md:106` and `:108` are the closest thing to a written ownership statement, and they
  are about skills, not `taste` or `settings.json`.

**Verdict:** sufficient to stop "unowned" from being the blocker; **not** sufficient to justify
committing a permission grant. A file nobody has an opinion about should not be the one that grants
shell access.

## 7. Risks

| # | Risk | Severity | Proved by |
|---|---|---|---|
| R1 | `Shell(show:*)` is an unbounded wildcard with `deny: []`. In a **public** GitHub repo every future clone and every agent that reads it starts with a broad shell grant. The repo is public per `AGENTS.md`. | **High if tracked** | §2, §5 |
| R2 | `settings.json` is unmapped in the verification registry **by design**; tracking it commits a permission-bearing file no boundary can verify, and `verify-change.ps1` will print `(unmapped)`. | **High if tracked** | §4 |
| R3 | `taste.md` is knowledge that exists only inside `.commandcode/`, which `.claude/README.md:108` forbids. A second maintainer would inherit one person's preferences as if they were the repo's. Already true for the committed file. | **Medium** | §3, §1 |
| R4 | `taste.md:6` (committed) states the owner "keeps permissions fully open (bypass/auto-accept, --yolo)", while `settings.json` sets `defaultMode: "default"`. Tracked config and tracked taste describe **different postures**. Not a vulnerability — a truthfulness defect, and it is one reason R3 deserves a ruling. | **Low** | §2 |
| R5 | Name collision: **3** tracked `taste.md` and **2** tracked `settings.json` after this bundle. A maintainer writing a bare `taste.md:12` citation gets a HIGH D3 from the citation audit, because the rule resolves by basename. | **Low** | §8 |
| R6 | The `.commandcode` scope of the citation audit is **already red** — 11 HIGH (10 D1 + 1 D3) across 3 documents, all in `.commandcode/skills/**`, unrelated to these three files. Per-file scoping keeps the taste files clean, but the owning boundary is not green scope-wide. | **Pre-existing** | §8 |

## 8. Exact evidence commands and outputs

All run in this worktree, foreground, on branch `opencode/resume-30-commandcode-config-review-20260925`
at `67f16a23`.

**Hashes of the captured copies** (`Get-FileHash -Algorithm SHA256`, reproducing the MANIFEST values):

```
SHA256  4CB9784F1025E84C8FE9827BA47545A1AD9772EF3D1A8643F3E1EDA654C02FAA  settings.json
SHA256  1DBDCD9A3C9B5111EC5F5C3F01DC64789E81CD5214CE4915E922E610ABC1D14F  taste.md
SHA256  9F36148D37A22571A353D510106F01E0458694236D1DA132A4D91B785B4CF9EB  workflow-taste.md
```

**Tracked / ignored state** (`git ls-files --error-unmatch` and `git check-ignore -v`, per path):

```
.commandcode/settings.json                => NOT ignored, UNTRACKED
.commandcode/taste/taste/taste.md         => NOT ignored, TRACKED
.commandcode/taste/workflow/taste.md      => NOT ignored, UNTRACKED
```

`git ls-files -- .commandcode` returns **27** tracked paths and **all 27 are Markdown** — the
repository's `.commandcode/` tree is docs-only today, which is exactly why the registry maps it with a
`**/*.md` pattern and why `settings.json` is the first non-Markdown candidate any owner would have to
decide about. `settings.json` and `workflow/taste.md` are absent from that list, and
`git log --oneline --all -- <both>` returns **nothing** — neither has ever been committed on any ref.

**The pending `taste.md` change** (`git diff --no-index` HEAD copy vs bundle copy):

```
@@ -13,0 +14,8 @@     (8 insertions, 0 deletions — pure append)
```

**Registry resolution** (`. scripts/lib/VerificationBoundaries.ps1`, then `Resolve-Owner` per path
against the 449 owner boundaries):

```
owner boundaries: 449
.commandcode/settings.json                                 => UNMAPPED
.commandcode/taste/taste/taste.md                          => docs-and-assistant-config  (specificity 100020)
.commandcode/taste/workflow/taste.md                       => docs-and-assistant-config  (specificity 100020)
tasks/reports/resume-30-commandcode-config-review-20260925.md => session-and-program-records  (specificity 8)
```

**Doc-citation gate**, per-file as `docs/contributing/creative-mode.md:454` requires — all **exit 0**:

```
python scripts/audit-doc-citations.py --strict --scope tasks/evidence-fragments/.../taste.md          -> exit 0
python scripts/audit-doc-citations.py --strict --scope tasks/evidence-fragments/.../workflow-taste.md -> exit 0
python scripts/audit-doc-citations.py --strict --scope .commandcode/taste/taste/taste.md             -> exit 0
```

Pre-existing red, for context (R6) — `python scripts/audit-doc-citations.py --scope .commandcode --summary`:

```
Doc-citation audit - 27 documents, 15 resolvable citations checked
  D1 file does not exist        10   (10 HIGH)
  D3 ambiguous basename          1   (1 HIGH)
HIGH findings by document, worst first:
      7  .commandcode/skills/demon-fix-unresolved/SKILL.md
      3  .commandcode/skills/html-design-implementation/SKILL.md
      1  .commandcode/skills/local-web-review/SKILL.md
```

`--scope .commandcode --strict` exits 1. **None** of those 11 HIGH findings is in a `taste` file; they
are pre-existing rot in `skills/**`, and this lane did not cause or fix them.

**Tracked-config inventory** (`git ls-files`, filtered to assistant trees) — the established pattern:

```
.claude/settings.json     -> {"attribution": {"commit": "", "pr": "", "sessionUrl": false}}   (identity blanked)
.cursor/mcp.json         -> ${workspaceFolder}/tools/debug-mcp/server.py
.kilo/kilo.json          -> repo-relative command
.mcp.json                -> repo-relative command
```

No tracked file in this repository carries a tool permission allow-list.

**Ownership** — `.github/CODEOWNERS` is 4 lines and its catch-all `* @letuhao` covers
`.commandcode/**`; `docs/architecture/decisions.md` has 0 hits for `commandcode`, `assistant config`,
`taste`, `settings.json`.

## 9. Recommendations — one option per file, owner decides

I am **not** choosing a policy. Each file gets one recommended option; the decision is the owner's.

### 9.1 `.commandcode/taste/taste/taste.md` → **TRACK (keep it tracked; commit the append)**

It is already in the index, already owned by a boundary, gate-clean, secret-free, portable and
watermark-free. Doing nothing leaves a permanent 8-line drift between the committed file and every
clone. The only live argument against is R3 (knowledge inside `.commandcode/`), which is a ruling to
make once, not per file — and it already cuts against the status quo.

*If the owner rejects this, the fallback is local-only with a narrow rule `.commandcode/taste/`, which
would also untrack the already-committed file — a larger decision than it looks.*

### 9.2 `.commandcode/taste/workflow/taste.md` → **TRACK (add it)**

Same properties as 9.1, and it lands in a boundary that already covers the path — no registry change,
no new guard, gate-clean per-file. Structurally, the existing `taste/taste.md` is a pointer stub whose
link to `taste/taste/taste.md` **does resolve** (verified), so the tree's convention is
`taste/<domain>/taste.md` behind a stub. `workflow/` is a second domain with no stub.

*Optional, and it widens the fence by one file: add the symmetric stub for consistency.*

### 9.3 `.commandcode/settings.json` → **LOCAL-ONLY, narrow ignore rule. Do not track.**

It is the one file where tracking is actively harmful: a wildcard shell grant (R1) in a public repo,
under a permission file no verification boundary owns (R2), for a machine whose tool state the tool
itself keeps at `~`. Every repo convention points the same way. This is the recommendation I would
defend hardest, and it is still the owner's call.

## 10. The exact patch, if the owner chooses tracked configuration

**Not applied.** All three hunks below are for the owner to apply; this lane changed none of them.

**Hunk A — unblock the pending `taste.md` append** (no fence change; the file is already tracked):

```
git add .commandcode/taste/taste/taste.md
```

**Hunk B — track the workflow taste file** (this is the only new tracked path; needs the fence widened
to include it before staging):

```
git add .commandcode/taste/workflow/taste.md
```

**Hunk C — optional symmetry stub** (new file, `.commandcode/taste/workflow.md`), matching the existing
`# Taste` / `See [taste/taste.md](taste/taste.md)` two-line form of `taste/taste.md`:

```
# Workflow Taste
See [taste/workflow/taste.md](taste/workflow/taste.md)
```

**Hunk D — the narrow ignore for `settings.json`,** if 9.3 is accepted. Add to `.gitignore` beside the
other assistant-runtime local-state rules (after the `.kilo/sessions/` rule at line 174):

```
# Command Code per-machine permission state (local-only; see tasks/reports/resume-30-commandcode-config-review-20260925.md)
.commandcode/settings.json
.commandcode/settings.local.json
```

Deliberately **not** `.commandcode/` and deliberately **not** `.commandcode/taste/` — a broad rule
would silently swallow the two files 9.1 and 9.2 recommend tracking, which is the exact mistake that
made these three paths ambiguous in the first place.

**No registry change is needed for any of the above.** `.commandcode/**/*.md` is already inside
`docs-and-assistant-config`; `.commandcode/settings.json` is *supposed* to stay unmapped, so
broadening the boundary to cover it would contradict the written contract at
`scripts/lib/VerificationBoundaries.ps1:54`.

**If the owner instead rules R3 against tracked `taste`**, the work is larger than these three files:
a ruling in `docs/architecture/decisions.md`, untracking the committed `taste/taste.md`, and deciding
where the knowledge goes instead (per `.claude/README.md:108`, into `docs/`). That is a separate lane.

## 11. What is provable from the bundle, and what is not

**Proved here (bundle + this worktree):** the three hashes and their equality with the MANIFEST's
recorded source hashes; the full content of all three files; that `taste.md` is tracked and its
pending change is an 8-line pure append; that neither `settings.json` nor `workflow/taste.md` is
tracked **or** ignored **or** has ever been committed on any ref; the registry resolution of all three
paths and the written reason `settings.json` is unmapped; per-file citation-gate exit 0; the secret,
machine-path and watermark scan; the tracked-config inventory; `CODEOWNERS` coverage; the absence of
any `decisions.md` entry; the pre-existing `.commandcode` audit red.

**Requires the owner or the main checkout — not provable here, and I did not read it:**

1. **The live `git status` of the main checkout.** The MANIFEST's untracked/modified column describes
   that checkout; this worktree is clean at `67f16a23` and cannot confirm or refute it. The three
   files may have changed again since capture — the hashes prove what was captured, not what is there
   now.
2. **Whether the bundle's copies still match the source paths.** Re-hash the three source paths in the
   main checkout before applying any hunk; if a hash differs, this review's content findings are
   stale.
3. **The `Shell(...)` permission grammar.** No file in this repository documents `Shell(show:*)`,
   `Shell(worktree:*)`, or `defaultMode` — I checked. Whether these are the real tool's syntax, and
   what `Shell(show:*)` actually authorizes, can only be settled against the tool's own schema. I
   treated it as a permission allow-list on the strength of the file's own shape, and labelled it as
   such.
4. **Whether the two untracked files are regenerated on every run** (and therefore whether tracking
   them means tracking a moving target), and whether any other tool or lane depends on them being
   untracked.
5. **Whether the owner wants a decision-register entry** for assistant-config policy. The repository
   has none, and I did not create one.

## 12. Unresolved owner questions

1. **Do tracked `taste` files satisfy R3, or must learned-preference knowledge live in `docs/`?**
   Recommendation: rule that `taste` stays a tracked `.commandcode` artifact, and record the ruling
   in `docs/architecture/decisions.md` so 9.1 and 9.2 stop being a per-file judgement call. If instead
   the answer is no, the work grows well past these three files (§10).
2. **Do you accept committing `settings.json`'s wildcard shell grant to a public repo (R1/R2)?**
   Recommendation: **no** — local-only, Hunk D. This is the single decision I would not delegate.
3. **Should the undecided state be closed at all?** Two untracked-but-not-ignored files will keep
   appearing in every `git status` indefinitely. Recommendation: yes — the three recommendations in
   §9 close it.
4. **Do you want the ownership made specific** — a `CODEOWNERS` line and/or a `decisions.md` entry for
   assistant config, rather than relying on the `* @letuhao` catch-all? Recommendation: a
   `decisions.md` entry is worth more than a `CODEOWNERS` line, because the thing that needs recording
   is *policy*, not *a person*.
5. **Is R4's divergence (taste says bypass, settings says `default`) a contradiction to reconcile, or
   a harmless historical note?** Recommendation: treat as a note, and do not let it be read as
   permission policy.
6. **Should the pre-existing `.commandcode` audit red (R6, 11 HIGH in `skills/**`) be a separate lane?**
   Recommendation: yes — it is unrelated rot in a different subtree, and this lane should not have
   absorbed it.

## 13. Next steps

1. Owner answers §12.1–§12.3. Nothing else can proceed without them.
2. Re-hash the three source paths in the main checkout and confirm they still match §1.
3. Owner (or a follow-on lane with a widened fence) applies the chosen hunks from §10 — remembering
   that Hunk B and Hunk C need the session fence widened first, and Hunk D needs the R2 question
   answered.
4. If tracked: run `.\scripts\verify-change.ps1 -Paths <the staged .commandcode paths> -Session
   resume-30-commandcode-config-review-20260925` and the per-file
   `audit-doc-citations.py --strict --scope <file>`; both are already predicted clean here, and the
   per-file gate is the correct scope per `docs/contributing/creative-mode.md:454`.
5. If the R3 ruling goes against tracked `taste`, open a new lane for the decision entry, the untrack,
   and the relocation of the knowledge.

## 14. Change attestation

**No `.commandcode` source path was read from or written to in the main checkout. No ignore rule was
added. No cleanup tool was created or run. No integration checkout was created, modified or merged. No
branch, commit, push or merge was made. The evidence bundle was read, never modified.** The only file
this lane wrote is `tasks/reports/resume-30-commandcode-config-review-20260925.md`.

## 15. Verification log

| Command | Result |
|---|---|
| `Get-FileHash -Algorithm SHA256` on the three bundle copies | All three match the MANIFEST's recorded source hashes exactly |
| `git status --short --branch` | `## opencode/resume-30-commandcode-config-review-20260925` — clean, only this report untracked |
| `python scripts/audit-doc-citations.py --scope tasks/reports/resume-30-commandcode-config-review-20260925.md --strict` | exit 0, no HIGH findings |
| `git diff --check` | clean — no whitespace errors |

Supporting runs quoted in §8: per-file citation gates (exit 0 ×3), `Resolve-Owner` registry
resolution, the `git ls-files` / `git check-ignore` state probe, the secret/portability/watermark scan,
and the pre-existing `.commandcode` scope audit (exit 1, 11 HIGH, all in `skills/**`).
