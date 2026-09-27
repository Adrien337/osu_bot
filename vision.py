import time
import numpy as np
import mss
from config import Config


class Vision:
    def __init__(self):
        self.sct = mss.mss()
        self.monitor = self.sct.monitors[1]  # Écran principal

    def wait_for_black_screen(self, threshold: float = None, timeout: float = None):
        """
        Attend que l'écran soit suffisamment sombre (version plus stable).
        """
        if threshold is None:
            threshold = Config.BLACK_THRESHOLD
        if timeout is None:
            timeout = Config.BLACK_SCREEN_TIMEOUT

        start = time.perf_counter()

        while True:
            img = self.sct.grab(self.monitor)
            data = np.array(img)[:, :, :3].astype(np.float32)

            # Luminosité moyenne (0 = noir total, 255 = blanc)
            brightness = np.mean(data)

            # On considère "noir" quand la luminosité moyenne est très basse
            # threshold est en % de noir → on convertit en luminosité max acceptable
            max_brightness = 255 * (1 - threshold / 100)

            if brightness <= max_brightness:
                if Config.DEBUG:
                    print(f"[Vision] Écran sombre détecté (luminosité moyenne : {brightness:.1f})")
                return

            if time.perf_counter() - start > timeout:
                raise TimeoutError(
                    f"Timeout : l'écran n'est pas assez sombre (luminosité {brightness:.1f})"
                )

            time.sleep(0.025)

    def wait_for_pixel_change(self, x: int, y: int, timeout: float = 10.0):
        """
        Attend que le pixel à la position (x, y) ne soit plus noir.
        Utile pour synchroniser sur le premier cercle.
        """
        start = time.perf_counter()

        while True:
            img = self.sct.grab(self.monitor)
            data = np.array(img)[:, :, :3]

            # Attention : mss donne (height, width), donc data[y, x]
            pixel = data[y, x]

            if not np.array_equal(pixel, [0, 0, 0]):
                if Config.DEBUG:
                    print(f"[Vision] Pixel non-noir détecté à ({x}, {y}) → {pixel}")
                return

            if time.perf_counter() - start > timeout:
                raise TimeoutError(f"Timeout : le pixel ({x}, {y}) est resté noir.")

            time.sleep(0.01)

    def close(self):
        """Ferme proprement mss."""
        self.sct.close()