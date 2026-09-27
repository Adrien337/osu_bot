from typing import List
from beatmap.models import (
    Beatmap, TimingPoint, HitObject, Circle, Slider, Spinner, HitObjectType
)


class BeatmapParser:
    def parse(self, beatmap: Beatmap) -> Beatmap:
        """
        Parse le fichier .osu et remplit l'objet Beatmap.
        """
        with open(beatmap.file_path, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()

        self._parse_general(lines, beatmap)
        self._parse_difficulty(lines, beatmap)
        self._parse_timing_points(lines, beatmap)
        self._parse_hit_objects(lines, beatmap)

        return beatmap

    def _get_value(self, lines: List[str], key: str) -> str:
        for line in lines:
            if line.startswith(f"{key}:"):
                return line.split(":", 1)[1].strip()
        raise ValueError(f"Clé '{key}' introuvable dans le fichier .osu")

    def _parse_general(self, lines: List[str], beatmap: Beatmap):
        try:
            beatmap.mode = int(self._get_value(lines, "Mode"))
        except ValueError:
            beatmap.mode = 0

    def _parse_difficulty(self, lines: List[str], beatmap: Beatmap):
        beatmap.hp_drain_rate = float(self._get_value(lines, "HPDrainRate"))
        beatmap.circle_size = float(self._get_value(lines, "CircleSize"))
        beatmap.overall_difficulty = float(self._get_value(lines, "OverallDifficulty"))
        beatmap.approach_rate = float(self._get_value(lines, "ApproachRate"))
        beatmap.slider_multiplier = float(self._get_value(lines, "SliderMultiplier"))
        beatmap.slider_tick_rate = float(self._get_value(lines, "SliderTickRate"))

    def _parse_timing_points(self, lines: List[str], beatmap: Beatmap):
        in_section = False

        for line in lines:
            if line.strip() == "[TimingPoints]":
                in_section = True
                continue

            if in_section:
                if line.startswith("["):
                    break
                if not line.strip():
                    continue

                parts = line.split(",")
                if len(parts) < 2:
                    continue

                time = float(parts[0])
                beat_length = float(parts[1])
                meter = int(parts[2]) if len(parts) > 2 else 4
                uninherited = True if len(parts) < 7 else parts[6] == "1"

                tp = TimingPoint(
                    time=time,
                    beat_length=beat_length,
                    meter=meter,
                    uninherited=uninherited
                )
                beatmap.timing_points.append(tp)

    def _parse_hit_objects(self, lines: List[str], beatmap: Beatmap):
        in_section = False

        for line in lines:
            if line.strip() == "[HitObjects]":
                in_section = True
                continue

            if in_section:
                if line.startswith("["):
                    break
                if not line.strip():
                    continue

                obj = self._parse_single_hit_object(line)
                if obj:
                    beatmap.hit_objects.append(obj)

    def _parse_single_hit_object(self, line: str) -> HitObject | None:
        parts = line.split(",")
        if len(parts) < 5:
            return None

        x = float(parts[0])
        y = float(parts[1])
        time = float(parts[2])
        obj_type = HitObjectType(int(parts[3]))
        hit_sound = int(parts[4])

        # Spinner
        if obj_type & HitObjectType.SPINNER:
            end_time = float(parts[5]) if len(parts) > 5 else time + 1000
            return Spinner(x=x, y=y, time=time, type=obj_type, hit_sound=hit_sound, end_time=end_time)

        # Slider
        if obj_type & HitObjectType.SLIDER:
            if len(parts) < 8:
                return None

            slider_data = parts[5]  # ex: B|100:100|200:200
            slides = int(parts[6])
            length = float(parts[7])

            curve_type = slider_data[0]
            curve_points = []

            points_raw = slider_data[2:].split("|") if len(slider_data) > 2 else []
            for point in points_raw:
                if ":" in point:
                    px, py = point.split(":")
                    curve_points.append((float(px), float(py)))

            return Slider(
                x=x, y=y, time=time, type=obj_type, hit_sound=hit_sound,
                curve_type=curve_type,
                curve_points=curve_points,
                slides=slides,
                length=length
            )

        # Circle (par défaut)
        if obj_type & HitObjectType.CIRCLE:
            return Circle(x=x, y=y, time=time, type=obj_type, hit_sound=hit_sound)

        return None