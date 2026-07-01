import threading

from kivymd.uix.screen import MDScreen
from kivy.clock import Clock
from kivy.app import App

from app.widgets.track_card import TrackCard


class SearchScreen(MDScreen):
    def do_search(self, query):
        query = (query or "").strip()
        container = self.ids.get("results_container")
        if not container:
            return
        container.clear_widgets()
        if not query:
            return
        self.ids.loading_spinner.active = True
        app = App.get_running_app()

        def worker():
            results = app.youtube.search(query)
            Clock.schedule_once(lambda dt: self._populate(results), 0)

        threading.Thread(target=worker, daemon=True).start()

    def _populate(self, results):
        self.ids.loading_spinner.active = False
        container = self.ids.get("results_container")
        container.clear_widgets()
        if not results:
            self.ids.empty_label.text = "Aucun résultat."
            self.ids.empty_label.opacity = 1
            return
        self.ids.empty_label.opacity = 0
        for track in results:
            card = TrackCard(
                title_text=track["title"],
                artist_text=track["artist"],
                show_favorite=False,
                show_add=False,
            )
            card.on_press_cb = lambda t=track: self._download_and_play(t)
            container.add_widget(card)

    def _download_and_play(self, track):
        app = App.get_running_app()

        def on_done(local_track):
            Clock.schedule_once(lambda dt: app.player.queue_and_play(local_track), 0)

        app.youtube.download_track_async(
            track["video_id"], track["title"], track["artist"], track.get("thumb"),
            on_done
        )
