#!/usr/bin/env python
# _*_ coding:utf-8 _*_
#
# @Version : 1.0
# @Time    : 2024/6/12
# @Author  : 圈圈烃
# @File    : main
# @Description:
#
#
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QSize, QTimer, QSharedMemory
from PyQt5.QtWidgets import QApplication, QMessageBox
import sys

from app.windows.system_tray import SystemTray
from qfluentwidgets import (
    FluentWindow,
    MSFluentWindow,
    FluentIcon,
    SplashScreen,
    Theme,
    setThemeColor
)
from qframelesswindow import StandardTitleBar
from app.windows.setting_window import SettingWindow
from app.windows.home_window import HomeWindow
from app.utils.resource_path import get_resource_path


class PoDWindow(MSFluentWindow):
    def __init__(self):
        super().__init__()

        # Constants
        self.WIN_TITLE = '时移星动'
        self.WIN_LOGO_PATH = get_resource_path('app/resources/pod.ico')

        # Setup system tray and windows
        self._setup_system_tray()
        self._setup_windows()

        # Initialize window and UI
        self._init_window()
        self._create_splash_screen()
        self._init_navigation()

    def _setup_system_tray(self):
        """Setup system tray with the application icon"""
        self.system_tray = SystemTray(self, QIcon(self.WIN_ICON_PATH))

    def _setup_windows(self):
        """Initialize sub-windows"""
        self.setting_window = SettingWindow(self)
        self.home_window = HomeWindow(self)

    def _init_window(self):
        """Configure main window properties"""
        self.setWindowTitle(self.WIN_TITLE)
        self.setWindowIcon(QIcon(self.WIN_ICON_PATH))
        self.setFixedSize(720, 480)
        self.titleBar.maxBtn.hide()

    def _create_splash_screen(self):
        """Create and configure splash screen"""
        self.splash_screen = SplashScreen(self.windowIcon(), self)

        title_bar = StandardTitleBar(self.splash_screen)
        title_bar.setIcon(QIcon(self.WIN_ICON_PATH))
        title_bar.setTitle(self.WIN_TITLE)
        title_bar.maxBtn.hide()

        self.splash_screen.setTitleBar(title_bar)
        self.splash_screen.setIconSize(QSize(128, 128))
        self.show()

    def _init_navigation(self):
        """Initialize navigation interfaces"""
        self.addSubInterface(self.home_window, FluentIcon.HOME, "主页")
        self.addSubInterface(self.setting_window, FluentIcon.SETTING, "设置")

        # Close splash screen after a short delay
        QTimer.singleShot(1500, self.splash_screen.close)

    def closeEvent(self, event):
        # 重写关闭事件，最小化到托盘
        event.ignore()
        self.hide()

    def changeEvent(self, event):
        """Handle window state change events"""
        if event.type() == event.WindowStateChange:
            # 判断窗口是否最小化
            minimized = bool(self.windowState() & Qt.WindowMinimized)
            # 打印状态
            state = "minimized" if minimized else "restored"
            print(f"Window is {state}")

        super().changeEvent(event)


def main():
    # 创建共享内存
    shared_memory = QSharedMemory("PoD_oVx3xi2ykQG78Zo")
    # 如果共享内存已经存在，说明程序已运行
    if shared_memory.attach():
        QMessageBox.warning(None, "警告", "程序已运行！")
        sys.exit(0)
    # 尝试创建共享内存（加锁）
    if not shared_memory.create(1):
        QMessageBox.critical(None, "错误", "无法创建共享内存！")
        sys.exit(1)

    # High DPI scaling configuration
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    # Create application
    app = QApplication(sys.argv)

    # Set theme color
    setThemeColor('#f43e06')

    # Run the application
    window = PoDWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
