import json


def generate():
    """
    Outputs a file of item_id:item_icon_id

    :return: None
    """
    with open('output/Items.json', 'r') as f:
        data = json.load(f)

    output = []
    for item in data:
        output.append({'id': item['id'], 'iconId': item['iconId']})

    with open('definitive_output/itemid_to_itemiconid.json', 'w') as f:
        json.dump(output, f)