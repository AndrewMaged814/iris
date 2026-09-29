"""Shared setup for Iris's cron scripts: find the plugin modules and the data folder.

Scripts live in <profile>/scripts and the plugin in <profile>/plugins/iris (same layout in the repo),
so both resolve to the same <profile>/iris/iris.db whichever process runs them.
"""
import os
import sys
from pathlib import Path

PROFILE_HOME = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROFILE_HOME / "plugins" / "iris"))
os.environ.setdefault("IRIS_DATA_DIR", str(PROFILE_HOME / "iris"))
