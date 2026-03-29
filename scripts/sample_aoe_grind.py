"""
Sample AOE Grinding Script
For法师 25+ with Blizzard
"""

import time

class Script:
    """AOE grinding script for mages"""
    
    def __init__(self, ctx, logger):
        self.ctx = ctx
        self.logger = logger
        self.controller = ctx.get('controller')
        self.recognizer = ctx.get('recognizer')
        self.capture = ctx.get('capture')
        self.config = ctx.get('config')
        self.status = ctx.get('status', {})
        
        self.in_combat = False
        self.last_blizzard_time = 0
        self.last_cast_time = 0
    
    def run(self):
        """Main script execution."""
        screenshot = self.capture.capture()
        
        hp = self.recognizer.detect_hp_bar(screenshot)
        mp = self.recognizer.detect_mp_bar(screenshot)
        
        self.status['player_hp'] = hp
        self.status['player_mp'] = mp
        
        # Count enemies (red bar regions)
        enemy_regions = self.recognizer.detect_color_region(
            screenshot,
            ((0, 0, 150), (80, 80, 255))
        )
        
        enemy_count = len(enemy_regions)
        self.status['enemy_count'] = enemy_count
        has_target = enemy_count > 0
        self.status['target_exists'] = has_target
        
        # Consumables
        self._check_consumables()
        
        if has_target:
            if not self.in_combat:
                self.logger.info(f"AOE Combat started with {enemy_count} enemies")
                self.in_combat = True
            
            return self._aoe_combat(enemy_count)
        else:
            if self.in_combat:
                self.logger.info("AOE Combat ended")
                self.in_combat = False
            
            return self._idle_action()
    
    def _check_consumables(self):
        hp = self.status.get('player_hp', 100)
        mp = self.status.get('player_mp', 100)
        
        if hp < self.config.get('hp_threshold', 70) and self.config.get('auto_eat_enabled'):
            self.controller.key_press('5')
        
        if mp < self.config.get('mp_threshold', 40) and self.config.get('auto_drink_enabled'):
            self.controller.key_press('6')
    
    def _aoe_combat(self, enemy_count):
        """AOE combat rotation."""
        current_time = time.time()
        
        mp = self.status.get('player_mp', 100)
        
        # AOE if we have enough enemies and mana
        if enemy_count >= 3 and mp > 160:
            if current_time - self.last_blizzard_time > 8:  # Blizzard cost
                self.controller.key_press('4')  # Blizzard
                self.logger.info("Casting Blizzard")
                self.last_blizzard_time = current_time
                self.last_cast_time = current_time
                return True
        
        # Fill with arcane explosion if low mana
        if mp > 35 and current_time - self.last_cast_time > 1.5:
            self.controller.key_press('9')  # Arcane Explosion
            self.last_cast_time = current_time
            return True
        
        # Attack if nothing else
        if current_time - self.last_cast_time > 2:
            self.controller.key_press('1')
            return True
        
        return False
    
    def _idle_action(self):
        """Find targets when idle."""
        self.controller.key_press('tab')
        time.sleep(0.3)
        return True
