"""Controlled vocabulary for choreography annotation."""

ACTION_LABELS = [
    "STILLNESS", "SLOW_RISE", "BOWED_BODY", "KNEEL", "PROSTRATION",
    "CHEST_TOUCH", "CHEST_BEAT", "UPWARD_REACH", "OUTWARD_OPENING",
    "OFFERING_GESTURE", "HAND_TO_HEAD", "PRAYER_PALMS", "DHARMA_WHEEL",
    "SHIELDING", "ADVANCING_STEP", "SWAY_CONFUSION", "SLOW_MOTION_GRIEF",
    "FACE_COVER", "OPEN_PALMS_APPEAL", "INWARD_CLOSING", "KNEEL_TO_RISE",
    "FINAL_UPLIFT", "FINAL_TABLEAU",
]

FORMATION_LABELS = [
    "CENTER_LEAD", "ENSEMBLE_LOW_FRAME", "OPEN_SEMICIRCLE", "LOOSE_SPACING",
    "SOLO_FOREGROUND", "ENSEMBLE_ECHO", "WIDE_ENSEMBLE_SPREAD",
    "COMPACT_CLUSTER", "FRONTAL_GROUP", "ADVANCING_LINE", "STAGGERED_GROUP",
    "LAYERED_FRONT_BACK", "KNEELING_GROUP", "BROAD_ARC", "WIDENING_LINE",
    "FULL_ENSEMBLE_UNISON", "FINAL_UNIFIED_FORMATION",
]

LEVEL_LABELS = [
    "LOW_LEVEL", "MID_LEVEL", "HIGH_LEVEL", "KNEELING_LEVEL",
    "PROSTRATED_LEVEL", "RISING_LEVEL",
]

INTENT_LABELS = [
    "SACRED_ATMOSPHERE", "SHOCK", "MOURNING", "GRIEF", "REVERENCE", "LONGING",
    "REMEMBRANCE", "COMPASSION", "PERSONAL_SEARCHING", "SUPPLICATION",
    "RESPONSIBILITY", "CONTINUATION", "PROTECTION", "CONFUSION", "TEMPTATION",
    "SUFFERING", "DECLINE", "PLEADING", "AWAKENING", "HOPE", "MORAL_COMMITMENT",
    "VOW", "PERSISTENCE", "UNITY", "ENDURING_DHARMA", "CONVICTION",
]

ACTION_DEFINITIONS = {
    "DHARMA_WHEEL": "Circular or rotating hand/arm motion suggesting turning/transmission of the Dharma.",
    "PRAYER_PALMS": "Palms together or hands gathered in devotional posture.",
    "OFFERING_GESTURE": "Hands extend outward/upward as if giving or presenting.",
    "SHIELDING": "Hands/arms protect chest, face, or group space.",
    "KNEEL": "One or both knees lowered to the ground.",
    "PROSTRATION": "Full body lowered to ground in deep reverence.",
    "BOWED_BODY": "Torso inclined forward in deference or grief.",
    "CHEST_TOUCH": "Hand(s) placed on chest in emotional acknowledgment.",
    "CHEST_BEAT": "Hand(s) strike chest in grief or emphasis.",
    "UPWARD_REACH": "Arms/hands extend upward toward the sky or heavens.",
    "OUTWARD_OPENING": "Arms open wide in offering, welcome, or release.",
    "FACE_COVER": "Hands cover face in grief, shame, or distress.",
    "SWAY_CONFUSION": "Body sways or wavers indicating uncertainty or temptation.",
    "INWARD_CLOSING": "Body or arms draw inward, contracted in suffering.",
    "OPEN_PALMS_APPEAL": "Palms open and extended outward in pleading.",
    "SLOW_RISE": "Gradual ascent from low to higher level.",
    "KNEEL_TO_RISE": "Transition from kneeling position to standing.",
    "FINAL_UPLIFT": "Final expansive upward gesture.",
    "FINAL_TABLEAU": "Held still pose at the conclusion of a section or piece.",
    "STILLNESS": "Complete or near-complete absence of movement.",
    "ADVANCING_STEP": "Steps moving toward the audience or forward.",
    "HAND_TO_HEAD": "Hand(s) placed on or near the head.",
    "SLOW_MOTION_GRIEF": "Sustained, slowed movement expressing sorrow.",
    "SLOW_RISE": "Body rises slowly from a low or kneeling position.",
}
