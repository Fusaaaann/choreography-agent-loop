"""
Source-video annotator with vision.

Sends extracted frames to Claude claude-sonnet-4-6 (via OpenRouter vision) for each phase,
produces structured SegmentAnnotation objects (the "reference trace"),
then runs the agentic generation + verification loop on a fresh candidate.

Usage:
  python annotate_video.py --frames-dir /tmp/choreo_frames [--max-iter 3]
"""

from __future__ import annotations
import argparse
import base64
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from schema import SegmentAnnotation, EventAnnotation
from contract_builder import load_default_contract
from verifier import verify_candidate
import loop as agent_loop
from ontology import ACTION_LABELS, FORMATION_LABELS, LEVEL_LABELS, INTENT_LABELS, ACTION_DEFINITIONS
from llm_client import get_client, chat

# Phase metadata: (phase_label, name, time_window_sec, lyric_anchor, frame_keys)
PHASES = [
    ("A", "Nirvana mourning",           (0,   43),  "释迦入灭了",  ["A1", "A2"]),
    ("B", "Remembrance and compassion", (28,  135), "忆念/众生",   ["B1", "B2"]),
    ("C", "Dharma continuation",        (135, 162), "谁来转法轮",  ["C1", "C2"]),
    ("D", "Crisis and appeal",          (154, 218), "诱惑/佛陀",   ["D1", "D2"]),
    ("E", "Prayer, awakening, vow",     (218, 268), "祈求/唤醒",   ["E1", "E2"]),
    ("F", "Final unity",                (260, 344), "正法必久住",  ["F1", "F2"]),
]

_ANNOTATE_SYSTEM = f"""You are a choreography video annotator for a Buddhist devotional dance.

Rules:
1. Mark only what is VISIBLE — movement, formation, body level. Separate observation from interpretation.
2. Use ONLY the allowed labels below. No free-form labels.
3. Lower confidence if unclear. Add evidence notes.
4. Return valid JSON only — no markdown fences.

Key gesture definitions:
{chr(10).join(f'  {k}: {v}' for k, v in ACTION_DEFINITIONS.items())}

Allowed action labels: {json.dumps(ACTION_LABELS)}
Allowed formation labels: {json.dumps(FORMATION_LABELS)}
Allowed level labels: {json.dumps(LEVEL_LABELS)}
Allowed intent labels: {json.dumps(INTENT_LABELS)}

Return schema:
{{
  "segment_id": "<string>",
  "start": <float>,
  "end": <float>,
  "lyric_text": "<lyrics>",
  "phase_guess": "<A|B|C|D|E|F>",
  "formation": ["<label>"],
  "level": ["<label>"],
  "observed_actions": ["<label>"],
  "intent": ["<label>"],
  "events": [
    {{"start":<float>,"end":<float>,"label":"<label>","evidence":"<text>","confidence":<float>}}
  ],
  "confidence": {{"timing":<float>,"movement":<float>,"formation":<float>,"intent":<float>}},
  "evidence": [{{"time":<float>,"observation":"<text>"}}],
  "notes": "<optional>"
}}"""


def _encode_image(path: Path) -> str:
    return base64.standard_b64encode(path.read_bytes()).decode("utf-8")


def _strip_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        body = text.split("```")[1]
        if body.startswith("json"):
            body = body[4:]
        return body.strip()
    return text


def annotate_phase_with_frames(
    phase: str,
    name: str,
    time_window: tuple[float, float],
    lyric_anchor: str,
    frame_paths: list[Path],
) -> SegmentAnnotation:
    """Send frames to Claude claude-sonnet-4-6 vision (via OpenRouter) and get structured annotation."""
    client = get_client()
    start, end = time_window

    content: list[dict] = []
    for path in frame_paths:
        if path.exists():
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{_encode_image(path)}"},
            })

    content.append({
        "type": "text",
        "text": (
            f"Annotate phase {phase} ({name}) of a Buddhist devotional dance.\n"
            f"Time window: {start}s – {end}s\n"
            f"Lyric anchor: {lyric_anchor}\n"
            f"The images show representative frames from this section.\n"
            f"Return the JSON annotation object."
        ),
    })

    raw = chat(client, _ANNOTATE_SYSTEM, content, max_tokens=2048)
    try:
        d = json.loads(_strip_fences(raw))
    except json.JSONDecodeError:
        # Try to recover a partial object by finding the last complete field
        text = _strip_fences(raw)
        # Truncate to last complete key-value pair before the error
        for end in range(len(text), 0, -1):
            try:
                d = json.loads(text[:end] + "}")
                break
            except json.JSONDecodeError:
                continue
        else:
            # Hard fallback: return a minimal annotation
            d = {
                "start": start, "end": end, "lyric_text": lyric_anchor,
                "phase_guess": phase, "formation": [], "level": [],
                "observed_actions": [], "intent": [], "events": [],
                "confidence": {"timing": 0.5, "movement": 0.5, "formation": 0.5, "intent": 0.5},
                "evidence": [], "notes": "parse error — partial response",
            }

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
        segment_id=d.get("segment_id", f"src_{phase}"),
        start=float(d.get("start", start)),
        end=float(d.get("end", end)),
        lyric_text=d.get("lyric_text", lyric_anchor),
        phase_guess=d.get("phase_guess", phase),
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


def print_source_trace(trace: list[SegmentAnnotation]) -> None:
    print("\n" + "="*60)
    print("SOURCE VIDEO ANNOTATION TRACE")
    print("="*60)
    for seg in trace:
        print(f"\nPhase {seg.phase_guess} | {seg.start:.0f}s–{seg.end:.0f}s | {seg.lyric_text}")
        print(f"  Actions   : {seg.observed_actions}")
        print(f"  Formation : {seg.formation}")
        print(f"  Level     : {seg.level}")
        print(f"  Intent    : {seg.intent}")
        conf = seg.confidence
        print(f"  Confidence: mov={conf.get('movement',0):.2f} fmt={conf.get('formation',0):.2f} int={conf.get('intent',0):.2f}")
        if seg.notes:
            print(f"  Notes     : {seg.notes}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Annotate source video and run choreography loop")
    parser.add_argument("--frames-dir", default="/tmp/choreo_frames", help="Directory with extracted frames")
    parser.add_argument("--max-iter", type=int, default=4, help="Max generation/revision iterations")
    parser.add_argument("--output", help="Save final choreography to this file")
    parser.add_argument("--skip-annotation", action="store_true", help="Skip video annotation, go straight to generation loop")
    args = parser.parse_args()

    frames_dir = Path(args.frames_dir)
    contract = load_default_contract()
    contract.duration = 343.97

    if not args.skip_annotation:
        print(f"\nAnnotating source video frames from {frames_dir} ...")
        source_trace: list[SegmentAnnotation] = []
        for phase, name, time_window, lyric_anchor, frame_keys in PHASES:
            paths = [frames_dir / f"frame_{k}.jpg" for k in frame_keys]
            existing = [p for p in paths if p.exists()]
            print(f"  Phase {phase} ({name}) — {len(existing)}/{len(paths)} frames ...", end=" ", flush=True)
            seg = annotate_phase_with_frames(phase, name, time_window, lyric_anchor, existing)
            source_trace.append(seg)
            print("done")

        print_source_trace(source_trace)

        print("\n" + "="*60)
        print("SOURCE VIDEO SELF-VERIFICATION (sanity check)")
        print("="*60)
        src_result = verify_candidate(source_trace, contract)
        print(src_result.summary())
        print("\n(Note: snapshot-frame annotation always under-scores — actual performance is richer.)")

    # Run generation + improvement loop
    print("\n" + "="*60)
    print("RUNNING CHOREOGRAPHY GENERATION + IMPROVEMENT LOOP")
    print("="*60)

    final_choreo, final_result = agent_loop.run(
        contract=contract,
        initial_candidate=None,
        max_iterations=args.max_iter,
        verbose=True,
    )

    if args.output:
        Path(args.output).write_text(final_choreo)
        print(f"\nChoreography saved → {args.output}")

    print("\n" + "="*60)
    print("FINAL RESULT")
    print("="*60)
    print(final_result.summary())
    print("\nFINAL CHOREOGRAPHY:")
    print("─" * 60)
    print(final_choreo)


if __name__ == "__main__":
    main()
