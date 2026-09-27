import time
from typing import List
from beatmap.models import Beatmap, TimingPoint


class Timing:
    def __init__(self, beatmap: Beatmap, offset: int = 0):
        self.beatmap = beatmap
        self.offset = offset          # Offset global en ms (peut être négatif)
        self.start_time: float = 0.0  # time.perf_counter() au moment où la map commence vraiment

    def start(self):
        """
        À appeler au moment exact où le premier objet devrait apparaître
        (après l'attente de l'écran noir + préempt AR).
        """
        self.start_time = time.perf_counter()

    def get_current_time(self) -> float:
        """
        Retourne le temps actuel de la beatmap en millisecondes.
        """
        if self.start_time == 0.0:
            return 0.0
        return (time.perf_counter() - self.start_time) * 1000 + self.offset

    def wait_until(self, target_time: float):
        """
        Attend jusqu'à ce que le temps de la beatmap atteigne target_time (en ms).
        """
        while self.get_current_time() < target_time:
            # Petite pause pour ne pas spammer le CPU
            time.sleep(0.0005)

    @staticmethod
    def ar_to_preempt(ar: float) -> float:
        """
        Convertit l'Approach Rate en temps de préemption (ms).
        C'est le temps entre l'apparition du cercle et le moment où il faut cliquer.
        """
        if ar < 5:
            return 1200 + 600 * (5 - ar) / 5
        elif ar == 5:
            return 1200
        else:
            return 1200 - 750 * (ar - 5) / 5

    @staticmethod
    def ar_to_fade_in(ar: float) -> float:
        """
        Temps de fade-in de l'approach circle (ms).
        """
        if ar < 5:
            return 800 + 400 * (5 - ar) / 5
        elif ar == 5:
            return 800
        else:
            return 800 - 500 * (ar - 5) / 5

    def get_slider_duration(self, slider, timing_points: List[TimingPoint]) -> float:
        """
        Calcule la durée totale d'un slider (en ms) — version correcte.
        """
        beat_length = 500.0
        slider_velocity = 1.0

        for tp in timing_points:
            if tp.time > slider.time:
                break

            if tp.uninherited:
                # Ligne rouge
                beat_length = tp.beat_length
                slider_velocity = 1.0
            else:
                # Ligne verte : le beat_length est négatif
                # SV = -100 / beat_length
                if tp.beat_length != 0:
                    slider_velocity = -100.0 / tp.beat_length

        # Formule officielle
        duration = (slider.length / (self.beatmap.slider_multiplier * 100 * slider_velocity)) * beat_length
        total_duration = duration * max(1, slider.slides)
        return total_duration