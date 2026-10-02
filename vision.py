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

    def wait_for_circle_appear(self, x: int, y: int, timeout: float = 15.0, radius: int = 8):
        """
        Attend qu'un cercle d'approche apparaisse autour de (x, y).
        On compare la luminosité moyenne d'une petite zone à un baseline.
        """
        import time
        import numpy as np

        # Petite zone autour du point
        x1 = max(0, x - radius)
        y1 = max(0, y - radius)
        x2 = x + radius
        y2 = y + radius

        # Baseline : luminosité juste après l'écran noir
        img = self.sct.grab(self.monitor)
        data = np.array(img)[:, :, :3].astype(np.float32)
        baseline = np.mean(data[y1:y2, x1:x2])

        if Config.DEBUG:
            print(f"[Vision] Baseline luminosité zone ({x},{y}) = {baseline:.1f}")

        start = time.perf_counter()

        while True:
            img = self.sct.grab(self.monitor)
            data = np.array(img)[:, :, :3].astype(np.float32)
            current = np.mean(data[y1:y2, x1:x2])

            # On considère que le cercle apparaît quand la luminosité monte clairement
            if current > baseline + 25:          # seuil à ajuster si besoin (15-40)
                if Config.DEBUG:
                    print(f"[Vision] Cercle détecté ! luminosité {current:.1f} (baseline {baseline:.1f})")
                return

            if time.perf_counter() - start > timeout:
                raise TimeoutError(
                    f"Timeout : aucun cercle détecté à ({x}, {y}) "
                    f"(baseline={baseline:.1f}, actuel={current:.1f})"
                )

            time.sleep(0.008)

    def close(self):
        """Ferme proprement mss."""
        self.sct.close()