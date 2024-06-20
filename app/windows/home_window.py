#!/usr/bin/env python  
# _*_ coding:utf-8 _*_  
#  
# @Version : 1.0  
# @Time    : 2024/6/13
# @Author  : 圈圈烃
# @File    : home_window
# @Description:
#
#
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QPixmap, QPainter, QColor
from PyQt5.QtWidgets import QWidget
from app.controllers.main_controller import MainController
from qfluentwidgets import HorizontalFlipView

from app.views.home_ui import Ui_HomeForm


class HomeWindow(QWidget, Ui_HomeForm):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.controller = MainController(self)
        self.setupUi(self)
        self.setup_ui()

    def setup_ui(self):
        self.ImageWidget.addImages([
            r'app/resources/earth_template.png',
        ])
        self.ImageWidget.currentIndexChanged.connect(lambda index: print("当前页面：", index))
        self.ImageWidget.setItemSize(QSize(370, 210))
        self.setDesktopButton.clicked.connect(self.controller.start_to_set)
