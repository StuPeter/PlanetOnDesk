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
from PyQt5.QtCore import QTimer, QThread, pyqtSignal
from qfluentwidgets import MessageBox
from app.utils.wallpaper import AutoWallpaperSpider
from app.utils.earth_himawari8 import get_earth_h8_img_url
import json


class WorkerThread(QThread):
    result_signal = pyqtSignal(str)

    def run(self):
        try:
            img_url, img_name = get_earth_h8_img_url()
            print(img_url, img_name)
            with open(r'app/config.json', 'r', encoding='utf-8') as file:
                cfg = json.load(file)
            if cfg:
                image_folder = get_config_value(cfg, 'PoD', 'ImageFolder')
                aw = AutoWallpaperSpider(img_url, img_name, image_folder)
                aw.download_img()
                aw.set_desktop()
        except Exception as e:
            print(str(e))
        finally:
            result = "finished"
            self.result_signal.emit(result)


def get_config_value(data, *keys):
    """
    根据指定的键路径获取JSON配置项的值
    :param data: JSON数据
    :param keys: 键路径
    :return: 对应的配置项的值
    """
    try:
        for key in keys:
            data = data[key]
        return data
    except KeyError:
        print(f"键路径 {keys} 未找到")
    except TypeError:
        print(f"键路径 {keys} 无法解析")
    except Exception as e:
        print(f"获取配置项时发生意外错误: {e}")


class MainController:

    def __init__(self, main_window):
        self.mw = main_window
        self.thread = WorkerThread()
        self.timer = QTimer(self.mw)

    def init_timer(self):
        self.timer.timeout.connect(self.run_set_wallpaper)
        with open(r'app/config.json', 'r', encoding='utf-8') as file:
            cfg = json.load(file)
        print(cfg)
        if cfg:
            time_interval = get_config_value(cfg, 'PoD', 'TimeInterval')
            if time_interval == 'OFF':
                self.timer.stop()
            else:
                self.timer.start(int(time_interval) * 60 * 1000)

    def start_to_set(self):
        self.mw.setDesktopButton.setEnabled(False)
        self.run_set_wallpaper()
        self.init_timer()

    def on_task_finished(self):
        self.mw.setDesktopButton.setEnabled(True)

    def run_set_wallpaper(self):
        try:
            img_url, img_name = get_earth_h8_img_url()
            print(img_url, img_name)
            with open(r'app/config.json', 'r', encoding='utf-8') as file:
                cfg = json.load(file)
            if cfg:
                image_folder = get_config_value(cfg, 'PoD', 'ImageFolder')
                if image_folder:
                    aw = AutoWallpaperSpider(img_url, img_name, image_folder)
                    aw.download_img()
                    aw.set_desktop()
                else:
                    w = MessageBox('提示', '未找到壁纸保存路径，请先设置壁纸保存路径', self.mw)
                    w.yesButton.setText("好的")
                    w.cancelButton.hide()
                    if w.exec():
                        print('确认')
                    else:
                        print('取消')
        except Exception as e:
            print(str(e))
        finally:
            self.on_task_finished()
