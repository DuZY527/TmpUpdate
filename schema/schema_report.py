"""
生成最终报告的schema 定义
"""

from schema.schema_load import LoadBody

class LoadObject:
    pass


class ReportBody:
    loadBody: LoadBody
    loadObject: LoadObject
    solution: dict
