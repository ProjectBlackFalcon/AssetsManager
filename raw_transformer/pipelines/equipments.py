import json
import os
import traceback


def generate():
    """
    Outputs a json of items characteristics such as:
    {
        "180": {
            "Level": 105,
            "Stats": [[111, 1, 1], [128, 1, 1], [124, 21, 40], [126, 21, 40]],
            "Name": "La Baguette des Limbes"
        }
    }

    Stats are [effect_id, min, max]
    :return: None
    """

    # TODO put that in static_data
    equip_ids = [1, 9, 2, 114, 3, 11, 82, 4, 17, 10, 16, 169, 199, 5, 22, 19, 7, 177, 8, 21, 81, 151, 6]

    with open(os.path.abspath(os.path.join(os.path.dirname(__file__), '../output/Items.json')), 'r', encoding="utf8") as f:
        items = json.load(f)
    with open(os.path.abspath(os.path.join(os.path.dirname(__file__), '../output/i18n_fr.json')), 'r', encoding="utf8") as f:
        names = json.load(f)['texts']
    with open(os.path.abspath(os.path.join(os.path.dirname(__file__), '../static_data/runes_stats.json')), 'r', encoding="utf8") as f:
        runes = json.load(f)
    with open(os.path.abspath(os.path.join(os.path.dirname(__file__), '../definitive_output/effect_id_2_name.json')), 'r', encoding="utf8") as f:
        effect_id_2_name = json.load(f)

    output = {}
    for item in items:
        if item['typeId'] in equip_ids:
            try:
                output[item['id']] = {
                    'Level': item['level'],
                    'Name': names[str(item['nameId'])],
                    'Stats': [(effect['effectId'], effect['diceNum'], max(effect['diceNum'], effect['diceSide'])) for effect in item['possibleEffects'] if str(effect['effectId']) in effect_id_2_name.keys() and effect_id_2_name[str(effect['effectId'])] in runes.keys()]
                }
            except Exception:
                print(traceback.format_exc())

    with open(os.path.abspath(os.path.join(os.path.dirname(__file__), '../definitive_output/equipments.json')), 'w', encoding="utf8") as f:
        json.dump(output, f, ensure_ascii=False)
