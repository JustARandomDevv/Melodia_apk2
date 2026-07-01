from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import StringProperty
from kivy.app import App


class BottomNavBar(MDBoxLayout):
    active = StringProperty("home")

    def go(self, screen_name):
        app = App.get_running_app()
        sm = app.root_layout.ids.sm
        sm.current = screen_name
        self.active = screen_name
