import xlrd
from fastapi import BackgroundTasks

from route.root import app
from schema.schema_dict import SolarIndex, AshraeBody
from service.load.ashrae import AshraeService

"""
字典API：
- 标准库接口
- 模型库接口
- 气象参数库接口
- 设备库
- 能源信息库
- 字典设置
- 建筑类型   餐厅，办公室，酒店，写字楼
"""

solar_index_data = []


@app.get("/dict/solar", tags=['字典'])
def solar_index():
    """
    太阳字典数据
    """
    if len(solar_index_data) != 0:
        return solar_index_data

    xls = xlrd.open_workbook('resource/solar_index.xls')
    data = xls.sheet_by_index(0)

    # 读取所有行数据并转换为 SolarIndex 对象
    for row in range(1, data.nrows):  # 从第二行开始读取，跳过表头
        row_data = data.row_values(row)
        solar_index = SolarIndex(
            longitude=row_data[0],
            latitude=row_data[1],
            province=row_data[2],
            city=row_data[3],
            filename=row_data[4]
        )
        solar_index_data.append(solar_index)

    return solar_index_data

ashrae_index_data = []


@app.get("/dict/ashrae", tags=['字典'])
def ashrae_index():
    """
    ashrae数据
    """
    if len(ashrae_index_data) != 0:
        return ashrae_index_data

    xls = xlrd.open_workbook('resource/ashrae_index.xls')
    data = xls.sheet_by_index(0)

    # 读取所有行数据并转换为 SolarIndex 对象
    for row in range(1, data.nrows):  # 从第二行开始读取，跳过表头
        row_data = data.row_values(row)
        ashrae_index = AshraeBody(
            province=row_data[0],
            city=row_data[1],
            restaurant_fast_food=row_data[2],
            office_medium=row_data[3],
            hotel_small=row_data[4],
            apartment_high_rise=row_data[5]
        )
        ashrae_index_data.append(ashrae_index)

    return ashrae_index_data

@app.post("/util/updateAshrae", tags=['utils'])
async def update_ashrae():
    """
    更新ashrae 索引

    :return:
    """
    ashrae_service = AshraeService()
    ashrae_service.exec()
    print("更新ashrae 索引成功")


# 后台任务列表查看接口
@app.get("/tasks", tags=['任务'])
async def get_tasks(bakground_tasks:BackgroundTasks):
    """
    后台任务列表查看接口
    """
    return bakground_tasks.tasks