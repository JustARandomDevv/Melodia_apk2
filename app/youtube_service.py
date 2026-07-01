"""
YouTubeService — recherche (ytmusicapi) + téléchargement audio (yt-dlp).

IMPORTANT (lire le README) :
- Usage personnel / sideload uniquement. Cette fonctionnalité viole les CGU YouTube
  et n'est pas éligible au Play Store.
- Sur Android, la conversion en .mp3 nécessite ffmpeg, qui n'est pas fiable à
  empaqueter avec python-for-android. On télécharge donc directement le meilleur
  flux audio natif (m4a/webm/opus) SANS réencodage : kivy.core.audio le lit nativement.
"""
import os
import re
import threading
import urllib.request


def _safe_filename(text):
    return "".join(c for c in text if c.isalnum() or c in (" ", "-", "_")).strip()


class YouTubeService:
    def __init__(self, download_dir):
        self.download_dir = download_dir
        self._yt = None  # lazy init : ytmusicapi fait une requête réseau à l'init

    @property
    def yt(self):
        if self._yt is None:
            from ytmusicapi import YTMusic
            self._yt = YTMusic()
        return self._yt

    # ── Recherche ──────────────────────────────────────────────────
    def search(self, query, limit=15):
        try:
            results = self.yt.search(query, filter="songs")[:limit]
            return [self._format_result(t) for t in results]
        except Exception as e:
            print("Search error:", e)
            return []

    def get_recommendations(self, seed_text=None, limit=12):
        try:
            if seed_text:
                res = self.yt.search(seed_text, filter="songs", limit=1)
                if res and "videoId" in res[0]:
                    watch = self.yt.get_watch_playlist(videoId=res[0]["videoId"], limit=limit + 3)
                    tracks = watch.get("tracks", [])[1:limit + 1]
                    return [self._format_result(t) for t in tracks]
            results = self.yt.search("Top Hits Trending", filter="songs", limit=limit)
            return [self._format_result(t) for t in results]
        except Exception as e:
            print("Recommendations error:", e)
            return []

    def _format_result(self, t):
        thumbs = t.get("thumbnails") or t.get("thumbnail") or []
        thumb = thumbs[-1].get("url") if isinstance(thumbs, list) and thumbs else None
        return {
            "title": (t.get("title") or "Inconnu")[:60],
            "artist": (t.get("artists") or [{}])[0].get("name", "Inconnu"),
            "duration": t.get("duration", ""),
            "video_id": t.get("videoId", ""),
            "thumb": thumb,
        }

    # ── Téléchargement ────────────────────────────────────────────
    def download_track_async(self, video_id, title, artist, thumb_url, on_done, on_error=None):
        """Télécharge en arrière-plan et appelle on_done(track_dict) sur le thread worker.
        L'appelant est responsable de repasser sur le thread principal (Clock.schedule_once)."""
        t = threading.Thread(
            target=self._download_worker,
            args=(video_id, title, artist, thumb_url, on_done, on_error),
            daemon=True,
        )
        t.start()
        return t

    def _download_worker(self, video_id, title, artist, thumb_url, on_done, on_error):
        try:
            import yt_dlp

            safe = _safe_filename(f"{title} - {artist}") or video_id
            jpg_path = os.path.join(self.download_dir, safe + ".jpg")

            if thumb_url:
                try:
                    req = urllib.request.Request(thumb_url, headers={"User-Agent": "Mozilla/5.0"})
                    with urllib.request.urlopen(req, timeout=6) as r, open(jpg_path, "wb") as f:
                        f.write(r.read())
                except Exception as e:
                    print("Thumbnail download failed:", e)
                    jpg_path = None

            # Pas de postprocessor FFmpegExtractAudio : on garde le format natif
            # (m4a/opus/webm) pour éviter la dépendance ffmpeg sur Android.
            opts = {
                "format": "bestaudio[ext=m4a]/bestaudio/best",
                "outtmpl": os.path.join(self.download_dir, safe + ".%(ext)s"),
                "quiet": True,
                "no_warnings": True,
                "noplaylist": True,
            }
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(f"https://music.youtube.com/watch?v={video_id}", download=True)
                downloaded_path = ydl.prepare_filename(info)

            track = {
                "title": title,
                "artist": artist,
                "path": downloaded_path,
                "art_path": jpg_path if jpg_path and os.path.exists(jpg_path) else "",
                "filename": os.path.basename(downloaded_path),
                "video_id": video_id,
            }
            on_done(track)
        except Exception as e:
            print("Download error:", e)
            if on_error:
                on_error(str(e))

    # ── Paroles ──────────────────────────────────────────────────
    def fetch_lyrics(self, title, artist, video_id=None):
        try:
            vid = video_id
            if not vid:
                res = self.yt.search(f"{title} {artist}", filter="songs", limit=1)
                if res:
                    vid = res[0].get("videoId")
            if not vid:
                return "Impossible d'identifier le morceau."
            watch = self.yt.get_watch_playlist(videoId=vid)
            lid = watch.get("lyrics")
            if not lid:
                return "Instrumental ou paroles introuvables."
            return self.yt.get_lyrics(lid).get("lyrics", "Paroles introuvables.")
        except Exception as e:
            print("Lyrics error:", e)
            return "Échec du chargement des paroles."
