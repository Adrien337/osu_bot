import math
import time
import mouse
from typing import List, Tuple
from beatmap.models import Slider
from player.base import BasePlayer
from config import Config


class SliderPlayer(BasePlayer):

    def hit(self, slider: Slider):
        duration_ms = self.timing.get_slider_duration(slider, self.timing.beatmap.timing_points)

        if Config.DEBUG:
            print(f"[Slider] Début @ {slider.time:.0f}ms | durée totale {duration_ms:.0f}ms | "
                f"type {slider.curve_type} | slides {slider.slides}")

        # Pré-positionnement
        start_x, start_y = self.screen.osu_to_screen(slider.x, slider.y)
        mouse.move(start_x, start_y, absolute=True, duration=0)

        self.timing.wait_until(slider.time)

        import keyboard
        key = self.current_key
        keyboard.press(key)

        # Suivi du chemin
        self._follow_path(slider, duration_ms)

        # Petit maintien supplémentaire sur le dernier point (très important)
        time.sleep(0.012)          # 12 ms de maintien en plus

        keyboard.release(key)

        self.current_key = Config.KEY2 if self.current_key == Config.KEY1 else Config.KEY1

        if Config.DEBUG:
            print("[Slider] Terminé")

    def _follow_path(self, slider: Slider, total_duration_ms: float):
        """
        Suit la trajectoire du slider pendant toute sa durée (avec repeats).
        Version corrigée qui respecte la longueur pixel officielle.
        """
        control_points = [(slider.x, slider.y)] + slider.curve_points

        # Génère une courbe dense
        path = self._generate_path(slider.curve_type, control_points, point_count=300)

        if not path:
            path = [(slider.x, slider.y)]

        # On calcule les longueurs cumulées
        cumulative = [0.0]
        for i in range(1, len(path)):
            dist = math.hypot(path[i][0] - path[i-1][0], path[i][1] - path[i-1][1])
            cumulative.append(cumulative[-1] + dist)

        total_path_length = cumulative[-1]
        if total_path_length == 0:
            total_path_length = 1.0

        # Longueur officielle d'un aller (donnée par le .osu)
        # Si le modèle n'a pas .length, utilise total_path_length comme fallback
        slider_length = getattr(slider, "length", total_path_length)
        if slider_length <= 0:
            slider_length = total_path_length

        start = time.perf_counter()
        slides = max(1, slider.slides)

        while True:
            elapsed = (time.perf_counter() - start) * 1000
            if elapsed >= total_duration_ms:
                break

            # Progression globale 0 → 1
            progress = min(elapsed / total_duration_ms, 1.0)

            # Progression dans le cycle aller-retour
            slide_progress = (progress * slides) % 1.0
            current_slide = int(progress * slides)

            # Sens inverse sur les repeats impairs
            if current_slide % 2 == 1:
                slide_progress = 1.0 - slide_progress

            # Distance cible sur le chemin de base (un aller)
            target_dist = slide_progress * slider_length

            # On trouve le point correspondant (en restant dans la longueur officielle)
            pos = self._get_point_at_distance(path, cumulative, target_dist)
            screen_x, screen_y = self.screen.osu_to_screen(pos[0], pos[1])
            mouse.move(screen_x, screen_y, absolute=True, duration=0)

            time.sleep(0.003)  # un peu plus réactif

    # ------------------------------------------------------------------
    # Génération de la courbe
    # ------------------------------------------------------------------

    def _generate_path(self, curve_type: str, points: List[Tuple[float, float]], point_count: int = 200) -> List[Tuple[float, float]]:
        if len(points) < 2:
            return points

        curve_type = curve_type.upper()

        if curve_type == "L":
            return self._linear(points, point_count)
        elif curve_type == "P":
            return self._perfect(points, point_count)
        elif curve_type == "B":
            return self._bezier(points, point_count)
        elif curve_type == "C":
            return self._catmull(points, point_count)
        else:
            # Fallback
            return self._linear(points, point_count)

    def _linear(self, points: List[Tuple[float, float]], count: int) -> List[Tuple[float, float]]:
        path = []
        segments = len(points) - 1
        for i in range(count):
            t = i / (count - 1)
            idx = min(int(t * segments), segments - 1)
            local_t = (t * segments) - idx
            x = points[idx][0] + (points[idx + 1][0] - points[idx][0]) * local_t
            y = points[idx][1] + (points[idx + 1][1] - points[idx][1]) * local_t
            path.append((x, y))
        return path

    def _perfect(self, points: List[Tuple[float, float]], count: int) -> List[Tuple[float, float]]:
        """Cercle parfait passant par 3 points."""
        if len(points) < 3:
            return self._linear(points, count)

        a, b, c = points[0], points[1], points[2]

        # Calcul du cercle circonscrit
        D = 2 * (a[0] * (b[1] - c[1]) + b[0] * (c[1] - a[1]) + c[0] * (a[1] - b[1]))
        if abs(D) < 1e-6:
            return self._linear(points, count)

        ux = ((a[0]**2 + a[1]**2) * (b[1] - c[1]) + (b[0]**2 + b[1]**2) * (c[1] - a[1]) + (c[0]**2 + c[1]**2) * (a[1] - b[1])) / D
        uy = ((a[0]**2 + a[1]**2) * (c[0] - b[0]) + (b[0]**2 + b[1]**2) * (a[0] - c[0]) + (c[0]**2 + c[1]**2) * (b[0] - a[0])) / D
        center = (ux, uy)
        radius = math.hypot(a[0] - ux, a[1] - uy)

        start_angle = math.atan2(a[1] - uy, a[0] - ux)
        end_angle = math.atan2(c[1] - uy, c[0] - ux)

        # Direction (sens de rotation)
        cross = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
        if cross < 0:
            if end_angle > start_angle:
                end_angle -= 2 * math.pi
        else:
            if end_angle < start_angle:
                end_angle += 2 * math.pi

        path = []
        for i in range(count):
            t = i / (count - 1)
            angle = start_angle + (end_angle - start_angle) * t
            x = center[0] + radius * math.cos(angle)
            y = center[1] + radius * math.sin(angle)
            path.append((x, y))
        return path

    def _bezier(self, points: List[Tuple[float, float]], count: int) -> List[Tuple[float, float]]:
        """Bezier de degré n (simple et efficace)."""
        n = len(points) - 1
        path = []

        for i in range(count):
            t = i / (count - 1)
            x, y = 0.0, 0.0
            for j, (px, py) in enumerate(points):
                # Coefficient binomial
                coeff = math.comb(n, j) * (t ** j) * ((1 - t) ** (n - j))
                x += px * coeff
                y += py * coeff
            path.append((x, y))
        return path

    def _catmull(self, points: List[Tuple[float, float]], count: int) -> List[Tuple[float, float]]:
        """Approximation Catmull-Rom (assez bonne pour osu!)."""
        if len(points) < 2:
            return points

        # On duplique les extrémités pour stabiliser
        pts = [points[0]] + points + [points[-1]]
        path = []
        segments = len(pts) - 3

        for i in range(count):
            t = i / (count - 1)
            seg = min(int(t * segments), segments - 1)
            local_t = (t * segments) - seg

            p0, p1, p2, p3 = pts[seg], pts[seg + 1], pts[seg + 2], pts[seg + 3]

            # Formule Catmull-Rom
            t2 = local_t * local_t
            t3 = t2 * local_t

            x = 0.5 * ((2 * p1[0]) +
                       (-p0[0] + p2[0]) * local_t +
                       (2*p0[0] - 5*p1[0] + 4*p2[0] - p3[0]) * t2 +
                       (-p0[0] + 3*p1[0] - 3*p2[0] + p3[0]) * t3)

            y = 0.5 * ((2 * p1[1]) +
                       (-p0[1] + p2[1]) * local_t +
                       (2*p0[1] - 5*p1[1] + 4*p2[1] - p3[1]) * t2 +
                       (-p0[1] + 3*p1[1] - 3*p2[1] + p3[1]) * t3)

            path.append((x, y))
        return path

    # ------------------------------------------------------------------
    # Utilitaires
    # ------------------------------------------------------------------

    def _calculate_path_length(self, path: List[Tuple[float, float]]) -> float:
        length = 0.0
        for i in range(1, len(path)):
            length += math.hypot(path[i][0] - path[i-1][0], path[i][1] - path[i-1][1])
        return length

    def _get_point_at(self, path: List[Tuple[float, float]], total_length: float, t: float) -> Tuple[float, float]:
        """Retourne le point à la fraction t (0→1) le long du path."""
        if t <= 0:
            return path[0]
        if t >= 1:
            return path[-1]

        target = t * total_length
        current = 0.0

        for i in range(1, len(path)):
            seg_len = math.hypot(path[i][0] - path[i-1][0], path[i][1] - path[i-1][1])
            if current + seg_len >= target:
                local_t = (target - current) / seg_len if seg_len > 0 else 0
                x = path[i-1][0] + (path[i][0] - path[i-1][0]) * local_t
                y = path[i-1][1] + (path[i][1] - path[i-1][1]) * local_t
                return (x, y)
            current += seg_len

        return path[-1]

    def _get_point_at_distance(self, path: List[Tuple[float, float]], cumulative: List[float], distance: float) -> Tuple[float, float]:
        """Retourne le point à une distance donnée le long du path."""
        if distance <= 0:
            return path[0]
        if distance >= cumulative[-1]:
            return path[-1]

        # Recherche linéaire simple (suffisant)
        for i in range(1, len(cumulative)):
            if cumulative[i] >= distance:
                seg_start = cumulative[i-1]
                seg_len = cumulative[i] - seg_start
                t = (distance - seg_start) / seg_len if seg_len > 0 else 0
                x = path[i-1][0] + (path[i][0] - path[i-1][0]) * t
                y = path[i-1][1] + (path[i][1] - path[i-1][1]) * t
                return (x, y)

        return path[-1]