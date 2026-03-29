"""
Logger Module
"""
import os
from datetime import datetime

class Logger:
    def __init__(self, name="WoWAutoTool", log_dir="logs"):
        self.name = name
        self.log_dir = log_dir
        self.log_file = None
        self.start_time = datetime.now()
        
        os.makedirs(log_dir, exist_ok=True)
        log_filename = f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        self.log_file = os.path.join(log_dir, log_filename)
        
        self.log("INFO", "Logger initialized")
    
    def log(self, level, message):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] [{level}] {message}"
        print(log_entry)
        
        if self.log_file:
            try:
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    f.write(log_entry + '\n')
            except:
                pass
    
    def info(self, message):
        self.log("INFO", message)
    
    def warning(self, message):
        self.log("WARN", message)
    
    def error(self, message):
        self.log("ERROR", message)
    
    def debug(self, message):
        self.log("DEBUG", message)
    
    def get_uptime(self):
        delta = datetime.now() - self.start_time
        hours = int(delta.total_seconds() // 3600)
        minutes = int((delta.total_seconds() % 3600) // 60)
        seconds = int(delta.total_seconds() % 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
