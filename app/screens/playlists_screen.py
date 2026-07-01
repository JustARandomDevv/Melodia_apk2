import os

from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton
from kivy.app import App
from kivy.metrics import dp
from kivy.uix.behaviors import ButtonBehavior

from app import theme


class PlaylistRow(ButtonBehavior, MDBoxLayout):
    pass


class PlaylistsScreen(MDScreen):
    def on_pre_enter(self, *args):
        self.refresh()

    def refresh(self):
        app = App.get_running_app()
        container = self.ids.get("playlists_container")
        if not container:
            return
        container.clear_widgets()
        playlists = app.storage.data.get("playlists", {})

        if not playlists:
            self.ids.empty_label.opacity = 1
            return
        self.ids.empty_label.opacity = 0

        for name, files in playlists.items():
            row = PlaylistRow(
                orientation="horizontal",
                padding=[dp(14), dp(10), dp(10), dp(10)],
                spacing=dp(10),
                size_hint_y=None,
                height=dp(60),
            )
            with row.canvas.before:
                from kivy.graphics import Color, RoundedRectangle
                Color(*theme.GLASS)
                rr = RoundedRectangle(pos=row.pos, size=row.size, radius=[dp(14)])
                row.bind(pos=lambda inst, val, r=rr: setattr(r, "pos", val))
                row.bind(size=lambda inst, val, r=rr: setattr(r, "size", val))

            icon = MDIconButton(icon="playlist-music", disabled=True,
                                 theme_text_color="Custom", text_color=theme.ACCENT)
            label_box = MDBoxLayout(orientation="vertical")
            label_box.add_widget(MDLabel(
                text=name, bold=True, theme_text_color="Custom", text_color=theme.TEXT_PRIMARY
            ))
            label_box.add_widget(MDLabel(
                text=f"{len(files)} titre(s)", font_style="Label", role="small",
                theme_text_color="Custom", text_color=theme.TEXT_SECONDARY
            ))
            delete_btn = MDIconButton(icon="trash-can-outline",
                                       theme_text_color="Custom", text_color=theme.TEXT_SECONDARY)
            delete_btn.bind(on_release=lambda inst, n=name: self._delete_playlist(n))

            row.add_widget(icon)
            row.add_widget(label_box)
            row.add_widget(delete_btn)
            row.bind(on_release=lambda inst, n=name: self._play_playlist(n))
            container.add_widget(row)

    def _play_playlist(self, name):
        App.get_running_app().player.play_playlist(name)

    def _delete_playlist(self, name):
        App.get_running_app().storage.delete_playlist(name)
        self.refresh()

    def open_create_dialog(self):
        app = App.get_running_app()
        from kivymd.uix.dialog import (
            MDDialog, MDDialogHeadlineText, MDDialogSupportingText,
            MDDialogButtonContainer, MDDialogContentContainer
        )
        from kivymd.uix.button import MDButton, MDButtonText
        from kivymd.uix.textfield import MDTextField, MDTextFieldHintText

        name_field = MDTextField(MDTextFieldHintText(text="Nom de la playlist"))

        def do_create(*args):
            name = name_field.text.strip()
            if name:
                app.storage.create_playlist(name, [])
                self.refresh()
            dialog.dismiss()

        dialog = MDDialog(
            MDDialogHeadlineText(text="Nouvelle playlist"),
            MDDialogContentContainer(name_field),
            MDDialogButtonContainer(
                MDButton(MDButtonText(text="Annuler"), style="text",
                         on_release=lambda *a: dialog.dismiss()),
                MDButton(MDButtonText(text="Créer"), style="filled",
                         on_release=do_create),
            ),
        )
        dialog.open()
