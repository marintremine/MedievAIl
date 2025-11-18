import time

from models.battle_model import BattleModel
from views.battle_view import BattleView

class BattleController:
    def __init__(self, model : BattleModel, view : BattleView, tick_rate: int = 20, fps: int = 60):
        self.model = model
        self.view = view
        self.tick_rate = tick_rate
        self.fps = fps

    def run(self):
        tick_interval = 1 / self.tick_rate
        frame_interval = 1 / self.fps

        last_tick = time.time()
        last_frame = time.time()

        last_stats = time.time()
        tick_count = 0
        frame_count = 0

        while self.model.running:
            now = time.time()

            # --- LOGIC TICK ---
            if now - last_tick >= tick_interval:
                self.model.update()
                tick_count += 1
                last_tick = now
                # print(f"Tick executed ({tick_count}/{self.tick_rate} TPS)")

            # --- RENDER FRAME ---

            if now - last_frame >= frame_interval:
                self.view.render()
                frame_count += 1
                last_frame = now
                # print(f"Frame rendered ({frame_count}/{self.fps} FPS)")

            # --- STATS OUTPUT ---
            if now - last_stats >= 1.0:
                print(f"TPS: {tick_count} | FPS: {frame_count}")
                tick_count = 0
                frame_count = 0
                last_stats = now

            time.sleep(0.001) # Sleep pour éviter l'utilisation à 100% du CPU

    