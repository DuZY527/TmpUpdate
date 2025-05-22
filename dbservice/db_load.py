from dbservice import models

def add_or_update_load_record(db, record_obj: models.TLoadRecord):
    """
    要么新增 models.TLoadRecord 要么更新 models.TLoadRecord

    :param db: 数据库会话
    :param record_obj: TLoadRecord 模型对象
    :return: 更新或新增后的 TLoadRecord 记录
    """
    # 根据 id 查找数据库中的记录
    existing_record = db.query(models.TLoadRecord).filter(
        models.TLoadRecord.id == record_obj.id
    ).first()

    if existing_record:
        # 若记录存在，更新记录字段
        existing_record.status = record_obj.status
        existing_record.msg = record_obj.msg
        existing_record.memo = record_obj.memo
        existing_record.request_json = record_obj.request_json
        existing_record.result_json = record_obj.result_json
        record = existing_record
    else:
    # 刷新记录
        # 若记录不存在，新增记录
        db.add(record_obj)
        record = record_obj

    # 提交数据库更改
    db.commit()
    db.refresh(record)
    return record