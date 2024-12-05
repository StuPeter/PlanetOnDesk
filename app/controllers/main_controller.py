#!/usr/bin/env python  
# _*_ coding:utf-8 _*_  
#  
# @Version : 1.0  
# @Time    : 2024/6/12
# @Author  : 圈圈烃
# @File    : main_controller
# @Description:
#
#
import os
import json
import logging
from typing import Optional, Tuple

from PyQt5.QtCore import QObject, QTimer, QThread, pyqtSignal
from PyQt5.QtWidgets import QMessageBox
from qfluentwidgets import MessageBox

from app.utils.wallpaper import AutoWallpaperSpider
from app.utils.earth_himawari8 import get_earth_h8_img_url


class ConfigManager:

    @staticmethod
    def load_config(config_path: str = 'app/config.json') -> Optional[dict]:
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except FileNotFoundError:
            logging.error(f"配置文件未找到: {config_path}")
        except json.JSONDecodeError:
            logging.error(f"配置文件解析错误: {config_path}")
        return None

    @staticmethod
    def get_config_value(config: dict, *keys):
        try:
            for key in keys:
                config = config[key]
            return config
        except (KeyError, TypeError) as e:
            logging.error(f"获取配置项 {keys} 失败: {e}")
            return None


class WallpaperDownloadThread(QThread):
    """后台下载壁纸线程"""

    download_finished = pyqtSignal(bool, str)

    def __init__(self, img_url: str, img_name: str, save_folder: str):
        super().__init__()
        self.img_url = img_url
        self.img_name = img_name
        self.save_folder = save_folder

    def run(self):
        try:
            aw = AutoWallpaperSpider(self.img_url, self.img_name, self.save_folder)
            aw.download_img()
            aw.set_desktop()
            self.download_finished.emit(True, "壁纸下载成功")
        except Exception as e:
            logging.error(f"壁纸下载失败: {e}")
            self.download_finished.emit(False, str(e))


class MainController(QObject):

    def __init__(self, main_window):
        super().__init__()
        self.mw = main_window
        self.timer = QTimer(self.mw)
        self.timer_active = False  # 追踪定时器状态
        self.download_thread = None

        # 配置日志
        self._setup_logging()
        # 开启
        self.init_timer()

    def _setup_logging(self):
        """配置日志记录器"""
        log_dir = 'app/logs'
        os.makedirs(log_dir, exist_ok=True)
        logging.getLogger(__name__)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('app/logs/pod.log', encoding='utf-8'),
                logging.StreamHandler()  # 控制台输出
            ]
        )

    def init_timer(self):
        """初始化定时器"""

        # 如果定时器已经激活，先停止
        if self.timer_active:
            self.timer.stop()
            logging.info("停止已存在的定时器")

        self.timer.timeout.connect(self.run_set_wallpaper)

        config = ConfigManager.load_config()
        if config:
            time_interval = ConfigManager.get_config_value(config, 'PoD', 'TimeInterval')

            if time_interval == 'OFF':
                self.timer.stop()
                self.timer_active = False
                return
            else:
                # 将分钟转换为毫秒
                interval_ms = int(time_interval) * 60 * 1000
                self.timer.start(interval_ms)
                self.timer_active = True

    def start_to_set(self):
        """开始设置壁纸流程"""
        if not self.timer_active:
            self.run_set_wallpaper()
            self.init_timer()
        else:
            logging.info("定时器已在运行中")

    def run_set_wallpaper(self):
        """执行壁纸下载设置"""
        try:
            img_url, img_name = get_earth_h8_img_url()

            config = ConfigManager.load_config()
            if not config:
                raise ValueError("未找到配置文件")

            image_folder = ConfigManager.get_config_value(config, 'PoD', 'ImageFolder')

            if not image_folder:
                w = MessageBox('提示', '未找到壁纸保存路径，请先设置壁纸保存路径', self.mw)
                w.yesButton.setText("好的")
                w.cancelButton.hide()
                w.exec_()
                return
            # 判断是否保存历史图片
            auto_save = ConfigManager.get_config_value(config, 'PoD', 'AutoSave')
            if not auto_save:
                img_name = 'h8_earth.png'
            # 启动后台下载线程
            self.download_thread = WallpaperDownloadThread(img_url, img_name, image_folder)
            self.download_thread.download_finished.connect(self._on_download_finished)

            # 禁用按钮防止重复点击
            self.mw.setDesktopButton.setEnabled(False)
            self.download_thread.start()

            logging.info(f'开始下载壁纸: {img_url}')

        except Exception as e:
            logging.error(f'设置壁纸发生错误: {e}')
            QMessageBox.critical(self.mw, '错误', f'壁纸下载失败: {e}')

    def _on_download_finished(self, success: bool, message: str):
        """下载完成后回调"""
        # 重新启用按钮
        self.mw.setDesktopButton.setEnabled(True)
        print(success, message)
