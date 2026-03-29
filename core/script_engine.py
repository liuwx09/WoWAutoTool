"""
Script Engine Module
Loads and executes game scripts
"""
import os
import sys
import importlib.util
import time
from datetime import datetime

class ScriptEngine:
    def __init__(self, scripts_dir="scripts", logger=None):
        self.scripts_dir = scripts_dir
        self.logger = logger
        self.scripts = {}
        self.current_script = None
        self.running = False
        self.paused = False
        
        os.makedirs(scripts_dir, exist_ok=True)
        self.load_scripts()
    
    def load_scripts(self):
        """Load all scripts from the scripts directory."""
        self.scripts.clear()
        
        if not os.path.exists(self.scripts_dir):
            os.makedirs(self.scripts_dir, exist_ok=True)
            return
        
        for filename in os.listdir(self.scripts_dir):
            if filename.endswith('.py') and not filename.startswith('_'):
                script_path = os.path.join(self.scripts_dir, filename)
                script_name = os.path.splitext(filename)[0]
                
                try:
                    spec = importlib.util.spec_from_file_location(script_name, script_path)
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[script_name] = module
                    spec.loader.exec_module(module)
                    
                    if hasattr(module, 'Script'):
                        self.scripts[script_name] = module.Script
                        if self.logger:
                            self.logger.info(f"Loaded script: {script_name}")
                except Exception as e:
                    if self.logger:
                        self.logger.error(f"Failed to load script {script_name}: {e}")
    
    def get_script(self, name):
        """Get a script by name."""
        return self.scripts.get(name)
    
    def list_scripts(self):
        """List all available scripts."""
        return list(self.scripts.keys())
    
    def execute_script(self, script_name, context):
        """
        Execute a script with the given context.
        context contains: controller, recognizer, capture, config, logger, status
        """
        if script_name not in self.scripts:
            if self.logger:
                self.logger.error(f"Script not found: {script_name}")
            return False
        
        script_class = self.scripts[script_name]
        script_instance = script_class(context, self.logger)
        
        try:
            return script_instance.run()
        except Exception as e:
            if self.logger:
                self.logger.error(f"Script execution error: {e}")
            return False
    
    def create_sample_script(self):
        """Create a sample script file."""
        sample_content = '''"""
Sample Battle Script
Copy this as template for your own scripts
"""

class Script:
    """Battle script template"""
    
    def __init__(self, ctx, logger):
        """
        Initialize script with context.
        ctx contains:
            - controller: GameController instance
            - recognizer: ImageRecognizer instance
            - capture: ScreenCapture instance
            - config: Config instance
            - logger: Logger instance
            - status: dict with current game status
        """
        self.ctx = ctx
        self.logger = logger
        self.controller = ctx.get('controller')
        self.recognizer = ctx.get('recognizer')
        self.capture = ctx.get('capture')
        self.config = ctx.get('config')
        self.status = ctx.get('status', {})
        
        # Script-specific state
        self.in_combat = False
        self.last_cast_time = 0
    
    def run(self):
        """
        Main script execution loop.
        Returns: True if action taken, False if idle
        """
        # Update status
        screenshot = self.capture.capture()
        
        # Check game state
        hp = self.recognizer.detect_hp_bar(screenshot)
        mp = self.recognizer.detect_mp_bar(screenshot)
        
        self.status['player_hp'] = hp
        self.status['player_mp'] = mp
        
        # Check if in combat (simplified - looking for red bars)
        enemies = self.recognizer.find_all_templates(screenshot, 'enemy_redbar')
        
        if enemies:
            if not self.in_combat:
                self.logger.info("Combat started")
                self.in_combat = True
            
            return self.combat_action()
        else:
            if self.in_combat:
                self.logger.info("Combat ended")
                self.in_combat = False
            
            return self.idle_action()
    
    def combat_action(self):
        """Execute combat rotation."""
        current_time = time.time()
        
        # Prevent spamming
        if current_time - self.last_cast_time < 1.5:
            return False
        
        # Cast damage spell
        self.controller.key_press('2')  # Fireball
        self.last_cast_time = current_time
        
        return True
    
    def idle_action(self):
        """Actions when not in combat."""
        # Auto targeting
        self.controller.key_press('tab')
        return True
'''
        
        sample_path = os.path.join(self.scripts_dir, "sample_battle.py")
        with open(sample_path, 'w', encoding='utf-8') as f:
            f.write(sample_content)
        
        if self.logger:
            self.logger.info(f"Created sample script: {sample_path}")
