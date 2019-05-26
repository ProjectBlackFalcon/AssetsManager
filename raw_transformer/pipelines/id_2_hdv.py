import json


def generate():
    """
    Lists the auction house at which every item can be bought/sold as a dict of id:auction_house_name (in french)

    :return: None
    """
    with open('output/ItemTypes.json', 'r', encoding="utf8") as f:
        old_item_types = json.load(f)
    item_types = {}
    for item_type in old_item_types:
        item_types[item_type['id']] = item_type

    with open('output/Items.json', 'r', encoding="utf8") as f:
        items = json.load(f)
    with open('output/i18n_fr.json', 'r', encoding="utf8") as f:
        names = json.load(f)['texts']

    name_set = set([])
    runes, consumables, equipment, resources, pets = [], [], [], [], []
    for item in items:
        if item['isSaleable']:
            try:
                if item['typeId'] in [26, 189, 78]:
                    runes.append(item['id'])
                elif item['typeId'] in [79, 172, 184, 25, 42, 74, 166, 93, 33, 200, 76, 75, 188, 173, 13, 69, 49, 165, 86, 12, 43, 112, 100]:
                    consumables.append(item['id'])
                elif item['typeId'] in [1, 9, 2, 114, 3, 11, 82, 4, 17, 10, 16, 169, 199, 5, 22, 19, 7, 177, 8, 21, 81, 151, 6]:
                    equipment.append(item['id'])
                elif item['typeId'] in [164, 55, 178, 105, 109, 57, 36, 71, 167, 107, 88, 65, 181, 195, 53, 59, 63, 37, 41, 39, 179, 98, 183, 64, 66, 103, 56, 34, 46, 68, 48, 35, 60, 51, 52, 15, 47, 108, 119, 111, 182, 62, 96, 95, 58, 180, 54, 104, 110, 70, 152, 40, 106, 50, 185, 38, 84]:
                    resources.append(item['id'])
                elif item['typeId'] in [207, 90, 18, 124, 77, 122, 123, 121, 196, 97, 197, 99, 190, 113]:
                    pets.append(item['id'])
                else:
                    pass
                    name_set.add((names[str(item_types[item['typeId']]['nameId'])], item['typeId']))

            except Exception as e:
                print(e.args[0])
                pass

    print(name_set)

    output = {str(uid): 'Runes' for uid in runes}
    output.update({str(uid): 'Consommables' for uid in consumables})
    output.update({str(uid): 'Ressources' for uid in resources})
    output.update({str(uid): 'Animaux' for uid in pets})
    output.update({str(uid): 'Equipements' for uid in equipment})

    with open('output/Id2Hdv.json', 'w') as f:
        json.dump(output, f)

    output = {
        'Runes': runes,
        'Consommables': consumables,
        'Ressources': resources,
        'Animaux': pets,
        'Equipements': equipment,
    }
    print(len(runes) + len(consumables) + len(resources) + len(pets) + len(equipment))
    with open('definitive_output/hdv_2_id.json', 'w', encoding='utf8') as f:
        json.dump(output, f, ensure_ascii=False)


if __name__ == '__main__':
    generate()
