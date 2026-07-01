"""
PlayerService — logique de lecture audio, file d'attente, navigation piste suivante/précédente.

Remplace pygame.mixer (desktop-only) par kivy.core.audio.SoundLoader, qui s'appuie
sur des backends compatibles Android (ffpyplayer / gstreamer selon le build).
"""
import os
import random
import time
import threading

from kivy.core.audio import SoundLoader
from kivy.clock import Clock
from kivy.event import EventDispatcher
from kivy.properties import (
    BooleanProperty, StringProperty, NumericProperty, ListProperty
)


class PlayerService(EventDispatcher):
    is_playing = BooleanProperty(False)
    is_paused = BooleanProperty(False)
    current_title = StringProperty("Aucune lecture")
    current_artist = StringProperty("—")
    current_art_path = StringProperty("")
    track_duration = NumericProperty(0)
    current_position = NumericProperty(0.0)
    queue = ListProperty([])
    current_queue_idx = NumericProperty(-1)

    def __init__(self, storage, **kwargs):
        super().__init__(**kwargs)
        self.storage = storage
        self.download_dir = storage.download_dir
        self.favorites = storage.data.get("favorites", [])
        self.playlists = storage.data.get("playlists", {})
        self.settings = storage.data.get("settings", {"auto_play": True})

        self._sound = None
        self._is_switching = False
        self._intentional_stop = False
        self._pause_pos = 0.0
        self._position_event = None
        self.on_track_changed_cb = None  # callback UI facultatif

    # ── Lecture ──────────────────────────────────────────────────────
    def play_track(self, track_data):
        self._is_switching = True
        try:
            if self._sound:
                self._sound.stop()
                self._sound.unload()
                self._sound = None

            path = track_data["path"]
            snd = SoundLoader.load(path)
            if snd is None:
                print(f"Impossible de charger: {path}")
                self._is_switching = False
                return
            self._sound = snd
            self._sound.bind(on_stop=self._on_sound_stop)
            self._sound.play()

            self.track_duration = snd.length or 0
            self.current_position = 0.0
            self.is_playing = True
            self.is_paused = False
            self.current_title = track_data.get("title", "Inconnu")
            self.current_artist = track_data.get("artist", "Inconnu")
            self.current_art_path = track_data.get("art_path", "") or ""

            if self._position_event:
                self._position_event.cancel()
            self._position_event = Clock.schedule_interval(self._update_position, 0.3)

            if self.on_track_changed_cb:
                self.on_track_changed_cb(track_data)
        except Exception as e:
            print(f"Play error: {e}")
        finally:
            self._is_switching = False

    def _update_position(self, dt):
        if self._sound and self.is_playing and not self.is_paused:
            try:
                self.current_position = self._sound.get_pos()
            except Exception:
                pass

    def _on_sound_stop(self, *args):
        # Déclenché par kivy quand le son se termine naturellement OU via stop().
        # On n'avance que si on n'est pas en train de changer volontairement de piste
        # ni de mettre en pause manuellement.
        if self._is_switching or self._intentional_stop:
            self._intentional_stop = False
            return
        Clock.schedule_once(lambda dt: self._advance_track(), 0.1)

    def queue_and_play(self, track_data):
        self.queue = [track_data]
        self.current_queue_idx = 0
        self.play_track(track_data)

    def add_to_queue(self, track_data):
        self.queue = self.queue + [track_data]

    def play_next(self):
        if not self.queue or self.current_queue_idx >= len(self.queue) - 1:
            track = self._pick_random_local_track()
            if track:
                self.queue_and_play(track)
                return
            self.stop_music()
            return
        self.current_queue_idx += 1
        self.play_track(self.queue[self.current_queue_idx])

    def play_prev(self):
        if not self.queue or self.current_queue_idx <= 0:
            if self.queue and self.current_queue_idx >= 0:
                self.play_track(self.queue[self.current_queue_idx])
            return
        self.current_queue_idx -= 1
        self.play_track(self.queue[self.current_queue_idx])

    def _advance_track(self):
        self.current_position = 0.0
        if not self.queue or self.current_queue_idx >= len(self.queue) - 1:
            if self.settings.get("auto_play", True):
                track = self._pick_random_local_track()
                if track:
                    self.queue_and_play(track)
                    return
            self.stop_music()
            return
        self.play_next()

    def _pick_random_local_track(self):
        try:
            files = [f for f in os.listdir(self.download_dir) if f.lower().endswith((".mp3", ".m4a", ".opus", ".webm"))]
        except FileNotFoundError:
            files = []
        if not files:
            return None
        current_file = None
        if self.queue and self.current_queue_idx >= 0:
            current_file = os.path.basename(self.queue[self.current_queue_idx]["path"])
        available = [f for f in files if f != current_file] or files
        f = random.choice(available)
        return self._track_from_filename(f)

    def _track_from_filename(self, filename):
        base = os.path.splitext(filename)[0]
        parts = base.split(" - ")
        title = parts[0].strip()
        artist = parts[1].strip() if len(parts) > 1 else "Inconnu"
        jpg = os.path.join(self.download_dir, base + ".jpg")
        return {
            "title": title,
            "artist": artist,
            "path": os.path.join(self.download_dir, filename),
            "art_path": jpg if os.path.exists(jpg) else "",
            "filename": filename,
        }

    def toggle_pause(self):
        if not self.is_playing or not self._sound:
            return
        if self.is_paused:
            self._sound.play()
            # Sound.play() redémarre du début sur la plupart des backends Kivy :
            # on doit explicitement revenir à la position où on s'était arrêté.
            resume_pos = self._pause_pos
            Clock.schedule_once(lambda dt: self._sound.seek(resume_pos) if self._sound else None, 0.05)
        else:
            self._pause_pos = self._sound.get_pos()
            self._intentional_stop = True
            self._sound.stop()
        self.is_paused = not self.is_paused

    def seek(self, seconds):
        if not self._sound:
            return
        try:
            self._sound.seek(seconds)
            self.current_position = seconds
        except Exception as e:
            print("Seek error:", e)

    def stop_music(self):
        self._intentional_stop = True
        if self._sound:
            self._sound.stop()
            self._sound.unload()
            self._sound = None
        if self._position_event:
            self._position_event.cancel()
            self._position_event = None
        self.is_playing = False
        self.is_paused = False
        self.current_position = 0.0
        self.current_title = "Aucune lecture"
        self.current_artist = "—"
        self.current_art_path = ""

    def set_volume(self, vol):
        if self._sound:
            self._sound.volume = float(vol)

    def jump_to_queue_index(self, index):
        if 0 <= index < len(self.queue):
            self.current_queue_idx = index
            self.play_track(self.queue[index])

    def remove_from_queue(self, index):
        if 0 <= index < len(self.queue):
            q = list(self.queue)
            del q[index]
            if index < self.current_queue_idx:
                self.current_queue_idx -= 1
            self.queue = q

    def clear_queue(self):
        self.stop_music()
        self.queue = []
        self.current_queue_idx = -1

    def play_playlist(self, name):
        files = self.playlists.get(name, [])
        if not files:
            return
        self.stop_music()
        new_queue = []
        for f in files:
            full = os.path.join(self.download_dir, f)
            if not os.path.exists(full):
                continue
            new_queue.append(self._track_from_filename(f))
        self.queue = new_queue
        if self.queue:
            self.current_queue_idx = 0
            self.play_track(self.queue[0])

    def release(self):
        self.stop_music()
