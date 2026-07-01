import threading

from kivymd.uix.screen import MDScreen
from kivy.clock import Clock
from kivy.app import App

from app.widgets.track_card import TrackCard


class HomeScreen(MDScreen):
    def on_pre_enter(self, *args):
        self.refresh()

    def refresh(self):
        app = App.get_running_app()
        container = self.ids.get("recs_container")
        if not container:
            return
        container.clear_widgets()
        self.ids.loading_spinner.active = True

        def worker():
            recs = app.youtube.get_recommendations()
            Clock.schedule_once(lambda dt: self._populate(recs), 0)

        threading.Thread(target=worker, daemon=True).start()

    def _populate(self, recs):
        self.ids.loading_spinner.active = False
        container = self.ids.get("recs_container")
        if not container:
            return
        container.clear_widgets()
        app = App.get_running_app()
        if not recs:
            return
        for track in recs:
            card = TrackCard(
                title_text=track["title"],
                artist_text=track["artist"],
                art_source="",
                show_favorite=False,
                show_add=False,
            )
            card.on_press_cb = lambda t=track: self._play_cloud(t)
            container.add_widget(card)

    def _play_cloud(self, track):
        app = App.get_running_app()

        def on_done(local_track):
            Clock.schedule_once(lambda dt: app.player.queue_and_play(local_track), 0)

        def on_error(msg):
            pass

        app.youtube.download_track_async(
            track["video_id"], track["title"], track["artist"], track.get("thumb"),
            on_done, on_error
        )
