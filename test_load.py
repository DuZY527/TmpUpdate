import json

from schema.schema_load import LoadBody, CoolingHeatingPower
from service.load.load_service import LoadService

load_param_file = "./test_load.json"

with open(load_param_file, 'r', encoding='utf-8') as f:
    load_param = json.load(f)

load_body = LoadBody.model_validate(load_param)
loadService = LoadService()
result = loadService.exec(load_body)
