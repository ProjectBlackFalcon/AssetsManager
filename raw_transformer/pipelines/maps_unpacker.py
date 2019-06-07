import os
import json
import dlm_unpack
from math import ceil


def format_cells(cells):
    # 0 Walkable
    # 1 Void
    # 2 Obstacle
    # 3 invalid for change map
    map_change_cells = [i for i in range(28)] + [i for i in range(560) if i % 14 == 0] + [i for i in range(560) if i % 14 == 13] + [i for i in range(532, 560)]

    output = []
    i = 0
    for cell_pack_id in range(len(cells) // 14):
        cells_pack = []
        for cell in cells[14 * cell_pack_id: 14 * (cell_pack_id + 1)]:
            try:
                if cell['mov']:
                    value = 0
                else:
                    value = 1
                if not cell['los']:
                    value = 2

                if i in map_change_cells:
                    value = 0 if cell['mapChangeData'] else 3

                cells_pack.append(value)
                i += 1
            except:
                # Something strange with cells only having a 'floor' key...
                pass
        output.append(cells_pack)
    return output


def get_interactives(elements):
    with open('static_data/interactives.json', 'r') as f:
        interactives = json.load(f)
    for cell in elements:
        for element in cell['elements']:
            pass


def generate_map_info():
    """
    Outputs a list of maps characteristics. As this list is too big to fit in mongo, we split it into multiple map_info_n.json

    The map characteristics are:
    {
        'id': map_id,
        'coord': 'x;y',
        'subAreaid': I'm not sure we even use this,
        'worldMap': As an int. 1 is the normal world, the others I don't remember right now,
        'hasPriorityOnWorldMap': The maps you want usually have this set to 'True',
        'cells': a 40 lines by 14 columns matrix of int representing the map. 0 is walkable, 1 is void, 2 is a los blocking obstacle, 3 are invalid squares for changing maps.
    }

    :return:
    """
    maps = []
    for root, dir, files in os.walk('partially_unpacked_maps'):
        for file in files:
            maps.append(root + '/' + file)

    with open('output/MapPositions.json', 'r') as f:
        map_positions = json.load(f)
    map_positions_with_key = {}
    for map in map_positions:
        map_positions_with_key[map['id']] = map

    map_info = []
    for map in maps:
        data = dlm_unpack.unpack_dlm(map)
        map_id, cells, elements = data['mapId'], data['cells'], data['layers'][0]['cells']
        print('Generating data for map {} {};{}'.format(str(maps.index(map)) + '/' + str(len(maps)-1), map_positions_with_key[map_id]['posX'], map_positions_with_key[map_id]['posY']))
        map_data = {
            'id': map_id,
            'coord': '{};{}'.format(map_positions_with_key[map_id]['posX'], map_positions_with_key[map_id]['posY']),
            'subAreaid': map_positions_with_key[map_id]['subAreaId'],
            'worldMap': map_positions_with_key[map_id]['worldMap'],
            'hasPriorityOnWorldMap': map_positions_with_key[map_id]['hasPriorityOnWorldmap'],
            'cells': format_cells(cells),
            'interactives': get_interactives(elements)
        }
        map_info.append(map_data)

    # Got to split it for it to fit in mongoDB
    n_splits = ceil(len(json.dumps(map_info)) / 10000000)
    for i in range(n_splits):
        with open('definitive_output/map_info_{}.json'.format(i), 'w', encoding='utf8') as f:
            json.dump(map_info[i * (len(data) // n_splits): (i + 1) * (len(data) // n_splits)], f, ensure_ascii=False)
