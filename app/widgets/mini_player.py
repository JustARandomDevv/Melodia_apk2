from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import StringProperty, BooleanProperty, NumericProperty
from kivy.app import App

from app.widgets.bottom_nav import BottomNavBar  # noqa: F401 registers <BottomNavBar>
from app.widgets.track_card import TrackCard  # noqa: F401 registers <TrackCard>
from app.widgets.seek_slider import SeekSlider  # noqa: F401 registers <SeekSlider>


class MiniPlayer(MDBoxLayout):
    title_text = StringProperty("Aucune lecture")
    artist_text = StringProperty("—")
    art_source = StringProperty("")
    is_playing = BooleanProperty(False)
    is_paused = BooleanProperty(False)
    progress = NumericProperty(0.0)  # 0..1

    def refresh_from_player(self):
        app = App.get_running_app()
        p = app.player
        self.title_text = p.current_title
        self.artist_text = p.current_artist
        self.art_source = p.current_art_path or ""
        self.is_playing = p.is_playing
        self.is_paused = p.is_paused
        if p.track_duration:
            self.progress = min(p.current_position / p.track_duration, 1.0)
        else:
            self.progress = 0.0

    def toggle_pause(self):
        App.get_running_app().player.toggle_pause()

    def next_track(self):
        App.get_running_app().player.play_next()

    def open_now_playing(self):
        app = App.get_running_app()
        if app.player.current_title == "Aucune lecture":
            return
        sm = app.root_layout.ids.sm
        sm.current = "now_playing"
