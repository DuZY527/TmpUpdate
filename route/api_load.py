"""
业务相关API
"""
import datetime
import uuid
from typing import List

from fastapi import Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

import schema
from dbservice import models
from dbservice.db_core import get_db
from dbservice.db_load import add_or_update_load_record  # 导入 update_load_record 函数
from route.root import app
from schema.schema_load import LoadBody, CoolingHeatingPowerV2
from service.load.load_service import LoadService
from service.load.load_service_v2 import loop_calc_load_v2


@app.get("/load/{id}", description="查询负荷计算信息", response_model=schema.schema_load.LoadResponseBody)
async def get_load_info(id, db: Session = Depends(get_db)):
    """
    根据 transactionID 查询对应的负荷计算信息
    :param id: 事务 ID
    :param db: 数据库会话
    :return: 负荷计算信息
    """
    # 查询数据库
    record = db.query(models.TLoadRecord).filter(models.TLoadRecord.id == id).first()
    if not record:
        # 若未找到记录，返回 404 错误
        raise HTTPException(status_code=404, detail="未找到对应的负荷计算信息")
    # 将记录转换为schema.schema_load.LoadResponseBody返回
    result = schema.schema_load.LoadResponseBody(
        **record.__dict__
    )

    return result


@app.post("/load", description="负荷计算")
async def calc_load(load: LoadBody, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    运行 计算负荷
    """
    transID = uuid.uuid4().hex

    record = models.TLoadRecord(
        id=transID,
        request_json=load.json(),
        result_json=None,
        create_time=datetime.datetime.now(),
        status="0",  # 状态: 0 表示运行中(init)
        msg="计算开始"
    )

    def task(record):
        loadService = LoadService()
        # 初始状态：运行中

        try:
            # 使用 update_load_record 新增记录
            add_or_update_load_record(db, record)

            # 执行负荷计算
            result = loadService.exec(load)

            # 准备更新记录
            record.status = "1"
            record.msg = "计算成功"
            record.result_json = result
            add_or_update_load_record(db, record)

            # TODO 这里可添加回调逻辑，若回调成功，更新状态为 3
            # callback_success = call_callback_function()
            # if callback_success:

        except Exception as e:
            # 准备异常记录
            record.status = "2"
            record.msg = f"计算失败: {str(e)}"
            add_or_update_load_record(db, record)
            # 使用 update_load_record 更新或新增异常记录
            add_or_update_load_record(db, record)

    background_tasks.add_task(task, record)

    result = schema.schema_load.LoadResponseBody(
        **record.__dict__
    )
    return result


@app.post("/calc_load_v2", description="仅测试用")
async def calc_load_v2(cooling_heating_power_v2: List[CoolingHeatingPowerV2]):
    """
    TODO V1和V2需要嫁接在一起使用。
    运行 冷热电三联，执行V2计算负荷的算法
    """
    load = LoadBody.model_construct(cooling_heating_power_v2=cooling_heating_power_v2)
    result = loop_calc_load_v2(load)
    return result
