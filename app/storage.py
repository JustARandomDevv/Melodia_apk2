"""
Storage — persistance locale (JSON) des favoris, playlists et réglages.
Gère aussi le dossier de téléchargement, avec un chemin adapté à Android
(stockage privé de l'app, pas besoin de permissions supplémentaires).
"""
import os
import json

from kivy.utils import platform


class Storage:
    def __init__(self):
        self.base_dir = self._resolve_base_dir()
        self.download_dir = os.path.join(self.base_dir, "MelodiaMusic")
        os.makedirs(self.download_dir, exist_ok=True)

        self.data_file = os.path.join(self.base_dir, "melodia_data.json")
        self.data = {
            "settings": {"auto_play": True, "run_in_background": True},
            "playlists": {},
            "favorites": [],
        }
        self._load()

    def _resolve_base_dir(self):
        if platform == "android":
            try:
                from android.storage import app_storage_path
                return app_storage_path()
            except Exception:
                pass
        return os.path.join(os.path.expanduser("~"), ".melodia")

    def _load(self):
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    self.data.update(loaded)
        except Exception as e:
            print("Storage load error:", e)

    def save(self):
        try:
            os.makedirs(self.base_dir, exist_ok=True)
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print("Storage save error:", e)

    # ── Favoris ──
    def toggle_favorite(self, filename):
        favs = self.data.setdefault("favorites", [])
        if filename in favs:
            favs.remove(filename)
        else:
            favs.append(filename)
        self.save()

    # ── Playlists ──
    def create_playlist(self, name, files):
        self.data.setdefault("playlists", {})[name] = files
        self.save()

    def delete_playlist(self, name):
        if name in self.data.get("playlists", {}):
            del self.data["playlists"][name]
            self.save()

    def add_to_playlist(self, name, filename):
        pl = self.data.setdefault("playlists", {}).setdefault(name, [])
        if filename not in pl:
            pl.append(filename)
            self.save()

    # ── Settings ──
    def save_setting(self, key, value):
        self.data.setdefault("settings", {})[key] = value
        self.save()

    def get_setting(self, key, default=None):
        return self.data.get("settings", {}).get(key, default)
