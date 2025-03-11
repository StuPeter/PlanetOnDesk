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
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QWidget, QFormLayout, QFileDialog, QScrollArea, QVBoxLayout, QPushButton
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

from app.views.setting_ui import Ui_SettingForm
from app.utils.auto_start import StartupManager
from app.windows.pod_config import PoDConfig
from typing import Optional
import sys


class SettingWindow(QWidget, Ui_SettingForm):
    """Main settings window for the application"""

    def __init__(self, parent: Optional[QWidget] = None):

        super().__init__(parent=parent)
        self.setupUi(self)
        self._init_config()
        self._setup_setting_cards()

    def _init_config(self):
        """Initialize and load configuration"""
        self.cfg = PoDConfig()
        qconfig.load('app/config.json', self.cfg)

    def _setup_setting_cards(self):
        """Set up all setting cards in the window"""
        # 创建设置视图容器
        view = QWidget(self)
        layout = QVBoxLayout(view)

        # 创建设置组
        setting_group = SettingCardGroup(title='设置')

        # 添加各种设置卡片
        self._setup_auto_start_card(setting_group)
        self._setup_auto_save_card(setting_group)
        self._setup_folder_card(setting_group)
        self._setup_time_interval_card(setting_group)
        self._setup_about_card(setting_group)

        # 将设置组添加到布局
        layout.addWidget(setting_group)
        # 创建滚动区域
        scrollArea = SingleDirectionScrollArea(orient=Qt.Vertical)
        scrollArea.setWidgetResizable(True)  # 关键设置
        scrollArea.setWidget(view)
        # 必须给内部的视图也加上透明背景样式
        scrollArea.setStyleSheet("QScrollArea{background: transparent; border: none}")
        view.setStyleSheet("QWidget{background: transparent}")

        # 调整滚动区域大小（如果需要）
        scrollArea.resize(self.width(), self.height())

        # 将滚动区域添加到主窗口布局
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scrollArea)

    def _setup_auto_start_card(self, setting_group):
        """Setup auto-start setting card"""
        self.auto_start = SwitchSettingCard(
            configItem=self.cfg.autoStart,
            icon=FluentIcon.POWER_BUTTON,
            title='开机自启动',
            content='开机时自动启动软件',
        )
        self.auto_start.checkedChanged.connect(self._on_auto_start_changed)
        setting_group.addSettingCard(self.auto_start)

    def _setup_auto_save_card(self, setting_group):
        """Setup auto-save images card"""
        self.auto_save = SwitchSettingCard(
            configItem=self.cfg.autoSave,
            icon=FluentIcon.SAVE,
            title='保存历史壁纸',
            content='保存过往每一次的壁纸（注：会占用磁盘空间）',
        )
        self.auto_save.checkedChanged.connect(self._on_auto_save_changed)
        setting_group.addSettingCard(self.auto_save)

    def _setup_folder_card(self, setting_group):
        """Setup wallpaper folder selection card"""
        self.folder_card = PushSettingCard(
            icon=FluentIcon.DOWNLOAD,
            title='壁纸保存路径',
            text='选择文件夹',
            content='未选择文件夹',
        )
        self.folder_card.clicked.connect(self._select_folder)

        # Set initial folder path
        initial_folder = self.cfg.get(self.cfg.imageFolder)
        self.folder_card.setContent(initial_folder or '未选择文件夹')

        setting_group.addSettingCard(self.folder_card)

    def _setup_time_interval_card(self, setting_group):
        """Setup time interval selection card"""
        self.time_card = ComboBoxSettingCard(
            configItem=self.cfg.timeInterval,
            icon=FluentIcon.DATE_TIME,
            title='更新间隔',
            content='自动更新桌面的时间间隔',
            texts=PoDConfig.TIME_INTERVAL_TEXTS
        )
        self.time_card.configItem.valueChanged.connect(self._on_time_interval_changed)
        setting_group.addSettingCard(self.time_card)

    def _setup_about_card(self, setting_group):
        """Setup about section card"""
        self.about_card = PrimaryPushSettingCard(
            text='联系开发者',
            icon=FluentIcon.HELP,
            title='关于软件',
            content='©版权所有2024 圈圈烃. 版本：0.2.1'
        )
        self.about_card.clicked.connect(self._open_developer_page)
        setting_group.addSettingCard(self.about_card)

    def _select_folder(self):
        """Open folder selection dialog"""
        folder_path = QFileDialog.getExistingDirectory(self, '选择文件夹')
        if folder_path:
            # Update configuration and UI
            self.cfg.set(self.cfg.imageFolder, folder_path)
            self.folder_card.setContent(folder_path)

    def _on_time_interval_changed(self, time_interval):
        """Handle time interval change"""
        self._show_restart_message()

    def _show_restart_message(self):
        """Show restart required message"""
        msg_box = MessageBox('提示', '修改后需要重启软件才能生效', self)
        msg_box.yesButton.setText("好的")
        msg_box.cancelButton.hide()
        msg_box.exec_()

    def _on_auto_start_changed(self, is_checked):
        """Handle auto-start setting change"""
        # Log or perform any necessary actions on auto-start change
        try:
            # Get the application executable path
            if getattr(sys, 'frozen', False):
                # PyInstaller creates a temp folder and stores path in _MEIPASS
                app_path = sys.executable
            else:
                app_path = sys.argv[0]

            # Application name for registry
            app_name = 'PoDAutoStart'

            # Perform startup registration based on checkbox
            if is_checked:
                # success = StartupManager.add_to_startup(app_name, app_path)  # 注册列表
                success = StartupManager.enable_auto_start(app_name, app_path)  # 启动文件夹
            else:
                # success = StartupManager.remove_from_startup(app_name)
                success = StartupManager.disable_auto_start(app_name)

            # Provide user feedback
            if not success:
                # Revert the checkbox if operation failed
                self.auto_start.setChecked(not is_checked)

                # Show error message
                msg_box = MessageBox('提示', '无法修改开机启动设置。请检查系统权限。', self)
                msg_box.yesButton.setText("好的")
                msg_box.cancelButton.hide()
                msg_box.exec_()
            else:
                # Log the change
                print(f'Auto-start {"enabled" if is_checked else "disabled"}')

                msg_box = MessageBox('提示', f'应用已{"设置" if is_checked else "取消"}开机启动。', self)
                msg_box.yesButton.setText("好的")
                msg_box.cancelButton.hide()
                msg_box.exec_()

        except Exception as e:
            # Handle any unexpected errors
            # logging.error(f"Auto-start configuration error: {e}")
            msg_box = MessageBox('错误', '配置开机启动时发生意外错误。', self)
            msg_box.yesButton.setText("好的")
            msg_box.cancelButton.hide()
            msg_box.exec_()

    def _on_auto_save_changed(self, is_checked):
        """"""
        print('is_checked', is_checked)

    def _open_developer_page(self):
        """Open developer's homepage"""
        url = QUrl('https://space.bilibili.com/330626607')
        QDesktopServices.openUrl(url)
