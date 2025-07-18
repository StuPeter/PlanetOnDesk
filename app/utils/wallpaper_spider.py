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
import sys  # 导入 sys 模块用于判断操作系统
import subprocess  # 导入 subprocess 用于执行外部命令，如 AppleScript、gsettings

# 判断操作系统
IS_WINDOWS = sys.platform.startswith('win')
IS_MACOS = sys.platform == 'darwin'
IS_LINUX = sys.platform.startswith('linux')  # 新增 Linux 判断

if IS_WINDOWS:
    try:
        import win32api
        import win32con
        import win32gui
    except ImportError:
        print("警告：未找到 win32api、win32con、win32gui 模块。Windows 壁纸设置功能将受限。")
        IS_WINDOWS = False  # 如果导入失败，也认为 Windows 功能不可用
elif IS_MACOS:
    print("当前为 macOS 系统，将启用 macOS 壁纸设置功能。")
elif IS_LINUX:
    print("当前为 Linux 系统，将尝试使用 gsettings 设置壁纸。")
else:
    print("警告：当前操作系统既非 Windows、macOS 也非 Linux。壁纸设置功能可能无法使用。")


class AutoWallpaperSpider:
    def __init__(self, img_urls, img_name, wallpaper_dir, img_fill=False):
        """
        初始化 AutoWallpaperSpider 类。

        :param img_urls: 图像的 URL 或 URL 列表
        :param img_name: 最终壁纸文件名称
        :param wallpaper_dir: 壁纸存储目录
        :param img_fill: 是否填充图像以匹配屏幕分辨率
        """
        # 确保 img_urls 总是列表
        self.img_urls = [img_urls] if isinstance(img_urls, str) else img_urls
        self.img_name = img_name
        self.img_fill = img_fill
        self.wallpaper_dir = wallpaper_dir
        self.wallpaper_paths = []
        # self.wallpaper_path 在 merge_images 中确定最终路径
        self.wallpaper_path = ""
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

        # 确保壁纸目录存在
        os.makedirs(self.wallpaper_dir, exist_ok=True)
        print(f"壁纸存储目录: {self.wallpaper_dir}")

    def download_images(self, max_attempts=10):
        """下载图片，支持失败重试"""
        print("开始图片下载过程...")
        self.wallpaper_paths = []

        for index, img_url in enumerate(self.img_urls):
            temp_path = os.path.join(
                self.wallpaper_dir,
                f"temp_{index}_{self.img_name}"
            )
            print(f"正在下载图片: {img_url}")

            for attempt in range(1, max_attempts + 1):
                print(f"尝试下载图片 ({attempt}/{max_attempts})...")
                try:
                    response = requests.get(img_url, timeout=20, verify=False, headers=self.headers)
                    response.raise_for_status()  # 检查HTTP响应状态码

                    with open(temp_path, 'wb') as file:
                        file.write(response.content)

                    self.wallpaper_paths.append(temp_path)
                    print(f"成功下载图片到: {temp_path}")
                    break  # 下载成功，跳出重试循环

                except requests.RequestException as e:
                    print(f"下载失败: {e}")
                    if attempt == max_attempts:
                        print(f"在 {max_attempts} 次尝试后放弃下载 {img_url}。")
                        raise  # 达到最大重试次数，抛出异常
                    print("2 秒后重试...")
                    time.sleep(2)
        print("所有图片/瓦片下载完成。")

    def merge_images(self):
        """
        如果 img_fill 为 True 且存在多个 URL，则将多张图片合并为网格布局。
        否则，直接使用单张图片作为最终壁纸。
        """
        self.wallpaper_path = os.path.join(self.wallpaper_dir, self.img_name)  # 确定最终壁纸路径

        if len(self.img_urls) > 1 and self.img_fill:  # 只有在多个 URL 且 img_fill 为 True 时才合并
            print("开始图片合并过程...")

            # 检查目标文件是否存在，如果存在则删除
            if os.path.exists(self.wallpaper_path):
                try:
                    os.remove(self.wallpaper_path)
                    print(f"已删除已存在的合并图片文件: {self.wallpaper_path}")
                except OSError as e:
                    print(f"删除已存在合并图片文件 {self.wallpaper_path} 出错: {e}")
                    raise

            img_width = self.tile_size * self.grid_cols
            img_height = self.tile_size * self.grid_rows

            merged_img = Image.new('RGB', (img_width, img_height))

            # 假定 wallpaper_paths 已经排序或者顺序正确
            # 如果需要，这里可以添加排序逻辑，例如：
            # self.wallpaper_paths.sort(key=lambda x: int(x.split('_')[1]))

            for index, img_path in enumerate(self.wallpaper_paths):
                try:
                    with Image.open(img_path) as from_image:
                        x = (index % self.grid_cols) * self.tile_size
                        y = (index // self.grid_cols) * self.tile_size
                        merged_img.paste(from_image, (x, y))
                except IOError as e:
                    print(f"打开图片 {img_path} 进行合并时出错: {e}")
                    raise

            merged_img.save(self.wallpaper_path)
            print(f"图片已成功合并到: {self.wallpaper_path}")

            # 清理临时文件
            for path in self.wallpaper_paths:
                try:
                    os.remove(path)
                    print(f"已清理临时文件: {path}")
                except OSError as e:
                    print(f"清理临时文件 {path} 出错: {e}")
        else:  # 处理单张图片的情况
            if self.wallpaper_paths:
                # 检查目标文件是否存在，如果存在则删除
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
                else:
                    print(f"图片已直接下载到最终路径: {self.wallpaper_path}，无需重命名。")
            else:
                print("没有可合并或设置的图片。")
                raise RuntimeError("下载后未找到可用的图片路径。")

    def fill_image(self):
        """
        如果需要，将图片填充至匹配桌面分辨率。
        仅适用于 Windows 系统且 img_fill 为 True 时。
        对于 macOS/Linux，如果需要填充，通常在系统壁纸设置中处理。
        """
        # 此处填充逻辑主要针对 Windows，macOS/Linux 可以在其各自的设置命令中选择填充模式
        if not IS_WINDOWS or not self.img_fill:
            if not IS_WINDOWS:
                print("跳过图像填充：当前不是 Windows 系统。")
            else:
                print("跳过图像填充：img_fill 为 False。")
            return

        if not self.wallpaper_path or not os.path.exists(self.wallpaper_path):
            print(f"无法填充图像：壁纸路径无效或文件不存在: {self.wallpaper_path}")
            return

        print("开始图像填充过程 (Windows)...")
        try:
            with Image.open(self.wallpaper_path) as img_content:
                img_width, img_height = img_content.size

                # 获取屏幕分辨率 (仅限 Windows)
                if IS_WINDOWS:
                    monitor_width = win32api.GetSystemMetrics(0)
                    monitor_height = win32api.GetSystemMetrics(1)
                else:  # 非Windows系统无法获取，此处应已return，以防万一
                    print("错误：无法获取屏幕分辨率。")
                    return

                if img_width == monitor_width and img_height == monitor_height:
                    print("图像已匹配屏幕分辨率，无需填充。")
                    return

                fill_img = Image.new(img_content.mode, (monitor_width, monitor_height), color='black')

                paste_x = (monitor_width - img_width) // 2
                paste_y = (monitor_height - img_height) // 2

                fill_img.paste(img_content, (paste_x, paste_y))
                # 在保存填充图片之前，如果目标文件已存在，则先删除它
                if os.path.exists(self.wallpaper_path):
                    try:
                        os.remove(self.wallpaper_path)
                        print(f"已删除已存在的填充图片文件: {self.wallpaper_path}")
                    except OSError as e:
                        print(f"删除已存在填充图片文件 {self.wallpaper_path} 出错: {e}")
                        raise
                fill_img.save(self.wallpaper_path)
            print(f"{self.wallpaper_path} 成功填充至 {monitor_width}x{monitor_height}。")
        except Exception as e:
            print(f"图像填充过程中出错: {e}")
            raise

    def process_sun_image(self):
        """
        处理太阳图片：裁剪掉左下角 985 像素以下的部分。
        将 1024x1024 的图片裁剪为 1024x985。
        """
        # 检查是否是太阳图片的 URL (此处通过检查 URL 中是否包含 'sdo' 简单判断)
        # 更严谨的判断应从调用方传递一个 flag
        if not self.img_urls or 'sdo' not in self.img_urls[0]:  # 确保 img_urls 非空且包含 'sdo'
            print("跳过太阳图片处理：当前图片无需裁剪。")
            return

        if not self.wallpaper_path or not os.path.exists(self.wallpaper_path):
            print(f"无法处理太阳图片：壁纸路径无效或文件不存在: {self.wallpaper_path}")
            return

        print("开始处理太阳图片（裁剪左下角文字）...")
        try:
            with Image.open(self.wallpaper_path) as img:
                width, height = img.size
                if width != 1024 or height != 1024:
                    print(f"警告：太阳图片尺寸为 {width}x{height}，预期 1024x1024。可能无法正确裁剪。")

                # 定义裁剪区域 (left, upper, right, lower)
                # 保留从顶部到 985 像素高度的部分
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

    def _set_mac_wallpaper(self, image_path, fill_mode="scale"):
        """
        通过 AppleScript 在 macOS 上设置壁纸。
        :param image_path: 图像的完整路径
        :param fill_mode: 壁纸填充模式 ("scale", "fill", "fit", "center", "tile")
        """
        fill_mode_map = {
            "scale": 0,  # 缩放以适应屏幕，不裁剪（默认）
            "fill": 1,  # 填充屏幕，可能会裁剪
            "fit": 2,  # 适应屏幕，保持比例，可能会有黑边
            "center": 3,  # 居中，保持原尺寸
            "tile": 4  # 平铺
        }

        mode_value = fill_mode_map.get(fill_mode, 0)  # 默认为 scale

        script = f"""
        tell application "Finder"
            set desktop picture to POSIX file "{image_path}"
            set picture settings to {{scaling mode: {mode_value}}}
        end tell
        """

        try:
            subprocess.run(["osascript", "-e", script], check=True, capture_output=True)
            print(f"macOS 桌面壁纸成功设置为: {image_path} (模式: {fill_mode})")
        except subprocess.CalledProcessError as e:
            print(f"设置 macOS 壁纸时出错: {e.stderr.decode().strip()}")
            raise
        except Exception as e:
            print(f"设置 macOS 壁纸时发生意外错误: {e}")
            raise

    def _set_linux_wallpaper(self, image_path, fill_mode="zoom"):
        """
        通过 gsettings 在 Linux (GNOME) 上设置壁纸。
        :param image_path: 图像的完整路径
        :param fill_mode: 壁纸填充模式 ("none", "wallpaper", "centered", "scaled", "zoom", "stretched", "span")
                          "zoom" 对应“缩放”（保持比例填充，可能会裁剪）
                          "scaled" 对应“适应屏幕”（保持比例，可能会有黑边）
                          "stretched" 对应“拉伸”（不保持比例填充）
                          "wallpaper" 对应“平铺”
                          "centered" 对应“居中”
        """
        # 注意：gsettings 的键名和值在不同 GNOME 版本或桌面环境 (如 KDE, XFCE) 中可能有所不同。
        # 此处假定为 GNOME 3.x 或更高版本。

        # 设置图片路径
        try:
            subprocess.run([
                "gsettings", "set", "org.gnome.desktop.background", "picture-uri",
                f"file://{image_path}"  # 注意：file:// 协议是必需的
            ], check=True, capture_output=True)
            print(f"Linux (GNOME) 壁纸路径设置为: {image_path}")
        except subprocess.CalledProcessError as e:
            print(f"设置 Linux (GNOME) 壁纸路径时出错: {e.stderr.decode().strip()}")
            raise
        except Exception as e:
            print(f"设置 Linux (GNOME) 壁纸路径时发生意外错误: {e}")
            raise

        # 设置图片显示模式
        try:
            subprocess.run([
                "gsettings", "set", "org.gnome.desktop.background", "picture-options", fill_mode
            ], check=True, capture_output=True)
            print(f"Linux (GNOME) 壁纸模式设置为: {fill_mode}")
        except subprocess.CalledProcessError as e:
            print(f"设置 Linux (GNOME) 壁纸模式时出错: {e.stderr.decode().strip()}")
            raise
        except Exception as e:
            print(f"设置 Linux (GNOME) 壁纸模式时发生意外错误: {e}")
            raise

    def set_desktop_wallpaper(self):
        """
        将合并/填充后的图像设为桌面壁纸。
        支持 Windows、macOS 和 Linux (GNOME)。
        """
        if not self.wallpaper_path or not os.path.exists(self.wallpaper_path):
            print(f"无法设置壁纸：壁纸文件不存在于路径 {self.wallpaper_path}")
            return

        print("正在尝试设置桌面壁纸...")

        if IS_WINDOWS:
            try:
                key = win32api.RegOpenKeyEx(
                    win32con.HKEY_CURRENT_USER,
                    r"Control Panel\Desktop",
                    0,
                    win32con.KEY_SET_VALUE
                )
                if self.img_fill:
                    win32api.RegSetValueEx(key, "WallpaperStyle", 0, win32con.REG_SZ, "6")  # 适应
                    win32api.RegSetValueEx(key, "TileWallpaper", 0, win32con.REG_SZ, "0")  # 不平铺
                    print("壁纸样式设置为 '适应' (Windows)。")
                else:
                    win32api.RegSetValueEx(key, "WallpaperStyle", 0, win32con.REG_SZ, "0")  # 居中
                    win32api.RegSetValueEx(key, "TileWallpaper", 0, win32con.REG_SZ, "0")  # 不平铺
                    print("壁纸样式设置为 '居中' (Windows)。")

                win32gui.SystemParametersInfo(
                    win32con.SPI_SETDESKWALLPAPER,
                    self.wallpaper_path,
                    1 + 2
                )
                print(f"桌面壁纸成功设置为 {self.wallpaper_path} (Windows)")
            except Exception as e:
                print(f"设置 Windows 桌面壁纸时出错: {e}")
                raise
        elif IS_MACOS:
            mac_fill_mode = "fill" if self.img_fill else "scale"  # macOS 填充模式
            try:
                self._set_mac_wallpaper(self.wallpaper_path, fill_mode=mac_fill_mode)
            except Exception as e:
                print(f"设置 macOS 桌面壁纸时出错: {e}")
                raise
        elif IS_LINUX:
            linux_fill_mode = "zoom" if self.img_fill else "scaled"  # Linux (GNOME) 填充模式
            try:
                self._set_linux_wallpaper(self.wallpaper_path, fill_mode=linux_fill_mode)
            except Exception as e:
                print(f"设置 Linux (GNOME) 桌面壁纸时出错: {e}")
                raise
        else:
            print("当前操作系统不支持自动设置壁纸。")
            raise NotImplementedError("当前操作系统不支持自动设置壁纸。")

    def run(self):
        """
        执行整个壁纸设置流程。
        """
        print("开始自动壁纸程序...")
        try:
            self.download_images()
            self.merge_images()  # 此方法也处理了单张图片的情况
            self.process_sun_image()  # 太阳图片处理

            # fill_image 仅对 Windows 的 img_fill 模式有效，macOS/Linux 填充模式在 set_desktop_wallpaper 中通过各自命令控制
            if IS_WINDOWS and self.img_fill:
                self.fill_image()

            self.set_desktop_wallpaper()
            print("自动壁纸程序执行成功。")
        except Exception as e:
            print(f"自动壁纸程序执行失败: {e}")
            # 如果是 GUI 应用，这里可以考虑显示错误对话框
            raise


if __name__ == '__main__':
    from wallpaper_sources import (
        get_earth_h8_img_url,
        get_earth_h8_4x4_img_urls,
        get_moon_nasa_img_url,
        get_sun_nasa_img_url
    )

    # 针对不同操作系统设置不同的默认壁纸目录
    if IS_WINDOWS:
        wallpaper_dir = os.path.join(os.environ.get('USERPROFILE'), 'Pictures', 'AutoWallpaper')
    elif IS_MACOS:
        wallpaper_dir = os.path.join(os.path.expanduser('~'), 'Pictures', 'AutoWallpaper')
    elif IS_LINUX:
        wallpaper_dir = os.path.join(os.path.expanduser('~'), '.local', 'share', 'AutoWallpaper')  # Linux 推荐路径
    else:
        wallpaper_dir = os.path.join(os.path.expanduser('~'), 'AutoWallpaper')

    # 确保壁纸目录存在
    os.makedirs(wallpaper_dir, exist_ok=True)
    print(f"最终壁纸目录设置为: {wallpaper_dir}")

    # --- 选择要下载和设置的图片 ---
    # 参数来自选定的 get_*_url 函数，传递给 AutoWallpaperSpider

    # 选项 1: Himawari 8 (1x1 瓷砖)
    img_urls, img_name, img_fill = get_earth_h8_img_url()
    auto_wallpaper = AutoWallpaperSpider(img_urls=img_urls, img_name=img_name, img_fill=img_fill,
                                         wallpaper_dir=wallpaper_dir)

    # 选项 2: Himawari 8 (4x4 瓷砖，合并成一张图)
    # img_urls, img_name, img_fill = get_earth_h8_4x4_img_urls()
    # auto_wallpaper = AutoWallpaperSpider(
    #     img_urls=img_urls,
    #     img_name=img_name,
    #     img_fill=img_fill,
    #     wallpaper_dir=wallpaper_dir
    # )

    # 选项 3: NASA 月球图片
    # img_urls, img_name, img_fill = get_moon_nasa_img_url()
    # auto_wallpaper = AutoWallpaperSpider(img_urls=img_urls, img_name=img_name, img_fill=img_fill, wallpaper_dir=wallpaper_dir)

    # 选项 4: NASA 太阳图片 (包含裁剪逻辑)
    # img_urls, img_name, img_fill = get_sun_nasa_img_url()
    # auto_wallpaper = AutoWallpaperSpider(img_urls=img_urls, img_name=img_name, img_fill=img_fill,
    #                                      wallpaper_dir=wallpaper_dir)

    auto_wallpaper.run()