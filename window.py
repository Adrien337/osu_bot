import ctypes
import re
import time
from config import Config


class Window:
    def __init__(self):
        self.title = ""
        self.artist = ""
        self.title_name = ""
        self.difficulty = ""

    def get_active_window_title(self) -> str:
        """
        Retourne le titre de la fenêtre actuellement au premier plan.
        """
        user32 = ctypes.windll.user32
        hwnd = user32.GetForegroundWindow()
        length = user32.GetWindowTextLengthW(hwnd)
        buffer = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buffer, length + 1)
        self.title = buffer.value
        return self.title

    def wait_for_beatmap_load(self, timeout: float = None) -> str:
        """
        Attend que le titre de la fenêtre passe de "osu!" à un titre de beatmap.
        Lève une exception si le timeout est dépassé.
        """
        if timeout is None:
            timeout = Config.BEATMAP_LOAD_TIMEOUT

        start = time.perf_counter()

        while True:
            title = self.get_active_window_title()

            # On est encore sur le menu principal
            if title == "osu!":
                if time.perf_counter() - start >= timeout:
                    raise TimeoutError("La beatmap a mis trop de temps à charger.")
                time.sleep(0.01)
                continue

            # On a un titre de beatmap
            if title.startswith("osu!"):
                return title

            # Autre fenêtre
            raise RuntimeError(f"Fenêtre inattendue détectée : {title}")

    def parse_title(self, title: str = None):
        """
        Parse le titre de la fenêtre osu! pour extraire Artist, Title et Difficulty.
        Format attendu : "osu! - Artist - Title [Difficulty]"
        """
        if title is None:
            title = self.title

        # Regex robuste
        pattern = r"^osu! - (.+?) - (.+?) \[(.+)\]$"
        match = re.match(pattern, title)

        if not match:
            raise ValueError(f"Impossible de parser le titre de la fenêtre : {title}")

        self.artist = match.group(1).strip()
        self.title_name = match.group(2).strip()
        self.difficulty = match.group(3).strip()

        if Config.DEBUG:
            print(f"[Window] Artist     : {self.artist}")
            print(f"[Window] Title      : {self.title_name}")
            print(f"[Window] Difficulty : {self.difficulty}")