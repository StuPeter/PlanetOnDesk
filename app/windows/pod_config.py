#!/usr/bin/env python  
# _*_ coding:utf-8 _*_  
#  
# @Version : 1.0  
# @Time    : 2024/12/6
# @Author  : 圈圈烃
# @File    : pod_config
# @Description:
#
#
from qfluentwidgets import (
    QConfig,
    OptionsConfigItem,
    OptionsValidator,
    ConfigItem,
    FolderValidator,
)


class PoDConfig(QConfig):
    """Configuration class for the application settings"""
    TIME_INTERVAL_OPTIONS = [10, 30, 60, 60 * 12, 24 * 60, 'OFF']
    TIME_INTERVAL_TEXTS = ['10分钟', '30分钟', '1小时', '12小时', '1天', '从不更新']

    timeInterval = OptionsConfigItem(
        'PoD', 'TimeInterval', 10,
        OptionsValidator(TIME_INTERVAL_OPTIONS),
        restart=True
    )
    imageFolder = ConfigItem(
        'PoD', 'ImageFolder', "",
        FolderValidator()
    )
    autoStart = OptionsConfigItem(
        'PoD', 'AutoStart', False,
        OptionsValidator([True, False])
    )
    autoSave = OptionsConfigItem(
        'PoD', 'AutoSave', False,
        OptionsValidator([True, False])
    )
    imageSource = OptionsConfigItem(
        'PoD', 'ImageSource', 'Earth-H8',
        OptionsValidator(['Earth-H8', 'Moon-NASA', 'Sun-NASA'])
    )
