"""
choreography-agent-loop — CLI entry point.

Usage:
  # Full auto-loop (generate + verify + revise)
  python main.py

  # Feed an existing candidate choreography
  python main.py --candidate my_choreo.txt

  # Use a custom contract
  python main.py --contract my_contract.json

  # Save output
  python main.py --output result.txt --max-iter 3

  # Print the default contract and exit
  python main.py --show-contract
"""

from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

from contract_builder import load_default_contract, load_contract_file
from schema import PieceContract
import loop as agent_loop


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Choreography agentic improvement loop",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--contract", help="Path to contract JSON file (default: built-in Buddhist dance contract)")
    parser.add_argument("--candidate", help="Path to candidate choreography text file (default: auto-generate)")
    parser.add_argument("--max-iter", type=int, default=5, help="Max improvement iterations (default: 5)")
    parser.add_argument("--output", help="Save final choreography to this file")
    parser.add_argument("--show-contract", action="store_true", help="Print the contract and exit")
    parser.add_argument("--quiet", action="store_true", help="Suppress iteration logs")
    args = parser.parse_args()

    # Load contract
    if args.contract:
        contract = load_contract_file(args.contract)
    else:
        contract = load_default_contract()

    if args.show_contract:
        print(json.dumps(contract.to_dict(), ensure_ascii=False, indent=2))
        return

    print(f"Contract : {contract.piece_title}")
    print(f"Duration : {int(contract.duration // 60)}:{int(contract.duration % 60):02d}")
    print(f"Phases   : {[p.phase + ' – ' + p.name for p in contract.phases]}")
    print(f"Max iter : {args.max_iter}")

    # Load candidate
    initial_candidate: str | None = None
    if args.candidate:
        initial_candidate = Path(args.candidate).read_text()
        print(f"Candidate: {args.candidate} ({len(initial_candidate)} chars)")

    # Run loop
    final_choreo, final_result = agent_loop.run(
        contract=contract,
        initial_candidate=initial_candidate,
        max_iterations=args.max_iter,
        verbose=not args.quiet,
    )

    # Summary
    print(f"\n{'='*60}")
    print("FINAL RESULT")
    print(f"{'='*60}")
    print(final_result.summary())

    if args.output:
        Path(args.output).write_text(final_choreo)
        print(f"\nChoreography saved → {args.output}")
    else:
        print("\n" + "─" * 60)
        print("FINAL CHOREOGRAPHY")
        print("─" * 60)
        print(final_choreo)


if __name__ == "__main__":
    main()
