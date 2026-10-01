#!/usr/bin/env python3
"""Report every `ast.Name` in Load context that nothing in its own module binds.

THE DEFECT THIS HUNTS. A repository-wide path-resolution sweep renamed a helper at its IMPORT
sites but missed some CALL SITES. The module still names the old helper while binding the new
one, so the module imports cleanly - the old name usually still exists elsewhere in the import
graph, so collection passes - and the failure appears only on the specific path that reaches the
missed line, as a `NameError` rather than as a wrong path.

WHY THIS EXISTS ALONGSIDE `scripts/sweep-unbound-names.py`. That script walks each function body
with `for child in ast.iter_child_nodes(node): self.generic_visit(child)`. `generic_visit` does
not dispatch on the child's own type, so every `visit_Assign`, `visit_AnnAssign`,
`visit_For`-target and `visit_If`-nested binding inside a function body is skipped, and the names
it binds are never recorded. It therefore reports `x = 1` inside a function as an unbound use of
`x`, and measured over these nine repositories it returns 101,560 hits for 5,328 distinct names -
almost all of them ordinary local variables. A tool that reports everything is worse than no tool,
because the residue it is actually looking for is buried. This script walks with
`self.generic_visit(node)`, which dispatches correctly, and its control asserts BOTH directions
rather than only that a planted defect is caught.

WHAT IS BOUND, and what counts as bound. `bound` is the UNION of every name bound anywhere in the
module, across every scope. That is deliberate: the question is "does this module bind this name
AT ALL", which is exactly the question a missed call site turns on. A scope-strict pass would
answer a different question and would need real flow analysis, so its answers would be reported as
though they were facts about a rename sweep. Over-approximating scope loses a few true positives;
it never invents one.

Bound: `import a.b` -> `a` and `import a.b as c` -> `c`; `from .m import x [as y]` -> the alias;
function and class definitions and the class name itself; function parameters, positional-only,
keyword-only, `*args`, `**kwargs`; every assignment, annotated assignment and augmented-assignment
target; walrus targets; `except E as e`; every comprehension and generator target including
`async for`; `with ... as x`; `global` and `nonlocal`; `match` capture patterns; `del x` (recorded
as a USE, because deleting a name requires it to be bound first); and `from m import *`, which
makes the module's own binder INCOMPLETE and is reported as such rather than guessed at.

NOT bound, on purpose: `x += 1` does not introduce `x`, it reads it, so an augmented assignment
whose target appears nowhere else IS reported. That is the correct verdict, not a false positive.

`builtins` IS EXCLUDED EXPLICITLY, along with the module dunders. Without that exclusion `int`,
`str`, `dict`, `bytes` and `ValueError` all read as unbound - which is what a crude binder does,
and is the reason this file spells the exclusion out instead of relying on a caller to remember.

`from __future__ import annotations` is honoured: a use inside an annotation is a string at
runtime, so a `NameError` cannot come from one. Those uses are skipped rather than reported,
because a module whose annotations name a type it imports only under `TYPE_CHECKING` is correct
code. A use inside `if TYPE_CHECKING:` is a real reference for a type checker and not a runtime
reference, so it is reported with that flag and never confused with the defect above.

CONTROL. A sweep that has never been shown to catch a planted defect proves nothing, and one that
has only been shown to CATCH something proves it reports everything. `--self-test` therefore
asserts both halves: a reference to a name nothing binds must be flagged at the line it was
planted on, and a name bound on the line above it must NOT be flagged. Both plants go into COPIES
in a scratch directory; the originals are asserted byte-identical afterwards and the scratch is
removed, so the control cannot become a defect in the tree.

Usage:
    python scripts/sweep-unbound-references.py                 # markdown report on stdout
    python scripts/sweep-unbound-references.py --json          # machine-readable
    python scripts/sweep-unbound-references.py --repo gk-core  # one repository
    python scripts/sweep-unbound-references.py --self-test     # the two-sided control
    python scripts/sweep-unbound-references.py --self-test --plant-rename <file>
        # control in the SHAPE of the real defect: alias the import, leave the call site behind

Exit codes: 0 no hits, 1 hits reported, 2 refusal (bad input or unreadable tree).
"""

from __future__ import annotations

import argparse
import ast
import builtins
import json
import os
import shutil
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Iterator, Sequence

WORKSPACE_DEFAULT = Path(__file__).resolve().parents[1]

# The nine repositories. `gk-content`, `gk-data`, `gk-tests` and `gk-web` carry no first-party
# Python at the moment; they are still swept, so a new file cannot slip through unnoticed.
REPOSITORIES = (
    ".",  # the Keepverse root repository: scripts/, tools/, docs/, .agents/
    "gk-assets",
    "gk-content",
    "gk-core",
    "gk-data",
    "gk-forge",
    "gk-fusion",
    "gk-tests",
    "gk-web",
)

# Directories that cannot hold first-party source, or that hold a third party artefact whose name
# space is not this repository's to reason about. Every one skipped is named in the report, so a
# skipped tree is visible rather than silently absent.
SKIP_DIR_NAMES = frozenset(
    {
        ".git", ".hg", ".svn", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
        ".tox", ".nox", ".venv", "venv", "env", "node_modules", "bower_components",
        "site-packages", "dist-packages", ".eggs", ".git-crypt",
    }
)

# A `.py` larger than this is generated or vendored; the sweep records skipping it rather than
# skipping it quietly.
MAX_FILE_BYTES = 4 * 1024 * 1024

# `builtins` PLUS the names the module machinery and the class protocol supply. Without this set
# every `int` and every `__name__` reads as an unbound use, which is what turns a sweep into noise.
BUILTIN_NAMES = frozenset(dir(builtins)) | frozenset(
    {
        "__file__", "__name__", "__doc__", "__package__", "__spec__", "__loader__",
        "__builtins__", "__debug__", "__path__", "__annotations__", "__class__", "__module__",
        "__qualname__", "__dict__", "__weakref__", "__func__", "__self__", "__all__",
        "__init_subclass__", "__subclasshook__", "__class_getitem__", "__slots__", "__match_args__",
        "__dataclass_fields__", "__parameters__", "__origin__", "__args__", "__type_params__",
    }
)


@dataclass(frozen=True)
class Hit:
    """One Load-context name that no binding in its own module accounts for."""

    path: str
    line: int
    col: int
    name: str
    context: str
    kind: str  # "use" | "delete" | "annotation-skipped-not-reported"
    in_type_checking: bool

    @property
    def sort_key(self) -> tuple:
        return (self.path, self.line, self.col, self.name)


@dataclass
class FileReport:
    path: str
    repo: str
    hit_count: int = 0
    names: set[str] = field(default_factory=set)
    star_imports: list[str] = field(default_factory=list)
    future_annotations: bool = False
    annotations_skipped: int = 0
    error: str | None = None


class ModuleBinder(ast.NodeVisitor):
    """Every name this module binds at any scope, and every name it reads.

    Dispatch is left intact: the `visit_*` methods below call `self.generic_visit(node)` on the
    node itself, so each child is dispatched on its own type. Handing `generic_visit` a node's
    CHILDREN instead skips the child's own `visit_*` method, which silently loses every binding
    inside a function body - see the module docstring.
    """

    def __init__(self) -> None:
        self.bound: set[str] = set()  # every name bound anywhere in the module
        # Names bound somewhere OUTSIDE an `if TYPE_CHECKING:` block. A name that is in `bound` but
        # not here is bound only for a type checker, so a runtime use of it is a real NameError.
        self.bound_outside_type_checking: set[str] = set()
        # A comprehension has its own scope, so its target does NOT leak. A name that is in
        # `comprehension_only` and never bound anywhere else, then used outside every comprehension,
        # is a real NameError.
        self.comprehension_only: set[str] = set()
        self.bound_outside_comprehension: set[str] = set()
        self.star_imports: list[str] = []
        # (name, line, col, inside_a_comprehension), Load context only.
        self.loads: list[tuple[str, int, int, bool]] = []
        self.deletes: list[tuple[str, int, int]] = []  # `del x` needs x to be bound too
        self.future_annotations = False
        # (line, col) of every Name inside an annotation, when annotations are never evaluated.
        self.annotation_positions: set[tuple[int, int]] = set()

    # -- helpers ----------------------------------------------------------------------------------

    def _bind_name(self, name: str | None) -> None:
        if name:
            self.bound.add(name)
            if not self._in_type_checking:
                self.bound_outside_type_checking.add(name)
            if not self._comprehension_depth:
                self.bound_outside_comprehension.add(name)

    _in_type_checking = False
    _comprehension_depth = 0

    def _bind_args(self, args: ast.arguments) -> None:
        for arg in (*args.posonlyargs, *args.args, *args.kwonlyargs):
            self._bind_name(arg.arg)
            self._mark_annotation(arg.annotation)
        if args.vararg:
            self._bind_name(args.vararg.arg)
            self._mark_annotation(args.vararg.annotation)
        if args.kwarg:
            self._bind_name(args.kwarg.arg)
            self._mark_annotation(args.kwarg.annotation)

    def _mark_annotation(self, annotation: ast.expr | None) -> None:
        """Record an annotation node, and its descendants, as annotation positions.

        With `from __future__ import annotations` an annotation is never evaluated at runtime, so a
        `NameError` cannot come from one. A module that annotates with a type it imports only under
        `TYPE_CHECKING` is correct code, and reporting it would be a false positive.
        """
        if not self.future_annotations or annotation is None:
            return
        for node in ast.walk(annotation):
            if isinstance(node, ast.Name):
                self.annotation_positions.add((node.lineno, node.col_offset))

    # -- imports ----------------------------------------------------------------------------------

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            self._bind_name(alias.asname or alias.name.split(".")[0])

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        for alias in node.names:
            if alias.name == "*":
                self.star_imports.append("." * (node.level or 0) + (node.module or ""))
            else:
                self._bind_name(alias.asname or alias.name)

    # -- definitions ------------------------------------------------------------------------------

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._bind_name(node.name)
        self._bind_args(node.args)
        self._mark_annotation(node.returns)
        self.generic_visit(node)

    visit_AsyncFunctionDef = visit_FunctionDef  # type: ignore[assignment]

    def visit_Lambda(self, node: ast.Lambda) -> None:
        self._bind_args(node.args)
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._bind_name(node.name)
        self.generic_visit(node)

    # -- assignments ------------------------------------------------------------------------------

    def _bind_target(self, node: ast.AST | None, comprehension: bool = False) -> None:
        """Bind the names a target INTRODUCES. `a[0] = x` and `o.attr = x` introduce none."""
        if node is None:
            return
        if isinstance(node, ast.Name):
            self._bind_name(node.id)
            if comprehension:
                self.comprehension_only.add(node.id)
            else:
                self.bound_outside_comprehension.add(node.id)
        elif isinstance(node, (ast.Tuple, ast.List)):
            for elt in node.elts:
                self._bind_target(elt, comprehension)
        elif isinstance(node, ast.Starred):
            self._bind_target(node.value, comprehension)
        else:
            # A subscript or attribute target reads the object it hangs off, so that object still
            # has to be bound. Visit it, and let the Load rule judge it.
            self.visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        for target in node.targets:
            self._bind_target(target)
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        self._bind_target(node.target)
        self._mark_annotation(node.annotation)
        self.generic_visit(node)

    def visit_AugAssign(self, node: ast.AugAssign) -> None:
        # `x += 1` READS x; it does not introduce it. Binding it here would hide a real
        # NameError, so the target is deliberately left unbound and reported if nothing else binds it.
        self.generic_visit(node)

    def visit_NamedExpr(self, node: ast.NamedExpr) -> None:
        self._bind_target(node.target)
        self.generic_visit(node)

    def visit_Delete(self, node: ast.Delete) -> None:
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.deletes.append((target.id, target.lineno, target.col_offset))
            self.visit(target)  # a subscript/attribute delete still reads its object

    # -- exceptions -------------------------------------------------------------------------------

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        self._bind_name(node.name)  # None for a bare `except:` - nothing to bind
        self.generic_visit(node)

    # -- with -------------------------------------------------------------------------------------

    def visit_With(self, node: ast.With) -> None:
        for item in node.items:
            self._bind_target(item.optional_vars)
        self.generic_visit(node)

    visit_AsyncWith = visit_With  # type: ignore[assignment]

    # -- loops ------------------------------------------------------------------------------------
    #
    # A `for` target binds in the ENCLOSING scope, unlike a comprehension target, which is the one
    # binding in this language that does not leak. Handling both is what keeps `for x in xs:` from
    # reading as an unbound use of `x`.

    def visit_For(self, node: ast.For) -> None:
        self._bind_target(node.target)
        self.generic_visit(node)

    def visit_AsyncFor(self, node: ast.AsyncFor) -> None:
        self._bind_target(node.target)
        self.generic_visit(node)

    # -- comprehensions ---------------------------------------------------------------------------

    def visit_ListComp(self, node: ast.ListComp) -> None:
        self._comprehension(node)

    def visit_SetComp(self, node: ast.SetComp) -> None:
        self._comprehension(node)

    def visit_DictComp(self, node: ast.DictComp) -> None:
        self._comprehension(node)

    def visit_GeneratorExp(self, node: ast.GeneratorExp) -> None:
        self._comprehension(node)

    def _comprehension(self, node: ast.AST) -> None:
        # A comprehension target is the one binding in Python that does NOT leak: the comprehension
        # has its own scope. A name bound here and nowhere else, then used outside every
        # comprehension, is a real NameError - and it is detectable exactly, because the leak rule is
        # precise where function and class scopes are not. Those names are therefore tracked
        # SEPARATELY rather than folded into the union, so the union's deliberate
        # over-approximation does not swallow them.
        self._comprehension_depth += 1
        try:
            for gen in node.generators:  # type: ignore[attr-defined]
                self._bind_target(gen.target, comprehension=True)
            self.generic_visit(node)
        finally:
            self._comprehension_depth -= 1

    _comprehension_depth = 0

    # -- match patterns ---------------------------------------------------------------------------

    def visit_MatchAs(self, node: ast.MatchAs) -> None:
        self._bind_name(node.name)
        self.generic_visit(node)

    def visit_MatchStar(self, node: ast.MatchStar) -> None:
        self._bind_name(node.name)
        self.generic_visit(node)

    def visit_MatchMapping(self, node: ast.MatchMapping) -> None:
        self._bind_name(node.rest)
        self.generic_visit(node)

    def visit_MatchClass(self, node: ast.MatchClass) -> None:
        # `case C(...)` READS the name `C` as the class to match against; the pattern's own
        # sub-patterns then bind their names. Only `node.cls` is a load, so it is left to
        # `generic_visit` and judged by the Load rule like any other reference.
        self.generic_visit(node)

    # -- scope declarations -----------------------------------------------------------------------

    def visit_Global(self, node: ast.Global) -> None:
        for name in node.names:
            self._bind_name(name)

    def visit_Nonlocal(self, node: ast.Nonlocal) -> None:
        for name in node.names:
            self._bind_name(name)

    # -- `if TYPE_CHECKING:` ----------------------------------------------------------------------

    def visit_If(self, node: ast.If) -> None:
        if _guards_type_checking(node.test):
            previous = self._in_type_checking
            self._in_type_checking = True
            for stmt in node.body:
                self.visit(stmt)
            self._in_type_checking = previous
            # `else:` is real runtime code, so it is visited normally.
            for stmt in node.orelse:
                self.visit(stmt)
            return
        self.generic_visit(node)

    # -- leaves -----------------------------------------------------------------------------------

    def visit_Name(self, node: ast.Name) -> None:
        if isinstance(node.ctx, ast.Load):
            self.loads.append((node.id, node.lineno, node.col_offset, self._comprehension_depth > 0))
        self.generic_visit(node)


def _guards_type_checking(test: ast.expr) -> bool:
    return (isinstance(test, ast.Name) and test.id == "TYPE_CHECKING") or (
        isinstance(test, ast.Attribute) and test.attr == "TYPE_CHECKING"
    )


def _has_future_annotations(tree: ast.Module) -> bool:
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.module == "__future__":
            if any(alias.name == "annotations" for alias in node.names):
                return True
    return False


def _type_checking_lines(tree: ast.Module) -> set[int]:
    """Every line inside an `if TYPE_CHECKING:` block, for triage labelling only."""
    lines: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.If) and _guards_type_checking(node.test):
            for stmt in node.body:
                for child in ast.walk(stmt):
                    lineno = getattr(child, "lineno", None)
                    if lineno is not None:
                        lines.add(lineno)
    return lines


def analyse_text(text: str, path: str, repo: str) -> tuple[list[Hit], FileReport]:
    report = FileReport(path=path, repo=repo)
    try:
        tree = ast.parse(text, filename=path)
    except SyntaxError as exc:
        report.error = f"SyntaxError: {exc.msg} (line {exc.lineno})"
        return [], report

    binder = ModuleBinder()
    binder.future_annotations = _has_future_annotations(tree)
    report.future_annotations = binder.future_annotations
    binder.visit(tree)
    report.star_imports = list(binder.star_imports)

    # A star-import makes this module's binder INCOMPLETE: the imported module can export names
    # the file never binds and still uses. Reporting hits here would be guesswork, and staying
    # silent would read as proof of a clean file, so the file is listed as not-asserted instead.
    if binder.star_imports:
        return [], report

    tc_lines = _type_checking_lines(tree)
    source_lines = text.splitlines()
    bound = binder.bound | BUILTIN_NAMES
    # A name bound only under `if TYPE_CHECKING:` is not bound at runtime, so a use of it outside
    # that block is a real NameError even though the module does contain the import.
    type_checking_only = (binder.bound - binder.bound_outside_type_checking) - BUILTIN_NAMES
    # A comprehension target does not leak, so a name bound only there and used outside every
    # comprehension is a real NameError. Tracked separately so the union binder's deliberate
    # over-approximation of scope does not swallow it.
    comprehension_only = (binder.comprehension_only - binder.bound_outside_comprehension) - BUILTIN_NAMES

    hits: list[Hit] = []
    seen: set[tuple[int, int, str]] = set()

    def record(name: str, line: int, col: int, kind: str) -> None:
        key = (line, col, name)
        if key in seen:
            return
        seen.add(key)
        context = source_lines[line - 1].strip() if 0 < line <= len(source_lines) else ""
        hits.append(
            Hit(
                path=path,
                line=line,
                col=col,
                name=name,
                context=context[:200],
                kind=kind,
                in_type_checking=line in tc_lines,
            )
        )

    for name, line, col, in_comprehension in binder.loads:
        if (line, col) in binder.annotation_positions:
            report.annotations_skipped += 1
            continue
        if name in bound:
            if (
                name in type_checking_only
                and not in_comprehension
                and line not in tc_lines
            ):
                record(name, line, col, "type-checking-only")
            elif name in comprehension_only and not in_comprehension:
                record(name, line, col, "comprehension-scope-leak")
            continue
        record(name, line, col, "use")

    for name, line, col in binder.deletes:
        if name in bound:
            continue
        record(name, line, col, "delete")

    hits.sort(key=lambda h: h.sort_key)
    report.hit_count = len(hits)
    report.names = {h.name for h in hits}
    return hits, report


def iter_python_files(root: Path, also_prune: frozenset[str] = frozenset()) -> Iterator[Path]:
    """Every `.py` under `root`, deterministically, skipping vendored trees.

    `also_prune` names directories that are walked as repositories in their own right. Without it
    the root repository's own walk descends into gk-forge and gk-core as well, so every file there
    is scanned twice - once as the root repository and once as itself - and the report doubles
    every count. That is not a cosmetic problem: a doubled total reads as two defects where there
    is one, which is the same failure as a sweep that reports everything.
    """
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        dirnames[:] = sorted(
            d
            for d in dirnames
            if d not in SKIP_DIR_NAMES and d not in also_prune and not d.endswith(".egg-info")
        )
        for filename in sorted(filenames):
            if filename.endswith(".py"):
                yield Path(dirpath) / filename


def _rel(path: Path, workspace: Path) -> str:
    try:
        return path.resolve().relative_to(workspace.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def sweep(workspace: Path, repositories: Sequence[str], max_file_bytes: int) -> tuple[
    list[Hit], list[FileReport], int, list[str]
]:
    hits: list[Hit] = []
    reports: list[FileReport] = []
    scanned = 0
    skipped: list[str] = []
    # The root repository's walk must not descend into a sibling repository that is walked in its
    # own right, or every file in it is scanned twice.
    nested = frozenset(r for r in repositories if r != ".")
    for repo in repositories:
        repo_root = workspace.resolve() if repo == "." else (workspace / repo).resolve()
        if not repo_root.is_dir():
            skipped.append(f"{repo}: repository directory missing")
            continue
        for path in iter_python_files(repo_root, also_prune=nested):
            rel = _rel(path, workspace)
            try:
                size = path.stat().st_size
            except OSError as exc:
                reports.append(FileReport(path=rel, repo=repo, error=f"stat failed: {exc}"))
                continue
            if size > max_file_bytes:
                reports.append(
                    FileReport(path=rel, repo=repo, error=f"skipped: {size} bytes > --max-file-bytes")
                )
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError) as exc:
                reports.append(FileReport(path=rel, repo=repo, error=f"unreadable: {exc}"))
                continue
            scanned += 1
            file_hits, report = analyse_text(text, rel, repo)
            hits.extend(file_hits)
            reports.append(report)
    hits.sort(key=lambda h: h.sort_key)
    return hits, reports, scanned, skipped


# ------------------------------------------------------------------------------------------------
# CONTROL
# ------------------------------------------------------------------------------------------------


PLANT_UNBOUND = "_sweep_control_never_bound_"
PLANT_BOUND = "_sweep_control_bound_here_"


def _module_for_control(workspace: Path) -> Path:
    """A real first-party module to copy. Chosen because it exercises the whole binder: imports with
    aliases, a class, a comprehension, an except-as, a with-as, a walrus and a lambda."""
    candidate = (
        workspace / "gk-forge" / "tools" / "seedsmith" / "seedsmith" / "adapters" / "trees"
        / "plan" / "emit.py"
    )
    if candidate.is_file():
        return candidate
    raise SystemExit(f"REFUSED: control fixture missing at {candidate}")


def self_test(workspace: Path, scratch: Path | None, plant_rename: Path | None) -> int:
    """Both halves of the control, in COPIES, on a real module.

    Half one: a name nothing binds must be flagged, at the line it was planted on.
    Half two: a name bound on the line above it must NOT be flagged, because a sweep that flags
    everything has proven nothing about the first half.
    """
    source = _module_for_control(workspace) if plant_rename is None else plant_rename.resolve()
    if not source.is_file():
        print(f"REFUSED: control fixture missing at {source}", file=sys.stderr)
        return 2

    before = source.read_bytes()
    scratch = scratch or Path(tempfile.mkdtemp(prefix="sweep-control-"))
    scratch.mkdir(parents=True, exist_ok=True)
    target = scratch / "control_module.py"
    shutil.copyfile(source, target)

    # The plant mirrors the real defect's shape: a name that is defined immediately above the use,
    # and one that is not defined anywhere. They sit on adjacent lines so a binder that lost
    # function-body bindings fails half two as loudly as it should.
    plant = (
        "\n\n"
        "# Injected by the control. Nothing binds the first name; the second is bound above it.\n"
        f"def _control_probe():\n"
        f"    {PLANT_BOUND} = 1\n"
        f"    return {PLANT_UNBOUND}() + {PLANT_BOUND}\n"
    )
    text = target.read_text(encoding="utf-8") + plant
    target.write_text(text, encoding="utf-8")
    planted_return_line = len(text.splitlines())

    hits, _reports, scanned, _skipped = sweep(scratch, ["."], MAX_FILE_BYTES)
    unbound_hits = [h for h in hits if h.name == PLANT_UNBOUND]
    bound_hits = [h for h in hits if h.name == PLANT_BOUND]

    ok = True
    print("CONTROL: planted-defect detection, both directions")
    print(f"  fixture          : {_rel(source, workspace)}")
    print(f"  copy scanned at  : {target}")
    print(f"  files scanned    : {scanned}")
    print(f"  planted `return` : line {planted_return_line}")
    print("")
    print("  half 1 - a name nothing binds MUST be flagged")
    print(f"    planted name   : {PLANT_UNBOUND}")
    print(f"    hits           : {len(unbound_hits)}")
    if len(unbound_hits) != 1:
        print("    FAIL: expected exactly 1 hit")
        ok = False
    else:
        hit = unbound_hits[0]
        print(f"    flagged at     : {hit.path}:{hit.line}:{hit.name}")
        print(f"    source line    : {hit.context}")
        if hit.line != planted_return_line:
            print(f"    FAIL: flagged line {hit.line}, planted return is line {planted_return_line}")
            ok = False
    print("")
    print("  half 2 - a name bound on the line above MUST NOT be flagged")
    print(f"    planted name   : {PLANT_BOUND}")
    print(f"    hits           : {len(bound_hits)}")
    if bound_hits:
        for hit in bound_hits:
            print(f"    FALSE POSITIVE : {hit.path}:{hit.line} {hit.context}")
        print("    FAIL: the binder does not see a local assignment inside a function body")
        ok = False

    after = source.read_bytes()
    if after != before:
        print("  FAIL: the original file changed during the control")
        ok = False
    else:
        print(f"  original unchanged: True ({_rel(source, workspace)})")

    shutil.rmtree(scratch, ignore_errors=True)
    print(f"  verdict          : {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


# ------------------------------------------------------------------------------------------------
# REPORTING
# ------------------------------------------------------------------------------------------------


def render_markdown(hits: list[Hit], reports: list[FileReport], scanned: int, max_hits: int,
                    skipped: Sequence[str]) -> str:
    errors = [r for r in reports if r.error]
    star_files = [r for r in reports if r.star_imports]
    by_name: dict[str, list[Hit]] = {}
    for hit in hits:
        by_name.setdefault(hit.name, []).append(hit)
    by_repo: dict[str, int] = {}
    for hit in hits:
        repo = next((r.repo for r in reports if r.path == hit.path), "?")
        by_repo[repo] = by_repo.get(repo, 0) + 1

    out: list[str] = []
    out.append("# Unbound-reference sweep")
    out.append("")
    out.append(f"- files scanned        : {scanned}")
    out.append(f"- hits                 : {len(hits)}")
    out.append(f"- distinct names       : {len(by_name)}")
    out.append(f"- files unparsable     : {len(errors)}")
    out.append(f"- files with star-import (binder incomplete, NOT asserted for these): {len(star_files)}")
    out.append(f"- annotations skipped under `from __future__ import annotations`: "
               f"{sum(r.annotations_skipped for r in reports)}")
    out.append("")
    if skipped:
        out.append("## Repositories not swept")
        out.append("")
        for line in skipped:
            out.append(f"- {line}")
        out.append("")
    if errors:
        out.append("## Unparsable files")
        out.append("")
        for report in errors:
            out.append(f"- `{report.path}` -- {report.error}")
        out.append("")
    if star_files:
        out.append("## Files whose binder is incomplete (star-import)")
        out.append("")
        for report in star_files:
            out.append(f"- `{report.path}` -- `from {'|'.join(report.star_imports)} import *`")
        out.append("")
    if hits:
        out.append("## Hits by repository")
        out.append("")
        out.append("| repository | hits |")
        out.append("| --- | --- |")
        for repo, count in sorted(by_repo.items(), key=lambda kv: (-kv[1], kv[0])):
            out.append(f"| `{repo}` | {count} |")
        out.append("")
        out.append("## Hits by name")
        out.append("")
        out.append("| name | count | locations |")
        out.append("| --- | --- | --- |")
        for name, group in sorted(by_name.items(), key=lambda kv: (-len(kv[1]), kv[0])):
            locs = ", ".join(f"{h.path}:{h.line}" for h in group[:6])
            if len(group) > 6:
                locs += f", +{len(group) - 6} more"
            out.append(f"| `{name}` | {len(group)} | {locs} |")
        out.append("")
        out.append(f"## All hits (first {max_hits} of {len(hits)})")
        out.append("")
        for hit in hits[:max_hits]:
            flags = []
            if hit.in_type_checking:
                flags.append("TYPE_CHECKING")
            if hit.kind == "delete":
                flags.append("del")
            suffix = f" [{', '.join(flags)}]" if flags else ""
            out.append(f"- `{hit.path}:{hit.line}:{hit.col}` `{hit.name}`{suffix}")
            out.append(f"    `{hit.context}`")
        if len(hits) > max_hits:
            out.append("")
            out.append(f"... {len(hits) - max_hits} more; raise `--max-hits` or use `--json`.")
        out.append("")
    return "\n".join(out)


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", default=str(WORKSPACE_DEFAULT), help="workspace root")
    parser.add_argument(
        "--repo", action="append", dest="repositories", help="a repository under --root; repeatable"
    )
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    parser.add_argument("--max-hits", type=int, default=400)
    parser.add_argument("--max-file-bytes", type=int, default=MAX_FILE_BYTES)
    parser.add_argument(
        "--self-test", action="store_true", help="CONTROL: plant defects in a copy and prove detection"
    )
    parser.add_argument("--scratch", default=None, help="scratch directory for --self-test")
    parser.add_argument(
        "--plant-rename",
        default=None,
        metavar="FILE",
        help="CONTROL: use FILE as the fixture instead of the default one",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    workspace = Path(args.root).resolve()
    if not workspace.is_dir():
        print(f"REFUSED: --root {workspace} is not a directory", file=sys.stderr)
        return 2

    if args.self_test:
        scratch = Path(args.scratch) if args.scratch else None
        return self_test(workspace, scratch, Path(args.plant_rename) if args.plant_rename else None)

    repositories = tuple(args.repositories) if args.repositories else REPOSITORIES
    missing = [r for r in repositories if r != "." and not (workspace / r).is_dir()]
    if missing:
        print(f"REFUSED: --repo names not present: {', '.join(missing)}", file=sys.stderr)
        return 2

    hits, reports, scanned, skipped = sweep(workspace, repositories, args.max_file_bytes)

    if args.json:
        print(json.dumps(
            {
                "scanned": scanned,
                "hitCount": len(hits),
                "distinctNames": sorted({h.name for h in hits}),
                "hits": [
                    {
                        "path": h.path, "line": h.line, "col": h.col, "name": h.name,
                        "kind": h.kind, "inTypeChecking": h.in_type_checking, "context": h.context,
                    }
                    for h in hits
                ],
                "filesWithErrors": [
                    {"path": r.path, "repo": r.repo, "error": r.error} for r in reports if r.error
                ],
                "filesWithStarImports": [
                    {"path": r.path, "starImports": r.star_imports} for r in reports if r.star_imports
                ],
                "annotationsSkipped": sum(r.annotations_skipped for r in reports),
                "skippedRepositories": list(skipped),
            },
            indent=2,
        ))
    else:
        print(render_markdown(hits, reports, scanned, args.max_hits, skipped))
    return 1 if hits else 0


if __name__ == "__main__":
    raise SystemExit(main())
