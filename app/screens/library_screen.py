import os

from kivymd.uix.screen import MDScreen
from kivy.app import App

from app.widgets.track_card import TrackCard


class LibraryScreen(MDScreen):
    def on_pre_enter(self, *args):
        self.refresh()

    def refresh(self):
        app = App.get_running_app()
        container = self.ids.get("library_container")
        if not container:
            return
        container.clear_widgets()

        download_dir = app.storage.download_dir
        if not os.path.exists(download_dir):
            return
        files = [f for f in os.listdir(download_dir) if f.lower().endswith((".mp3", ".m4a", ".opus", ".webm"))]
        favorites = app.storage.data.get("favorites", [])
        files.sort(key=lambda x: (x not in favorites, x.lower()))

        if not files:
            self.ids.empty_label.opacity = 1
            return
        self.ids.empty_label.opacity = 0

        for f in files:
            base = os.path.splitext(f)[0]
            parts = base.split(" - ")
            title = parts[0].strip()
            artist = parts[1].strip() if len(parts) > 1 else "Inconnu"
            jpg = os.path.join(download_dir, base + ".jpg")
            art = jpg if os.path.exists(jpg) else ""

            card = TrackCard(
                title_text=title,
                artist_text=artist,
                art_source=art,
                is_favorite=f in favorites,
                show_favorite=True,
                show_add=True,
            )
            card.on_press_cb = lambda fn=f: self._play_local(fn)
            card.on_favorite_cb = lambda fn=f, c=card: self._toggle_fav(fn, c)
            card.on_add_cb = lambda fn=f: self._enqueue_local(fn)
            container.add_widget(card)

    def _play_local(self, filename):
        app = App.get_running_app()
        track = app.player._track_from_filename(filename)
        app.player.queue_and_play(track)

    def _enqueue_local(self, filename):
        app = App.get_running_app()
        track = app.player._track_from_filename(filename)
        app.player.add_to_queue(track)

    def _toggle_fav(self, filename, card):
        app = App.get_running_app()
        app.storage.toggle_favorite(filename)
        card.is_favorite = filename in app.storage.data.get("favorites", [])
