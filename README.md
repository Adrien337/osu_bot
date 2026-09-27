# Osu! Bot

Bot automatisé pour [osu!](https://osu.ppy.sh) développé dans un but **éducatif** et de **portfolio**.

> ⚠️ Ce projet est uniquement destiné à l'apprentissage et à la démonstration technique.  
> Il n'est **pas** conçu pour être utilisé en ranked ou pour tricher.

---

## Démonstration

<!-- Ajoute ici un GIF ou une vidéo plus tard -->
*[Insérer un GIF / vidéo du bot en action sur une map simple]*

---

## Fonctionnalités

- Détection automatique de la beatmap en cours via le titre de la fenêtre
- Parsing complet des fichiers `.osu` (TimingPoints + HitObjects)
- Support des 3 types d'objets :
  - Cercles
  - Sliders (Linear, Bezier, Perfect, Catmull + repeats)
  - Spinners
- Système de timing basé sur `perf_counter` + Approach Rate
- Conversion précise des coordonnées osu! → écran
- Alternance automatique des touches
- Arrêt d'urgence (touche Échap)
- Configuration via fichier `.env`

---

## Architecture
```
osu_bot/
├── beatmap/
│   ├── loader.py      # Recherche du fichier .osu
│   ├── parser.py      # Parsing du fichier .osu
│   └── models.py      # Dataclasses (Beatmap, HitObject, etc.)
├── player/
│   ├── base.py        # Déplacement souris + gestion des touches
│   ├── circle.py
│   ├── slider.py      # Gestion des courbes + repeats
│   └── spinner.py
├── bot.py             # Orchestration principale
├── config.py          # Configuration (via .env)
├── screen.py          # Calcul du playfield + conversion de coordonnées
├── window.py          # Détection et parsing du titre de fenêtre
├── vision.py          # Détection d'écran noir
├── timing.py          # Système de temps + calculs AR / durée slider
└── main.py            # Point d'entrée
```
---

## Installation

```bash
git clone https://github.com/TonPseudo/osu-bot.git
cd osu-bot

python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/Mac

pip install -r requirements.txt