import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIX = Path(__file__).resolve().parent / "fixtures"
sys.path.insert(0, str(ROOT / "plugins" / "iris"))
sys.path.insert(0, str(ROOT / "scripts"))


def fixture(name):
    return (FIX / name).read_text(encoding="utf-8")


class FakeWeb:
    """Maps URL prefixes to (status, body). Unknown URLs return 404. Records every request."""
    def __init__(self, routes):
        self.routes, self.calls = routes, []

    def __call__(self, url):
        self.calls.append(url)
        for prefix, (status, body) in self.routes.items():
            if url.startswith(prefix):
                return status, body if isinstance(body, str) else json.dumps(body)
        return 404, "not found"
