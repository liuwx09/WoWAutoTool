"""
Image Recognizer Module
Template matching and color detection
"""
import cv2
import numpy as np
import os

class ImageRecognizer:
    def __init__(self, template_dir="images"):
        self.template_dir = template_dir
        self.templates = {}
        self.threshold = 0.8
        
        # Load all templates from directory
        self.load_templates()
    
    def load_templates(self):
        """Load all template images from the template directory."""
        if not os.path.exists(self.template_dir):
            os.makedirs(self.template_dir, exist_ok=True)
            return
        
        for filename in os.listdir(self.template_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                template_path = os.path.join(self.template_dir, filename)
                template = cv2.imread(template_path, cv2.IMREAD_COLOR)
                if template is not None:
                    name = os.path.splitext(filename)[0]
                    self.templates[name] = template
                    print(f"Loaded template: {name}")
    
    def add_template(self, name, image):
        """Add a template programmatically."""
        self.templates[name] = image
    
    def find_template(self, screenshot, template_name, threshold=None):
        """
        Find a template in screenshot.
        Returns: (found: bool, x: int, y: int, confidence: float)
        """
        if template_name not in self.templates:
            return False, 0, 0, 0.0
        
        template = self.templates[template_name]
        threshold = threshold or self.threshold
        
        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        if max_val >= threshold:
            h, w = template.shape[:2]
            center_x = max_loc[0] + w // 2
            center_y = max_loc[1] + h // 2
            return True, center_x, center_y, float(max_val)
        
        return False, 0, 0, 0.0
    
    def find_all_templates(self, screenshot, template_name, threshold=None):
        """Find all occurrences of a template."""
        if template_name not in self.templates:
            return []
        
        template = self.templates[template_name]
        threshold = threshold or self.threshold
        
        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        locations = np.where(result >= threshold)
        
        matches = []
        h, w = template.shape[:2]
        
        for pt in zip(*locations[::-1]):
            center_x = pt[0] + w // 2
            center_y = pt[1] + h // 2
            confidence = float(result[pt[1], pt[0]])
            matches.append((center_x, center_y, confidence))
        
        return matches
    
    def detect_color_region(self, screenshot, color_range, region=None):
        """
        Detect color region.
        color_range: ((lower_b, lower_g, lower_r), (upper_b, upper_g, upper_r))
        Returns: list of bounding boxes
        """
        if region:
            img = screenshot[region[1]:region[1]+region[3], region[0]:region[0]+region[2]]
        else:
            img = screenshot
        
        lower, upper = color_range
        mask = cv2.inRange(img, np.array(lower), np.array(upper))
        
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        boxes = []
        for cnt in contours:
            if cv2.contourArea(cnt) > 50:
                x, y, w, h = cv2.boundingRect(cnt)
                boxes.append((x, y, w, h))
        
        return boxes
    
    def detect_hp_bar(self, screenshot, region=None):
        """
        Detect health bar percentage using red color.
        Returns: percentage 0-100
        """
        if region:
            img = screenshot[region[1]:region[1]+region[3], region[0]:region[0]+region[2]]
        else:
            img = screenshot
        
        # Convert to HSV
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # Red color mask (HP bars are typically red)
        lower_red1 = np.array([0, 100, 100])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([170, 100, 100])
        upper_red2 = np.array([180, 255, 255])
        
        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        mask = cv2.bitwise_or(mask1, mask2)
        
        total = mask.size
        if total == 0:
            return 0
        
        filled = np.count_nonzero(mask)
        return min(100, max(0, (filled / total) * 100))
    
    def detect_mp_bar(self, screenshot, region=None):
        """Detect mana bar percentage using blue color."""
        if region:
            img = screenshot[region[1]:region[1]+region[3], region[0]:region[0]+region[2]]
        else:
            img = screenshot
        
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # Blue color mask (mana bars are typically blue)
        lower_blue = np.array([100, 100, 100])
        upper_blue = np.array([130, 255, 255])
        
        mask = cv2.inRange(hsv, lower_blue, upper_blue)
        
        total = mask.size
        if total == 0:
            return 0
        
        filled = np.count_nonzero(mask)
        return min(100, max(0, (filled / total) * 100))
    
    def reload_templates(self):
        """Reload templates from disk."""
        self.templates.clear()
        self.load_templates()
