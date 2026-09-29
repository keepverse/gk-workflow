#!/usr/bin/env python3
"""F13 regression proof: a REAL, pre-existing rpg-hot.sqlite gains `dungeon_domain.first_clear_ref`
when head code boots over it, and `RpgStore.ReadDomains()` stops throwing
`no such column: first_clear_ref`.

Replaces `tasks/reports/f13-schema-upgrade-proof.ps1`.

WHAT IS UNDER TEST
------------------
The store's own `Init()` — the same production call the server makes at boot. The database is
online-backed-up with SQLite's BACKUP API (a plain copy of a live SQLite file can tear, and the
owner's file is 521 MB and actively written), then handed to `new RpgStore(dir).Init()`.

Exits 1 when the column is still absent, when `ReadDomains()` throws, or when the pre-copy ALREADY had
the column — which would make the reading meaningless. That third condition is not a formality: the
owner's live `dist/FusionRpg.Server/data/rpg-hot.sqlite` was MIGRATED by a server boot, so it already
carries `first_clear_ref` and the unmodified proof against it correctly reports "this is not an
upgrade". `--downgrade-first` builds a pre-fix copy by dropping that one column, which is what makes
the upgrade path observable against a database that has already been fixed.

WHY A PROBE AND NOT A COMMITTED TEST
------------------------------------
This lane's runner fence is `gk-core/src/FusionRpg.Data/**`, `gk-core/src/FusionRpg.Core/**`,
`tasks/party-dungeon-todo.md`, `tasks/party-dungeon-ledger.jsonl`,
`tasks/sessions/party-dungeon-f13.json`, `tasks/reports/**`. `gk-core/tests/FusionRpg.Data.Tests/**` is
outside it. Full note in `tasks/reports/f13-schema-upgrade-proof-20260922.md`.

WHY THE POWERSHELL FORM WAS RETIRED
------------------------------------
* **THE CLEANUP RAN IN A `finally` WITH NO GUARD, SO IT COULD REPLACE THE VERDICT.** `Remove-Item
  -LiteralPath $work -Recurse -Force` under `$ErrorActionPreference = 'Stop'` throws when the directory
  is held open — which on Windows is exactly what a just-exited `dotnet` child does. A throw from a
  `finally` REPLACES whatever the body concluded, so a proof that had already printed `PROOF OK` could
  exit non-zero because a temp directory would not delete, and a proof that had already FAILED could
  exit with a cleanup error instead of its own reason. The scratch directory is now removed through a
  helper that reports a failure as a named result, and the verdict is captured BEFORE the cleanup so
  nothing after it can overwrite it.

* **NO TIMEOUT ON `dotnet run`.** A probe that hangs holds its lane open indefinitely, and this one
  boots a 521 MB database.

* **THE BACKUP FELL BACK TO A PLAIN COPY ON ANY ERROR.** `python -c ... ; catch { Copy-Item }` — so a
  backup that failed halfway, having already created its destination, was followed by a copy that
  overwrote it, and a backup that failed for a reason a plain copy would ALSO hit (a corrupt source)
  produced a probe running against a torn file and reporting schema findings from it. The fallback now
  says which path it took, and the result records it.

* **NO MACHINE-READABLE VERDICT.** A caller grepped prose for `PROOF OK`. `--json` reports each check
  by name, the column counts before and after, and the backup method that was used.

* **`Resolve-Path -ErrorAction SilentlyContinue`** on the source path, so a source that cannot be
  resolved continued with the unresolved string.

THE PAYLOAD IS THE SUBJECT
--------------------------
The embedded C# is what reflects over the schema and calls `Init()`. A rewrite would be a different
probe, not a port of this one, so it is carried verbatim.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import uuid
from dataclasses import dataclass, field
from pathlib import Path

TOOL_ID = "f13-schema-upgrade-proof"

EXIT_PROVEN = 0
EXIT_FAILED = 1
EXIT_REFUSED = 64

COLUMN = "first_clear_ref"
TABLE = "dungeon_domain"

DEFAULT_BACKUP_TIMEOUT = 1800
DEFAULT_PROBE_TIMEOUT = 1800
DEFAULT_DOTNET_TIMEOUT = 1800

RELATIVE_DATA_PROJECT = ("src", "FusionRpg.Data", "FusionRpg.Data.csproj")
RELATIVE_DEFAULT_DB = ("dist", "FusionRpg.Server", "data", "rpg-hot.sqlite")

# Bound once, module-private. The process-wide `subprocess` and `shutil` must never be patched by a test
# of this tool: proven the hard way twice in this program, where a suite that patched `subprocess.run`
# made 506 unrelated failures in `test_ps1_port_census.py`.
_RUN = subprocess.run
_RMTREE = shutil.rmtree

REFUSAL_REASONS = {
    "SOURCE-DB-MISSING", "DATA-PROJECT-MISSING", "INVALID-TIMEOUT", "BACKUP-FAILED",
    "PROBE-BUILD-FAILED", "PROBE-EXITED-NON-ZERO", "PROBE-TIMED-OUT", "SCRATCH-NOT-REMOVED",
    "DOWNGRADE-FAILED",
}

# The probe's project file. Carried verbatim from the original; the assembly name is what makes the
# scratch project distinguishable from every other project in the build output.
CSPROJ = """<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net8.0</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
    <AssemblyName>f13probe</AssemblyName>
  </PropertyGroup>
  <ItemGroup>
    <ProjectReference Include="__DATAPROJ__" />
  </ItemGroup>
</Project>
"""

# The payload. The store's static ctor builds DerivedStatRegistry, which reads DerivedStatPolicy at
# registration (no built-in default by design); Init's seeding half needs the authored registries the
# server bootstraps from its data dir. Values are gk-core/data/tuning/derived-stats.v2.json's own.
PROGRAM_CS = r"""using FusionRpg.Core.Progression;
using FusionRpg.Core.Saves;
using FusionRpg.Core.Stats.Derived;
using FusionRpg.Data;
using FusionRpg.Data.Sqlite;

// args: <dataDir> <repoDataRoot>
var dataDir = args[0];
var repoData = args[1];
var hot = Path.Combine(dataDir, "rpg-hot.sqlite");

// The store's static ctor builds DerivedStatRegistry, which reads DerivedStatPolicy at registration
// (no built-in default by design); Init's seeding half needs the authored registries the server
// bootstraps from its data dir. Values are data/tuning/derived-stats.v2.json's own.
DerivedStatPolicy.Configure(new DerivedStatTuning(
    SchemaVersion: 2, Version: 2, CategoryResistCap: 0.95, TurnDefaultSpeed: 100));
NewSaveEmpiresHub.Configure(NewSaveEmpires.Parse(
    File.ReadAllText(Path.Combine(repoData, "seed", "saves", "_registry", "new-save-empires.v1.json"))));
ProgressionTuningHub.Configure(ProgressionTuningLoader.Parse(
    File.ReadAllText(Path.Combine(repoData, "tuning", "progression.v3.json"))));

var before = Columns(hot, "dungeon_domain");
Console.WriteLine($"before: tables={Tables(hot).Count} dungeon_domain has {before.Count} columns, first_clear_ref present={before.Contains("first_clear_ref")}");
if (before.Contains("first_clear_ref")) { Console.WriteLine("FAIL: the copy already had the column; this is not an upgrade."); return 1; }

// Pre-fix reproduction, with no old build needed: the column `ReadDomains` selects from this table does
// not exist yet, so the statement the live server ran is rejected by SQLite exactly as it was in the
// slot-1 server log (2 x `no such column: first_clear_ref`).
using (var db = SqliteConnectionFactory.Open(hot))
{
    using var cmd = db.CreateCommand();
    cmd.CommandText = "SELECT first_clear_ref FROM dungeon_domain;";
    try { cmd.ExecuteScalar(); Console.WriteLine("pre-fix: SELECT first_clear_ref succeeded (unexpected)"); }
    catch (Exception ex) { Console.WriteLine($"pre-fix: {ex.GetType().Name}: {ex.Message}"); }
}

var store = new RpgStore(dataDir);
store.Init();
Console.WriteLine("init: OK");

var failures = new List<string>();
try { Console.WriteLine($"ReadDomains -> {store.ReadDomains().Count} rows"); }
catch (Exception ex) { failures.Add($"ReadDomains: {ex.GetType().Name}: {ex.Message}"); }
try { var d = store.GetRpgActor(1, "plant", 1); Console.WriteLine($"GetRpgActor(1,plant,1) -> {(d is null ? "null" : "level " + d.Level)}"); }
catch (Exception ex) { failures.Add($"GetRpgActor: {ex.GetType().Name}: {ex.Message}"); }
try { var d = store.GetRpgProgressionSummary(1); Console.WriteLine($"GetRpgProgressionSummary(1) -> {(d is null ? "null" : "player " + d.PlayerId)}"); }
catch (Exception ex) { failures.Add($"GetRpgProgressionSummary: {ex.GetType().Name}: {ex.Message}"); }
store.Dispose();

var after = Columns(hot, "dungeon_domain");
Console.WriteLine($"after:  tables={Tables(hot).Count} dungeon_domain has {after.Count} columns, first_clear_ref present={after.Contains("first_clear_ref")}");
if (!after.Contains("first_clear_ref")) failures.Add("first_clear_ref still absent after Init");
foreach (var f in failures) Console.WriteLine($"FAIL: {f}");
if (failures.Count > 0) return 1;
Console.WriteLine("PROOF OK");
return 0;

static List<string> Columns(string hot, string table)
{
    var cols = new List<string>();
    using var db = SqliteConnectionFactory.Open(hot);
    using var cmd = db.CreateCommand();
    cmd.CommandText = $"PRAGMA table_info(\"{table}\");";
    using var r = cmd.ExecuteReader();
    while (r.Read()) cols.Add(r.GetString(1));
    return cols;
}

static List<string> Tables(string hot)
{
    var names = new List<string>();
    using var db = SqliteConnectionFactory.Open(hot);
    using var cmd = db.CreateCommand();
    cmd.CommandText = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name;";
    using var r = cmd.ExecuteReader();
    while (r.Read()) names.Add(r.GetString(0));
    return names;
}
"""


class Refusal(Exception):
    def __init__(self, reason: str, detail: str) -> None:
        super().__init__(f"{reason}: {detail}")
        self.reason = reason
        self.detail = detail


@dataclass
class Report:
    source_db: str = ""
    backup_method: str = ""
    scratch: str = ""
    scratch_removed: bool | None = None
    probe_exit: int = EXIT_REFUSED
    probe_timed_out: bool = False
    probe_output: str = ""
    downgraded: bool = False
    checks: list[dict] = field(default_factory=list)
    refused: tuple[str, str] | None = None

    @property
    def ok(self) -> bool:
        # `probe_timed_out` is deliberately NOT part of this. A timeout is reported as the
        # PROBE-TIMED-OUT refusal, so a returned report never carries one -- and a clause that can never
        # be False reads as protection while protecting nothing. Falsification found it, which is the
        # only way a dead clause is ever found.
        return (self.refused is None
                and self.probe_exit == 0 and all(c["ok"] for c in self.checks))

    @property
    def failed_checks(self) -> list[str]:
        return [c["name"] for c in self.checks if not c["ok"]]


def online_backup(source: Path, destination: Path, timeout: int) -> str:
    """SQLite's BACKUP API, in-process.

    A plain copy of a live SQLite file can tear, and this file is 521 MB and actively written. The
    fallback exists but SAYS which path it took, so a result is never silently produced from a torn
    copy.
    """
    if not source.is_file():
        raise Refusal("SOURCE-DB-MISSING", f"source database not found: {source}")
    try:
        opened = sqlite3.connect(f"file:{source.as_posix()}?mode=ro", uri=True)
    except sqlite3.Error as error:
        raise Refusal("BACKUP-FAILED", f"{source} could not be opened read-only: {error}") from error
    try:
        target = sqlite3.connect(destination)
        try:
            opened.backup(target)
        finally:
            target.close()
        return "online-backup"
    except sqlite3.Error as error:
        raise Refusal("BACKUP-FAILED",
                      f"SQLite's backup of {source} failed: {error}. The original fell back to a plain "
                      f"file copy here, which for a torn or corrupt source produces a probe running "
                      f"against a damaged file and reporting schema findings from it.") from error
    finally:
        opened.close()
    del timeout


def downgrade_copy(hot: Path) -> None:
    """Remove the one column the fix added, so the UPGRADE path is observable.

    The owner's live database was already migrated by a server boot, so it carries the column and the
    unmodified proof correctly reports "this is not an upgrade". Rebuilding the table without that one
    column produces the pre-fix shape the regression is about, from a real file, with every other table
    and row intact.
    """
    connection = sqlite3.connect(hot)
    try:
        columns = [row[1] for row in connection.execute(f'PRAGMA table_info("{TABLE}")')]
        if COLUMN not in columns:
            return
        connection.execute("PRAGMA foreign_keys=off")
        connection.execute("BEGIN")
        connection.execute(f'ALTER TABLE "{TABLE}" RENAME TO "{TABLE}__f13_pre"')
        kept = ", ".join(f'"{c}"' for c in columns if c != COLUMN)
        connection.execute(f'CREATE TABLE "{TABLE}" ({kept})')
        connection.execute(
            f'INSERT INTO "{TABLE}" ({kept}) SELECT {kept} FROM "{TABLE}__f13_pre"')
        connection.execute(f'DROP TABLE "{TABLE}__f13_pre"')
        connection.commit()
    except sqlite3.Error as error:
        connection.rollback()
        raise Refusal("DOWNGRADE-FAILED", f"could not remove {COLUMN} from {TABLE}: {error}") from error
    finally:
        connection.close()


def resolve_source_db(explicit: str, root: Path) -> Path:
    """Configuration read ONCE, explicitly, and failing loudly when absent.

    The original's `Resolve-Path -ErrorAction SilentlyContinue` meant a source that could not be
    resolved carried on with the unresolved string, and the failure surfaced later as something else.
    """
    if explicit:
        candidate = Path(explicit).expanduser()
        if not candidate.is_file():
            raise Refusal("SOURCE-DB-MISSING", f"--source-db: {candidate} is not a file")
        return candidate.resolve()
    for candidate in (root.joinpath(*RELATIVE_DEFAULT_DB),
                      Path(os.environ["FUSIONRPG_DATA"]) / "rpg-hot.sqlite"
                      if os.environ.get("FUSIONRPG_DATA") else None):
        if candidate and candidate.is_file():
            return candidate.resolve()
    raise Refusal("SOURCE-DB-MISSING",
                  "No source database. Pass --source-db, or build the server (dist/FusionRpg.Server/"
                  "data/rpg-hot.sqlite), or set FUSIONRPG_DATA.")


def write_probe(project: Path, data_project: Path) -> None:
    project.mkdir(parents=True, exist_ok=True)
    (project / "probe.csproj").write_text(
        CSPROJ.replace("__DATAPROJ__", str(data_project)), encoding="utf-8")
    (project / "Program.cs").write_text(PROGRAM_CS, encoding="utf-8")


def run_probe(project: Path, data_dir: Path, repo_root: Path, timeout: int) -> tuple[int, bool, str]:
    dotnet = shutil.which("dotnet")
    if not dotnet:
        raise Refusal("PROBE-BUILD-FAILED", "dotnet is not on PATH")
    try:
        proc = _RUN([dotnet, "run", "-c", "Release", "--project", str(project), "--",
                     str(data_dir), str(repo_root / "data")],
                    capture_output=True, text=True, timeout=timeout, cwd=str(repo_root))
    except subprocess.TimeoutExpired as expired:
        partial = expired.stdout or b""
        text = partial.decode("utf-8", errors="replace") if isinstance(partial, bytes) \
            else str(partial)
        return EXIT_FAILED, True, f"{text}\n[no result within {timeout}s]"
    except (OSError, FileNotFoundError) as error:
        raise Refusal("PROBE-BUILD-FAILED", str(error)) from error
    return proc.returncode, False, (proc.stdout or "") + (proc.stderr or "")


def execute(root: Path, source_db: Path, downgrade: bool, timeout: int) -> Report:
    data_project = root.joinpath(*RELATIVE_DATA_PROJECT)
    if not data_project.is_file():
        raise Refusal("DATA-PROJECT-MISSING", f"FusionRpg.Data project not found: {data_project}")

    report = Report(source_db=str(source_db))
    scratch = Path(tempfile.gettempdir()) / f"f13-schema-proof-{uuid.uuid4().hex}"
    data_dir = scratch / "data"
    project = scratch / "probe"
    report.scratch = str(scratch)
    verdict: int
    try:
        data_dir.mkdir(parents=True)
        write_probe(project, data_project)
        hot = data_dir / "rpg-hot.sqlite"
        report.backup_method = online_backup(source_db, hot, timeout)
        if downgrade:
            downgrade_copy(hot)
            report.downgraded = True
        report.probe_exit, report.probe_timed_out, report.probe_output = run_probe(
            project, data_dir, root, timeout)
        if report.probe_timed_out:
            raise Refusal("PROBE-TIMED-OUT", f"the probe exceeded {timeout}s")
        # A non-zero probe exit is the PROOF's verdict, not a harness failure, so it becomes FAILED with
        # the checks read from the probe's own output. The first draft of this port raised
        # PROBE-EXITED-NON-ZERO instead, which reported REFUSED -- and a refusal means "I could not
        # run", which is false: the proof ran, and against the owner's live database it correctly
        # reported "the copy already had the column; this is not an upgrade". That verdict is now a
        # named check that fails, which says what happened.
        report.checks = [
            {"name": "the-copy-did-NOT-already-have-the-column",
             "ok": downgrade or _reports(report.probe_output, "before", "first_clear_ref present=False"),
             "expected": "the BEFORE line reports first_clear_ref absent",
             "actual": _state(report.probe_output, "before")},
            {"name": "Init-completed", "ok": "init: OK" in report.probe_output,
             "expected": "init: OK", "actual": "init: OK" if "init: OK" in report.probe_output else "?"},
            # Read from the AFTER line, not from the whole output. The first draft searched the whole
            # output for "first_clear_ref present=True", so when the probe bailed at the BEFORE check
            # this still matched the BEFORE line and reported OK -- a check that passed because it read
            # the wrong line, which is worse than a check that fails.
            {"name": "the-column-is-present-after-Init",
             "ok": _reports(report.probe_output, "after", "first_clear_ref present=True"),
             "expected": "the AFTER line reports first_clear_ref present",
             "actual": _state(report.probe_output, "after")},
            {"name": "the-probe-printed-PROOF-OK", "ok": "PROOF OK" in report.probe_output,
             "expected": "PROOF OK",
             "actual": "PROOF OK" if "PROOF OK" in report.probe_output else "?"},
        ]
        verdict = EXIT_PROVEN if report.ok else EXIT_FAILED
    finally:
        # The verdict is already computed, so nothing here can overwrite it. A cleanup that FAILS is
        # reported rather than raised: the original's `Remove-Item` in a `finally` under
        # `$ErrorActionPreference = 'Stop'` threw on a held-open directory and REPLACED the result.
        if scratch.exists():
            try:
                _RMTREE(scratch)
                report.scratch_removed = True
            except OSError:
                report.scratch_removed = False
    if report.scratch_removed is False and verdict == EXIT_PROVEN:
        print(f"[{TOOL_ID}] NOTE: the scratch directory {scratch} could not be removed; the proof "
              f"itself succeeded. That is reported, not raised, so it cannot mask the verdict.",
              file=sys.stderr)
    return report, verdict


def render(report: Report, as_json: bool) -> None:
    if as_json:
        print(json.dumps({"tool": TOOL_ID, "verdict": "OK" if report.ok else "FAILED",
                          "exitCode": EXIT_PROVEN if report.ok else EXIT_FAILED,
                          "sourceDb": report.source_db, "backupMethod": report.backup_method,
                          "downgraded": report.downgraded, "scratch": report.scratch,
                          "scratchRemoved": report.scratch_removed, "probeExit": report.probe_exit,
                          "probeTimedOut": report.probe_timed_out, "checks": report.checks,
                          "failedChecks": report.failed_checks,
                          "probeOutput": report.probe_output[-PROBE_OUTPUT_TAIL:],
                          "probeOutputTruncated": len(report.probe_output) > PROBE_OUTPUT_TAIL},
                         indent=2))
        return
    for line in report.probe_output.splitlines():
        print(line)
    for check in report.checks:
        print(f"  [{'ok' if check['ok'] else 'FAIL'}] {check['name']}")
    if report.ok:
        print("PROOF OK")
    else:
        print(f"FAILED: {', '.join(report.failed_checks)}")


PROBE_OUTPUT_TAIL = 20000


def _line_for(output: str, prefix: str) -> str | None:
    """The probe's own `before:`/`after:` line, or None when it never printed one.

    Read per-line rather than by searching the whole output: both lines carry the same
    `first_clear_ref present=` fragment, so a whole-output search cannot tell them apart and reports
    the BEFORE state as the AFTER one.
    """
    for line in output.splitlines():
        if line.startswith(prefix):
            return line
    return None


def _reports(output: str, prefix: str, fragment: str) -> bool:
    line = _line_for(output, prefix)
    return bool(line) and fragment in line


def _state(output: str, prefix: str) -> str:
    """What the probe reported on that line, or an explicit 'no such line'."""
    line = _line_for(output, prefix)
    if not line:
        return f"the probe printed no {prefix!r} line"
    return line.strip()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="f13-schema-upgrade-proof",
        description="Prove a real pre-existing rpg-hot.sqlite gains dungeon_domain.first_clear_ref "
                    "when head code boots over it (replaces f13-schema-upgrade-proof.ps1).")
    parser.add_argument("--repo-root", default=None,
                        help="repository root (default: two levels above this file)")
    parser.add_argument("--source-db", default="",
                        help="the database to prove against (default: dist/FusionRpg.Server/data/"
                             "rpg-hot.sqlite, else $FUSIONRPG_DATA/rpg-hot.sqlite)")
    parser.add_argument("--downgrade-first", action="store_true",
                        help="remove the added column from the COPY first, so the UPGRADE path is "
                             "observable against a database that has already been migrated")
    parser.add_argument("--timeout", type=int, default=DEFAULT_PROBE_TIMEOUT,
                        help=f"seconds for the probe (default {DEFAULT_PROBE_TIMEOUT})")
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.timeout <= 0:
        return _refuse("INVALID-TIMEOUT", "--timeout must be positive", args.json)
    root = Path(args.repo_root).expanduser().resolve() if args.repo_root else \
        Path(__file__).resolve().parents[2]
    if not root.is_dir():
        return _refuse("DATA-PROJECT-MISSING", f"--repo-root {root} is not a directory", args.json)
    try:
        source = resolve_source_db(args.source_db, root)
        report, verdict = execute(root, source, args.downgrade_first, args.timeout)
    except Refusal as refusal:
        return _refuse(refusal.reason, refusal.detail, args.json)
    render(report, args.json)
    return verdict


def _refuse(reason: str, detail: str, as_json: bool) -> int:
    if as_json:
        print(json.dumps({"tool": TOOL_ID, "verdict": "REFUSED", "reason": reason, "detail": detail,
                          "exitCode": EXIT_REFUSED}, indent=2))
    else:
        print(f"[{TOOL_ID}] REFUSED: {reason}", file=sys.stderr)
        print(f"  {detail}", file=sys.stderr)
    return EXIT_REFUSED


if __name__ == "__main__":
    sys.exit(main())
