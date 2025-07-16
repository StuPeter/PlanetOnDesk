#!/usr/bin/env python  
# _*_ coding:utf-8 _*_  
#  
# @Version : 1.0  
# @Time    : 2024/12/8
# @Author  : 圈圈烃
# @File    : wallpaper_spider
# @Description:
#
#
import requests
import os
import time
from PIL import Image

try:
    import win32api
    import win32con
    import win32gui

    WINDOWS_OS = True
except ImportError:
    print("警告：未找到 win32api、win32con、win32gui 模块。壁纸设置功能将被禁用。")
    WINDOWS_OS = False


class AutoWallpaperSpider:
    def __init__(self, img_urls, img_name, wallpaper_dir, img_fill=False):
        """
        初始化 AutoWallpaperSpider 类。

        :param img_urls: 图像的 URL 或 URL 列表
        :param img_name: 最终壁纸文件名称
        :param wallpaper_dir: 壁纸存储目录
        :param img_fill: 是否填充图像以匹配屏幕分辨率
        """
        self.img_urls = img_urls
        self.img_name = img_name
        self.img_fill = img_fill
        self.wallpaper_dir = wallpaper_dir
        self.wallpaper_paths = []
        self.wallpaper_path = os.path.join(self.wallpaper_dir, self.img_name)
        self.grid_rows = 4
        self.grid_cols = 4
        self.tile_size = 550
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-GB;q=0.8,en;q=0.7,en-US;q=0.6',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }

    def download_images(self, max_attempts=10):
        """下载图片，支持失败重试"""
        self.wallpaper_paths = []

        for index, img_url in enumerate(self.img_urls):
            temp_path = os.path.join(
                self.wallpaper_dir,
                f"temp_{index}_{self.img_name}"
            )
            print(f"正在下载图片 {img_url}")

            for attempt in range(1, max_attempts + 1):
                print(f"尝试下载图片 ({attempt}/{max_attempts})...")
                try:
                    response = requests.get(img_url, timeout=20, verify=False, headers=self.headers)
                    response.raise_for_status()

                    with open(temp_path, 'wb') as file:
                        file.write(response.content)

                    self.wallpaper_paths.append(temp_path)
                    break

                except requests.RequestException as e:
                    if attempt == max_attempts:
                        raise
                    time.sleep(2)

    def merge_images(self):
        """
        如果 img_fill 为 True 且存在多个 URL，则将多张图片合并为网格布局。
        否则，直接使用单张图片作为最终壁纸。
        """
        if len(self.img_urls) > 1 and self.img_fill:  # 只有在多个 URL 且 img_fill 为 True 时才合并

            img_width = self.tile_size * self.grid_cols
            img_height = self.tile_size * self.grid_rows

            self.wallpaper_path = os.path.join(self.wallpaper_dir, self.img_name)
            merged_img = Image.new('RGB', (img_width, img_height))

            for index, img_path in enumerate(self.wallpaper_paths):
                try:
                    with Image.open(img_path) as from_image:
                        x = (index % self.grid_cols) * self.tile_size
                        y = (index // self.grid_cols) * self.tile_size
                        merged_img.paste(from_image, (x, y))
                except IOError as e:
                    print(f"打开图片 {img_path} 出错: {e}")
                    raise

            merged_img.save(self.wallpaper_path)

            for path in self.wallpaper_paths:
                try:
                    os.remove(path)
                except OSError as e:
                    print(f"清理临时文件 {path} 出错: {e}")
        else:
            if self.wallpaper_paths:
                self.wallpaper_path = os.path.join(self.wallpaper_dir, self.img_name)
                # 如果目标文件（最终壁纸文件）已经存在，先删除它
                if os.path.exists(self.wallpaper_path):
                    try:
                        os.remove(self.wallpaper_path)
                        print(f"已删除已存在的最终图片文件: {self.wallpaper_path}")
                    except OSError as e:
                        print(f"删除已存在最终图片文件 {self.wallpaper_path} 出错: {e}")
                        raise

                # 只有当临时文件路径和最终目标路径不同时才重命名
                if self.wallpaper_paths[0] != self.wallpaper_path:
                    try:
                        os.rename(self.wallpaper_paths[0], self.wallpaper_path)
                        print(f"已将下载的图片重命名为最终路径: {self.wallpaper_path}")
                    except OSError as e:
                        print(f"重命名图片 {self.wallpaper_paths[0]} 到 {self.wallpaper_path} 出错: {e}")
                        raise
                else:  # 如果临时文件路径就是最终路径 (这通常意味着只下载了一个文件，并且下载时直接用了最终文件名)
                    print(f"图片已直接下载到最终路径: {self.wallpaper_path}，无需重命名。")
            else:
                print("没有可合并或设置的图片。")
                raise RuntimeError("下载后未找到可用的图片路径。")

    def fill_image(self):
        """
        如果需要，将图片填充至匹配桌面分辨率。
        仅适用于 Windows 系统且 img_fill 为 True 时。
        """
        if not WINDOWS_OS or not self.img_fill:
            if not WINDOWS_OS:
                print("跳过图像填充：当前不是 Windows 系统。")
            else:
                print("跳过图像填充：img_fill 为 False。")
            return

        if not self.wallpaper_path or not os.path.exists(self.wallpaper_path):
            print(f"无法填充图像：壁纸路径无效或文件不存在: {self.wallpaper_path}")
            return

        print("开始图像填充过程...")
        try:
            with Image.open(self.wallpaper_path) as img_content:
                img_width, img_height = img_content.size

                monitor_width = win32api.GetSystemMetrics(0)
                monitor_height = win32api.GetSystemMetrics(1)

                if img_width == monitor_width and img_height == monitor_height:
                    print("图像已匹配屏幕分辨率，无需填充。")
                    return

                fill_img = Image.new(img_content.mode, (monitor_width, monitor_height), color='black')

                paste_x = (monitor_width - img_width) // 2
                paste_y = (monitor_height - img_height) // 2

                fill_img.paste(img_content, (paste_x, paste_y))
                fill_img.save(self.wallpaper_path)
            print(f"{self.wallpaper_path} 成功填充至 {monitor_width}x{monitor_height}")
        except Exception as e:
            print(f"图像填充过程中出错: {e}")
            raise

    def process_sun_image(self):
        """
        处理太阳图片
        :return:
        """
        if 'sdo' not in self.img_urls[0]:
            return
        else:
            try:
                with Image.open(self.wallpaper_path) as img:
                    width, height = img.size
                    if width != 1024 or height != 1024:
                        print(f"警告：太阳图片尺寸为 {width}x{height}，预期 1024x1024。可能无法正确裁剪。")

                    # 定义裁剪区域 (left, upper, right, lower)
                    # 保留从顶部到 990 像素高度的部分
                    # 左上角坐标 (0, 0)，右下角坐标 (width, 985)
                    cropped_img = img.crop((0, 0, width, 985))

                    # 在保存裁剪图片之前，如果目标文件已存在，则先删除它
                    if os.path.exists(self.wallpaper_path):
                        try:
                            os.remove(self.wallpaper_path)
                            print(f"已删除已存在的太阳裁剪图片文件: {self.wallpaper_path}")
                        except OSError as e:
                            print(f"删除已存在太阳裁剪图片文件 {self.wallpaper_path} 出错: {e}")
                            raise

                    cropped_img.save(self.wallpaper_path)
                    print(f"太阳图片已成功裁剪并保存为 {cropped_img.size}。")
            except Exception as e:
                print(f"处理太阳图片时出错: {e}")
                raise

    def set_desktop_wallpaper(self):
        """
        将合并/填充后的图像设为桌面壁纸。
        仅适用于 Windows 系统。
        """
        if not WINDOWS_OS:
            print("跳过设置桌面壁纸：当前不是 Windows 系统。")
            return

        if not self.wallpaper_path or not os.path.exists(self.wallpaper_path):
            print(f"无法设置壁纸：壁纸文件不存在于路径 {self.wallpaper_path}")
            return

        print("正在尝试设置桌面壁纸...")
        try:
            # 打开注册表键
            key = win32api.RegOpenKeyEx(
                win32con.HKEY_CURRENT_USER,
                r"Control Panel\Desktop",
                0,
                win32con.KEY_SET_VALUE
            )
            # 设置壁纸样式：
            # "WallpaperStyle"
            #   0: 居中
            #   2: 拉伸
            #   6: 适应
            #   10: 填充
            # "TileWallpaper"
            #   0: 不平铺
            #   1: 平铺
            if self.img_fill:  # 如果图像已填充至屏幕大小，使用“居中”或“适应”
                win32api.RegSetValueEx(key, "WallpaperStyle", 0, win32con.REG_SZ, "6")  # 适应
                win32api.RegSetValueEx(key, "TileWallpaper", 0, win32con.REG_SZ, "0")  # 不平铺
                print("壁纸样式设置为 '适应'。")
            else:  # 对于其他图像，默认使用“居中”
                win32api.RegSetValueEx(key, "WallpaperStyle", 0, win32con.REG_SZ, "0")  # 居中
                win32api.RegSetValueEx(key, "TileWallpaper", 0, win32con.REG_SZ, "0")  # 不平铺
                print("壁纸样式设置为 '居中'。")

            # 更改壁纸
            win32gui.SystemParametersInfo(
                win32con.SPI_SETDESKWALLPAPER,
                self.wallpaper_path,
                1 + 2  # SPIF_UPDATEINIFILE (1) + SPIF_SENDCHANGE (2)
            )
            print(f"桌面壁纸成功设置为 {self.wallpaper_path}")
        except Exception as e:
            print(f"设置桌面壁纸时出错: {e}")
            raise

    def run(self):
        """
        执行整个壁纸设置流程。
        """
        print("开始自动壁纸程序...")
        try:
            self.download_images()
            self.merge_images()  # 此方法也处理了单张图片的情况
            # self.fill_image()
            self.process_sun_image()
            self.set_desktop_wallpaper()
            print("自动壁纸程序执行成功。")
        except Exception as e:
            print(f"自动壁纸程序执行失败: {e}")


if __name__ == '__main__':
    from wallpaper_sources import (
        get_earth_h8_img_url,
        get_earth_h8_4x4_img_urls,
        get_moon_nasa_img_url,
        get_sun_nasa_img_url
    )

    wallpaper_dir = r'F:\Users\QQT\Downloads'

    # --- 选择要下载和设置的图片 ---
    # 参数来自选定的 get_*_url 函数，传递给 AutoWallpaperSpider

    # 选项 1: Himawari 8 (1x1 瓷砖)
    # img_urls, img_name, img_fill = get_earth_h8_img_url()
    # auto_wallpaper = AutoWallpaperSpider(img_urls=img_urls, img_name=img_name, img_fill=img_fill, wallpaper_dir=wallpaper_dir)

    # 选项 2: Himawari 8 (4x4 瓷砖，合并成一张图)
    # img_urls, img_name, img_fill = get_earth_h8_4x4_img_urls()
    # auto_wallpaper = AutoWallpaperSpider(
    #     img_urls=img_urls,
    #     img_name=img_name,
    #     img_fill=img_fill,
    #     wallpaper_dir=wallpaper_dir
    # )
    # auto_wallpaper.wallpaper_path = r'F:\Users\QQT\Downloads\spacesniffer_2_0_2_5_x64\himawari8_4x4_2025_07_16_05_30.png'
    # auto_wallpaper.img_fill = True
    # auto_wallpaper.set_desktop_wallpaper()

    # 选项 3: NASA 月球图片
    # img_urls, img_name, img_fill = get_moon_nasa_img_url()
    # auto_wallpaper = AutoWallpaperSpider(img_urls=img_urls, img_name=img_name, img_fill=img_fill, wallpaper_dir=wallpaper_dir)

    # 选项 4: NASA 太阳图片
    img_urls, img_name, img_fill = get_sun_nasa_img_url()
    auto_wallpaper = AutoWallpaperSpider(img_urls=img_urls, img_name=img_name, img_fill=img_fill,
                                         wallpaper_dir=wallpaper_dir)

    auto_wallpaper.run()
