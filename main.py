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
from PyQt5.QtCore import Qt, QSize, QEventLoop, QTimer, QEvent
from PyQt5.QtWidgets import QApplication
from app.windows.system_tray import SystemTray
from qfluentwidgets import MSFluentWindow, FluentIcon, SplashScreen, Theme, setTheme, setThemeColor
from qframelesswindow import StandardTitleBar
from app.windows.setting_window import SettingWindow
from app.windows.home_window import HomeWindow
import sys


class PoDWindow(MSFluentWindow):
    def __init__(self):
        super().__init__()
        self.win_title = '时移星动'
        self.win_icon = 'app/resources/pod.ico'
        self.system_tray = SystemTray(self, QIcon(self.win_icon))
        self.setWindowTitle(self.win_title)
        self.setWindowIcon(QIcon(self.win_icon))
        self.setFixedSize(720, 480)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.titleBar.maxBtn.hide()

        # 加载窗口
        self.setting_window = SettingWindow(self)
        self.home_window = HomeWindow(self)
        # 创建启动页面
        self.splashScreen = SplashScreen(self.windowIcon(), self)
        title_bar = StandardTitleBar(self.splashScreen)
        title_bar.setIcon(QIcon(self.win_icon))
        title_bar.setTitle(self.win_title)
        title_bar.maxBtn.hide()
        self.splashScreen.setTitleBar(title_bar)
        self.splashScreen.setIconSize(QSize(128, 128))
        self.show()
        # 创建子页面
        self.create_window()
        # 关闭启动页面
        self.splashScreen.close()

    def create_window(self):
        loop = QEventLoop(self)
        self.addSubInterface(self.home_window, FluentIcon.HOME, "主页")
        self.addSubInterface(self.setting_window, FluentIcon.SETTING, "设置")
        QTimer.singleShot(2000, loop.quit)
        loop.exec()

    def changeEvent(self, event):
        """捕获窗口状态变化事件"""
        if event.type() == QEvent.WindowStateChange:
            if self.windowState() & Qt.WindowMinimized:
                print('Window is minimized')
                self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint)
            else:
                print('Window is restored')
                self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        super().changeEvent(event)


if __name__ == '__main__':
    # enable dip scale
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)

    # 设置主题颜色
    # setTheme(Theme.DARK)
    setThemeColor('#f43e06')  # 设置主要颜色

    w = PoDWindow()
    w.show()
    sys.exit(app.exec_())
