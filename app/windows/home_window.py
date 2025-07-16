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
    SingleDirectionScrollArea,
    setThemeColor
)

from app.controllers.main_controller import MainController
from app.views.home_ui import Ui_HomeForm
from app.windows.pod_config import PoDConfig
from app.utils.resource_path import get_resource_path


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
        config_path = get_resource_path('app/config.json')
        qconfig.load(config_path, self.cfg)

    def setup_ui(self):
        image1 = get_resource_path('app/resources/earth_template.jpg')
        image2 = get_resource_path('app/resources/earth_16_template.jpg')
        image3 = get_resource_path('app/resources/moon_template.jpg')
        image4 = get_resource_path('app/resources/sun_template.jpg')
        self.ImageWidget.addImages([image1, image2, image3, image4])
        # 同步当前模式
        image_source = self.cfg.get(self.cfg.imageSource)
        if image_source == 'Earth-H8':
            current_index = 0
        elif image_source == 'Earth-H8-16':
            current_index = 1
        elif image_source == 'Moon-NASA':
            current_index = 2
        elif image_source == 'Sun-NASA':
            current_index = 3
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
            setThemeColor('#2f90b9')
        elif index == 1:
            self.label.setText('地球卫星图像(超大)')
            self.label_2.setText(
                "简介：更高分辨率的合成地球影像，因为一次需要获取多张影像，网络不佳情况下可能会失败。\n\n"
                "推荐频率：每小时更新一次，实时捕捉地球天气和光影变化\n\n"
                "数据来源：https://himawari8.nict.go.jp/zh/himawari8-image.htm\n"
            )
            self.cfg.set(self.cfg.imageSource, 'Earth-H8-16')
            setThemeColor('#30394b')
        elif index == 2:
            self.label.setText('NASA 月相数据')
            self.label_2.setText(
                "简介：展示月球的实时变化，精确显示每晚的月相情况，包括新月、满月等不同阶段。\n\n"
                "推荐频率：每天更新一次，匹配月球的自然变化周期。\n\n"
                "数据来源：https://svs.gsfc.nasa.gov/gallery/moonphase/\n"
            )
            self.cfg.set(self.cfg.imageSource, 'Moon-NASA')
            setThemeColor('#b7ae8f')
        elif index == 3:
            self.label.setText('NASA SDO太阳')
            self.label_2.setText(
                "简介：NASA 的太阳动力学天文台，能够以极高分辨率和多波段成像方式持续监测太阳表面和大气层（日冕）。\n\n"
                "推荐频率：每小时更新一次，可关注太阳动态变化。\n\n"
                "数据来源：https://sdo.gsfc.nasa.gov/\n"
            )
            self.cfg.set(self.cfg.imageSource, 'Sun-NASA')
            setThemeColor('#ffa205')
        else:
            self.label.setText('哦豁！你看到BUG了')
            self.label_2.setText(
                "简介：记得反馈给我哈\n\n"
                "联系：rasfu_1@163.com\n"
            )
            self.cfg.set(self.cfg.imageSource, 'FUCK')
        # 设置标签的自动换行
        self.label_2.setWordWrap(True)
        # 设置标签的宽度
        self.label_2.setFixedWidth(200)
