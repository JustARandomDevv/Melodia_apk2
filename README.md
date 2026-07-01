# Melodia — Android (Kivy/KivyMD)

Réécriture complète de l'application desktop Python originale (pywebview + pygame)
en une vraie application Android, avec Kivy/KivyMD comme framework UI et un moteur
audio compatible mobile.

## ⚠️ À lire avant toute chose

- **Cet APK n'est pas publiable sur le Google Play Store.** La recherche/téléchargement
  de musique via YouTube Music (`ytmusicapi` + `yt-dlp`) repose sur une API non
  officielle et viole les conditions d'utilisation de YouTube. C'est un usage
  **personnel, en sideload** (installation manuelle de l'APK), pas un produit
  distribuable publiquement.
- Ces bibliothèques non officielles peuvent cesser de fonctionner à tout moment si
  YouTube change son site — ce n'est pas un bug de l'app en tant que tel.
- Utilise cette app avec ta propre bibliothèque ou du contenu libre de droits si tu
  veux rester dans un cadre confortable légalement.

## Ce qui a changé par rapport à la version desktop

| Original (desktop) | Version Android |
|---|---|
| `pywebview` (fenêtre native + HTML/CSS/JS) | `Kivy` + `KivyMD` (UI native Python, Material Design 3) |
| `pygame.mixer` (lecture audio) | `kivy.core.audio.SoundLoader` (compatible Android) |
| `pystray` (icône barre système) | Retiré — n'existe pas sur Android |
| `keyboard` (raccourcis clavier globaux) | Retiré — interdit par le sandboxing Android |
| `pypresence` (statut Discord) | Retiré — nécessite un Discord desktop local |
| Conversion MP3 via ffmpeg (yt-dlp postprocessor) | Téléchargement du flux audio natif (m4a/opus), **sans réencodage**, pour rester compilable sur Android sans dépendance ffmpeg fragile |
| Stockage dans `~/Music/MelodiaDownloads` | Stockage dans le dossier privé de l'app (`app_storage_path()`), pas de permission de stockage externe nécessaire |

Fonctionnalités conservées : recherche YouTube Music, recommandations, téléchargement
et lecture, file d'attente, bibliothèque locale, favoris, playlists, paroles, mini-player
persistant, écran plein écran avec seek bar.

## Structure du projet

```
melodia-android/
├── main.py                      # Point d'entrée de l'app
├── buildozer.spec                # Config de compilation Android
├── requirements.txt              # Dépendances pour test desktop
├── app/
│   ├── theme.py                  # Jetons de design (couleurs, rayons)
│   ├── storage.py                # Persistance JSON (favoris, playlists, réglages)
│   ├── player.py                 # Moteur de lecture audio + file d'attente
│   ├── youtube_service.py        # Recherche + téléchargement YouTube Music
│   ├── screens/                  # Un fichier par écran (accueil, recherche, etc.)
│   ├── widgets/                  # Composants réutilisables (carte piste, mini-player...)
│   └── kv/                       # Fichiers de layout .kv correspondants
├── assets/icons/                 # Icône + splash screen générés
└── .github/workflows/build-apk.yml   # Pipeline de compilation cloud
```

## Compiler l'APK (recommandé : GitHub Actions, tu es sous Windows)

Buildozer ne fonctionne pas nativement sous Windows (il dépend d'outils Linux pour
le NDK Android). Le plus simple depuis Windows :

1. Crée un dépôt GitHub et pousse-y ce dossier tel quel (le workflow est déjà inclus
   dans `.github/workflows/build-apk.yml`).
   ```bash
   cd melodia-android
   git init
   git add .
   git commit -m "Melodia Android"
   git branch -M main
   git remote add origin https://github.com/TON-COMPTE/melodia-android.git
   git push -u origin main
   ```
2. Va dans l'onglet **Actions** de ton dépôt GitHub : le build se lance automatiquement.
   Compte **20 à 40 minutes** pour le premier build (les suivants sont plus rapides
   grâce au cache).
3. Une fois le workflow terminé (coche verte), ouvre le run, descends jusqu'à
   **Artifacts**, et télécharge `melodia-apk` — cela contient le fichier `.apk`.
4. Transfère l'APK sur ton téléphone (câble USB, Drive, etc.) et installe-le en
   autorisant "Sources inconnues" dans les réglages Android si demandé.

Tu peux aussi relancer le build manuellement depuis l'onglet Actions
(`workflow_dispatch`) sans avoir à repush du code.

## Tester sur PC avant de compiler (optionnel mais recommandé)

Pour vérifier l'UI et la logique avant de lancer un build Android (plus rapide à
itérer) :

```bash
pip install -r requirements.txt
python main.py
```

Sous Windows, si l'installation de Kivy échoue, essaie :
```bash
pip install "kivy[base]" kivymd
```

## Limitations connues de cette version

- **Pas de lecture en arrière-plan avancée** (notification media style Spotify) —
  ajoutable via un service Android foreground si besoin, non inclus ici pour garder
  le projet simple à compiler.
- **Pochettes non masquées en cercle/coins arrondis** — Kivy `Image` standard ne
  supporte pas nativement le masquage de forme sans shader dédié ; c'est un axe
  d'amélioration visuelle possible plus tard.
- **Pas de Discord RPC ni de tray icon** — concepts desktop-only, non transposables.
- Le stockage est dans le dossier privé de l'app : si tu désinstalles l'app, ta
  musique téléchargée est perdue (comportement standard Android pour le stockage
  privé, évite d'avoir à demander des permissions de stockage intrusives).

## Prochaines étapes possibles

- Ajouter un service Android en foreground pour la lecture en arrière-plan avec
  notification (play/pause/next depuis l'écran verrouillé).
- Ajouter un import manuel de fichiers audio déjà présents sur le téléphone.
- Masquer les pochettes en coins arrondis via un shader `fbo`/stencil.
