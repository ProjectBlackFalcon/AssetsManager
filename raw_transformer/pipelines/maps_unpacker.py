import os
import json
import time
from multiprocessing import Pool, cpu_count

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


def format_cell_for_dofus_pf(cells):
    output = []
    for cell in cells:
        output.append([
            cell['mov'],
            cell['nonWalkableDuringFight'],
            cell['floor'],
            cell['moveZone'],
            cell['los'],
            cell['speed'],
        ])
    return output


def get_interactives(elements):
    formatted_elements = {}
    for cell in elements:
        for element in cell['elements']:
            formatted_elements[element['elementId']] = {'cell': cell['cellId']}
    return formatted_elements


def is_using_new_movement_system(cells):
    using = False
    for cell in cells:
        if cell['moveZone']:
            using = True
            break
    return using


def generate_single_map_data(map_path, map_positions_with_key):
    data = dlm_unpack.unpack_dlm(map_path)
    map_id, cells, elements = str(int(data['mapId'])), data['cells'], data['layers'][0]['cells']
    map_data = {
        'id': int(map_id),
        'coord': '{};{}'.format(map_positions_with_key[map_id]['posX'], map_positions_with_key[map_id]['posY']),
        'subAreaid': map_positions_with_key[map_id]['subAreaId'],
        'worldMap': map_positions_with_key[map_id]['worldMap'],
        'hasPriorityOnWorldMap': map_positions_with_key[map_id]['hasPriorityOnWorldmap'],
        'rawCells': format_cell_for_dofus_pf(cells),
        'cells': format_cells(cells),
        'isUsingNewMovementSystem': is_using_new_movement_system(cells)
    }
    interactives = get_interactives(elements)
    return map_data, interactives


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
    print('Generating map info')
    start = time.time()
    maps = []
    with open(os.path.abspath(os.path.join(os.path.dirname(__file__), '../output/MapPositions.json')), 'r') as f:
        map_positions = json.load(f)
    map_positions_with_key = {}
    for map in map_positions:
        if -39 <= map['posX'] <= 24 and -65 <= map['posY'] <= 48:
            map_positions_with_key[str(int(map['id']))] = map

    for root, dir, files in os.walk(os.path.abspath(os.path.join(os.path.dirname(__file__), '../partially_unpacked_maps'))):
        for file in files:
            if file.endswith('.dlm') and 'maps' in root and os.path.basename(file).replace('.dlm', '') in map_positions_with_key.keys():
                maps.append(root + '/' + file)

    map_info = []
    elements_info = {}
    with Pool(cpu_count() - 1) as p:
        results_list = p.starmap(generate_single_map_data, [(map, map_positions_with_key) for map in maps])
    for map_data, interactives in results_list:
        map_info.append(map_data)
        elements_info[map_data['id']] = interactives

    # Got to split it for it to fit in mongoDB
    size = len(json.dumps(map_info[0])) * len(map_info)
    n_splits = ceil(size / 10000000)
    for i in range(n_splits):
        with open(os.path.abspath(os.path.join(os.path.dirname(__file__), '../definitive_output/map_info_{}.json'.format(i))), 'w', encoding='utf8') as f:
            print('Mapinfo_{} contains indices {} through {}'.format(i, i * (len(map_info) // n_splits), (i + 1) * (len(map_info) // n_splits)))
            json.dump(map_info[i * (len(map_info) // n_splits): (i + 1) * (len(map_info) // n_splits)], f, ensure_ascii=False)

    n_splits = ceil(len(str(elements_info)) / 10000000)
    for i in range(n_splits):
        with open(os.path.abspath(os.path.join(os.path.dirname(__file__), '../definitive_output/elements_info_{}.json'.format(i))), 'w', encoding='utf8') as f:
            json.dump(dict(list(elements_info.items())[i * (len(elements_info.keys()) // n_splits): (i + 1) * (len(elements_info.keys()) // n_splits)]), f, ensure_ascii=False)
    print('Mapinfo generation done in {}s'.format(round(time.time() - start)))


if __name__ == '__main__':
    start = time.time()
    generate_map_info()
    print('Done in ', time.time() - start)
