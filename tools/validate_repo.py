#!/usr/bin/env python3
"""Checks that keep the repo honest. Covers tracked and non-ignored untracked source files.

- every skill has a name matching its folder and a description starting with "Use when"
- skill bodies stay under 200 lines and linked references exist
- no secrets or private paths in tracked files
- no model or provider pinned in config.yaml
- exactly the history and calculation tools are registered
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SECRET = re.compile(r"(shpat_|shpss_)[A-Za-z0-9]{8,}|\b\d{8,10}:[A-Za-z0-9_-]{30,}\b|-----BEGIN [A-Z ]*PRIVATE KEY|/home/[a-z]+/|\bsk-lf-[a-f0-9-]{20,}|\bgh[pousr]_[A-Za-z0-9]{30,}|\bgithub_pat_[A-Za-z0-9_]{30,}|\bsk-(?:proj-|ant-)?[A-Za-z0-9_-]{32,}")
TOOLS = {"read_store", "watchlist", "market_changes", "market_math"}


def tracked() -> list[Path]:
    try:
        out = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
        files = [ROOT / line for line in out.splitlines() if line]
        if files:
            return files
    except (OSError, subprocess.CalledProcessError):
        pass
    return [p for p in ROOT.rglob("*") if p.is_file() and ".git" not in p.parts and "__pycache__" not in p.parts]


def main() -> int:
    problems = []
    files = tracked()
    for skill in sorted((ROOT / "skills").glob("*/SKILL.md")):
        text = skill.read_text(encoding="utf-8")
        head = re.match(r"^---\n(.*?)\n---\n", text, re.S)
        meta = dict(re.findall(r"^(\w+):\s*(.+)$", head.group(1), re.M)) if head else {}
        if meta.get("name") != skill.parent.name:
            problems.append(f"{skill}: name must be '{skill.parent.name}'")
        if not meta.get("description", "").startswith("Use when"):
            problems.append(f"{skill}: description must start with 'Use when'")
        if text.count("\n") > 200:
            problems.append(f"{skill}: longer than 200 lines")
        for ref in re.findall(r"`(references/[^`]+)`", text):
            if not (skill.parent / ref).exists():
                problems.append(f"{skill}: missing {ref}")
    for f in files:
        if f.suffix in {".png", ".jpg", ".gif", ".webp"} or f.name == "validate_repo.py":
            continue
        try:
            if SECRET.search(f.read_text(encoding="utf-8")):
                problems.append(f"{f.relative_to(ROOT)}: looks like a secret or a private path")
        except (UnicodeDecodeError, OSError):
            pass
    config = (ROOT / "config.yaml").read_text()
    if re.search(r'^model:\s*"?[^"\s]', config, re.M):
        problems.append("config.yaml: don't pin a model; the operator chooses it")
    plugin = (ROOT / "plugins" / "iris" / "__init__.py").read_text()
    handlers = set(re.findall(r'"(\w+)": \w+_tool', plugin))
    if handlers != TOOLS:
        problems.append(f"plugin tools {sorted(handlers)} differ from the declared tool set")
    for p in problems:
        print("FAIL", p)
    print("ok" if not problems else f"{len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
