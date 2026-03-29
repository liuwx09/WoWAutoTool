# 脚本目录

放置游戏自动化脚本。

## 脚本结构

```python
class Script:
    def __init__(self, ctx, logger):
        """
        初始化脚本
        
        ctx 包含:
        - controller: GameController 实例 (按键操作)
        - recognizer: ImageRecognizer 实例 (图像识别)
        - capture: ScreenCapture 实例 (屏幕截图)
        - config: Config 实例 (配置)
        - logger: Logger 实例 (日志)
        - status: dict (当前状态)
        """
        pass
    
    def run(self):
        """
        主循环
        
        返回:
        - True: 执行了动作
        - False: 空闲
        """
        pass
```

## 可用方法

### Controller (按键操作)
```python
controller.key_press('2')      # 按键
controller.key_down('w')       # 按下
controller.key_up('w')         # 释放
controller.hold_key('w', 1.0)  # 按住1秒
controller.combo(['ctrl', 'v'])# 组合键
controller.mouse_click(100, 200) # 鼠标点击
```

### Recognizer (图像识别)
```python
recognizer.detect_hp_bar(screenshot)           # 检测血条百分比
recognizer.detect_mp_bar(screenshot)           # 检测蓝条百分比
recognizer.find_template(screenshot, 'enemy')  # 查找模板
recognizer.detect_color_region(screenshot, color_range)  # 颜色区域
```

### Capture (屏幕截图)
```python
screenshot = capture.capture()              # 全屏截图
screenshot = capture.capture(region)        # 区域截图 (x, y, w, h)
```

## 示例

见 `sample_mage_rotation.py`
