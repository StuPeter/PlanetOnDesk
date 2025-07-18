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
import logging
import sys
import os

IS_WINDOWS = sys.platform.startswith('win')
IS_MACOS = sys.platform == 'darwin'
IS_LINUX = sys.platform.startswith('linux')


def get_log_directory():
    """获取一个用户可写入的日志目录"""
    if sys.platform.startswith('win'):
        # Windows: AppData/Roaming/YourAppName/logs
        log_base_dir = os.path.join(os.environ.get('APPDATA'), "PlanetOnDesktop")
    elif sys.platform == 'darwin':
        # macOS: ~/Library/Application Support/YourAppName/logs
        log_base_dir = os.path.join(os.path.expanduser('~'), 'Library', 'Application Support', "PlanetOnDesktop")
    else:
        # Linux: ~/.config/YourAppName/logs 或者 ~/.local/share/YourAppName/logs
        log_base_dir = os.path.join(os.path.expanduser('~'), '.config', "PlanetOnDesktop")
        # 或者使用XDG_DATA_HOME: os.path.join(os.environ.get('XDG_DATA_HOME', os.path.join(os.path.expanduser('~'), '.local', 'share')), "PlanetOnDesktop")

    log_dir = os.path.join(log_base_dir, 'logs')
    os.makedirs(log_dir, exist_ok=True)  # 确保目录存在
    return log_dir


log_dir = get_log_directory()
logger_path = os.path.join(log_dir, 'pod.log')
print('日志地址：', logger_path)
logging.basicConfig(
    level=logging.INFO,  # 将级别设置为 INFO，这样 INFO 和 ERROR 都会显示
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(logger_path, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)  # 明确指定输出到 stdout，确保控制台显示
    ]
)

# 获取根记录器或你自己的应用记录器
root_logger = logging.getLogger()  # 获取根记录器


class PoDWindow(MSFluentWindow):
    def __init__(self):
        super().__init__()

        # Constants
        self.WIN_TITLE = '时移星动'
        self.WIN_ICON_PATH = get_resource_path('app/resources/pod.ico')

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
    # --- 共享内存优化部分 ---
    # 定义一个唯一的共享内存键
    SHARED_MEMORY_KEY = "PoD_oVx3xi2ykQG78Zo_Mutex"
    shared_memory = QSharedMemory(SHARED_MEMORY_KEY)

    # 尝试创建共享内存，如果失败则说明可能已有实例或上次异常退出
    # lock() 尝试获取锁，如果成功，则说明没有其他实例在运行或锁已释放
    if not shared_memory.create(1):  # 尝试创建1字节的共享内存段
        # 如果创建失败，尝试连接已存在的共享内存
        if not shared_memory.attach():
            # 理论上attach不会失败，如果创建失败且attach也失败，说明系统状态有问题
            QMessageBox.critical(None, "错误", "无法连接到共享内存，可能存在严重问题！")
            sys.exit(1)

        # 此时共享内存已存在且已连接，尝试获取锁
        # 如果能获取锁，说明上次异常退出，但锁现在可获取，可以继续运行
        # 如果不能获取锁，说明已有实例正在运行
        if not shared_memory.lock():
            QMessageBox.warning(None, "警告", "程序已在运行中！")
            sys.exit(0)
        else:
            # 获取到锁，但之前可能存在实例，清理旧锁 (理论上lock成功就说明不需要额外清理了)
            # 这通常意味着上一个实例崩溃但没有释放锁。在 Linux/macOS 上，共享内存的销毁需要显式操作。
            # 这里简单地释放掉，让当前实例继续持有。
            pass  # shared_memory.lock() 已经做到了这一点

    # 如果运行到这里，说明当前实例成功创建了共享内存或获得了锁
    # 在程序退出时，需要确保共享内存被解锁和销毁。
    # 否则，下次启动可能还会遇到问题。
    # shared_memory.lock() 已经隐式地获取了锁，并需要在程序结束时通过 shared_memory.unlock() 释放

    # --- 高DPI配置 ---
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    # --- 创建应用程序实例 ---
    app = QApplication(sys.argv)

    # --- 确保在应用退出时释放共享内存 ---
    # 连接 aboutToQuit 信号，确保在应用程序退出前释放共享内存
    app.aboutToQuit.connect(shared_memory.unlock)
    app.aboutToQuit.connect(shared_memory.detach)  # 确保从共享内存段分离

    # --- 设置主题颜色 ---
    setThemeColor('#2f90b9')

    # --- 运行应用程序 ---
    window = PoDWindow()
    window.show()

    # --- 启动 Qt 事件循环 ---
    exit_code = app.exec_()

    # 在这里，因为使用了 app.aboutToQuit.connect，所以通常不需要手动调用 unlock/detach
    # 但作为最后的保障，可以再次检查，但在 Python 中，当 QSharedMemory 对象被垃圾回收时，
    # 它应该会自动尝试释放资源。
    # if shared_memory.isAttached():
    #     shared_memory.unlock()
    #     shared_memory.detach()

    sys.exit(exit_code)


if __name__ == '__main__':
    main()
