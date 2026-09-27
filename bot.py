import time
from config import Config
from screen import Screen
from window import Window
from vision import Vision
from timing import Timing
from beatmap.loader import BeatmapLoader
from beatmap.parser import BeatmapParser
from beatmap.models import Circle, Slider, Spinner
from player.circle import CirclePlayer
from player.slider import SliderPlayer
from player.spinner import SpinnerPlayer


class OsuBot:
    def __init__(self):
        self.screen = Screen()
        self.window = Window()
        self.vision = Vision()
        self.loader = BeatmapLoader()
        self.parser = BeatmapParser()

        self.beatmap = None
        self.timing = None

        # Players (seront initialisés après le parsing)
        self.circle_player = None
        self.slider_player = None
        self.spinner_player = None

    def play(self):
        """
        Point d'entrée principal du bot.
        """
        try:
            self._prepare()
            self._synchronize()
            self._play_objects()
            print("\n[Bot] Beatmap terminée avec succès.")

        except KeyboardInterrupt:
            print("\n[Bot] Arrêt d'urgence (Échap).")

        except FileNotFoundError as e:
            print(f"\n[Bot] Fichier introuvable : {e}")

        except ValueError as e:
            print(f"\n[Bot] Erreur de parsing : {e}")

        except TimeoutError as e:
            print(f"\n[Bot] Timeout : {e}")

        except Exception as e:
            print(f"\n[Bot] Erreur inattendue : {type(e).__name__} → {e}")

        finally:
            try:
                self.vision.close()
            except Exception:
                pass
            print("[Bot] Nettoyage terminé.")

    def _prepare(self):
        """
        Détecte la fenêtre, charge et parse la beatmap.
        """
        print(f"[DEBUG] TIMING_OFFSET chargé = {Config.TIMING_OFFSET} ms")
        print("[Bot] Recherche de la fenêtre osu!...")
        title = self.window.get_active_window_title()

        if title == "osu!":
            print("[Bot] En attente du chargement de la beatmap...")
            title = self.window.wait_for_beatmap_load()

        print(f"[Bot] Titre détecté : {title}")
        self.window.parse_title(title)

        print("[Bot] Recherche du fichier .osu...")
        self.beatmap = self.loader.load(
            self.window.artist,
            self.window.title_name,
            self.window.difficulty
        )
        print(f"[Bot] Fichier trouvé : {self.beatmap.file_path}")

        print("[Bot] Parsing de la beatmap...")
        self.beatmap = self.parser.parse(self.beatmap)

        print(f"[Bot] {len(self.beatmap.hit_objects)} objets chargés.")
        print(f"[Bot] AR={self.beatmap.approach_rate} | CS={self.beatmap.circle_size} | "
              f"OD={self.beatmap.overall_difficulty}")

        # Initialisation du système de timing + players
        self.timing = Timing(self.beatmap, offset=Config.TIMING_OFFSET)

        self.circle_player = CirclePlayer(self.screen, self.timing)
        self.slider_player = SliderPlayer(self.screen, self.timing)
        self.spinner_player = SpinnerPlayer(self.screen, self.timing)

    def _synchronize(self):
        """
        Synchronisation simple et stable.
        """
        print("[Bot] En attente de l'écran noir...")
        self.vision.wait_for_black_screen()

        self.screen.update()

        first_object = self.beatmap.hit_objects[0]
        preempt = Timing.ar_to_preempt(self.beatmap.approach_rate)

        print(f"[Bot] Premier objet @ {first_object.time:.0f}ms | Preempt AR = {preempt:.0f}ms")
        print(f"[Bot] TIMING_OFFSET = {Config.TIMING_OFFSET} ms")

        # Petit délai pour laisser l'écran noir se stabiliser
        time.sleep(0.06)

        # Démarre le chrono
        self.timing.start()

    def _play_objects(self):
        print("[Bot] Début de la map !")
        print("[Bot] Appuie sur ÉCHAP pour arrêter le bot à tout moment.\n")

        for i, obj in enumerate(self.beatmap.hit_objects):
            self._check_emergency_stop()   # ← ajouté ici

            if Config.DEBUG:
                print(f"[{i+1}/{len(self.beatmap.hit_objects)}] {obj.__class__.__name__} @ {obj.time:.0f}ms")

            if isinstance(obj, Circle):
                self.circle_player.hit(obj)
            elif isinstance(obj, Slider):
                self.slider_player.hit(obj)
            elif isinstance(obj, Spinner):
                self.spinner_player.hit(obj)
            else:
                print(f"[Bot] Type d'objet non géré : {type(obj)}")

    def _check_emergency_stop(self):
        """
        Vérifie si la touche de secours est pressée (Échap par défaut).
        """
        import keyboard
        if keyboard.is_pressed("esc"):
            raise KeyboardInterrupt("Arrêt d'urgence demandé (Échap)")