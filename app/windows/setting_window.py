#!/usr/bin/env python  
# _*_ coding:utf-8 _*_  
#  
# @Version : 1.0  
# @Time    : 2024/6/12
# @Author  : 圈圈烃
# @File    : setting_window
# @Description:
#
#
from PyQt5.QtCore import QUrl, QStandardPaths
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QWidget, QFormLayout, QHBoxLayout, QLineEdit
from qfluentwidgets import FluentIcon, qconfig, QConfig, OptionsConfigItem, OptionsValidator, OptionsSettingCard, \
    FolderListSettingCard, ComboBoxSettingCard, PrimaryPushSettingCard, SettingCardGroup, ConfigItem, \
    FolderListValidator, MessageBox

from app.views.setting_ui import Ui_SettingForm


class PoDConfig(QConfig):
    timeInterval = OptionsConfigItem(
        'PoD', 'TimeInterval', 10, OptionsValidator([10, 20, 30, 60, 'OFF']), restart=True)
    imageFolder = ConfigItem(
        'PoD', 'ImageFolder', [], FolderListValidator()
    )


class SettingWindow(QWidget, Ui_SettingForm):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
        self.setup_ui()

    def setup_ui(self):
        # 加载配置
        cfg = PoDConfig()
        qconfig.load('app/config.json', cfg)
        # 创建表单布局
        form_layout = QFormLayout(self)
        setting_group = SettingCardGroup(
            title='设置'
        )
        # 壁纸保存路径
        folder_card = FolderListSettingCard(
            configItem=cfg.imageFolder,
            title='保存路径',
            content='选择壁纸保存路径',
            directory=QStandardPaths.writableLocation(QStandardPaths.PicturesLocation)
        )
        folder_card.folderChanged.connect(self.change_theme)
        setting_group.addSettingCard(folder_card)
        # 分辨率配置
        time_card = ComboBoxSettingCard(
            configItem=cfg.timeInterval,
            icon=FluentIcon.DATE_TIME,
            title='更新间隔',
            content='自动更新桌面的时间间隔',
            texts=['10分钟', '20分钟', '30分钟', '60分钟', '从不更新']
        )
        cfg.timeInterval.valueChanged.connect(self.time_card_change)
        setting_group.addSettingCard(time_card)
        # 关于
        about_card = PrimaryPushSettingCard(
            text='联系开发者',
            icon=FluentIcon.HELP,
            title='关于软件',
            content='Version：0.1.0 Copyright：圈圈烃'
        )
        about_card.clicked.connect(self.click_about)
        setting_group.addSettingCard(about_card)
        form_layout.addRow(setting_group)

    def time_card_change(self, time_interval):
        print('time_interval', time_interval)
        w = MessageBox('提示', '修改后需要重启软件才能生效', self)
        w.yesButton.setText("好的")
        w.cancelButton.hide()
        if w.exec():
            print('确认')
        else:
            print('取消')

    def change_theme(self, theme):
        print('change', theme)

    def click_about(self):
        url = QUrl('https://space.bilibili.com/330626607')
        QDesktopServices.openUrl(url)
