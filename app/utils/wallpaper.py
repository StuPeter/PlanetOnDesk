#!/usr/bin/env python  
# _*_ coding:utf-8 _*_  
#  
# @Version : 1.0  
# @Time    : 2024/6/17
# @Author  : 圈圈烃
# @File    : wallpaper
# @Description:
#
#
import win32api
import win32con
import win32gui
import requests
import os


class AutoWallpaperSpider:
    def __init__(self, img_url, img_name, wallpaper_dir):
        """
        初始化
        :param img_url: 图片链接
        :param img_name: 图片名称
        """
        self.img_url = img_url
        self.img_name = img_name
        self.wallpaper_dir = wallpaper_dir
        self.wallpaper_path = os.path.join(self.wallpaper_dir, self.img_name)

    def download_img(self):
        """下载图片"""
        response = requests.get(self.img_url, timeout=20)
        response.raise_for_status()
        with open(self.wallpaper_path, 'wb') as fw:
            fw.write(response.content)

    def set_desktop(self):
        """设置桌面"""
        key = win32api.RegOpenKeyEx(win32con.HKEY_CURRENT_USER, "Control Panel\\Desktop", 0, win32con.KEY_SET_VALUE)
        win32api.RegSetValueEx(key, "WallpaperStyle", 0, win32con.REG_SZ, "0")
        win32api.RegSetValueEx(key, "TileWallpaper", 0, win32con.REG_SZ, "0")
        win32gui.SystemParametersInfo(win32con.SPI_SETDESKWALLPAPER, self.wallpaper_path, 1 + 2)

    def auto_main(self):
        """主函数"""
        self.download_img()
        self.set_desktop()


def set_desktop(wallpaper_path):
    """设置桌面"""
    key = win32api.RegOpenKeyEx(win32con.HKEY_CURRENT_USER, "Control Panel\\Desktop", 0, win32con.KEY_SET_VALUE)
    win32api.RegSetValueEx(key, "WallpaperStyle", 0, win32con.REG_SZ, "0")
    win32api.RegSetValueEx(key, "TileWallpaper", 0, win32con.REG_SZ, "0")
    win32gui.SystemParametersInfo(win32con.SPI_SETDESKWALLPAPER, wallpaper_path, 1 + 2)


if __name__ == '__main__':
    url = "https://himawari8.nict.go.jp/img/D531106/thumbnail/550/2024/06/17/093000_0_0.png"
    auto_wallpaper = AutoWallpaperSpider(img_url=url, img_name="moon.jpg", wallpaper_dir=f'F:/Users/QQT/Pictures')
    auto_wallpaper.auto_main()
    set_desktop()
