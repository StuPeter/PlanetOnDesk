#!/usr/bin/env python  
# _*_ coding:utf-8 _*_  
#  
# @Version : 1.0  
# @Time    : 2024/12/5
# @Author  : 圈圈烃
# @File    : auto_start
# @Description:
#
#
import winreg
import subprocess
import logging
import winshell
import sys
import os


class StartupManager:
    """Manages application auto-start functionality for Windows"""

    @staticmethod
    def get_startup_path():
        """获取开机自启快捷方式路径"""
        return os.path.join(
            os.environ["APPDATA"],
            "Microsoft", "Windows", "Start Menu", "Programs", "Startup",
            "PlanetOnDesktop.lnk"
        )

    def enable_auto_start(self):
        """启用开机自启"""
        try:
            target_path = sys.executable
            shortcut_path = self.get_startup_path()

            command = (
                f"$WshShell = New-Object -ComObject WScript.Shell; "
                f"$Shortcut = $WshShell.CreateShortcut('{shortcut_path}'); "
                f"$Shortcut.TargetPath = '{target_path}'; "
                "$Shortcut.Save()"
            )
            subprocess.run(
                ["powershell", "-Command", command],
                check=True,
                shell=True
            )
            print("成功", "已启用开机自启！")
            return True
        except Exception as e:
            logging.error(f"启用失败: {e}")
            print("错误", f"启用失败: {str(e)}")
            return False

    def disable_auto_start(self):
        """禁用开机自启"""
        try:
            shortcut_path = self.get_startup_path()
            if os.path.exists(shortcut_path):
                os.remove(shortcut_path)
                print("成功", "已禁用开机自启！")
                return True
            else:
                print("错误", "未找到自启动项")
                return False
        except Exception as e:
            print("错误", f"禁用失败: {str(e)}")
            logging.error(f"禁用失败: {e}")
            return False

    @staticmethod
    def create_shortcut_for_startup(app_name, app_path):
        # 启动文件夹路径
        startup_path = os.path.join(
            os.getenv("APPDATA"), r"Microsoft\Windows\Start Menu\Programs\Startup"
        )
        # 快捷方式完整路径
        shortcut_path = os.path.join(startup_path, f"{app_name}.lnk")

        try:
            with winshell.shortcut(shortcut_path) as shortcut:
                shortcut.path = app_path
                shortcut.working_directory = os.path.dirname(app_path)
            print(f"快捷方式创建成功: {shortcut_path}")
            return True
        except Exception as e:
            logging.error(f"无法创建快捷方式: {e}")
            return False

    @staticmethod
    def remove_shortcut_from_startup(app_name):
        startup_path = os.path.join(
            os.getenv("APPDATA"), r"Microsoft\Windows\Start Menu\Programs\Startup"
        )
        shortcut_path = os.path.join(startup_path, f"{app_name}.lnk")
        try:
            os.remove(shortcut_path)
            print(f"快捷方式已删除: {shortcut_path}")
            return True
        except FileNotFoundError:
            print(f"快捷方式不存在: {shortcut_path}")
            return False
        except Exception as e:
            print(f"无法删除快捷方式: {e}")
            return False


if __name__ == '__main__':
    app_name = "PlanetOnDesktop"
    app_path = r"F:\Users\QQT\Downloads\PlanetOnDesktop-0.2.0\PlanetOnDesktop.exe"
    # StartupManager.create_shortcut_for_startup(app_path, app_name)
    # StartupManager.remove_shortcut_from_startup(app_name)
    # StartupManager.enable_auto_start(app_name, app_path)
    start_manager = StartupManager()
    # start_manager.enable_auto_start()
    start_manager.disable_auto_start()
