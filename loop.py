"""
Agentic choreography improvement loop.

Cycle:
  1. Generate (or accept) a candidate choreography table.
  2. Parse the table into SegmentAnnotation objects.
  3. Verify against the piece contract.
  4. If not passing, generate targeted feedback and revise.
  5. Repeat until passing or max_iterations reached.
"""

from __future__ import annotations
from schema import PieceContract, VerifierResult
from parser import parse_choreography_text
from verifier import verify_candidate
from generator import generate_choreography, revise_choreography


def run(
    contract: PieceContract,
    initial_candidate: str | None = None,
    max_iterations: int = 5,
    verbose: bool = True,
) -> tuple[str, VerifierResult]:
    """
    Run the choreography improvement loop.

    Returns (best_choreography_text, best_verifier_result).
    """

    def log(msg: str) -> None:
        if verbose:
            print(msg)

    candidate = initial_candidate
    if candidate is None:
        log("Generating initial choreography...")
        candidate = generate_choreography(contract)

    best_candidate = candidate
    best_result: VerifierResult | None = None

    for iteration in range(1, max_iterations + 1):
        log(f"\n{'='*60}")
        log(f"Iteration {iteration}/{max_iterations}")
        log(f"{'='*60}")
        log("Parsing candidate...")

        trace = parse_choreography_text(candidate)
        log(f"  {len(trace)} segments parsed.")

        log("Verifying...")
        result = verify_candidate(trace, contract)
        result.iteration = iteration

        log(result.summary())

        if best_result is None or result.score > best_result.score:
            best_result = result
            best_candidate = candidate

        if result.passed:
            log(f"\nPASSED on iteration {iteration}.")
            break

        if iteration < max_iterations:
            log("\nRevising choreography...")
            candidate = revise_choreography(candidate, result, contract)
        else:
            log(f"\nMax iterations reached. Best score: {best_result.score}/100.")

    return best_candidate, best_result
