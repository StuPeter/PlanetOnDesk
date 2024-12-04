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
from PyQt5.QtWidgets import QWidget, QFormLayout, QHBoxLayout, QLineEdit, QFileDialog
from qfluentwidgets import FluentIcon, qconfig, QConfig, OptionsConfigItem, OptionsValidator, OptionsSettingCard, \
    FolderListSettingCard, ComboBoxSettingCard, PrimaryPushSettingCard, SettingCardGroup, ConfigItem, \
    FolderListValidator, MessageBox, PushSettingCard, FolderValidator

from app.views.setting_ui import Ui_SettingForm


class PoDConfig(QConfig):
    timeInterval = OptionsConfigItem(
        'PoD', 'TimeInterval', 10, OptionsValidator([10, 20, 30, 60, 'OFF']), restart=True)
    imageFolder = ConfigItem(
        'PoD', 'ImageFolder', "", FolderValidator())


class SettingWindow(QWidget, Ui_SettingForm):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)
        self.setup_ui()

    def setup_ui(self):
        # 加载配置
        self.cfg = PoDConfig()
        qconfig.load('app/config.json', self.cfg)
        # 创建表单布局
        form_layout = QFormLayout(self)
        setting_group = SettingCardGroup(
            title='设置'
        )
        # 开机自启动#TODO
        # 壁纸保存路径
        self.folder_card = PushSettingCard(
            icon=FluentIcon.DOWNLOAD,
            title='壁纸保存路径',
            text='选择文件夹',
            content='未选择文件夹',
        )
        self.folder_card.clicked.connect(self.select_folder)
        setting_group.addSettingCard(self.folder_card)
        # 添加配置中的路径
        self.folder_card.setContent(self.cfg.get(self.cfg.imageFolder))
        # 分辨率配置
        time_card = ComboBoxSettingCard(
            configItem=self.cfg.timeInterval,
            icon=FluentIcon.DATE_TIME,
            title='更新间隔',
            content='自动更新桌面的时间间隔',
            texts=['10分钟', '20分钟', '30分钟', '60分钟', '从不更新']
        )
        self.cfg.timeInterval.valueChanged.connect(self.time_card_change)
        setting_group.addSettingCard(time_card)
        # 关于
        about_card = PrimaryPushSettingCard(
            text='联系开发者',
            icon=FluentIcon.HELP,
            title='关于软件',
            content='©版权所有2024 圈圈烃. 版本：0.1.0'
        )
        about_card.clicked.connect(self.click_about)
        setting_group.addSettingCard(about_card)
        form_layout.addRow(setting_group)

    def select_folder(self):
        # 打开文件夹选择对话框
        folder_path = QFileDialog.getExistingDirectory(self, '选择文件夹')
        if folder_path:
            # 更新 content 显示选定的文件夹路径
            print('folder_path', folder_path)
            self.cfg.set(self.cfg.imageFolder, folder_path)
            self.folder_card.setContent(folder_path)

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
