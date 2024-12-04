#!/usr/bin/env python  
# _*_ coding:utf-8 _*_  
#  
# @Version : 1.0  
# @Time    : 2024/6/18
# @Author  : 圈圈烃
# @File    : earth_himawari8
# @Description:
#
#
import datetime


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


if __name__ == '__main__':
    url = get_earth_h8_img_url()
    print(url)
