import time
from pynput import keyboard
from settings import FPS, TICK_RATE, GAME_SPEED
from models.battle_model import BattleModel
from views.battle_view import BattleView



class BattleController:
    def __init__(self, model : BattleModel, view : BattleView):
        self.model = model
        self.view = view
        self.game_speed = GAME_SPEED

        self._start_keyboard_listener()

    def _start_keyboard_listener(self):
        def on_press(key):
            try:
                if key == keyboard.Key.space:
                    self.model.pause()
                elif key == keyboard.Key.up:
                    # Augmenter la vitesse
                    self.game_speed = min(self.game_speed + 0.25, 10.0)
                elif key == keyboard.Key.down:
                    # Diminuer la vitesse
                    self.game_speed = max(self.game_speed - 0.25, 0.25)
            except AttributeError:
                pass

        listener = keyboard.Listener(on_press=on_press)
        listener.daemon = True
        listener.start()

    def run(self):
        tick_interval = 1 / TICK_RATE
        frame_interval = 1 / FPS

        last_tick = time.time()
        last_frame = time.time()
        last_stats = time.time()

        tick_count = 0
        frame_count = 0

        while True:
            now = time.time()
            # --- LOGIC TICK ---
            if self.model.running and (now - last_tick >= tick_interval):
                self.model.delta_time = tick_interval * self.game_speed
                self.model.update()
                tick_count += 1
                last_tick = now
                #print(f"Tick executed ({tick_count}/{self.tick_rate} TPS)")

            # --- RENDER FRAME ---

            if now - last_frame >= frame_interval:
                self.view.render()
                frame_count += 1
                last_frame = now
                #print(f"Frame rendered ({frame_count}/{self.fps} FPS)")

            # --- STATS OUTPUT ---
            if now - last_stats >= 1.0:
                #print(f"TPS: {tick_count} | FPS: {frame_count}")
                tick_count = 0
                frame_count = 0
                last_stats = now

            time.sleep(0.0001) # Sleep pour éviter l'utilisation à 100% du CPU

    