import os
import json
import time

import dlm_unpack
from math import ceil


def format_cells(cells):
    # 0 Walkable
    # 1 Void
    # 2 Obstacle
    # 3 change map north
    # 4 change map north east
    # 5 change map east
    # 6 change map south east
    # 7 change map south
    # 8 change map south west
    # 9 change map west
    # 10 change map north west
    map_change_cells = {
        'n': [i for i in range(28)],
        'w': [i for i in range(560) if i % 14 == 0],
        'e': [i for i in range(560) if i % 14 == 13],
        's': [i for i in range(532, 560)]
    }

    output = []
    cell_id = 0
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

                n, s, w, e = False, False, False, False
                if cell['mapChangeData'] and (cell['mapChangeData'] & 1 or (cell_id + 1) % 28 == 0 and cell['mapChangeData'] & 2 or (cell_id + 1) % 28 == 0 and cell['mapChangeData'] & 128):
                    e = True
                if cell['mapChangeData'] and (cell_id == 0 and cell['mapChangeData'] & 8 or cell['mapChangeData'] & 16 or cell_id == 0 and cell['mapChangeData'] & 32):
                    w = True
                if cell['mapChangeData'] and (cell_id < 14 and cell['mapChangeData'] & 32 or cell['mapChangeData'] & 64 or cell_id < 14 and cell['mapChangeData'] & 128):
                    n = True
                if cell['mapChangeData'] and (cell_id >= 546 and cell['mapChangeData'] & 2 or cell['mapChangeData'] & 4 or cell_id >= 546 and cell['mapChangeData'] & 8):
                    s = True


                if n and e:
                    value = 4
                elif n and w:
                    value = 10
                elif s and e:
                    value = 6
                elif s and w:
                    value = 8
                elif n:
                    value = 3
                elif s:
                    value = 7
                elif w:
                    value = 9
                elif e:
                    value = 5

                cells_pack.append(value)
                cell_id += 1
            except:
                # Something strange with cells only having a 'floor' key...
                pass
        output.append(cells_pack)
    return output


def get_interactives(elements):
    formatted_elements = {}
    for cell in elements:
        for element in cell['elements']:
            formatted_elements[element['elementId']] = {'cell': cell['cellId']}
    return formatted_elements


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
        'cells': a 40 lines by 14 columns matrix of int representing the map. 0 is walkable, 1 is void, 2 is a los blocking obstacle, 3 are invalid squares for changing maps,
        'interactives': {elementId: {cell: 0}, }
    }

    :return:
    """
    maps = []
    for root, dir, files in os.walk(os.path.abspath(os.path.join(os.path.dirname(__file__), '../partially_unpacked_maps'))):
        for file in files:
            if file.endswith('.dlm'):
                maps.append(root + '/' + file)

    with open(os.path.abspath(os.path.join(os.path.dirname(__file__), '../output/MapPositions.json')), 'r') as f:
        map_positions = json.load(f)
    map_positions_with_key = {}
    for map in map_positions:
        map_positions_with_key[map['id']] = map

    map_info = []
    elements_info = {}
    for map in maps:
        data = dlm_unpack.unpack_dlm(map)
        map_id, cells, elements = data['mapId'], data['cells'], data['layers'][0]['cells']
        # if map_id == 133889:
        #     i = 0
        #     for cell_pack_id in range(len(cells) // 14):
        #         cells_pack = []
        #         for cell in cells[14 * cell_pack_id: 14 * (cell_pack_id + 1)]:
        #             value = cell['mapChangeData']
        #             cells_pack.append(value)
        #             i += 1
        #         print(cells_pack)
        #     print(format_cells(cells))
        #     raise Exception
        print('Generating data for map {} {};{}'.format(str(maps.index(map)) + '/' + str(len(maps)-1), map_positions_with_key[map_id]['posX'], map_positions_with_key[map_id]['posY']))
        map_data = {
            'id': map_id,
            'coord': '{};{}'.format(map_positions_with_key[map_id]['posX'], map_positions_with_key[map_id]['posY']),
            'subAreaid': map_positions_with_key[map_id]['subAreaId'],
            'worldMap': map_positions_with_key[map_id]['worldMap'],
            'hasPriorityOnWorldMap': map_positions_with_key[map_id]['hasPriorityOnWorldmap'],
            'cells': format_cells(cells)
        }
        map_info.append(map_data)
        elements_info[map_id] = get_interactives(elements)

    # Got to split it for it to fit in mongoDB
    n_splits = ceil(len(json.dumps(map_info)) / 5000000)
    for i in range(n_splits):
        with open(os.path.abspath(os.path.join(os.path.dirname(__file__), '../definitive_output/map_info_{}.json'.format(i))), 'w', encoding='utf8') as f:
            print('Mapinfo_{} contains indices {} through {}'.format(i, i * (len(map_info) // n_splits), (i + 1) * (len(map_info) // n_splits)))
            json.dump(map_info[i * (len(map_info) // n_splits): (i + 1) * (len(map_info) // n_splits)], f, ensure_ascii=False)

    n_splits = ceil(len(json.dumps(elements_info)) / 5000000)
    for i in range(n_splits):
        with open(os.path.abspath(os.path.join(os.path.dirname(__file__), '../definitive_output/elements_info_{}.json'.format(i))), 'w', encoding='utf8') as f:
            json.dump(dict(list(elements_info.items())[i * (len(elements_info.keys()) // n_splits): (i + 1) * (len(elements_info.keys()) // n_splits)]), f, ensure_ascii=False)


if __name__ == '__main__':
    generate_map_info()
