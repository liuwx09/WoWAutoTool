# WoW Auto Tool

一个基于图像识别的游戏自动化工具，支持自定义脚本，可编译为独立exe运行。

## 目录结构

```
WoWAutoTool/
├── main.py                 # 主程序入口
├── WoWAutoTool.spec        # PyInstaller配置文件
├── requirements.txt        # 依赖列表
│
├── core/                   # 核心模块
│   ├── capture.py         # 屏幕截图
│   ├── recognizer.py      # 图像识别
│   ├── controller.py      # 输入控制
│   └── script_engine.py   # 脚本引擎
│
├── scripts/                # 打怪脚本目录
│   ├── sample_mage_rotation.py   # 法师单体循环
│   └── sample_aoe_grind.py       # AOE练级脚本
│
├── images/                 # 模板图片目录
│   └── (放置你的模板图片)
│
├── logs/                   # 运行日志
│
├── utils/                  # 工具模块
│
├── wow_addon/              # WoW插件（合规版）
│   └── SimpleMageRotation/ # 简单技能循环插件
│
├── build.bat               # 编译脚本（推荐）
├── build_onefile.bat       # 单文件编译脚本
├── start.bat               # 开发模式启动
└── config.json            # 配置文件
```

## 编译为exe（不需要Python环境）

### 方法一：使用编译脚本（推荐）

1. 双击运行 `build.bat`
2. 等待编译完成（约5-10分钟）
3. 找到输出文件：`dist\WoWAutoTool\WoWAutoTool.exe`

### 方法二：手动编译

```cmd
pip install -r requirements.txt
pyinstaller WoWAutoTool.spec --clean
```

输出目录：`dist/WoWAutoTool/`

## 目录文件说明

编译后的exe需要以下文件夹在同目录下：
- `images/` - 模板图片
- `scripts/` - 打怪脚本
- `config.json` - 配置文件

## 开发模式运行

如果已有Python环境：
```bash
pip install -r requirements.txt
python main.py
```

## 模板图片

将模板图片放到 `images/` 目录：
- `enemy_redbar.png` - 敌人红条模板
- `loot_window.png` - 拾取窗口模板
- 自定义命名...

## 脚本目录

在 `scripts/` 目录创建Python脚本：

```python
class Script:
    def __init__(self, ctx, logger):
        self.ctx = ctx
        self.logger = logger
        self.controller = ctx.get('controller')
        self.recognizer = ctx.get('recognizer')
        self.capture = ctx.get('capture')
    
    def run(self):
        screenshot = self.capture.capture()
        hp = self.recognizer.detect_hp_bar(screenshot)
        self.controller.key_press('2')  # 施放技能
        return True
```

## 游戏内插件

将 `wow_addon/SimpleMageRotation/` 复制到 WoW 的 `Interface/AddOns/` 目录

命令：
- `/smr on` - 启用技能循环
- `/smr off` - 禁用
- `/smr aoe on` - 启用AOE
- `/smr aoe off` - 禁用AOE

## 依赖

- Python 3.8+（仅开发时需要）
- OpenCV
- NumPy
- mss
- PyDirectInput
- PyQt5
- Pillow
- pywin32
- PyInstaller（仅编译时需要）

## 免责声明

本工具仅供学习交流，使用后果自负。
