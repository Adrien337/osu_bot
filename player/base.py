import time
import mouse
import keyboard
from config import Config
from screen import Screen
from timing import Timing


class BasePlayer:
    def __init__(self, screen: Screen, timing: Timing):
        self.screen = screen
        self.timing = timing
        self.current_key = Config.KEY1
        self.keys = [Config.KEY1, Config.KEY2]

    def move_to(self, x: float, y: float):
        """
        Déplace la souris vers les coordonnées osu! (x, y).
        """
        screen_x, screen_y = self.screen.osu_to_screen(x, y)
        mouse.move(screen_x, screen_y, absolute=True, duration=0)

        if Config.DEBUG:
            print(f"[Player] Move → osu({x:.0f}, {y:.0f}) = screen({screen_x}, {screen_y})")

    def press_key(self):
        """
        Appuie sur la touche actuelle puis alterne.
        """
        key = self.current_key
        keyboard.press(key)
        # Très court pour les cercles (osu! détecte le press)
        time.sleep(0.01)
        keyboard.release(key)

        # Alternance des touches
        self.current_key = Config.KEY2 if self.current_key == Config.KEY1 else Config.KEY1

        if Config.DEBUG:
            print(f"[Player] Key pressed : {key}")

    def hold_key(self, duration_ms: float):
        """
        Maintient la touche enfoncée pendant duration_ms millisecondes.
        Utile pour les sliders et spinners.
        """
        key = self.current_key
        keyboard.press(key)
        time.sleep(duration_ms / 1000)
        keyboard.release(key)

        # Alternance après le hold
        self.current_key = Config.KEY2 if self.current_key == Config.KEY1 else Config.KEY1

    def click_at(self, x: float, y: float, target_time: float):
        self.move_to(x, y)

        current = self.timing.get_current_time()
        if Config.DEBUG:
            late = current - target_time
            print(f"[Timing] Cible {target_time:.0f}ms | Actuel {current:.0f}ms | Écart {late:+.1f}ms")

        self.timing.wait_until(target_time)
        self.press_key()