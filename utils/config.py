"""
Configuration Manager
"""
import json
import os

DEFAULT_CONFIG = {
    "version": "1.0",
    "capture_interval_ms": 100,
    "template_match_threshold": 0.8,
    "max_actions_per_second": 3,
    "random_delay_min_ms": 50,
    "random_delay_max_ms": 150,
    "hp_threshold": 70,
    "mp_threshold": 40,
    "combat_check_interval_ms": 200,
    "loot_check_enabled": True,
    "auto_eat_enabled": True,
    "auto_drink_enabled": True,
    "log_level": "INFO",
}

class Config:
    def __init__(self, config_path="config.json"):
        self.config_path = config_path
        self.config = DEFAULT_CONFIG.copy()
        self.load()
    
    def load(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    self.config.update(loaded)
            except Exception as e:
                print(f"Config load error: {e}")
    
    def save(self):
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Config save error: {e}")
    
    def get(self, key, default=None):
        return self.config.get(key, default)
    
    def set(self, key, value):
        self.config[key] = value
    
    def update(self, updates):
        self.config.update(updates)
