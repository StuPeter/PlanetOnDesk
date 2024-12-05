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


class StartupManager:
    """Manages application auto-start functionality for Windows"""

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
