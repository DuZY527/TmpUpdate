import pyscipopt
from pyscipopt import Model, quicksum, multidict
import numpy as np
import xlwt
import xlrd
import json
import pandas as pd
import random
import time
from schema.schema_optimization import OptimizationBody


#-------------函数定义--------------#
#0：判断数组是多少维数的数组
def is_Empty(arr):
    if not arr:
        return True
    for element in arr:
        if not isinstance(element, list):
            return False
        if not is_Empty(element):
            return False
    return True


def is_multi_dim_arr(arr):
    count = 1
    if type(arr) != list or is_Empty(arr):
        return 0
    while type(arr[0]) == list:
        count += 1
        arr = arr[0]
    return count


#1：保存函数
def to_csv(res, filename, custom_energy_num, custom_device_num, custom_storge_device_num):
    """将规划结果生成csv，并保存到doc文件夹下

    Args:
        res (_type_): dict字典，规划结果
        filename (_type_): 保存的文件名
    """
    res_dict = "doc/"  #保存在doc文件夹
    items = list(res.keys())
    wb = xlwt.Workbook()
    total = wb.add_sheet('garden')
    col = 0
    for i in range(len(items)):
        if res[items[i]] == []:
            continue
        if is_multi_dim_arr(res[items[i]]) == 0:  #数字
            total.write(0, col, items[i])
            total.write(1, col, res[items[i]])
            col += 1
        elif is_multi_dim_arr(res[items[i]]) == 1:  #一维数组
            total.write(0, col, items[i])
            for j in range(len(res[items[i]])):
                total.write(j + 1, col, (res[items[i]])[j])
            col += 1
        elif is_multi_dim_arr(res[items[i]]) == 2:  #二维数组
            for j in range(len(res[items[i]])):
                total.write(0, col, items[i] + str(j))
                for k in range(len(res[items[i]][j])):
                    total.write(k + 1, col, (res[items[i]])[j][k])
                col += 1
        elif is_multi_dim_arr(res[items[i]]) == 3:  #三维数组
            for j in range(len(res[items[i]])):
                for k in range(len(res[items[i]][j])):
                    total.write(0, col, items[i] + str(j) + str(k))
                    for l in range(len(res[items[i]][j][k])):
                        total.write(l + 1, col, (res[items[i]])[j][k][l])
                    col += 1
    wb.save(res_dict + filename)


#2：年化收益率函数
def crf(year):
    """
        将输入文件中的设备寿命转为年化收益率

        Args:
            year: 设备寿命
    """
    i = 0.08
    crf = ((1 + i) ** year) * i / ((1 + i) ** year - 1)
    return crf


#3：计算配套设备价格函数
def support_device(d_cost, d_se):
    return d_cost * d_se


#4：保存结果为json
# def save_json(j,name):
#     res_dict = "doc/" #保存在doc文件夹
#     jj = json.dumps(j)
#     f = open(res_dict+name+".json",'w')
#     f.write(jj)
#     f.close()
#     return 0

def save_json(data, name):
    res_dict = "doc/"  #保存在doc文件夹
    with open(res_dict + name + '.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

class ISService:
    def __init__(self):
        pass

    def exec(self, inputBody: OptimizationBody):
        return 'success'



