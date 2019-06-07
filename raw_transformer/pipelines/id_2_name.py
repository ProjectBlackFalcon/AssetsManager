import d2o_unpack
import d2i_unpack
import os
import json


def generate():
    """
    Outputs a json of id:name (in french)

    :return: None
    """
    with open(os.path.abspath(os.path.join(os.path.dirname(__file__), '../output/Items.json')), 'r') as f:
        items = json.load(f)

    id_nameids = {}
    for item in items:
        id_nameids[str(item['id'])] = item['nameId']

    with open(os.path.abspath(os.path.join(os.path.dirname(__file__), '../output/i18n_fr.json')), 'r', encoding='utf8') as f:
        texts = json.load(f)['texts']

    id_2_names = {}
    print(id_nameids)
    for id in id_nameids:
        try:
            id_2_names[str(id)] = texts[str(id_nameids[str(id)])]
        except:
            pass

    with open(os.path.abspath(os.path.join(os.path.dirname(__file__), '../definitive_output/id_2_names.json')), 'w', encoding='utf8') as f:
        json.dump(id_2_names, f, ensure_ascii=False)


if __name__ == '__main__':
    generate()
