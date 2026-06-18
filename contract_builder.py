"""Builds and loads piece contracts."""

from __future__ import annotations
import json
from pathlib import Path
from schema import PhaseContract, PieceContract

_HERE = Path(__file__).parent
_DEFAULT_CONTRACT_PATH = _HERE / "default_contract.json"
_EXAMPLE_CONTRACT_PATH = _HERE / "default_contract.example.json"


def load_default_contract() -> PieceContract:
    """Load the default contract from default_contract.json (git-ignored).

    Copy default_contract.example.json → default_contract.json and fill in
    your piece details to get started.
    """
    if not _DEFAULT_CONTRACT_PATH.exists():
        raise FileNotFoundError(
            f"No default contract found at {_DEFAULT_CONTRACT_PATH}.\n"
            f"Copy {_EXAMPLE_CONTRACT_PATH.name} → default_contract.json "
            "and fill in your piece details, or pass --contract <file>."
        )
    with open(_DEFAULT_CONTRACT_PATH) as f:
        return PieceContract.from_dict(json.load(f))


def load_contract_file(path: str) -> PieceContract:
    with open(path) as f:
        return PieceContract.from_dict(json.load(f))


def build_contract_from_annotations(
    annotations: list,
    piece_title: str = "Derived Contract",
) -> PieceContract:
    """Derive a contract from source video annotations, falling back to defaults."""
    contract = load_default_contract()
    contract.piece_title = piece_title
    return contract
