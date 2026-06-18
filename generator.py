"""
LLM choreography generator.

Produces and revises choreography tables (markdown) that the parser then
converts into SegmentAnnotation objects for verification.
"""

from __future__ import annotations
from schema import PieceContract, VerifierResult
from llm_client import get_client, chat

_SYSTEM = """You are a choreography designer for a Buddhist devotional dance piece.

Narrative arc:
  A (0–43s):    Opening grief — Buddha enters nirvana. Bowed, kneeling, sacred shock.
  B (28–135s):  Remembrance — compassion, devotion, gentle searching.
  C (135–162s): Who will continue? Compact group, circular DHARMA_WHEEL motif, resolve.
  D (154–218s): Crisis — temptation, confusion, suffering, pleading appeal.
  E (218–268s): Collective prayer → awakening → vow. Kneeling then rising.
  F (260–344s): Final unity — Dharma endures. Broad formation, final tableau.

Spatial arc: low mourning → open remembrance → compact responsibility
             → staggered crisis → kneeling prayer → broad unified final.

Hard requirements:
  • DHARMA_WHEEL motif (circular hand gesture) must appear in phase C near "谁来转法轮"
  • Collective prayer (KNEEL + PRAYER_PALMS) must appear in phase E
  • FINAL_TABLEAU (held still unified pose) must end phase F
  • Phase A must open with low/bowed/kneeling energy — NOT celebratory

Output format — markdown table with these columns (no preamble, no explanation):
| Time (mm:ss–mm:ss) | Lyrics | Formation | Movement/Actions | Intent |"""


def generate_choreography(contract: PieceContract) -> str:
    """Generate an initial candidate choreography table."""
    client = get_client()
    prompt = (
        f"Generate a complete choreography table for this piece.\n\n"
        f"Duration: {int(contract.duration // 60)}:{int(contract.duration % 60):02d}\n"
        f"Contract phases: {[p.phase + ' ' + p.name for p in contract.phases]}\n\n"
        "Cover all 6 phases A–F in sequence. "
        "Use roughly 3–5 rows per phase. "
        "Return ONLY the markdown table."
    )
    return chat(client, _SYSTEM, prompt, max_tokens=3000)


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
        "3. Hard failures MUST be fixed (DHARMA_WHEEL in C, PRAYER_PALMS+KNEEL in E, FINAL_TABLEAU in F).\n"
        "Return ONLY the complete revised markdown table."
    )
    return chat(client, _SYSTEM, prompt, max_tokens=3000)
