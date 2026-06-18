"""
LLM-based video/clip annotator.

For source-video annotation (not the main loop path — the parser handles
text-only candidates). Use this when you have actual clip descriptions,
frame strips, or pose summaries from a source recording.
"""

from __future__ import annotations
import json
from schema import SegmentAnnotation, EventAnnotation
from ontology import ACTION_LABELS, FORMATION_LABELS, LEVEL_LABELS, INTENT_LABELS, ACTION_DEFINITIONS
from llm_client import get_client, chat

_SYSTEM = f"""You are a choreography video annotator.
Your task: annotate a clip into structured evidence for a verifier program.

Rules:
1. Do not judge beauty or quality. Mark only visible movement, formation, level, and plausible intent.
2. Separate observed movement (observed_actions) from interpreted intent (intent).
3. Use ONLY the allowed labels. Lower confidence if uncertain; never invent labels.
4. Mark abstract motifs, not exact poses.
5. Return valid JSON only — no markdown fences.

Context: Buddhist devotional/spiritual narrative.
Phases: A=mourning, B=remembrance/compassion, C=Dharma continuation/protection,
        D=crisis/appeal, E=prayer/awakening/vow, F=final unity.

Key gesture definitions:
{chr(10).join(f'  {k}: {v}' for k, v in ACTION_DEFINITIONS.items())}

Allowed action labels: {json.dumps(ACTION_LABELS)}
Allowed formation labels: {json.dumps(FORMATION_LABELS)}
Allowed level labels: {json.dumps(LEVEL_LABELS)}
Allowed intent labels: {json.dumps(INTENT_LABELS)}

Return schema:
{{
  "segment_id": "<auto>",
  "start": <float>,
  "end": <float>,
  "lyric_text": "<lyrics>",
  "phase_guess": "<A-F>",
  "formation": ["<label>"],
  "level": ["<label>"],
  "observed_actions": ["<label>"],
  "intent": ["<label>"],
  "events": [
    {{"start": <float>, "end": <float>, "label": "<label>", "evidence": "<text>", "confidence": <float>}}
  ],
  "confidence": {{"timing": <float>, "movement": <float>, "formation": <float>, "intent": <float>}},
  "evidence": [{{"time": <float>, "observation": "<text>"}}],
  "notes": "<optional>"
}}"""


def _strip_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        parts = text.split("```")
        body = parts[1]
        if body.startswith("json"):
            body = body[4:]
        return body.strip()
    return text


def annotate_segment(
    start: float,
    end: float,
    lyric: str,
    description: str = "",
    segment_id: str | None = None,
) -> SegmentAnnotation:
    """
    Annotate a single clip segment.

    description: free-text notes about what is visible (from frames, pose data,
    or a human observer). If empty, the LLM reasons from lyric + phase context.
    """
    client = get_client()
    user_msg = (
        f"Annotate this clip segment:\n\n"
        f"start: {start}\nend: {end}\nlyrics: {lyric}\n"
        f"description: {description if description else '(no visual description — infer from lyric/phase context)'}"
    )

    raw = chat(client, _SYSTEM, user_msg, max_tokens=1024)
    d = json.loads(_strip_fences(raw))

    events = [
        EventAnnotation(
            start=float(e.get("start", start)),
            end=float(e.get("end", end)),
            label=e["label"],
            evidence=e.get("evidence", ""),
            confidence=float(e.get("confidence", 0.7)),
        )
        for e in d.get("events", [])
    ]

    return SegmentAnnotation(
        segment_id=segment_id or d.get("segment_id", f"src_{int(start)}_{int(end)}"),
        start=float(d.get("start", start)),
        end=float(d.get("end", end)),
        lyric_text=d.get("lyric_text", lyric),
        phase_guess=d.get("phase_guess"),
        formation=d.get("formation", []),
        level=d.get("level", []),
        observed_actions=d.get("observed_actions", []),
        intent=d.get("intent", []),
        events=events,
        confidence=d.get("confidence", {"timing": 0.7, "movement": 0.7, "formation": 0.7, "intent": 0.7}),
        evidence=d.get("evidence", []),
        notes=d.get("notes", ""),
        source="reference_video",
    )
