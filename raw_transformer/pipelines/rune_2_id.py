import json
import os


def generate():
    """
    Outputs a json of rune_name:id (in french)

    :return: None
    """
    with open(os.path.abspath(os.path.join(os.path.dirname(__file__), '../definitive_output/id_2_names.json')), 'r', encoding="utf8") as f:
        ids = json.load(f)

    runes_ids = {}
    for item_id, name in ids.items():
        if 'Rune' in name.split(' ')[0] and 'vers' not in name:
            runes_ids[name] = int(item_id)
            # print(item_id, name)

    with open(os.path.abspath(os.path.join(os.path.dirname(__file__), '../definitive_output/rune_2_id.json')), 'w', encoding="utf8") as f:
        json.dump(runes_ids, f, ensure_ascii=False)
