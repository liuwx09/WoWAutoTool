"""
Game Controller Module
Keyboard and mouse input simulation
"""
import time
import random
import platform

if platform.system() == "Windows":
    import pydirectinput

class GameController:
    def __init__(self, config=None):
        self.config = config
        self.last_action_time = 0
        self.action_count = 0
        self.max_actions_per_second = 3
        
        if platform.system() == "Windows":
            pydirectinput.PAUSE = 0
    
    def _get_delay(self):
        """Get random delay based on config."""
        if self.config and self.config.get('random_delay_max_ms', 150) > 0:
            min_ms = self.config.get('random_delay_min_ms', 50)
            max_ms = self.config.get('random_delay_max_ms', 150)
            return random.uniform(min_ms / 1000, max_ms / 1000)
        return 0.05
    
    def _can_act(self):
        """Rate limiting check."""
        if not self.config or not self.config.get('max_actions_per_second'):
            return True
        
        now = time.time()
        min_interval = 1.0 / self.max_actions_per_second
        if now - self.last_action_time < min_interval:
            return False
        return True
    
    def key_press(self, key):
        """Press and release a key."""
        if not self._can_act():
            return False
        
        try:
            time.sleep(self._get_delay())
            pydirectinput.press(key)
            self.last_action_time = time.time()
            self.action_count += 1
            return True
        except Exception as e:
            print(f"Key press error: {e}")
            return False
    
    def key_down(self, key):
        """Hold down a key."""
        try:
            time.sleep(self._get_delay())
            pydirectinput.keyDown(key)
            return True
        except Exception as e:
            print(f"Key down error: {e}")
            return False
    
    def key_up(self, key):
        """Release a key."""
        try:
            pydirectinput.keyUp(key)
            return True
        except Exception as e:
            print(f"Key up error: {e}")
            return False
    
    def hold_key(self, key, duration):
        """Hold a key for specified duration."""
        try:
            self.key_down(key)
            time.sleep(duration)
            self.key_up(key)
            return True
        except Exception as e:
            print(f"Hold key error: {e}")
            return False
    
    def combo(self, keys):
        """Press multiple keys simultaneously."""
        try:
            for key in keys:
                self.key_down(key)
                time.sleep(0.05)
            time.sleep(0.1)
            for key in keys:
                self.key_up(key)
            return True
        except Exception as e:
            print(f"Combo error: {e}")
            return False
    
    def mouse_click(self, x=None, y=None, button='left'):
        """Click at position."""
        if not self._can_act():
            return False
        
        try:
            time.sleep(self._get_delay())
            
            if x is not None and y is not None:
                offset_x = random.randint(-2, 2)
                offset_y = random.randint(-2, 2)
                pydirectinput.moveTo(x + offset_x, y + offset_y)
                time.sleep(0.05)
            
            pydirectinput.click(button=button)
            self.last_action_time = time.time()
            self.action_count += 1
            return True
        except Exception as e:
            print(f"Mouse click error: {e}")
            return False
    
    def scroll(self, clicks):
        """Scroll mouse wheel."""
        try:
            time.sleep(self._get_delay())
            pydirectinput.scroll(clicks)
            self.last_action_time = time.time()
            return True
        except Exception as e:
            print(f"Scroll error: {e}")
            return False
    
    def stop_all(self):
        """Emergency stop - release all keys."""
        try:
            pydirectinput.press('escape')
            for key in ['w', 'a', 's', 'd', 'space', 'shift', 'ctrl', 'alt']:
                try:
                    pydirectinput.keyUp(key)
                except:
                    pass
            return True
        except:
            return False
