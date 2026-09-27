from dataclasses import dataclass, field
from enum import IntFlag
from typing import List, Optional, Tuple


class HitObjectType(IntFlag):
    CIRCLE = 1
    SLIDER = 2
    NEW_COMBO = 4
    SPINNER = 8
    # Les bits plus élevés sont utilisés pour la couleur de combo, on les ignore


@dataclass
class TimingPoint:
    time: float                  # Temps en ms
    beat_length: float           # Durée d'un beat (ms). Négatif = inherited
    meter: int = 4
    sample_set: int = 0
    sample_index: int = 0
    volume: int = 100
    uninherited: bool = True
    effects: int = 0

    @property
    def is_inherited(self) -> bool:
        return not self.uninherited


@dataclass
class HitObject:
    x: float
    y: float
    time: float                  # Temps en ms
    type: HitObjectType
    hit_sound: int = 0

    @property
    def is_circle(self) -> bool:
        return bool(self.type & HitObjectType.CIRCLE)

    @property
    def is_slider(self) -> bool:
        return bool(self.type & HitObjectType.SLIDER)

    @property
    def is_spinner(self) -> bool:
        return bool(self.type & HitObjectType.SPINNER)


@dataclass
class Circle(HitObject):
    pass


@dataclass
class Slider(HitObject):
    curve_type: str = "B"                    # B, C, L, P
    curve_points: List[Tuple[float, float]] = field(default_factory=list)
    slides: int = 1                          # Nombre de repeats + 1
    length: float = 0.0                      # Longueur en osu!pixels


@dataclass
class Spinner(HitObject):
    end_time: float = 0.0


@dataclass
class Beatmap:
    # General
    mode: int = 0

    # Difficulty
    hp_drain_rate: float = 5.0
    circle_size: float = 5.0
    overall_difficulty: float = 5.0
    approach_rate: float = 5.0
    slider_multiplier: float = 1.4
    slider_tick_rate: float = 1.0

    # Parsed data
    timing_points: List[TimingPoint] = field(default_factory=list)
    hit_objects: List[HitObject] = field(default_factory=list)

    # Meta (rempli par le loader)
    artist: str = ""
    title: str = ""
    difficulty: str = ""
    file_path: str = ""