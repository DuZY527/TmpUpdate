import json
from datetime import datetime

import pypinyin
from fastapi import requests


def location_to_province(Longitude,latitude):
    key = 'GjG3XAdmywz7CyETWqHwIuEC6ZExY6QT'
    location = str(Longitude)+','+str(latitude)
    print(location)
    # r = requests.get(url='http://api.map.baidu.com/geocoder/v2/', params={'location':location, 'ak':key,'output':'json'})
    # result = r.json()
    url = 'http://api.map.baidu.com/geocoder/v2/'
    data = {
        'ak': key,
        'location': location,
        'output': 'json'
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36',
        'Referer': 'https://www.google.com/'
    }

    res = requests.get(url, headers=headers, params=data)  # 添加请求头
    print(res.text)
    try:
        json.loads(res.text)
        result = json.loads(res.text)
        print(result)
        province = result['result']['addressComponent']['province']
        city = result['result']['addressComponent']['city']
        print(province)
        return province, city
    except ValueError:
        province = 0
        city = 0
        return '0','0'


def pinyin(word):
    s = ''
    for i in pypinyin.pinyin(word, style=pypinyin.NORMAL):
        s += ''.join(i)
    return s


def num_hour_of_year_v1(year, month, day):
    """
    求取一年内的低多少个小时
    :param year:
    :param month:
    :param day:
    :return:
    """

    return (datetime(year,month,day) - datetime(year,1,1)).days*24

def num_hour_of_year(time_str):
    """
    求取一年内的多少个小时
    :param time_str: 格式为 'YYYY-MM-DD' 的日期字符串
    :return: 一年内的小时数
    """
    try:
        date_obj = datetime.strptime(time_str, '%Y-%m-%d')
        year = date_obj.year
        month = date_obj.month
        day = date_obj.day
        return (datetime(year, month, day) - datetime(year, 1, 1)).days * 24
    except ValueError:
        raise ValueError(f"Invalid date format: {time_str}. Expected format: 'YYYY-MM-DD'")

def diff_day(start_time, end_time):
    start_date = datetime.strptime(start_time, "%Y-%m-%d")
    end_date = datetime.strptime(end_time, "%Y-%m-%d")

    # 计算日期差
    delta = end_date - start_date
    return delta.days