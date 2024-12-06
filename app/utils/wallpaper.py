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
import time


class AutoWallpaperSpider:
    def __init__(self, img_url, img_name, wallpaper_dir):
        """
        初始化
        :param img_url: 图片链接
        :param img_name: 图片名称
        :param wallpaper_dir: 壁纸保存目录
        """
        self.img_url = img_url
        self.img_name = img_name
        self.wallpaper_dir = wallpaper_dir
        self.wallpaper_path = os.path.join(self.wallpaper_dir, self.img_name)

    def download_img(self, retries=3):
        """下载图片，支持失败重试"""
        for attempt in range(retries):
            try:
                print(f"尝试下载图片 ({attempt + 1}/{retries})...")
                response = requests.get(self.img_url, timeout=20)
                response.raise_for_status()  # 检查响应状态
                with open(self.wallpaper_path, 'wb') as fw:
                    fw.write(response.content)
                print("图片下载成功！")
                return
            except requests.RequestException as e:
                print(f"下载失败: {e}")
                if attempt < retries - 1:
                    time.sleep(2)  # 等待 2 秒后重试
                else:
                    print("多次尝试下载失败，退出程序。")
                    raise

    def set_desktop(self):
        """设置桌面壁纸"""
        print("正在设置桌面壁纸...")
        key = win32api.RegOpenKeyEx(win32con.HKEY_CURRENT_USER, "Control Panel\\Desktop", 0, win32con.KEY_SET_VALUE)
        win32api.RegSetValueEx(key, "WallpaperStyle", 0, win32con.REG_SZ, "0")  # 0: 居中显示
        win32api.RegSetValueEx(key, "TileWallpaper", 0, win32con.REG_SZ, "0")  # 0: 不平铺
        win32gui.SystemParametersInfo(win32con.SPI_SETDESKWALLPAPER, self.wallpaper_path, 1 + 2)
        print("桌面壁纸设置成功！")

    def auto_main(self):
        """主函数"""
        self.download_img()
        self.set_desktop()


def set_desktop(wallpaper_path):
    """设置桌面壁纸（独立函数）"""
    print("正在设置桌面壁纸...")
    key = win32api.RegOpenKeyEx(win32con.HKEY_CURRENT_USER, "Control Panel\\Desktop", 0, win32con.KEY_SET_VALUE)
    win32api.RegSetValueEx(key, "WallpaperStyle", 0, win32con.REG_SZ, "0")  # 0: 居中显示
    win32api.RegSetValueEx(key, "TileWallpaper", 0, win32con.REG_SZ, "0")  # 0: 不平铺
    win32gui.SystemParametersInfo(win32con.SPI_SETDESKWALLPAPER, wallpaper_path, 1 + 2)
    print("桌面壁纸设置成功！")


if __name__ == '__main__':
    # 示例图片链接
    url = "https://himawari8.nict.go.jp/img/D531106/thumbnail/550/2024/06/17/093000_0_0.png"

    # 初始化 AutoWallpaperSpider 类
    auto_wallpaper = AutoWallpaperSpider(
        img_url=url,
        img_name="moon.jpg",
        wallpaper_dir=r'F:\Users\QQT\Downloads'
    )

    try:
        # 执行主功能
        auto_wallpaper.auto_main()
        # 也可以直接使用独立函数设置桌面
        # set_desktop(auto_wallpaper.wallpaper_path)
    except Exception as e:
        print(f"程序执行中发生错误: {e}")
