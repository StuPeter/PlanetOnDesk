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
from qfluentwidgets import (
    FluentIcon,
    qconfig,
    SwitchSettingCard,
    PushSettingCard,
    ComboBoxSettingCard,
    PrimaryPushSettingCard,
    SettingCardGroup,
    MessageBox,
    SingleDirectionScrollArea
)
from app.controllers.main_controller import MainController
from app.views.home_ui import Ui_HomeForm
from app.windows.pod_config import PoDConfig


class HomeWindow(QWidget, Ui_HomeForm):

    def __init__(self, parent=None):

        super().__init__(parent=parent)
        self.setupUi(self)
        self.controller = MainController(self)
        self._init_config()
        self.setup_ui()

    def _init_config(self):
        """Initialize and load configuration"""
        self.cfg = PoDConfig()
        qconfig.load('app/config.json', self.cfg)

    def setup_ui(self):
        self.ImageWidget.addImages([
            r'app/resources/earth_template.png',
            r'app/resources/moon_template.jpg',
        ])
        # 同步当前模式
        image_source = self.cfg.get(self.cfg.imageSource)
        if image_source == 'Earth-H8':
            current_index = 0
        elif image_source == 'Moon-NASA':
            current_index = 1
        else:
            current_index = 0
        self.ImageWidget.setCurrentIndex(current_index)
        self._on_change_image(current_index)

        self.ImageWidget.currentIndexChanged.connect(self._on_change_image)
        self.ImageWidget.setItemSize(QSize(370, 210))
        self.setDesktopButton.clicked.connect(self.controller.run_set_wallpaper)

    def _on_change_image(self, index):

        if index == 0:
            self.label.setText('向日葵8号气象卫星')
            self.label_2.setText(
                "简介：由日本气象厅运营，提供高分辨率的地球全貌影像，展现地球在日光下的动态变化。\n\n"
                "推荐频率：每小时更新一次，实时捕捉地球天气和光影变化。\n\n"
                "数据来源：https://himawari8.nict.go.jp/zh/himawari8-image.htm\n"
            )
            self.cfg.set(self.cfg.imageSource, 'Earth-H8')
        elif index == 1:
            self.label.setText('NASA 月相数据')
            self.label_2.setText(
                "简介：展示月球的实时变化，精确显示每晚的月相情况，包括新月、满月等不同阶段。\n\n"
                "推荐频率：每天更新一次，匹配月球的自然变化周期。\n\n"
                "数据来源：https://svs.gsfc.nasa.gov/gallery/moonphase/\n"
            )
            self.cfg.set(self.cfg.imageSource, 'Moon-NASA')
        else:
            self.label.setText('哦豁！你看到BUG了')
            self.label_2.setText(
                "简介：记得反馈给我哈\n\n"
                "联系：rasfu_1@163.com\n"
            )
            self.cfg.set(self.cfg.imageSource, 'Earth-H8')
        # 设置标签的自动换行
        self.label_2.setWordWrap(True)
        # 设置标签的宽度
        self.label_2.setFixedWidth(200)
