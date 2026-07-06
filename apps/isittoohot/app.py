import app
from app_components import tokens
from events.input import Buttons, BUTTON_TYPES
from tildagonos import tildagonos


def _get_state(temp):
    if temp >= 34: return "WE'RE ALL GONNA DIE", (1.0, 0.0, 0.0), (255,   0,   0)
    if temp >= 33: return "DEAR GOD YES",        (1.0, 0.0, 0.0), (255,   0,   0)
    if temp >= 32: return "ABSOLUTELY YES",       (1.0, 0.0, 0.0), (255,   0,   0)
    if temp >= 31: return "OH GOD YES",           (1.0, 0.0, 0.0), (255,   0,   0)
    if temp >= 30: return "SEND HELP",            (0.9, 0.1, 0.0), (230,  25,   0)
    if temp >= 29: return "YEAH IT IS",           (0.8, 0.2, 0.0), (200,  50,   0)
    if temp >= 28: return "OH YES",               (0.8, 0.2, 0.0), (200,  50,   0)
    if temp >= 27: return "YES",                  (0.7, 0.3, 0.0), (180,  80,   0)
    if temp >= 26: return "yes...",               (0.8, 0.5, 0.0), (200, 130,   0)
    if temp >= 25: return "a bit yeah",           (0.9, 0.7, 0.0), (220, 170,   0)
    if temp >= 21: return "NO",                   (0.0, 0.6, 0.1), (  0, 150,  25)
    if temp >= 18: return "no",                   (0.0, 0.5, 0.1), (  0, 120,  25)
    return             "ABSOLUTELY NOT",          (0.0, 0.4, 0.2), (  0, 100,  50)


class IsItTooHotApp(app.App):
    def __init__(self):
        super().__init__()
        self.button_states = Buttons(self)

    def update(self, delta):
        if self.button_states.get(BUTTON_TYPES["CANCEL"]):
            self.button_states.clear()
            self.minimise()
        return False

    def draw(self, ctx):
        ctx.rgb(0.4, 0.4, 0.4).rectangle(-120, -120, 240, 240).fill()
        ctx.rgb(1, 1, 1)
        ctx.font_size = 24
        ctx.text_align = ctx.CENTER
        ctx.text_baseline = "middle"
        ctx.move_to(0, 0).text("skeleton")
        self.draw_overlays(ctx)


__app_export__ = IsItTooHotApp
