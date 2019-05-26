import json


def generate():
    """
    Outputs a json of id: type_id. The type id references to the item's category (e.g. hat, cloak, ...)

    :return: None
    """
    with open('output/Items.json', 'r', encoding="utf8") as f:
        items = json.load(f)

    output = {}
    for item in items:
        output[item['id']] = item['typeId']

    with open('definitive_output/id_2_type.json', 'w', encoding='utf8') as f:
        json.dump(output, f, ensure_ascii=False)
