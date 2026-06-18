"""Builds and loads piece contracts."""

from __future__ import annotations
import json
from schema import PhaseContract, PieceContract

_DEFAULT_CONTRACT: dict = {
    "piece_title": "Buddhist Devotional Dance",
    "duration": 331,
    "phases": [
        {
            "phase": "A",
            "name": "Nirvana mourning",
            "time_window": [0, 43],
            "core_function": "Establish sacred grief after Buddha's entering nirvana.",
            "lyric_anchors": ["释迦入灭了"],
            "required_motif_groups": [
                ["STILLNESS", "BOWED_BODY"],
                ["KNEEL", "PROSTRATION"],
                ["UPWARD_REACH", "OUTWARD_OPENING", "CHEST_TOUCH"],
            ],
            "required_intents": ["MOURNING", "REVERENCE"],
            "required_formations_any": ["CENTER_LEAD", "ENSEMBLE_LOW_FRAME"],
            "hard_requirements": [
                "must_have_low_mourning_image",
                "must_not_open_with_celebratory_high_energy",
            ],
            "weight": 15,
        },
        {
            "phase": "B",
            "name": "Remembrance and compassion",
            "time_window": [28, 135],
            "core_function": "Remember Buddha's compassion and effort for sentient beings.",
            "lyric_anchors": ["寂静月夜", "忆念", "四十九年", "众生", "有情"],
            "required_motif_groups": [
                ["OFFERING_GESTURE", "OUTWARD_OPENING"],
                ["CHEST_TOUCH", "HAND_TO_HEAD"],
                ["ADVANCING_STEP"],
            ],
            "required_intents": ["REMEMBRANCE", "COMPASSION"],
            "required_formations_any": ["OPEN_SEMICIRCLE", "SOLO_FOREGROUND", "WIDE_ENSEMBLE_SPREAD"],
            "hard_requirements": [],
            "weight": 15,
        },
        {
            "phase": "C",
            "name": "Dharma continuation and protection",
            "time_window": [135, 162],
            "core_function": "Ask who will turn the Dharma wheel and continue the vow.",
            "lyric_anchors": ["谁来转法轮", "谁来续悲愿", "捍卫真理", "破邪见"],
            "required_motif_groups": [
                ["DHARMA_WHEEL"],
                ["PRAYER_PALMS", "CHEST_TOUCH"],
                ["SHIELDING"],
            ],
            "required_intents": ["RESPONSIBILITY", "CONTINUATION", "PROTECTION"],
            "required_formations_any": ["COMPACT_CLUSTER", "FRONTAL_GROUP", "ADVANCING_LINE"],
            "hard_requirements": ["must_have_dharma_wheel_near_lyric"],
            "weight": 20,
        },
        {
            "phase": "D",
            "name": "Crisis and appeal",
            "time_window": [154, 218],
            "core_function": "Show temptation, confusion, suffering, and pleading.",
            "lyric_anchors": ["诱惑", "真假难辨", "山在崩", "地在裂", "血泪", "佛陀"],
            "required_motif_groups": [
                ["SWAY_CONFUSION", "INWARD_CLOSING"],
                ["SLOW_MOTION_GRIEF", "FACE_COVER", "CHEST_TOUCH"],
                ["OPEN_PALMS_APPEAL", "UPWARD_REACH"],
            ],
            "required_intents": ["CONFUSION", "SUFFERING", "PLEADING"],
            "required_formations_any": ["STAGGERED_GROUP", "LAYERED_FRONT_BACK"],
            "hard_requirements": [],
            "weight": 15,
        },
        {
            "phase": "E",
            "name": "Prayer, awakening, and vow",
            "time_window": [218, 268],
            "core_function": "Collective supplication becomes hope and moral vow.",
            "lyric_anchors": ["祈求", "请您再住世", "唤醒", "莫负佛", "莫负法"],
            "required_motif_groups": [
                ["KNEEL", "PRAYER_PALMS"],
                ["SLOW_RISE", "KNEEL_TO_RISE"],
                ["CHEST_TOUCH", "UPWARD_REACH", "OUTWARD_OPENING"],
            ],
            "required_intents": ["SUPPLICATION", "AWAKENING", "VOW", "HOPE"],
            "required_formations_any": ["KNEELING_GROUP", "FRONTAL_GROUP"],
            "hard_requirements": ["must_have_collective_prayer"],
            "weight": 20,
        },
        {
            "phase": "F",
            "name": "Final unity and enduring Dharma",
            "time_window": [260, 331],
            "core_function": "The vow expands into unified final conviction that Dharma endures.",
            "lyric_anchors": ["大行大愿", "久住", "如轮不息", "如来在心", "正法必久住"],
            "required_motif_groups": [
                ["DHARMA_WHEEL", "PRAYER_PALMS"],
                ["OUTWARD_OPENING", "FINAL_UPLIFT"],
                ["FINAL_TABLEAU"],
            ],
            "required_intents": ["UNITY", "PERSISTENCE", "ENDURING_DHARMA", "CONVICTION"],
            "required_formations_any": [
                "BROAD_ARC", "WIDENING_LINE", "FULL_ENSEMBLE_UNISON", "FINAL_UNIFIED_FORMATION"
            ],
            "hard_requirements": ["must_end_with_unified_still_tableau"],
            "weight": 20,
        },
    ],
}


def load_default_contract() -> PieceContract:
    return PieceContract.from_dict(_DEFAULT_CONTRACT)


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
