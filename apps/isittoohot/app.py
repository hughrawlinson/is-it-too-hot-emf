import app
import asyncio
import json
import random
from events.input import Buttons, BUTTON_TYPES
from tildagonos import tildagonos

_BROKER = "mqtt.emf.camp"
_PORT = 1883
_TOPIC = b"weather/hq"
_DETAIL_MS = 4000
_NAV_BTNS = tuple(BUTTON_TYPES[b] for b in ("CONFIRM", "UP", "DOWN", "LEFT", "RIGHT"))


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
        self.temp = None
        self._state = None
        self.view = "loading"
        self._connected = False
        self._detail_ms = 0
        self._set_leds()

    def _set_leds(self):
        if self._state is None or self.view in ("loading", "error"):
            color = (10, 10, 10)
        else:
            _, _, color = self._state
        for i in range(19):
            tildagonos.leds[i] = color
        tildagonos.leds.write()

    def _on_mqtt_message(self, topic, msg):
        try:
            data = json.loads(msg)
            self.temp = float(data["temp"])
            self._state = _get_state(self.temp)
            self.view = "verdict"
            self._set_leds()
        except Exception as e:
            print("MQTT parse error:", e)

    async def _mqtt_loop(self):
        try:
            from umqtt.robust import MQTTClient
        except ImportError:
            from umqtt.simple import MQTTClient

        client_id = "badge-hot-{:04x}".format(random.getrandbits(16))

        while True:
            try:
                client = MQTTClient(client_id, _BROKER, port=_PORT, keepalive=60)
                client.set_callback(self._on_mqtt_message)
                client.connect()
                client.subscribe(_TOPIC)
                self._connected = True

                while True:
                    client.check_msg()
                    await asyncio.sleep(1)

            except Exception as e:
                print("MQTT error:", e)
                self._connected = False
                self.view = "error"
                self._set_leds()
                await asyncio.sleep(15)

    async def run(self, render_update):
        asyncio.create_task(self._mqtt_loop())
        await super().run(render_update)

    def update(self, delta):
        if self.button_states.get(BUTTON_TYPES["CANCEL"]):
            self.button_states.clear()
            self.minimise()
            return False

        if self.view == "detail":
            self._detail_ms -= delta
            for btn in _NAV_BTNS:
                if self.button_states.get(btn):
                    self.button_states.clear()
                    self.view = "verdict"
                    return True
            if self._detail_ms <= 0:
                self.view = "verdict"
                return True
            return False

        if self.view == "verdict" and self._state is not None:
            for btn in _NAV_BTNS:
                if self.button_states.get(btn):
                    self.button_states.clear()
                    self.view = "detail"
                    self._detail_ms = _DETAIL_MS
                    return True

        return True

    def draw(self, ctx):
        ctx.text_align = ctx.CENTER
        ctx.text_baseline = "middle"
        state = self._state

        if self.view == "loading":
            ctx.rgb(0.15, 0.15, 0.15).rectangle(-120, -120, 240, 240).fill()
            ctx.rgb(1, 1, 1)
            ctx.font_size = 20
            if self._connected:
                ctx.move_to(0, -12).text("Waiting for")
                ctx.move_to(0, 14).text("weather data...")
            else:
                ctx.move_to(0, 0).text("Connecting...")

        elif self.view == "error":
            ctx.rgb(0.15, 0.15, 0.15).rectangle(-120, -120, 240, 240).fill()
            ctx.rgb(1, 0.3, 0.3)
            ctx.font_size = 20
            ctx.move_to(0, -12).text("No data")
            ctx.rgb(0.7, 0.7, 0.7)
            ctx.font_size = 14
            ctx.move_to(0, 14).text("Retrying...")

        elif self.view == "verdict" and state is not None:
            verdict, (r, g, b), _ = state
            ctx.rgb(r * 0.5, g * 0.5, b * 0.5).rectangle(-120, -120, 240, 240).fill()
            ctx.rgb(1, 1, 1)
            ctx.font_size = 16
            ctx.move_to(0, -30).text("Is it too hot at EMF?")
            ctx.rgb(r, g, b)
            ctx.font_size = 28
            ctx.move_to(0, 10).text(verdict)
            ctx.rgb(0.8, 0.8, 0.8)
            ctx.font_size = 12
            ctx.move_to(0, 45).text("Press any button for temp")

        elif self.view == "detail" and state is not None:
            verdict, (r, g, b), _ = state
            ctx.rgb(0.08, 0.08, 0.08).rectangle(-120, -120, 240, 240).fill()
            ctx.rgb(r, g, b)
            ctx.font_size = 13
            ctx.move_to(0, -40).text("Is it too hot at EMF?")
            ctx.rgb(1, 1, 1)
            ctx.font_size = 44
            ctx.move_to(0, 5).text("{:.1f}C".format(self.temp))
            ctx.rgb(r, g, b)
            ctx.font_size = 18
            ctx.move_to(0, 46).text(verdict)

        self.draw_overlays(ctx)


__app_export__ = IsItTooHotApp
