"""Data models for choreography annotation, contracts, and verification."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
import json


@dataclass
class EventAnnotation:
    start: float
    end: float
    label: str
    evidence: str
    confidence: float
    event_id: Optional[str] = None
    segment_id: Optional[str] = None
    event_type: str = "MOTIF"
    body_parts: list[str] = field(default_factory=list)
    spatial_direction: Optional[str] = None
    quality: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items() if v is not None and v != []}


@dataclass
class SegmentAnnotation:
    start: float
    end: float
    lyric_text: str
    observed_actions: list[str]
    formation: list[str]
    level: list[str]
    intent: list[str]
    confidence: dict
    events: list[EventAnnotation] = field(default_factory=list)
    segment_id: Optional[str] = None
    source: str = "candidate"
    phase_guess: Optional[str] = None
    evidence: list[dict] = field(default_factory=list)
    notes: str = ""

    def to_dict(self) -> dict:
        d = self.__dict__.copy()
        d["events"] = [e.to_dict() for e in self.events]
        return d


@dataclass
class PhaseContract:
    phase: str
    name: str
    time_window: list[float]
    core_function: str
    lyric_anchors: list[str]
    required_motif_groups: list[list[str]]
    required_intents: list[str]
    required_formations_any: list[str]
    weight: float
    hard_requirements: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return self.__dict__.copy()


@dataclass
class PieceContract:
    piece_title: str
    duration: float
    phases: list[PhaseContract]

    def to_dict(self) -> dict:
        return {
            "piece_title": self.piece_title,
            "duration": self.duration,
            "phases": [p.to_dict() for p in self.phases],
        }

    @classmethod
    def from_dict(cls, d: dict) -> "PieceContract":
        phases = [PhaseContract(**p) for p in d["phases"]]
        return cls(
            piece_title=d["piece_title"],
            duration=d["duration"],
            phases=phases,
        )

    @classmethod
    def from_file(cls, path: str) -> "PieceContract":
        with open(path) as f:
            return cls.from_dict(json.load(f))


@dataclass
class PhaseResult:
    phase: str
    name: str
    score: float
    missing_motifs: list[list[str]]
    missing_intents: list[list[str]]
    formation_ok: bool
    lyric_score: float
    weight: float
    feedback: list[str] = field(default_factory=list)


@dataclass
class VerifierResult:
    score: float
    passed: bool
    phase_results: list[PhaseResult]
    hard_failures: list[str]
    feedback: list[str]
    iteration: int = 0

    def summary(self) -> str:
        lines = [
            f"Score: {self.score}/100 | Pass: {self.passed} | Iteration: {self.iteration}",
        ]
        for pr in self.phase_results:
            marker = "OK" if pr.score >= 75 else "WEAK"
            lines.append(f"  Phase {pr.phase} ({pr.name}): {pr.score}/100 [{marker}]")
        if self.hard_failures:
            lines.append("Hard failures:")
            for hf in self.hard_failures:
                lines.append(f"  - {hf}")
        if self.feedback:
            lines.append("Feedback:")
            for fb in self.feedback:
                lines.append(f"  - {fb}")
        return "\n".join(lines)
