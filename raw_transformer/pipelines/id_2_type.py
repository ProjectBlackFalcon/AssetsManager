import json
import os


def generate():
    """
    Outputs a json of id: type_id. The type id references to the item's category (e.g. hat, cloak, ...)

    :return: None
    """
    with open(os.path.abspath(os.path.join(os.path.dirname(__file__), '../output/Items.json')), 'r', encoding="utf8") as f:
        items = json.load(f)

    output = {}
    for item in items:
        output[item['id']] = item['typeId']

    with open(os.path.abspath(os.path.join(os.path.dirname(__file__), '../definitive_output/id_2_type.json')), 'w', encoding='utf8') as f:
        json.dump(output, f, ensure_ascii=False)
