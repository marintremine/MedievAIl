import time
from pynput import keyboard, mouse
import queue
from settings import FPS, TICK_RATE, GAME_SPEED
from models.battle_model import BattleModel
from views.battle_view import BattleView



class BattleController:
    def __init__(self, model : BattleModel, view : BattleView):
        self.model = model
        self.view = view
        self.game_speed = GAME_SPEED
        self.datafile = None

        self.actions = queue.Queue()
        self._start_keyboard_listener()

    def _start_keyboard_listener(self):
        def on_press(key):
            try:
                if key == keyboard.KeyCode.from_char('p'):
                    self.actions.put("pause")
                elif key == keyboard.Key.f11:
                    self.actions.put("save")
                elif key == keyboard.Key.up:
                    self.actions.put("move_up")
                elif key == keyboard.Key.down:
                    self.actions.put("move_down")
                elif key == keyboard.Key.left:
                    self.actions.put("move_left")
                elif key == keyboard.Key.right:
                    self.actions.put("move_right")
                elif key == keyboard.KeyCode.from_char('+'):
                    self.actions.put("speed_up")
                elif key == keyboard.KeyCode.from_char('-'):
                    self.actions.put("speed_down")
                elif key == keyboard.Key.f1:
                    self.actions.put("next_view_mode")
                elif key == keyboard.Key.f2:
                    self.actions.put("prev_view_mode")
                elif key == keyboard.Key.esc:
                    self.actions.put("exit")

            except AttributeError:
                pass
        
        def on_scroll(x, y, dx, dy):
            if dy > 0:
                self.actions.put("scroll_up")
            elif dy < 0:
                self.actions.put("scroll_down")

        listener = keyboard.Listener(on_press=on_press)
        listener.daemon = True # Permet au thread de se fermer avec le programme principal
        listener.start()

        mouse_listener = mouse.Listener(on_scroll=on_scroll)
        mouse_listener.daemon = True
        mouse_listener.start()

    def speed_up(self):
        self.game_speed = min(self.game_speed + 0.25, 10.0)

    def speed_down(self):
        self.game_speed = max(self.game_speed - 0.25, 0.25)

    def run(self):
        tick_interval = 1 / TICK_RATE
        frame_interval = 1 / FPS

        last_tick = time.time()
        last_frame = time.time()
        last_stats = time.time()

        tick_count = 0
        frame_count = 0

        try:
            while True:
                now = time.time()

                while not self.actions.empty():
                    action = self.actions.get()
                    match action:
                        case "pause":
                            self.model.pause()
                            break
                        case "save":
                            self.model.save(self.datafile)
                            break
                        case "snapshot":
                            self.model.running = False
                            self.model.snapshot_html()
                            break
                        case "speed_up":
                            self.speed_up()
                            break
                        case "speed_down":
                            self.speed_down()
                            break
                        case "move_up":
                            self.view.move_view(0, -1)
                            break
                        case "move_down":
                            self.view.move_view(0, 1)
                            break
                        case "move_left":
                            self.view.move_view(-1, 0)
                            break
                        case "move_right":
                            self.view.move_view(1, 0)
                            break
                        case "scroll_up":
                            self.view.scroll_up()
                            break
                        case "scroll_down":
                            self.view.scroll_down()
                            break
                        case "next_view_mode":
                            self.view.next_view_mode()
                            break
                        case "prev_view_mode":
                            self.view.prev_view_mode()
                            break
                        case "exit":
                            return

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
        finally:
            # Nettoyage terminal à la fin de la boucle
            self.view.cleanup()