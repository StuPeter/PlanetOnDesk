#!/usr/bin/env python  
# _*_ coding:utf-8 _*_  
#  
# @Version : 1.0  
# @Time    : 2024/12/8
# @Author  : 圈圈烃
# @File    : wallpaper_sources
# @Description:
#
#
import datetime
import math


def round_down_time(dt):
    """
    将时间向下取整
    """
    rounded = dt - datetime.timedelta(
        minutes=dt.minute % 10,
        seconds=dt.second,
        microseconds=dt.microsecond
    )
    return rounded


def get_earth_h8_img_url():
    utc_time = datetime.datetime.utcnow() - datetime.timedelta(minutes=30)  # 获取GMT时间并减去30分钟
    rounded_time = round_down_time(utc_time)
    utc_time_str = rounded_time.strftime("%Y/%m/%d/%H%M")  # 时间格式化
    img_name = f'{rounded_time.strftime("%Y_%m_%d_%H_%M")}.png'
    # img_url = f'https://himawari.asia/img/D531106/1d/550/{utc_time_str}00_0_0.png'
    img_url = f'https://himawari8.nict.go.jp/img/D531106/1d/550/{utc_time_str}00_0_0.png'
    return img_url, img_name


def get_moon_nasa_img_url():
    # 判断今年是哪一年
    year = datetime.datetime.utcnow().year
    time_diff = datetime.datetime.utcnow() - datetime.datetime(year, 1, 1, 0)  # 获取GMT时间并减2024-01-01,0时
    time_diff_hours = math.floor(time_diff.days * 24 + time_diff.seconds / 3600) + 1
    img_name = f'{time_diff_hours}.jpg'
    if year == 2024:
        img_url = "https://svs.gsfc.nasa.gov/vis/a000000/a005100/a005187/frames/730x730_1x1_30p/moon." + str(
            time_diff_hours) + ".jpg"  # 2024年
    else:
        img_url = "https://svs.gsfc.nasa.gov/vis/a000000/a005400/a005415/frames/730x730_1x1_30p/moon." + str(
            time_diff_hours) + ".jpg"  # 2025年
    return img_url, img_name


def get_sun_nasa_img_url():
    img_name = f'sun.jpg'
    img_url = "https://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_0304.jpg"
    return img_url, img_name


if __name__ == '__main__':
    img_url, img_name = get_moon_nasa_img_url()
    print(img_url, img_name)
