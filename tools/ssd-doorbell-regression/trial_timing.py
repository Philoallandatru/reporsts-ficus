import json
import math


def tool_wait_seconds(events):
    intervals = []
    for line in events:
        try:
            entry = json.loads(line)
        except ValueError:
            continue
        message = entry.get("message", {})
        duration, finished = message.get("durationMs"), message.get("timestamp")
        if (entry.get("type") == "message_end" and message.get("role") == "toolResult"
                and message.get("toolName", "").startswith("spec_") and type(finished) is int
                and type(duration) in (int, float) and math.isfinite(duration) and duration >= 0):
            intervals.append((finished - duration, finished))
    elapsed = 0.0
    end = -math.inf
    for start, finish in sorted(intervals):
        if finish > end:
            elapsed += finish - max(start, end)
            end = finish
    return elapsed / 1000


def phases(total, first_model, review, prefetch, tool_wait, *, direct_signoff=False):
    waited = min(first_model, tool_wait)
    generation = first_model - waited
    return {"retrieval": round(prefetch + waited, 3), "draft": 0 if direct_signoff else round(generation, 3),
            "review": round(review + (generation if direct_signoff else 0), 3),
            "other": round(max(0, total - first_model - review - prefetch), 3)}
