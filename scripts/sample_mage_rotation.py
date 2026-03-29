"""
Sample Battle Script - Mage Leveling (1-60)
Copy this file and modify for your own use
"""

import time

class Script:
    """Mage auto-combat script for leveling"""
    
    def __init__(self, ctx, logger):
        self.ctx = ctx
        self.logger = logger
        self.controller = ctx.get('controller')
        self.recognizer = ctx.get('recognizer')
        self.capture = ctx.get('capture')
        self.config = ctx.get('config')
        self.status = ctx.get('status', {})
        
        # Combat state
        self.in_combat = False
        self.last_cast_time = 0
        self.cast_sequence = []
        self.cast_index = 0
        
        # Settings
        self.cast_delay = 1.8  # Seconds between casts
        self.pull_delay = 0.5
    
    def run(self):
        """Main script execution. Returns True if action taken."""
        screenshot = self.capture.capture()
        
        # Update HP/MP
        hp = self.recognizer.detect_hp_bar(screenshot)
        mp = self.recognizer.detect_mp_bar(screenshot)
        
        self.status['player_hp'] = hp
        self.status['player_mp'] = mp
        
        # Check for target (simplified - using template or color detection)
        hp_regions = self.recognizer.detect_color_region(
            screenshot,
            ((0, 0, 150), (80, 80, 255))  # Red color range for enemy HP
        )
        
        has_target = len(hp_regions) > 0
        self.status['target_exists'] = has_target
        
        # Auto eat/drink check
        self._check_consumables()
        
        # Combat logic
        if has_target:
            if not self.in_combat:
                self.logger.info("Combat started")
                self.in_combat = True
                self.cast_index = 0
            
            return self._combat_action()
        else:
            if self.in_combat:
                self.logger.info("Combat ended")
                self.in_combat = False
                self.cast_index = 0
            
            return self._idle_action()
    
    def _check_consumables(self):
        """Check and use consumables."""
        hp = self.status.get('player_hp', 100)
        mp = self.status.get('player_mp', 100)
        
        hp_threshold = self.config.get('hp_threshold', 70)
        mp_threshold = self.config.get('mp_threshold', 40)
        
        if hp < hp_threshold and self.config.get('auto_eat_enabled', True):
            self.controller.key_press('5')  # Food key
            self.logger.debug("Using food")
        
        if mp < mp_threshold and self.config.get('auto_drink_enabled', True):
            self.controller.key_press('6')  # Drink key
            self.logger.debug("Using drink")
    
    def _combat_action(self):
        """Execute combat rotation."""
        current_time = time.time()
        
        # Check cast delay
        if current_time - self.last_cast_time < self.cast_delay:
            return False
        
        # Simple rotation: fireball spam
        # In real script, you'd check mana and use different spells
        mp = self.status.get('player_mp', 100)
        
        if mp > 60:
            # High mana - use fireball
            self.controller.key_press('2')  # Fireball
            self.logger.debug("Casting Fireball")
        elif mp > 40:
            # Medium mana - use frostbolt
            self.controller.key_press('3')  # Frostbolt
            self.logger.debug("Casting Frostbolt")
        else:
            # Low mana - wand
            self.controller.key_press('1')  # Attack/Wand
            self.logger.debug("Using wand")
        
        self.last_cast_time = current_time
        return True
    
    def _idle_action(self):
        """Actions when not in combat."""
        # Find next target
        self.controller.key_press('tab')
        return True
