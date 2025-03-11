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
import logging
import winshell
import os


class StartupManager:
    """Manages application auto-start functionality for Windows"""

    @staticmethod
    def enable_auto_start(app_name, app_path):
        """ 启用开机自启 """
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"

        try:
            # 打开注册表键
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                key_path,
                0,  # 默认权限
                winreg.KEY_SET_VALUE
            )
            # 设置键值（程序名称和路径）
            winreg.SetValueEx(
                key,
                app_name,  # 自定义程序标识名称
                0,
                winreg.REG_SZ,
                f'"{app_path}"'
            )
            winreg.CloseKey(key)
            return True
        except Exception as e:
            print(f"Error enabling auto-start: {e}")
            return False

    @staticmethod
    def disable_auto_start(app_name):
        """ 禁用开机自启 """
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                key_path,
                0,
                winreg.KEY_SET_VALUE
            )
            winreg.DeleteValue(key, app_name)  # 删除键值
            winreg.CloseKey(key)
            return True
        except Exception as e:
            print(f"Error disabling auto-start: {e}")
            return False

    @staticmethod
    def add_to_startup(app_name, app_path):
        """
        Add application to Windows startup registry

        :param app_name: Name of the application
        :param app_path: Full path to the application executable
        :return: Boolean indicating success
        """
        try:
            # Windows startup registry key
            key_path = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Run'

            # Open the registry key
            with winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    key_path,
                    0,
                    winreg.KEY_ALL_ACCESS
            ) as key:
                # Set the registry value
                winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, app_path)

            return True
        except Exception as e:
            logging.error(f"Failed to add to startup: {e}")
            return False

    @staticmethod
    def remove_from_startup(app_name):
        """
        Remove application from Windows startup registry

        :param app_name: Name of the application
        :return: Boolean indicating success
        """
        try:
            # Windows startup registry key
            key_path = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Run'

            # Open the registry key
            with winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    key_path,
                    0,
                    winreg.KEY_ALL_ACCESS
            ) as key:
                # Delete the registry value
                winreg.DeleteValue(key, app_name)

            return True
        except FileNotFoundError:
            # Value already doesn't exist
            return True
        except Exception as e:
            logging.error(f"Failed to remove from startup: {e}")
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
    StartupManager.disable_auto_start(app_name)
