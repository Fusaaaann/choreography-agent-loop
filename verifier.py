"""Verifier: scores a candidate annotation trace against a piece contract."""

from __future__ import annotations
from schema import SegmentAnnotation, PhaseContract, PieceContract, PhaseResult, VerifierResult


def has_label(
    trace: list[SegmentAnnotation],
    start: float,
    end: float,
    label: str,
    fields: tuple[str, ...] = ("observed_actions", "formation", "intent"),
) -> bool:
    for seg in trace:
        if seg.start < end and seg.end > start:
            for f in fields:
                if label in getattr(seg, f, []):
                    return True
            for event in seg.events:
                if event.label == label:
                    return True
    return False


def has_any(
    trace: list[SegmentAnnotation],
    start: float,
    end: float,
    labels: list[str],
    fields: tuple[str, ...] = ("observed_actions", "formation", "intent"),
) -> bool:
    return any(has_label(trace, start, end, lbl, fields) for lbl in labels)


def _score_groups(
    trace: list[SegmentAnnotation],
    start: float,
    end: float,
    groups: list[list[str]],
    fields: tuple[str, ...] = ("observed_actions", "formation", "intent"),
) -> tuple[float, list[list[str]]]:
    if not groups:
        return 1.0, []
    hits = 0
    missing = []
    for group in groups:
        if has_any(trace, start, end, group, fields):
            hits += 1
        else:
            missing.append(group)
    return hits / len(groups), missing


def score_phase(trace: list[SegmentAnnotation], contract: PhaseContract) -> PhaseResult:
    start, end = contract.time_window

    motif_score, missing_motifs = _score_groups(trace, start, end, contract.required_motif_groups)
    intent_score, missing_intents = _score_groups(
        trace, start, end, [[x] for x in contract.required_intents]
    )
    formation_score = 1.0 if has_any(
        trace, start, end, contract.required_formations_any, fields=("formation",)
    ) else 0.0

    lyric_text = " ".join(
        seg.lyric_text for seg in trace if seg.start < end and seg.end > start
    )
    lyric_hits = sum(1 for anchor in contract.lyric_anchors if anchor in lyric_text)
    lyric_score = lyric_hits / max(1, len(contract.lyric_anchors))

    total = (
        0.25 * lyric_score
        + 0.35 * motif_score
        + 0.20 * intent_score
        + 0.20 * formation_score
    )

    feedback = []
    if motif_score < 0.7:
        feedback.append(f"Weak motifs — missing: {missing_motifs}")
    if intent_score < 0.7:
        feedback.append(f"Weak intent — missing: {missing_intents}")
    if not formation_score:
        feedback.append(f"No expected formation. Need one of: {contract.required_formations_any}")
    if lyric_score < 0.4:
        feedback.append(f"Low lyric coverage ({lyric_hits}/{len(contract.lyric_anchors)} anchors). Need: {contract.lyric_anchors}")

    return PhaseResult(
        phase=contract.phase,
        name=contract.name,
        score=round(total * 100, 1),
        missing_motifs=missing_motifs,
        missing_intents=missing_intents,
        formation_ok=bool(formation_score),
        lyric_score=lyric_score,
        weight=contract.weight,
        feedback=feedback,
    )


def _check_hard_requirements(
    trace: list[SegmentAnnotation],
    phase_results: list[PhaseResult],
    contract: PieceContract,
) -> list[str]:
    failures = []
    for result, phase in zip(phase_results, contract.phases):
        s, e = phase.time_window
        for req in phase.hard_requirements:
            if req == "must_have_dharma_wheel_near_lyric":
                if not has_label(trace, s, e, "DHARMA_WHEEL"):
                    failures.append(f"[Phase {phase.phase}] Missing DHARMA_WHEEL motif near 谁来转法轮.")
            elif req == "must_have_collective_prayer":
                if not has_any(trace, s, e, ["KNEEL", "PRAYER_PALMS"]):
                    failures.append(f"[Phase {phase.phase}] Missing collective prayer (KNEEL or PRAYER_PALMS).")
            elif req == "must_end_with_unified_still_tableau":
                if not has_any(trace, s, e, ["FINAL_TABLEAU", "FINAL_UPLIFT"]):
                    failures.append(f"[Phase {phase.phase}] Missing final unified still tableau.")
            elif req == "must_have_low_mourning_image":
                low_labels = ["LOW_LEVEL", "KNEELING_LEVEL", "PROSTRATED_LEVEL", "BOWED_BODY", "KNEEL", "PROSTRATION"]
                if not has_any(trace, s, e, low_labels):
                    failures.append(f"[Phase {phase.phase}] Missing low mourning image (bowed/kneeling).")
            elif req == "must_not_open_with_celebratory_high_energy":
                phase_segs = sorted(
                    [seg for seg in trace if seg.start < e and seg.end > s],
                    key=lambda x: x.start,
                )
                if phase_segs:
                    first = phase_segs[0]
                    grief_actions = {"BOWED_BODY", "KNEEL", "PROSTRATION", "STILLNESS", "CHEST_TOUCH"}
                    if "HIGH_LEVEL" in first.level and not grief_actions.intersection(first.observed_actions):
                        failures.append(f"[Phase {phase.phase}] Opening must not be celebratory high-energy.")
    return failures


def verify_candidate(
    trace: list[SegmentAnnotation],
    contract: PieceContract,
) -> VerifierResult:
    phase_results = [score_phase(trace, phase) for phase in contract.phases]

    weighted_total = sum(r.score * p.weight for r, p in zip(phase_results, contract.phases))
    total_weight = sum(p.weight for p in contract.phases)
    final_score = weighted_total / total_weight if total_weight else 0.0

    hard_failures = _check_hard_requirements(trace, phase_results, contract)
    feedback = _make_feedback(phase_results, hard_failures)

    return VerifierResult(
        score=round(final_score, 1),
        passed=final_score >= 80.0 and not hard_failures,
        phase_results=phase_results,
        hard_failures=hard_failures,
        feedback=feedback,
    )


def _make_feedback(phase_results: list[PhaseResult], hard_failures: list[str]) -> list[str]:
    feedback = [f"HARD FAILURE: {hf}" for hf in hard_failures]
    for result in phase_results:
        if result.score < 75:
            feedback.append(
                f"Phase {result.phase} ({result.name}) — {result.score}/100. "
                + "; ".join(result.feedback)
            )
    if not feedback:
        feedback.append("All phases pass threshold. Fine-tune for higher score.")
    return feedback
