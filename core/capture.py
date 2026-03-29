"""
Screen Capture Module
"""
import mss
import numpy as np
import cv2

class ScreenCapture:
    def __init__(self):
        self.sct = mss.mss()
        self.monitor = self.sct.monitors[1]  # Primary monitor
    
    def set_monitor(self, monitor_id=1):
        self.monitor = self.sct.monitors[monitor_id]
        return self.monitor
    
    def capture(self, region=None):
        """Capture screen or specific region. Returns BGR numpy array."""
        if region:
            bbox = {
                "left": int(region[0]),
                "top": int(region[1]),
                "width": int(region[2]),
                "height": int(region[3])
            }
        else:
            bbox = self.monitor
        
        screenshot = self.sct.grab(bbox)
        img = np.array(screenshot)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        return img
    
    def capture_gray(self, region=None):
        """Capture as grayscale image."""
        img = self.capture(region)
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    def get_pixel(self, x, y):
        """Get pixel color at (x, y). Returns BGR tuple."""
        screenshot = self.sct.grab({
            "left": int(x),
            "top": int(y),
            "width": 1,
            "height": 1
        })
        img = np.array(screenshot)
        return tuple(int(c) for c in img[0][0][:3])
    
    def save(self, filename, region=None):
        """Save screenshot to file."""
        img = self.capture(region)
        cv2.imwrite(filename, img)
        return filename
    
    def close(self):
        self.sct.close()
