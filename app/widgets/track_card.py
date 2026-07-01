from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import StringProperty, BooleanProperty, ObjectProperty


class TrackCard(MDBoxLayout):
    """Ligne réutilisable : pochette, titre, artiste, bouton d'action.
    Utilisée dans Search, Library, Queue, Playlist detail."""
    title_text = StringProperty("")
    artist_text = StringProperty("")
    art_source = StringProperty("")
    is_favorite = BooleanProperty(False)
    show_favorite = BooleanProperty(False)
    show_add = BooleanProperty(False)
    on_press_cb = ObjectProperty(None, allownone=True)
    on_favorite_cb = ObjectProperty(None, allownone=True)
    on_add_cb = ObjectProperty(None, allownone=True)

    def fire_press(self):
        if self.on_press_cb:
            self.on_press_cb()

    def fire_favorite(self):
        if self.on_favorite_cb:
            self.on_favorite_cb()

    def fire_add(self):
        if self.on_add_cb:
            self.on_add_cb()
