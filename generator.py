"""
LLM choreography generator.

Produces and revises choreography tables (markdown) that the parser then
converts into SegmentAnnotation objects for verification.
"""

from __future__ import annotations
from schema import PieceContract, VerifierResult
from llm_client import get_client, chat


def _build_system_prompt(contract: PieceContract) -> str:
    phase_lines = "\n".join(
        f"  {p.phase} ({int(p.time_window[0])}–{int(p.time_window[1])}s):  "
        f"{p.name} — {p.core_function}"
        for p in contract.phases
    )
    hard_reqs = "\n".join(
        f"  • [{p.phase}] {req}"
        for p in contract.phases
        for req in p.hard_requirements
    )
    return (
        f'You are a choreography designer for a devotional dance piece titled "{contract.piece_title}".\n\n'
        "Narrative arc:\n"
        f"{phase_lines}\n\n"
        + ("Hard requirements:\n" + hard_reqs + "\n\n" if hard_reqs else "")
        + "Output format — markdown table with these columns (no preamble, no explanation):\n"
        "| Time (mm:ss–mm:ss) | Lyrics | Formation | Movement/Actions | Intent |"
    )


def generate_choreography(contract: PieceContract) -> str:
    """Generate an initial candidate choreography table."""
    client = get_client()
    prompt = (
        f"Generate a complete choreography table for this piece.\n\n"
        f"Duration: {int(contract.duration // 60)}:{int(contract.duration % 60):02d}\n"
        f"Contract phases: {[p.phase + ' ' + p.name for p in contract.phases]}\n\n"
        f"Cover all {len(contract.phases)} phases in sequence. "
        "Use roughly 3–5 rows per phase. "
        "Return ONLY the markdown table."
    )
    return chat(client, _build_system_prompt(contract), prompt, max_tokens=3000)


def revise_choreography(
    current: str,
    result: VerifierResult,
    contract: PieceContract,
) -> str:
    """Revise a choreography table to address verifier feedback."""
    client = get_client()
    weak_phases = [
        f"Phase {pr.phase} ({pr.name}): {pr.score}/100\n"
        f"  Missing motifs: {pr.missing_motifs}\n"
        f"  Missing intents: {pr.missing_intents}\n"
        f"  Formation OK: {pr.formation_ok}\n"
        f"  Feedback: {'; '.join(pr.feedback)}"
        for pr in result.phase_results
        if pr.score < 80
    ]

    prompt = (
        f"Revise this choreography to fix the verifier's findings.\n\n"
        f"CURRENT CHOREOGRAPHY:\n{current}\n\n"
        f"SCORE: {result.score}/100 | PASS: {result.passed}\n\n"
        "HARD FAILURES:\n" + ("\n".join(result.hard_failures) if result.hard_failures else "None") + "\n\n"
        "WEAK PHASES:\n" + ("\n\n".join(weak_phases) if weak_phases else "None") + "\n\n"
        "Instructions:\n"
        "1. Keep phases that scored ≥ 80 unchanged.\n"
        "2. Fix ONLY the weak/failed phases — address each missing element explicitly.\n"
        "3. Hard failures MUST be fixed.\n"
        "Return ONLY the complete revised markdown table."
    )
    return chat(client, _build_system_prompt(contract), prompt, max_tokens=3000)
