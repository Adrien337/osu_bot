import keyboard
from bot import OsuBot
from config import Config


def main():
    print("=" * 55)
    print("               Osu! Bot - Portfolio Project")
    print("=" * 55)
    print(f"  Touches           : {Config.KEY1}  /  {Config.KEY2}")
    print(f"  Offset timing     : {Config.TIMING_OFFSET} ms")
    print(f"  Mode Debug        : {Config.DEBUG}")
    print(f"  Dossier Songs     : {Config.OSU_SONGS_PATH}")
    print("=" * 55)
    print("\nInstructions :")
    print("  1. Lance osu! et va sur le menu principal")
    print("  2. Choisis une map et lance-la")
    print("  3. Reviens ici et appuie sur ENTRÉE")
    print("  4. Pendant la map → appuie sur ÉCHAP pour arrêter")
    print("\nAppuie sur ENTRÉE pour démarrer...")

    keyboard.wait("enter")
    print("\n→ Démarrage du bot...\n")

    bot = OsuBot()
    bot.play()


if __name__ == "__main__":
    main()