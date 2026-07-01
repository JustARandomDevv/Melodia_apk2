[app]
title = Melodia
package.name = melodia
package.domain = org.melodia

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,ttf,json

version = 1.0.0

# Dépendances Python embarquées dans l'APK.
# NB: pas de "ffmpeg" ici volontairement — voir README pour l'explication
# (yt-dlp télécharge le flux audio natif sans réencodage pour rester compilable).
requirements = python3,kivy==2.3.1,kivymd==2.0.1,pillow,ytmusicapi,yt-dlp,requests,certifi,charset-normalizer,idna,urllib3,mutagen

orientation = portrait
fullscreen = 0

icon.filename = %(source.dir)s/assets/icons/icon.png
presplash.filename = %(source.dir)s/assets/icons/presplash.png

android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,FOREGROUND_SERVICE,POST_NOTIFICATIONS

android.api = 34
android.minapi = 24
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True
android.accept_sdk_license = True

# Kivy/KivyMD ont besoin d'AndroidX
android.enable_androidx = True

[buildozer]
log_level = 2
warn_on_root = 1
