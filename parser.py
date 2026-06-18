"""
Parse a free-text choreography table into structured SegmentAnnotation objects.

The LLM maps natural language descriptions (from a human-written table or
a generator's output) onto the controlled ontology so the verifier can score it.
"""

from __future__ import annotations
import json
from schema import SegmentAnnotation, EventAnnotation
from ontology import ACTION_LABELS, FORMATION_LABELS, LEVEL_LABELS, INTENT_LABELS
from llm_client import get_client, chat

_SYSTEM = f"""You are a choreography annotation parser.
Convert free-text choreography descriptions into structured JSON arrays.

Each row / phrase becomes one segment object. Map natural language to allowed labels:
- "kneeling" → KNEEL
- "hands in prayer" / "palms together" → PRAYER_PALMS
- "wheel-turning hand motion" / "circular arm motion" → DHARMA_WHEEL
- "group moving forward" → ADVANCING_LINE
- "scattered / stumbling / confused" → STAGGERED_GROUP, SWAY_CONFUSION
- "final held still pose" → FINAL_TABLEAU
- "arms open wide" → OUTWARD_OPENING
- "arms reach up" → UPWARD_REACH
- "hands on heart" → CHEST_TOUCH
- "shielding or protective gesture" → SHIELDING

Time: convert mm:ss → seconds (02:15 = 135.0). If only one timestamp, infer duration from context.

Allowed action labels: {json.dumps(ACTION_LABELS)}
Allowed formation labels: {json.dumps(FORMATION_LABELS)}
Allowed level labels: {json.dumps(LEVEL_LABELS)}
Allowed intent labels: {json.dumps(INTENT_LABELS)}

Return ONLY a valid JSON array (no markdown fences, no extra text):
[
  {{
    "start": <seconds float>,
    "end": <seconds float>,
    "lyric_text": "<lyrics>",
    "phase_guess": "<A|B|C|D|E|F or null>",
    "formation": ["<label>"],
    "level": ["<label>"],
    "observed_actions": ["<label>"],
    "intent": ["<label>"],
    "events": [],
    "confidence": {{"timing": 0.8, "movement": 0.75, "formation": 0.7, "intent": 0.7}},
    "evidence": [],
    "notes": ""
  }}
]"""


def _strip_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        parts = text.split("```")
        body = parts[1]
        if body.startswith("json"):
            body = body[4:]
        return body.strip()
    return text


def parse_choreography_text(text: str) -> list[SegmentAnnotation]:
    """Convert a text choreography table into SegmentAnnotation objects."""
    client = get_client()
    raw = chat(client, _SYSTEM, f"Parse this choreography:\n\n{text}", max_tokens=8000)

    cleaned = _strip_fences(raw)
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        # Truncated response — try to close the array at the last complete object
        for end in range(len(cleaned), 0, -1):
            try:
                data = json.loads(cleaned[:end] + "]")
                break
            except json.JSONDecodeError:
                continue
        else:
            raise ValueError(f"Could not parse choreography JSON: {cleaned[:200]}")

    segments = []
    for i, d in enumerate(data):
        raw_events = d.get("events", [])
        events = [
            EventAnnotation(
                start=float(e.get("start", d.get("start", 0))),
                end=float(e.get("end", d.get("end", 0))),
                label=e["label"],
                evidence=e.get("evidence", ""),
                confidence=float(e.get("confidence", 0.7)),
            )
            for e in raw_events
            if isinstance(e, dict) and "label" in e
        ]
        seg = SegmentAnnotation(
            segment_id=f"cand_{i:03d}",
            start=float(d.get("start", 0)),
            end=float(d.get("end", 0)),
            lyric_text=d.get("lyric_text", ""),
            phase_guess=d.get("phase_guess"),
            formation=d.get("formation", []),
            level=d.get("level", []),
            observed_actions=d.get("observed_actions", []),
            intent=d.get("intent", []),
            events=events,
            confidence=d.get("confidence", {"timing": 0.8, "movement": 0.75, "formation": 0.7, "intent": 0.7}),
            evidence=d.get("evidence", []),
            notes=d.get("notes", ""),
            source="candidate",
        )
        segments.append(seg)
    return segments
