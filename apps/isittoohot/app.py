import app
from app_components import tokens
from events.input import Buttons, BUTTON_TYPES
from tildagonos import tildagonos


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
