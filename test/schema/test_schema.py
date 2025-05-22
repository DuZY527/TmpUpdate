import json

from schema.schema_load import LoadBody


def test_schema():
    with open('../../resource/load.json', 'r') as file:
        data = json.load(file)
    c = LoadBody.parse_obj(data)
    print(c.province)