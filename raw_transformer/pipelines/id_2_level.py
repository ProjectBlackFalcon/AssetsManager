import os
import json


def generate():
    """
    Outputs a json of id:level of items

    :return: None
    """
    with open(os.path.abspath(os.path.join(os.path.dirname(__file__), '../output/Items.json')), 'r') as f:
        items = json.load(f)

    id_weight = {}
    for item in items:
        id_weight[str(item['id'])] = item['level']

    with open(os.path.abspath(os.path.join(os.path.dirname(__file__), '../definitive_output/id_2_level.json')), 'w', encoding='utf8') as f:
        json.dump(id_weight, f, ensure_ascii=False)


if __name__ == '__main__':
    generate()