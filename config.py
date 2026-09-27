import os
from dotenv import load_dotenv

# Charge les variables d'environnement depuis le fichier .env
load_dotenv()


class Config:
    # Chemin vers le dossier Songs
    OSU_SONGS_PATH: str = os.getenv("OSU_SONGS_PATH", r"C:\Users\Default\AppData\Local\osu!\Songs")

    # Touches de frappe
    KEY1: str = os.getenv("KEY1", "w")
    KEY2: str = os.getenv("KEY2", "x")

    # Offset de timing global (en millisecondes)
    TIMING_OFFSET: int = int(os.getenv("TIMING_OFFSET", "0"))

    # Seuil de noir pour la détection d'écran (en %)
    BLACK_THRESHOLD: float = float(os.getenv("BLACK_THRESHOLD", "75.0"))

    # Mode debug
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")

    # Timeouts (en secondes)
    BEATMAP_LOAD_TIMEOUT: float = 10.0
    BLACK_SCREEN_TIMEOUT: float = 8.0