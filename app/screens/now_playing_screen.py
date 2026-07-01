import threading

from kivymd.uix.screen import MDScreen
from kivy.clock import Clock
from kivy.app import App


def _fmt_time(seconds):
    seconds = int(max(seconds, 0))
    m, s = divmod(seconds, 60)
    return f"{m}:{s:02d}"


class NowPlayingScreen(MDScreen):
    _lyrics_loaded_for = None

    def on_pre_enter(self, *args):
        self.refresh_from_player()

    def refresh_from_player(self):
        app = App.get_running_app()
        p = app.player
        self.ids.np_title.text = p.current_title
        self.ids.np_artist.text = p.current_artist
        self.ids.np_art.source = p.current_art_path or ""
        self.ids.np_art.opacity = 1 if p.current_art_path else 0
        self.ids.np_play_icon_btn.icon = "pause" if (p.is_playing and not p.is_paused) else "play"

        dur = p.track_duration or 0
        pos = min(p.current_position, dur) if dur else 0
        self.ids.np_slider.max = max(dur, 1)
        if not self.ids.np_slider.active_drag:
            self.ids.np_slider.value = pos
        self.ids.np_time_pos.text = _fmt_time(pos)
        self.ids.np_time_dur.text = _fmt_time(dur)

        favs = app.storage.data.get("favorites", [])
        filename = None
        if p.queue and p.current_queue_idx >= 0:
            filename = p.queue[p.current_queue_idx].get("filename")
        self.ids.np_fav_icon_btn.icon = "heart" if (filename and filename in favs) else "heart-outline"

        if self._lyrics_loaded_for != p.current_title:
            self._maybe_load_lyrics()

    def _maybe_load_lyrics(self):
        app = App.get_running_app()
        p = app.player
        if p.current_title == "Aucune lecture":
            self.ids.np_lyrics.text = ""
            return
        self._lyrics_loaded_for = p.current_title
        self.ids.np_lyrics.text = "Chargement des paroles..."

        title, artist = p.current_title, p.current_artist
        video_id = None
        if p.queue and p.current_queue_idx >= 0:
            video_id = p.queue[p.current_queue_idx].get("video_id")

        def worker():
            lyrics = app.youtube.fetch_lyrics(title, artist, video_id)
            Clock.schedule_once(lambda dt: self._set_lyrics(title, lyrics), 0)

        threading.Thread(target=worker, daemon=True).start()

    def _set_lyrics(self, for_title, lyrics):
        app = App.get_running_app()
        if app.player.current_title == for_title:
            self.ids.np_lyrics.text = lyrics

    def toggle_pause(self):
        App.get_running_app().player.toggle_pause()

    def play_next(self):
        App.get_running_app().player.play_next()

    def play_prev(self):
        App.get_running_app().player.play_prev()

    def on_slider_seek(self, value):
        App.get_running_app().player.seek(value)

    def toggle_favorite(self):
        app = App.get_running_app()
        p = app.player
        if not (p.queue and p.current_queue_idx >= 0):
            return
        filename = p.queue[p.current_queue_idx].get("filename")
        if not filename:
            return
        app.storage.toggle_favorite(filename)
        favs = app.storage.data.get("favorites", [])
        self.ids.np_fav_icon_btn.icon = "heart" if filename in favs else "heart-outline"

    def go_back(self):
        App.get_running_app().root_layout.ids.sm.current = "home"
