import math
import time
import mouse
from beatmap.models import Spinner
from player.base import BasePlayer
from config import Config


class SpinnerPlayer(BasePlayer):
    def hit(self, spinner: Spinner):
        """
        Joue un spinner.
        On tourne la souris en cercle pendant toute la durée du spinner.
        """
        # Centre du playfield osu! (presque toujours 256, 192)
        center_x, center_y = 256.0, 192.0
        screen_cx, screen_cy = self.screen.osu_to_screen(center_x, center_y)

        # Rayon de rotation (en pixels écran). 80-100 est un bon compromis.
        radius = 90

        # Durée totale du spinner
        duration_ms = spinner.end_time - spinner.time
        if duration_ms <= 0:
            duration_ms = 1000  # sécurité

        if Config.DEBUG:
            print(f"[Spinner] Début @ {spinner.time:.0f}ms → fin @ {spinner.end_time:.0f}ms "
                  f"(durée {duration_ms:.0f}ms)")

        # On attend le début du spinner
        self.timing.wait_until(spinner.time)

        # On appuie sur la touche et on la maintient
        key = self.current_key
        keyboard_press = True
        try:
            import keyboard
            keyboard.press(key)
        except Exception:
            keyboard_press = False

        # Boucle de rotation
        start = time.perf_counter()
        angle = 0.0
        # Vitesse de rotation (radians par seconde). 12 ≈ 2 tours/seconde (largement assez)
        speed = 50.0

        while True:
            elapsed = (time.perf_counter() - start) * 1000  # ms
            if elapsed >= duration_ms:
                break

            # Position sur le cercle
            angle += speed * 0.008  # ~125 FPS de mise à jour
            x = screen_cx + radius * math.cos(angle)
            y = screen_cy + radius * math.sin(angle)

            mouse.move(x, y, absolute=True, duration=0)

            time.sleep(0.008)

        # On relâche la touche
        if keyboard_press:
            import keyboard
            keyboard.release(key)

        # Alternance des touches pour le prochain objet
        self.current_key = Config.KEY2 if self.current_key == Config.KEY1 else Config.KEY1

        if Config.DEBUG:
            print(f"[Spinner] Terminé")