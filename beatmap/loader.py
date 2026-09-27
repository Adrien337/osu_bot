import os
from typing import List, Optional
from config import Config
from beatmap.models import Beatmap


class BeatmapLoader:
    def __init__(self):
        self.songs_path = Config.OSU_SONGS_PATH

    def _sanitize(self, text: str, is_difficulty: bool = False) -> str:
        """
        Nettoie un nom pour qu'il corresponde à ce qu'osu! met dans les dossiers/fichiers.
        """
        # Caractères interdits ou remplacés par osu!
        forbidden = [":", "*", "?", '"', "<", ">", "|"]
        result = ""

        for char in text:
            if char in forbidden:
                result += "_"
            elif char in ["/", "\\"]:
                # Ces caractères sont simplement supprimés
                continue
            else:
                result += char

        # Limite de longueur (osu! tronque)
        max_len = 50 if not is_difficulty else 50
        return result[:max_len]

    def find_beatmap_file(self, artist: str, title: str, difficulty: str) -> str:
        """
        Cherche le fichier .osu correspondant.
        Lève une exception claire si 0 ou plusieurs fichiers sont trouvés.
        """
        corrected_artist = self._sanitize(artist)
        corrected_title = self._sanitize(title)
        corrected_diff = self._sanitize(difficulty, is_difficulty=True)

        matching_files: List[str] = []

        if not os.path.isdir(self.songs_path):
            raise FileNotFoundError(f"Dossier Songs introuvable : {self.songs_path}")

        for folder_name in os.listdir(self.songs_path):
            folder_path = os.path.join(self.songs_path, folder_name)

            if not os.path.isdir(folder_path):
                continue

            # On regarde si l'artiste est dans le nom du dossier
            if corrected_artist.lower() not in folder_name.lower():
                continue

            # On cherche les fichiers .osu dans ce dossier
            for file_name in os.listdir(folder_path):
                if not file_name.endswith(".osu"):
                    continue

                file_lower = file_name.lower()

                # Vérifie que le titre est présent
                if corrected_title.lower() not in file_lower:
                    continue

                # Extraction de la difficulté entre les derniers crochets [ ]
                # Exemple : "... [Galaxy].osu" → "galaxy"
                if "[" in file_name and "]" in file_name:
                    start = file_name.rfind("[") + 1
                    end = file_name.rfind("]")
                    file_diff = file_name[start:end].strip().lower()
                else:
                    continue

                # Comparaison EXACTE de la difficulté (insensible à la casse)
                if file_diff == corrected_diff.lower():
                    matching_files.append(os.path.join(folder_path, file_name))

        if len(matching_files) == 0:
            raise FileNotFoundError(
                f"Aucun fichier .osu trouvé pour : {artist} - {title} [{difficulty}]"
            )

        if len(matching_files) > 1:
            files_list = "\n".join(f"  - {f}" for f in matching_files)
            raise RuntimeError(
                f"Plusieurs fichiers trouvés pour {artist} - {title} [{difficulty}] :\n{files_list}\n"
                "Tu devras améliorer la détection ou choisir manuellement."
            )

        return matching_files[0]

    def load(self, artist: str, title: str, difficulty: str) -> Beatmap:
        """
        Point d'entrée principal : trouve le fichier et retourne un objet Beatmap vide
        (le parsing se fera ensuite).
        """
        file_path = self.find_beatmap_file(artist, title, difficulty)

        beatmap = Beatmap()
        beatmap.artist = artist
        beatmap.title = title
        beatmap.difficulty = difficulty
        beatmap.file_path = file_path

        return beatmap