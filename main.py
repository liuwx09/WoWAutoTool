"""
WoW Auto Tool - Main Application
A template-based game automation tool with image recognition
"""
import sys
import os
import time
import threading
from datetime import datetime

# Handle frozen state (compiled with PyInstaller)
if getattr(sys, 'frozen', False):
    application_path = sys._MEIPASS
    base_path = sys._MEIPASS
else:
    application_path = os.path.dirname(os.path.abspath(__file__))
    base_path = application_path

# Add to path
sys.path.insert(0, base_path)

# Change working directory to where the exe is located
os.chdir(base_path)

from core.capture import ScreenCapture
from core.recognizer import ImageRecognizer
from core.controller import GameController
from core.script_engine import ScriptEngine
from utils.config import Config
from utils.logger import Logger

try:
    from PyQt5.QtWidgets import (
        QApplication,
        QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QPushButton, QLabel, QTextEdit, QGroupBox,
        QSpinBox, QCheckBox, QTabWidget, QStatusBar,
        QMenuBar, QMenu, QAction, QProgressBar, QComboBox,
        QListWidget, QListWidgetItem, QAbstractItemView,
        QSplitter, QFrame, QGridLayout, QSlider, QScrollArea,
        QMessageBox, QFileDialog
    )
    from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject, QSize
    from PyQt5.QtGui import QFont, QIcon, QPixmap, QImage, QPainter, QColor, QPen
except ImportError:
    print("PyQt5 not installed. Run: pip install PyQt5")
    sys.exit(1)

class Communicator(QObject):
    status_update = pyqtSignal(dict)
    log_message = pyqtSignal(str, str)

class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        
        global base_path
        
        # Initialize components with proper paths
        config_path = os.path.join(base_path, "config.json")
        logs_path = os.path.join(base_path, "logs")
        images_path = os.path.join(base_path, "images")
        scripts_path = os.path.join(base_path, "scripts")
        
        self.config = Config(config_path)
        self.logger = Logger("WoWAutoTool", logs_path)
        
        self.capture = ScreenCapture()
        self.recognizer = ImageRecognizer(images_path)
        self.controller = GameController(self.config)
        self.script_engine = ScriptEngine(scripts_path, self.logger)
        
        # Control state
        self.running = False
        self.paused = False
        self.main_loop_thread = None
        
        # Status
        self.kill_count = 0
        self.death_count = 0
        self.start_time = None
        
        # Setup UI
        self.init_ui()
        
        # Setup timer for updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_status)
        
        # Capture timer for preview
        self.capture_timer = QTimer()
        self.capture_timer.timeout.connect(self.update_preview)
        
        self.logger.info("Application initialized")
    
    def init_ui(self):
        """Initialize the UI."""
        self.setWindowTitle("WoW Auto Tool v1.0")
        self.setGeometry(100, 100, 1000, 700)
        
        central = QWidget()
        self.setCentralWidget(central)
        
        # Main layout
        main_layout = QHBoxLayout(central)
        
        # Left panel - Controls
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel, 1)
        
        # Right panel - Info
        right_panel = self.create_right_panel()
        main_layout.addWidget(right_panel, 2)
        
        # Menu bar
        self.create_menu_bar()
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪")
    
    def create_left_panel(self):
        """Create left control panel."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Control buttons
        control_group = QGroupBox("控制")
        control_layout = QVBoxLayout()
        
        self.start_btn = QPushButton("▶ 开始")
        self.start_btn.setStyleSheet("font-size: 14px; padding: 8px;")
        self.start_btn.clicked.connect(self.on_start)
        
        self.pause_btn = QPushButton("⏸ 暂停")
        self.pause_btn.setEnabled(False)
        self.pause_btn.clicked.connect(self.on_pause)
        
        self.stop_btn = QPushButton("⏹ 停止")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.on_stop)
        
        control_layout.addWidget(self.start_btn)
        control_layout.addWidget(self.pause_btn)
        control_layout.addWidget(self.stop_btn)
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)
        
        # Scripts selection
        scripts_group = QGroupBox("脚本选择")
        scripts_layout = QVBoxLayout()
        
        self.script_list = QListWidget()
        self.script_list.addItems(self.script_engine.list_scripts())
        self.script_list.setMaximumHeight(120)
        self.script_list.setSelectionMode(QAbstractItemView.SingleSelection)
        
        self.reload_scripts_btn = QPushButton("🔄 刷新脚本")
        self.reload_scripts_btn.clicked.connect(self.on_reload_scripts)
        
        scripts_layout.addWidget(self.script_list)
        scripts_layout.addWidget(self.reload_scripts_btn)
        scripts_group.setLayout(scripts_layout)
        layout.addWidget(scripts_group)
        
        # Quick settings
        settings_group = QGroupBox("快速设置")
        settings_layout = QGridLayout()
        
        settings_layout.addWidget(QLabel("血量阈值 (%):"), 0, 0)
        self.hp_threshold_spin = QSpinBox()
        self.hp_threshold_spin.setRange(1, 100)
        self.hp_threshold_spin.setValue(self.config.get('hp_threshold', 70))
        settings_layout.addWidget(self.hp_threshold_spin, 0, 1)
        
        settings_layout.addWidget(QLabel("蓝量阈值 (%):"), 1, 0)
        self.mp_threshold_spin = QSpinBox()
        self.mp_threshold_spin.setRange(1, 100)
        self.mp_threshold_spin.setValue(self.config.get('mp_threshold', 40))
        settings_layout.addWidget(self.mp_threshold_spin, 1, 1)
        
        self.auto_eat_cb = QCheckBox("自动吃食物")
        self.auto_eat_cb.setChecked(self.config.get('auto_eat_enabled', True))
        settings_layout.addWidget(self.auto_eat_cb, 2, 0, 1, 2)
        
        self.auto_drink_cb = QCheckBox("自动喝水")
        self.auto_drink_cb.setChecked(self.config.get('auto_drink_enabled', True))
        settings_layout.addWidget(self.auto_drink_cb, 3, 0, 1, 2)
        
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)
        
        # Apply settings button
        self.apply_btn = QPushButton("💾 应用设置")
        self.apply_btn.clicked.connect(self.on_apply_settings)
        layout.addWidget(self.apply_btn)
        
        layout.addStretch()
        return widget
    
    def create_right_panel(self):
        """Create right info panel."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Tabs
        tabs = QTabWidget()
        
        tabs.addTab(self.create_status_tab(), "状态")
        tabs.addTab(self.create_preview_tab(), "画面预览")
        tabs.addTab(self.create_templates_tab(), "模板管理")
        tabs.addTab(self.create_log_tab(), "日志")
        
        layout.addWidget(tabs)
        return widget
    
    def create_status_tab(self):
        """Create status display tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Status info
        status_group = QGroupBox("运行状态")
        status_layout = QGridLayout()
        
        self.state_label = QLabel("已停止")
        self.state_label.setStyleSheet("font-size: 16px; font-weight: bold; color: gray;")
        status_layout.addWidget(QLabel("状态:"), 0, 0)
        status_layout.addWidget(self.state_label, 0, 1)
        
        status_layout.addWidget(QLabel("血量:"), 1, 0)
        self.hp_bar = QProgressBar()
        self.hp_bar.setRange(0, 100)
        status_layout.addWidget(self.hp_bar, 1, 1)
        
        status_layout.addWidget(QLabel("蓝量:"), 2, 0)
        self.mp_bar = QProgressBar()
        self.mp_bar.setRange(0, 100)
        status_layout.addWidget(self.mp_bar, 2, 1)
        
        self.kill_count_label = QLabel("0")
        status_layout.addWidget(QLabel("击杀:"), 3, 0)
        status_layout.addWidget(self.kill_count_label, 3, 1)
        
        self.death_count_label = QLabel("0")
        status_layout.addWidget(QLabel("死亡:"), 4, 0)
        status_layout.addWidget(self.death_count_label, 4, 1)
        
        self.uptime_label = QLabel("00:00:00")
        status_layout.addWidget(QLabel("运行时间:"), 5, 0)
        status_layout.addWidget(self.uptime_label, 5, 1)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # Current script info
        script_info_group = QGroupBox("当前脚本")
        script_info_layout = QVBoxLayout()
        self.script_info_label = QLabel("未选择")
        script_info_layout.addWidget(self.script_info_label)
        script_info_group.setLayout(script_info_layout)
        layout.addWidget(script_info_group)
        
        layout.addStretch()
        return widget
    
    def create_preview_tab(self):
        """Create screen preview tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        self.preview_label = QLabel()
        self.preview_label.setMinimumSize(640, 400)
        self.preview_label.setStyleSheet("background-color: #1a1a1a; border: 1px solid #444;")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setText("点击'开始'后显示画面预览")
        
        layout.addWidget(self.preview_label)
        
        # Preview controls
        preview_controls = QHBoxLayout()
        
        self.show_hp_region_cb = QCheckBox("显示血条区域")
        self.show_hp_region_cb.stateChanged.connect(self.update_preview)
        preview_controls.addWidget(self.show_hp_region_cb)
        
        self.show_target_cb = QCheckBox("显示目标区域")
        self.show_target_cb.stateChanged.connect(self.update_preview)
        preview_controls.addWidget(self.show_target_cb)
        
        preview_controls.addStretch()
        
        layout.addLayout(preview_controls)
        return widget
    
    def create_templates_tab(self):
        """Create template management tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Template list
        templates_group = QGroupBox("已加载模板")
        templates_layout = QVBoxLayout()
        
        self.template_list = QListWidget()
        self.template_list.addItems(list(self.recognizer.templates.keys()))
        self.template_list.setMaximumHeight(150)
        templates_layout.addWidget(self.template_list)
        
        # Template actions
        template_actions = QHBoxLayout()
        
        add_template_btn = QPushButton("➕ 添加模板")
        add_template_btn.clicked.connect(self.on_add_template)
        template_actions.addWidget(add_template_btn)
        
        remove_template_btn = QPushButton("➖ 移除模板")
        remove_template_btn.clicked.connect(self.on_remove_template)
        template_actions.addWidget(remove_template_btn)
        
        reload_template_btn = QPushButton("🔄 重新加载")
        reload_template_btn.clicked.connect(self.on_reload_templates)
        template_actions.addWidget(reload_template_btn)
        
        templates_layout.addLayout(template_actions)
        templates_group.setLayout(templates_layout)
        layout.addWidget(templates_group)
        
        # Image directory info
        dir_group = QGroupBox("图片目录")
        dir_layout = QVBoxLayout()
        dir_layout.addWidget(QLabel("模板目录: images/"))
        dir_layout.addWidget(QLabel("支持的格式: PNG, JPG, BMP"))
        
        open_dir_btn = QPushButton("📂 打开图片目录")
        open_dir_btn.clicked.connect(lambda: os.system('start images' if os.name == 'nt' else 'open images'))
        dir_layout.addWidget(open_dir_btn)
        
        dir_group.setLayout(dir_layout)
        layout.addWidget(dir_group)
        
        # Scripts directory info
        scripts_dir_group = QGroupBox("脚本目录")
        scripts_dir_layout = QVBoxLayout()
        scripts_dir_layout.addWidget(QLabel("脚本目录: scripts/"))
        scripts_dir_layout.addWidget(QLabel("脚本格式: Python (.py)"))
        
        open_scripts_btn = QPushButton("📂 打开脚本目录")
        open_scripts_btn.clicked.connect(lambda: os.system('start scripts' if os.name == 'nt' else 'open scripts'))
        scripts_dir_layout.addWidget(open_scripts_btn)
        
        create_sample_btn = QPushButton("📝 创建示例脚本")
        create_sample_btn.clicked.connect(self.script_engine.create_sample_script)
        scripts_dir_layout.addWidget(create_sample_btn)
        
        scripts_dir_group.setLayout(scripts_dir_layout)
        layout.addWidget(scripts_dir_group)
        
        layout.addStretch()
        return widget
    
    def create_log_tab(self):
        """Create log display tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setStyleSheet("background-color: #1a1a1a; color: #ccc; font-family: Consolas; font-size: 11px;")
        
        layout.addWidget(self.log_display)
        
        # Log controls
        log_controls = QHBoxLayout()
        
        clear_log_btn = QPushButton("清空日志")
        clear_log_btn.clicked.connect(self.log_display.clear)
        log_controls.addWidget(clear_log_btn)
        
        log_controls.addStretch()
        
        layout.addLayout(log_controls)
        return widget
    
    def create_menu_bar(self):
        """Create menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("文件")
        
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("工具")
        
        settings_action = QAction("设置", self)
        settings_action.triggered.connect(self.show_settings)
        tools_menu.addAction(settings_action)
        
        create_script_action = QAction("创建示例脚本", self)
        create_script_action.triggered.connect(self.script_engine.create_sample_script)
        tools_menu.addAction(create_script_action)
        
        # Help menu
        help_menu = menubar.addMenu("帮助")
        
        about_action = QAction("关于", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def on_start(self):
        """Start the automation."""
        if self.running:
            return
        
        # Apply settings first
        self.on_apply_settings()
        
        self.running = True
        self.paused = False
        self.start_time = time.time()
        
        # Get selected script
        selected = self.script_list.currentItem()
        script_name = selected.text() if selected else None
        
        if script_name:
            self.script_info_label.setText(f"运行中: {script_name}")
            self.logger.info(f"Starting script: {script_name}")
        else:
            self.script_info_label.setText("运行中: (无脚本)")
            self.logger.warning("No script selected")
        
        # Start main loop
        self.main_loop_thread = threading.Thread(target=self._main_loop, daemon=True)
        self.main_loop_thread.start()
        
        # Start timers
        self.timer.start(100)
        self.capture_timer.start(200)
        
        # Update UI
        self.start_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)
        self.stop_btn.setEnabled(True)
        self.state_label.setText("运行中")
        self.state_label.setStyleSheet("font-size: 16px; font-weight: bold; color: green;")
        self.status_bar.showMessage("运行中")
        
        self.log_message("info", "自动化已启动")
    
    def on_pause(self):
        """Pause/resume the automation."""
        if not self.running:
            return
        
        self.paused = not self.paused
        
        if self.paused:
            self.pause_btn.setText("▶ 继续")
            self.state_label.setText("已暂停")
            self.state_label.setStyleSheet("font-size: 16px; font-weight: bold; color: orange;")
            self.status_bar.showMessage("已暂停")
            self.logger.info("Automation paused")
        else:
            self.pause_btn.setText("⏸ 暂停")
            self.state_label.setText("运行中")
            self.state_label.setStyleSheet("font-size: 16px; font-weight: bold; color: green;")
            self.status_bar.showMessage("运行中")
            self.logger.info("Automation resumed")
    
    def on_stop(self):
        """Stop the automation."""
        self.running = False
        self.paused = False
        
        # Emergency stop
        self.controller.stop_all()
        
        # Stop timers
        self.timer.stop()
        self.capture_timer.stop()
        
        # Update UI
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.pause_btn.setText("⏸ 暂停")
        self.stop_btn.setEnabled(False)
        self.state_label.setText("已停止")
        self.state_label.setStyleSheet("font-size: 16px; font-weight: bold; color: gray;")
        self.script_info_label.setText("未选择")
        self.status_bar.showMessage("已停止")
        
        self.logger.info("Automation stopped")
        self.log_message("info", "自动化已停止")
    
    def on_apply_settings(self):
        """Apply current settings."""
        updates = {
            'hp_threshold': self.hp_threshold_spin.value(),
            'mp_threshold': self.mp_threshold_spin.value(),
            'auto_eat_enabled': self.auto_eat_cb.isChecked(),
            'auto_drink_enabled': self.auto_drink_cb.isChecked(),
        }
        self.config.update(updates)
        self.config.save()
        self.log_message("info", "设置已应用")
    
    def on_reload_scripts(self):
        """Reload scripts from disk."""
        self.script_engine.load_scripts()
        self.script_list.clear()
        self.script_list.addItems(self.script_engine.list_scripts())
        self.log_message("info", f"已刷新脚本，找到 {len(self.script_engine.list_scripts())} 个")
    
    def on_add_template(self):
        """Add a template image."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择模板图片", "",
            "Image Files (*.png *.jpg *.jpeg *.bmp)"
        )
        
        if file_path:
            import shutil
            filename = os.path.basename(file_path)
            dest_path = os.path.join("images", filename)
            shutil.copy(file_path, dest_path)
            self.recognizer.reload_templates()
            self.template_list.clear()
            self.template_list.addItems(list(self.recognizer.templates.keys()))
            self.log_message("info", f"已添加模板: {filename}")
    
    def on_remove_template(self):
        """Remove selected template."""
        selected = self.template_list.currentItem()
        if selected:
            template_name = selected.text()
            template_path = os.path.join("images", template_name + ".png")
            if os.path.exists(template_path):
                os.remove(template_path)
            self.recognizer.reload_templates()
            self.template_list.clear()
            self.template_list.addItems(list(self.recognizer.templates.keys()))
            self.log_message("info", f"已移除模板: {template_name}")
    
    def on_reload_templates(self):
        """Reload templates from disk."""
        self.recognizer.reload_templates()
        self.template_list.clear()
        self.template_list.addItems(list(self.recognizer.templates.keys()))
        self.log_message("info", f"已刷新模板，找到 {len(self.recognizer.templates)} 个")
    
    def _main_loop(self):
        """Main automation loop running in thread."""
        self.logger.info("Main loop started")
        
        status = {
            'player_hp': 100,
            'player_mp': 100,
            'target_exists': False,
            'in_combat': False,
        }
        
        last_script_run = 0
        
        while self.running:
            if self.paused:
                time.sleep(0.1)
                continue
            
            try:
                current_time = time.time()
                
                # Capture screen
                screenshot = self.capture.capture()
                
                # Update HP/MP detection
                hp = self.recognizer.detect_hp_bar(screenshot)
                mp = self.recognizer.detect_mp_bar(screenshot)
                
                status['player_hp'] = hp
                status['player_mp'] = mp
                
                # Check for enemies (using template matching)
                enemy_found, ex, ey, conf = self.recognizer.find_template(screenshot, 'enemy_redbar')
                status['target_exists'] = enemy_found
                
                # Check if in combat (red bars present)
                status['in_combat'] = enemy_found
                
                # Run selected script
                selected = self.script_list.currentItem()
                script_name = selected.text() if selected else None
                
                if script_name and (current_time - last_script_run) > 0.1:
                    context = {
                        'controller': self.controller,
                        'recognizer': self.recognizer,
                        'capture': self.capture,
                        'config': self.config,
                        'logger': self.logger,
                        'status': status,
                    }
                    
                    self.script_engine.execute_script(script_name, context)
                    last_script_run = current_time
                
                # Auto eat/drink
                if hp < self.config.get('hp_threshold', 70) and self.config.get('auto_eat_enabled'):
                    self.controller.key_press('5')  # Food key
                
                if mp < self.config.get('mp_threshold', 40) and self.config.get('auto_drink_enabled'):
                    self.controller.key_press('6')  # Drink key
                
                # Small delay
                time.sleep(0.05)
                
            except Exception as e:
                self.logger.error(f"Main loop error: {e}")
                time.sleep(1)
        
        self.logger.info("Main loop exited")
    
    def update_status(self):
        """Update status display."""
        if not self.running:
            return
        
        # Calculate uptime
        uptime = "00:00:00"
        if self.start_time:
            delta = time.time() - self.start_time
            hours = int(delta // 3600)
            mins = int((delta % 3600) // 60)
            secs = int(delta % 60)
            uptime = f"{hours:02d}:{mins:02d}:{secs:02d}"
        
        self.uptime_label.setText(uptime)
    
    def update_preview(self):
        """Update screen preview."""
        if not self.running:
            return
        
        try:
            screenshot = self.capture.capture()
            
            # Convert to QImage
            h, w, c = screenshot.shape
            bytes_per_line = c * w
            qt_image = QImage(screenshot.data, w, h, bytes_per_line, QImage.Format_BGR888)
            
            # Scale to fit label
            pixmap = QPixmap.fromImage(qt_image)
            scaled_pixmap = pixmap.scaled(
                self.preview_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            
            # Draw overlay if enabled
            if self.show_hp_region_cb.isChecked() or self.show_target_cb.isChecked():
                painter = QPainter(scaled_pixmap)
                painter.setPen(QPen(QColor(0, 255, 0), 2))
                
                if self.show_hp_region_cb.isChecked():
                    # Draw HP bar region (example)
                    painter.drawRect(100, 650, 250, 30)
                
                if self.show_target_cb.isChecked():
                    # Draw target region (example)
                    painter.drawRect(400, 300, 200, 20)
                
                painter.end()
            
            self.preview_label.setPixmap(scaled_pixmap)
            
        except Exception as e:
            pass
    
    def log_message(self, level, message):
        """Add message to log display."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        colors = {
            'info': '#66ccee',
            'warning': '#ffcc00',
            'error': '#ff6666',
            'debug': '#999999'
        }
        color = colors.get(level, '#ffffff')
        
        self.log_display.append(f'<span style="color: {color}">[{timestamp}] {message}</span>')
    
    def show_settings(self):
        """Show settings dialog."""
        QMessageBox.information(self, "设置", "请在主界面调整设置，然后点击'应用设置'")
    
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "关于 WoW Auto Tool",
            "WoW Auto Tool v1.0\n\n"
            "一个基于图像识别的游戏自动化工具\n\n"
            "功能:\n"
            "- 模板匹配图像识别\n"
            "- 可编写脚本的战斗逻辑\n"
            "- 自动吃喝\n"
            "- 可自定义按键绑定\n\n"
            "作者: 小光"
        )
    
    def closeEvent(self, event):
        """Handle window close."""
        if self.running:
            self.on_stop()
        event.accept()


def main():
    """Main entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName("WoW Auto Tool")
    app.setStyle('Fusion')
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
