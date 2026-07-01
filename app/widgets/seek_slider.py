from kivy.uix.slider import Slider
from kivy.properties import BooleanProperty, ObjectProperty


class SeekSlider(Slider):
    """Slider standard Kivy (pas KivyMD, plus simple à styliser en canvas custom)
    avec suivi explicite de l'état de drag pour ne déclencher le seek
    qu'au relâchement du doigt."""
    active_drag = BooleanProperty(False)
    on_seek_cb = ObjectProperty(None, allownone=True)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.active_drag = True
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        was_dragging = self.active_drag
        result = super().on_touch_up(touch)
        if was_dragging and self.collide_point(*touch.pos) or was_dragging:
            self.active_drag = False
            if self.on_seek_cb:
                self.on_seek_cb(self.value)
        return result
