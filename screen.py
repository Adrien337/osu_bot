import ctypes
from config import Config


class Screen:
    def __init__(self):
        self.screen_width = 0
        self.screen_height = 0
        self.playfield_width = 0.0
        self.playfield_height = 0.0
        self.osu_scale = 0.0
        self.playfield_x = 0.0
        self.playfield_y = 0.0

        self.update()

    def update(self):
        """
        Met à jour toutes les informations liées à l'écran et au playfield.
        """
        self.screen_width = ctypes.windll.user32.GetSystemMetrics(0)
        self.screen_height = ctypes.windll.user32.GetSystemMetrics(1)

        # === Réglages principaux ===
        # Tu peux ajuster ces deux valeurs si besoin
        height_ratio = 0.8          # hauteur du playfield par rapport à l'écran
        vertical_offset_ratio = 0.02  # petit décalage vers le bas (2%)

        self.playfield_height = self.screen_height * height_ratio
        self.playfield_width = self.playfield_height * (4 / 3)

        # Scale (384 = hauteur interne d'osu!)
        self.osu_scale = self.playfield_height / 384.0

        # Centrage horizontal + léger décalage vertical
        self.playfield_x = (self.screen_width - self.playfield_width) / 2
        self.playfield_y = ((self.screen_height - self.playfield_height) / 2) + (self.screen_height * vertical_offset_ratio)

        if Config.DEBUG:
            print(f"[Screen] Résolution : {self.screen_width}x{self.screen_height}")
            print(f"[Screen] Playfield : {self.playfield_width:.1f}x{self.playfield_height:.1f}")
            print(f"[Screen] Scale : {self.osu_scale:.4f}")
            print(f"[Screen] Offset : ({self.playfield_x:.1f}, {self.playfield_y:.1f})")

    def osu_to_screen(self, x: float, y: float) -> tuple[int, int]:
        """
        Convertit des coordonnées osu! (0-512 / 0-384) en coordonnées écran.
        """
        screen_x = int(round(x * self.osu_scale + self.playfield_x))
        screen_y = int(round(y * self.osu_scale + self.playfield_y))
        return screen_x, screen_y