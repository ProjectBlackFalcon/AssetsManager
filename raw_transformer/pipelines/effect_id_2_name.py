import json


def generate():
    """
    Outputs a json of effect_id:name (in french). The effects are lines in items: damage, stats, etc.

    :return: None
    """
    with open('output/i18n_fr.json', 'r', encoding="utf8") as f:
        names = json.load(f)['texts']

    with open('output/Effects.json', 'r', encoding="utf8") as f:
        old_stats = json.load(f)

    with open('output/Items.json', 'r', encoding="utf8") as f:
        items = json.load(f)

    items_effect_ids = set([])
    for item in items:
        [items_effect_ids.add(thing['effectId']) for thing in item['possibleEffects']]

    stats = {}
    for stat in old_stats:
        stats[stat['id']] = stat

    output = {}
    for stat, value in stats.items():
        try:
            thing = names[str(value['descriptionId'])]

            effect = thing.replace('#1{~1~2 à }#2', '').replace('-#1{~1~2 à -}#2', '').strip()
            effect = '-' + effect if '-#1{~1~2 à -}#2' in thing else effect
            print(stat, effect)
            output[stat] = effect
        except:
            pass

    with open('definitive_output/effect_id_2_name.json', 'w', encoding="utf8") as f:
        json.dump(output, f, ensure_ascii=False)
