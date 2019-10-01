import json
import os
import traceback


def generate():
    """
    Outputs a json of item stats that a modifiable trough FM:
    {
        "% Critique": [115, [7433]],  # [effect_id, [regular rune id]]
        "Prospection": [176, [7451, 10662]]  # [effect_id, [regular rune id, PA rune id]]
    }

    :return: None
    """
    equip_ids = [1, 9, 2, 114, 3, 11, 82, 4, 17, 10, 16, 169, 199, 5, 22, 19, 7, 177, 8, 21, 81, 151, 6]

    with open(os.path.abspath(os.path.join(os.path.dirname(__file__), '../output/Items.json')), 'r', encoding="utf8") as f:
        items = json.load(f)
    with open(os.path.abspath(os.path.join(os.path.dirname(__file__), '../output/i18n_fr.json')), 'r', encoding="utf8") as f:
        names = json.load(f)['texts']
    with open(os.path.abspath(os.path.join(os.path.dirname(__file__), '../static_data/runes_stats.json')), 'r', encoding="utf8") as f:
        # "Stat_name": [weight per point of stat, normal rune weight, pa rune weight, ra rune weight]
        runes = json.load(f)
    with open(os.path.abspath(os.path.join(os.path.dirname(__file__), '../definitive_output/rune_2_id.json')), 'r', encoding="utf8") as f:
        runes_ids = json.load(f)
    with open(os.path.abspath(os.path.join(os.path.dirname(__file__), '../definitive_output/effect_id_2_name.json')), 'r', encoding="utf8") as f:
        effect_id_2_name = json.load(f)

    output = {}
    runes_stats = {}
    for item in items:
        if item['typeId'] in equip_ids:
            try:
                output[item['id']] = {
                    'Level': item['level'],
                    'Name': names[str(item['nameId'])],
                    'Stats': [(effect['effectId'], effect['diceNum'], max(effect['diceNum'], effect['diceSide'])) for effect in item['possibleEffects'] if str(effect['effectId']) in effect_id_2_name.keys() and effect_id_2_name[str(effect['effectId'])] in runes.keys()]
                }
            except Exception:
                print('Caught error')
                print(traceback.format_exc())

        if item['id'] in runes_ids.values():
            try:
                # print(effect_id_2_name[str(item['possibleEffects'][0]['effectId'])])
                if effect_id_2_name[str(item['possibleEffects'][0]['effectId'])] in runes_stats.keys():
                    runes_stats[effect_id_2_name[str(item['possibleEffects'][0]['effectId'])]].append(item['id'])
                else:
                    runes_stats[effect_id_2_name[str(item['possibleEffects'][0]['effectId'])]] = [item['id']]
            except:
                pass

    fmable_stats = dict(set([(effect_id_2_name[str(effect[0])], effect[0]) for item_id, caracs in output.items() for effect in caracs['Stats']]))
    fmable_stats = {stat: (effect_id, runes_stats[stat]) for stat, effect_id in fmable_stats.items()}
    # print(fmable_stats)

    with open(os.path.abspath(os.path.join(os.path.dirname(__file__), '../definitive_output/fmable_stats.json')), 'w', encoding="utf8") as f:
        json.dump(fmable_stats, f, ensure_ascii=False)
