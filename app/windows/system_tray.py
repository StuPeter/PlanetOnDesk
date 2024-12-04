#!/usr/bin/env python  
# _*_ coding:utf-8 _*_  
#  
# @Version : 1.0  
# @Time    : 2024/6/12
# @Author  : 圈圈烃
# @File    : system_tray
# @Description:
#
#
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction, qApp


class SystemTray(QSystemTrayIcon):
    def __init__(self, main_window, icon):
        super().__init__(icon, main_window)
        self.main_window = main_window

        # 创建菜单
        menu = QMenu()

        show_action = QAction('显示', self)
        quit_action = QAction('退出', self)

        menu.addAction(show_action)
        menu.addAction(quit_action)

        self.setContextMenu(menu)

        show_action.triggered.connect(self.show_main_window)
        quit_action.triggered.connect(qApp.quit)

        self.activated.connect(self.on_tray_icon_activated)

        self.show()

    def show_main_window(self):
        self.main_window.showNormal()
        self.main_window.activateWindow()

    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.show_main_window()
