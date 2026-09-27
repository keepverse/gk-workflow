"""The root template's bootstrap_skills.py, tested as shipped code.

The script is emitted into the migrated workspace by `apply`, so a defect in it is a
defect in the migration output. Its one dangerous failure mode is picking the wrong
root: an upward walk that stops at "a directory containing .agents/skills" finds a
developer's home directory on any machine with a global skill install, and then writes
symlinks into it. That is why every test here passes an explicit --root and asserts on
the refusal path as hard as on the happy path.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

TEMPLATE = (Path(__file__).resolve().parents[1]
            / "rules" / "templates" / "root" / "tools" / "bootstrap_skills.py")


def _script(tmp_path: Path) -> Path:
    assert TEMPLATE.is_file(), f"root template is missing: {TEMPLATE}"
    dst = tmp_path / "bootstrap_skills.py"
    dst.write_bytes(TEMPLATE.read_bytes())
    return dst


def _workspace(root: Path, skills: tuple[str, ...] = ("alpha", "beta"),
               marker: str | None = "AGENTS.md") -> Path:
    for name in skills:
        d = root / ".agents" / "skills" / name
        d.mkdir(parents=True)
        (d / "SKILL.md").write_text(f"skill {name}\n", encoding="utf-8")
    if marker:
        (root / marker).parent.mkdir(parents=True, exist_ok=True)
        (root / marker).write_text("root\n", encoding="utf-8")
    return root


def _run(script: Path, *args: str) -> tuple[int, dict]:
    p = subprocess.run([sys.executable, str(script), *args, "--json"],
                       capture_output=True, text=True, timeout=60)
    assert p.stdout.strip(), f"no JSON on stdout; stderr={p.stderr}"
    return p.returncode, json.loads(p.stdout)


def test_refuses_a_tree_that_is_not_a_workspace_root(tmp_path):
    """No marker: refuse, and create nothing. This is the case that reached $HOME."""
    script = _script(tmp_path)
    root = _workspace(tmp_path / "ws", marker=None)
    code, out = _run(script, "--root", str(root))
    assert code == 2
    assert out["ok"] is False
    assert "not a workspace root" in out["refusal"]
    assert not (root / ".claude").exists()
    assert not (root / ".kiro").exists()


def test_refuses_when_there_is_no_canonical_skills_tree(tmp_path):
    script = _script(tmp_path)
    root = tmp_path / "empty"
    root.mkdir()
    (root / "AGENTS.md").write_text("root\n", encoding="utf-8")
    code, out = _run(script, "--root", str(root))
    assert code == 2
    assert out["ok"] is False


def test_creates_one_alias_per_skill_per_tool_root(tmp_path):
    script = _script(tmp_path)
    root = _workspace(tmp_path / "ws")
    code, out = _run(script, "--root", str(root))
    assert code == 0 and out["ok"] is True
    assert len(out["created"]) == 4          # 2 skills x 2 tool roots
    for tool in (".claude", ".kiro"):
        link = root / tool / "skills" / "alpha"
        assert link.is_symlink()
        assert (link / "SKILL.md").read_text(encoding="utf-8") == "skill alpha\n"


def test_links_use_the_relative_form_the_legacy_repo_used(tmp_path):
    """The legacy links were ../../.agents/skills/<name>; a checkout on Windows without
    core.symlinks renders the target as text, so the form is part of the contract."""
    script = _script(tmp_path)
    root = _workspace(tmp_path / "ws")
    _run(script, "--root", str(root))
    link = root / ".claude" / "skills" / "alpha"
    assert Path(link.readlink()).parts == ("..", "..", ".agents", "skills", "alpha")


def test_check_mode_writes_nothing(tmp_path):
    script = _script(tmp_path)
    root = _workspace(tmp_path / "ws")
    code, out = _run(script, "--root", str(root), "--check")
    assert code == 0 and out["ok"] is True
    assert len(out["wouldCreate"]) == 4
    assert out["created"] == []
    assert not (root / ".claude").exists()


def test_is_idempotent(tmp_path):
    script = _script(tmp_path)
    root = _workspace(tmp_path / "ws")
    _run(script, "--root", str(root))
    code, out = _run(script, "--root", str(root))
    assert code == 0
    assert out["created"] == [] and out["repaired"] == []
    assert len(out["skipped"]) == 4


def test_never_clobbers_a_real_directory_with_a_link(tmp_path):
    script = _script(tmp_path)
    root = _workspace(tmp_path / "ws")
    _run(script, "--root", str(root))
    real = root / ".kiro" / "skills" / "alpha"
    real.unlink()                                  # remove the alias
    real.mkdir()
    (real / "SKILL.md").write_text("REAL\n", encoding="utf-8")
    code, out = _run(script, "--root", str(root))
    assert code == 0
    assert (real / "SKILL.md").read_text(encoding="utf-8") == "REAL\n"
    assert not real.is_symlink()


def test_a_dangling_alias_is_reported_broken_then_pruned(tmp_path):
    """A canonical skill deleted leaves a stale alias. It cannot be repaired - there is
    nothing to point at - so a mirror must remove it, not leave it dangling."""
    script = _script(tmp_path)
    root = _workspace(tmp_path / "ws")
    _run(script, "--root", str(root))
    assert (root / ".claude" / "skills" / "alpha").is_symlink()
    shutil.rmtree(root / ".agents" / "skills" / "alpha")   # the canonical source is gone

    code, out = _run(script, "--root", str(root), "--check")
    assert code == 1 and out["ok"] is False
    assert ".claude\\skills\\alpha" in out["broken"]
    assert ".claude\\skills\\alpha" in out["wouldPrune"]
    assert (root / ".claude" / "skills" / "alpha").is_symlink()   # check wrote nothing

    code, out = _run(script, "--root", str(root))
    assert code == 0 and out["ok"] is True
    assert ".claude\\skills\\alpha" in out["pruned"]
    assert not (root / ".claude" / "skills" / "alpha").exists()
    assert (root / ".claude" / "skills" / "beta").is_symlink()    # the rest survive


def test_a_dangling_alias_with_a_live_canonical_is_rebuilt(tmp_path):
    """Right relative form but the target vanished: rebuild it from the canonical tree."""
    script = _script(tmp_path)
    root = _workspace(tmp_path / "ws")
    _run(script, "--root", str(root))
    link = root / ".claude" / "skills" / "alpha"
    link.unlink()
    link.symlink_to("../../.agents/skills/gone")   # same shape, missing target

    code, out = _run(script, "--root", str(root))
    assert code == 0 and out["ok"] is True
    assert ".claude\\skills\\alpha" in out["repaired"]
    assert (link / "SKILL.md").read_text(encoding="utf-8") == "skill alpha\n"
