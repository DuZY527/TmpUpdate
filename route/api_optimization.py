"""
业务相关API
"""

from route.root import app
from schema.schema_optimization import OptimizationBody
from service.optimization.intelligent_solution_service import ISService


@app.post("/optimization", description="方案计算")
async def calc_optimization(inputBody: OptimizationBody):
    """
    运行 优化
    :param model_id:  可能会有多个优化模型进行计算
    :param inputBody: 请求body体
    :return:
    """
    # 打印  inputBody
    service = ISService()
    result = service.exec(inputBody)
    print(inputBody)
    return {'status': result}
