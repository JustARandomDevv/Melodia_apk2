"""
Melodia — lecteur de musique Android (réécriture Kivy/KivyMD)
Point d'entrée de l'application.
"""
import os

# Doit être défini avant l'import de kivy pour un rendu correct sur Android
os.environ.setdefault("KIVY_NO_ARGS", "1")

from kivy.utils import platform
from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.clock import Clock

from app.player import PlayerService
from app.storage import Storage
from app.youtube_service import YouTubeService
from app.screens.home_screen import HomeScreen
from app.screens.search_screen import SearchScreen
from app.screens.library_screen import LibraryScreen
from app.screens.playlists_screen import PlaylistsScreen
from app.screens.now_playing_screen import NowPlayingScreen
from app.widgets.mini_player import MiniPlayer  # noqa: F401 (enregistré via kv)


KV_ROOT = os.path.join(os.path.dirname(__file__), "app", "kv")


class MelodiaApp(MDApp):
    def build(self):
        self.title = "Melodia"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Green"
        self.theme_cls.primary_hue = "500"

        if platform != "android":
            Window.size = (400, 800)

        # ── Services (logique métier, indépendante de l'UI) ──
        self.storage = Storage()
        self.player = PlayerService(self.storage)
        self.youtube = YouTubeService(self.storage.download_dir)

        # Charge tous les fichiers .kv de règles (widgets/écrans) du dossier app/kv,
        # puis root.kv en dernier car il instancie directement l'arbre de widgets.
        for fname in sorted(os.listdir(KV_ROOT)):
            if fname.endswith(".kv") and fname != "root.kv":
                Builder.load_file(os.path.join(KV_ROOT, fname))

        self.root_layout = Builder.load_file(os.path.join(KV_ROOT, "root.kv"))
        return self.root_layout

    def on_start(self):
        # Rafraîchit l'état du mini-player régulièrement
        Clock.schedule_interval(self._tick, 0.5)
        self.request_android_permissions()
        Clock.schedule_once(lambda dt: self.root_layout.ids.sm.get_screen("home").refresh(), 0.3)

    def request_android_permissions(self):
        if platform == "android":
            try:
                from android.permissions import request_permissions, Permission
                perms = [
                    Permission.INTERNET,
                    Permission.WRITE_EXTERNAL_STORAGE,
                    Permission.READ_EXTERNAL_STORAGE,
                    Permission.FOREGROUND_SERVICE,
                ]
                # POST_NOTIFICATIONS n'existe que sur les API 33+, on l'ajoute si dispo
                if hasattr(Permission, "POST_NOTIFICATIONS"):
                    perms.append(Permission.POST_NOTIFICATIONS)
                request_permissions(perms)
            except Exception as e:
                print("Permission request failed:", e)

    def _tick(self, dt):
        mini = self.root_layout.ids.get("mini_player")
        if mini:
            mini.refresh_from_player()
        np = self.root_layout.ids.sm.get_screen("now_playing") if self.root_layout.ids.sm.has_screen("now_playing") else None
        if np and self.root_layout.ids.sm.current == "now_playing":
            np.refresh_from_player()

    def on_stop(self):
        self.player.release()


if __name__ == "__main__":
    MelodiaApp().run()
