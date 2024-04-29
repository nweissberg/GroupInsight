import json
from pathlib import Path

collection = Path("data")
store_name = "test"
jsonpath = collection / (store_name + ".json")

data = None

with open(jsonpath) as json_file:
    data = json.load(json_file)
    print(data)

collection.mkdir(exist_ok=True)
jsonpath.write_text(json.dumps(data, indent=4, sort_keys=True, ensure_ascii=False))
