from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, func, Text, JSON, Index
from sqlalchemy.orm import declarative_base

from dbservice.db_core import engine

Base = declarative_base()


class TLoadRecord(Base):
    __tablename__ = "t_load_record"

    id = Column(String(128), primary_key=True, comment="transaction_id")  # transaction_id
    request_json = Column(JSON, comment="请求参数")
    result_json = Column(JSON,comment="计算结果")
    create_time = Column(DateTime, default=datetime.now())
    refresh_time = Column(DateTime, default=datetime.now(), onupdate=datetime.now())
    msg = Column(String(512), comment='信息')
    status = Column(String(32), default=0,
                    comment='状态: 0:运行中(init); 1:计算完成; 2:计算异常; 3:回调完成; 4：回调异常')
    memo = Column(String(255), comment='备注')


# initial
Base.metadata.create_all(engine)
