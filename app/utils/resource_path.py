#!/usr/bin/env python  
# _*_ coding:utf-8 _*_  
#  
# @Version : 1.0  
# @Time    : 2025/3/12
# @Author  : 圈圈烃
# @File    : resource_path
# @Description:
#
#
import sys
import os


def get_resource_path(relative_path):
    """获取资源的绝对路径（兼容开发环境和 PyInstaller 打包环境）"""
    if hasattr(sys, '_MEIPASS'):
        # 打包后：资源在临时解压目录
        base_path = sys._MEIPASS
    else:
        # 开发环境：使用当前工作目录
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
