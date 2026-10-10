"""Skip an identical search already attempted this turn. Do not otherwise gate research.

Hermes searches and reads pages. A different query is more research, including another
look at a site whose earlier leads are still unread. Blocking those calls spends a model
round and does not produce the market comparison.
"""
import json
import threading
import time
from urllib.parse import urlsplit, urlunsplit


def canonical(url):
    try:
        parts = urlsplit(url)
        if parts.scheme not in ("http", "https") or not parts.hostname:
            return None
        host = parts.hostname.lower().removeprefix("www.")
        return host, urlunsplit(("https", host, parts.path.rstrip("/") or "/", parts.query, ""))
    except (ValueError, TypeError):
        return None


def search_urls(result):
    if isinstance(result, str):
        if result.startswith("<untrusted_tool_result"):
            result = result[result.find("{"):result.rfind("}") + 1]
        try:
            result = json.loads(result)
        except ValueError:
            return []
    if not isinstance(result, dict) or result.get("error") or result.get("success") is False:
        return []
    # Native providers differ in envelopes. Only named URL/link fields count;
    # prose, snippets and instructions in them do not control the guard.
    found = []
    def walk(value):
        if isinstance(value, dict):
            for key, child in value.items():
                if key in ("url", "link") and isinstance(child, str) and canonical(child):
                    found.append(child)
                elif isinstance(child, (dict, list)):
                    walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)
    walk(result)
    return list(dict.fromkeys(found))[:30]


def _completed(result):
    data = result
    if isinstance(result, str):
        text = result[result.find("{"):result.rfind("}") + 1] if result.startswith("<untrusted_tool_result") else result
        try:
            data = json.loads(text)
        except ValueError:
            return False
    if not isinstance(data, dict) or data.get("error") or data.get("success") is False or data.get("search_executed") is False:
        return False
    return True


def _reminder(result):
    text = result if isinstance(result, str) else json.dumps(result, ensure_ascii=False)
    if len(text) <= 8000:
        return result
    return {"cached_urls": search_urls(result),
            "note": "The full result is earlier in this turn. Reuse it."}


class ResearchProgress:
    def __init__(self):
        self.lock = threading.Lock()
        self.turns = {}

    def _state(self, session_id, turn_id):
        if not session_id or not turn_id:
            return None  # older/unidentified hooks cannot safely scope a policy
        key = (session_id, turn_id)
        now = time.monotonic()
        for old_key, value in list(self.turns.items()):
            if now - value["updated"] > 1800:
                del self.turns[old_key]
        if key not in self.turns and len(self.turns) >= 128:
            del self.turns[min(self.turns, key=lambda k: self.turns[k]["updated"])]
        state = self.turns.setdefault(key, {"results": {}, "updated": now})
        state["updated"] = now
        return state

    def before(self, tool_name="", args=None, session_id="", turn_id="", **_):
        if tool_name != "web_search" or not isinstance(args, dict):
            return None
        query = " ".join(str(args.get("query", "")).lower().split())
        if not query:
            return None
        with self.lock:
            state = self._state(session_id, turn_id)
            if state is None:
                return None
            prior = state["results"].get(query)
            if prior and prior.get("pending"):
                return {"action": "block", "message": json.dumps({"error": "query_already_in_flight",
                    "search_executed": False, "recovery": "wait_for_that_search_result"})}
            if prior and prior.get("ok"):
                return {"action": "block", "message": json.dumps({"error": "query_already_completed_this_turn",
                    "search_executed": False, "cached_result": prior["result"],
                    "recovery": "use_cached_result"})}
            state["results"][query] = {"pending": True}
        return None

    def after(self, tool_name="", args=None, result=None, session_id="", turn_id="", **_):
        if tool_name != "web_search" or not isinstance(args, dict):
            return None
        query = " ".join(str(args.get("query", "")).lower().split())
        if not query:
            return None
        with self.lock:
            state = self._state(session_id, turn_id)
            if state is None:
                return None
            if _completed(result):
                state["results"][query] = {"pending": False, "ok": True, "result": _reminder(result)}
            else:
                state["results"].pop(query, None)
        return None


progress = ResearchProgress()
