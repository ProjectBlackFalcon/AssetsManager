import json
from heapq import *
import os
import uuid
import numpy as np
from math import ceil
import matplotlib.pyplot as plt
from multiprocessing import Pool, cpu_count

import time
from random import randint


def get_edges(cells):
    north = [j for i in zip(cells[0], cells[1]) for j in i]
    south = [j for i in zip(cells[38], cells[39]) for j in i]
    west = [line[0] for line in cells]
    east = [line[-1] for line in cells]
    return {'n': north, 's': south, 'w': west, 'e': east}


def edge_cell_to_map_cell(edge_cell, direction):
    if direction == 'n':
        return edge_cell // 2 if edge_cell % 2 == 0 else edge_cell // 2 + 14
    if direction == 's':
        return edge_cell // 2 + 532 if edge_cell % 2 == 0 else edge_cell // 2 + 546
    if direction == 'w':
        return edge_cell * 14
    if direction == 'e':
        return  edge_cell * 14 + 13


def cells_2_map(cells):
    maps = np.array(cells)
    shape = maps.shape
    flattened = maps.flatten()
    new_base = np.zeros((14 * shape[1] // 14 + 20 * shape[0] // 40 - 1, 14 * shape[1] // 14 + 20 * shape[0] // 40))
    new_base[new_base == 0] = -1
    for i in range(len(flattened)):
        coord = i % shape[1] + int((i // shape[1]) / 2 + 0.5), (shape[1] - 1 - i % shape[1] + int((i // shape[1]) / 2))
        new_base[coord[1]][coord[0]] = flattened[i]
    return new_base[:]


def cell_2_coord(cell):
    return (14 - 1 - cell % 14 + int((cell // 14) / 2)), cell % 14 + int((cell // 14) / 2 + 0.5)


def path_exists_between_nodes(map, node1, node2):
    start_pos = cell_2_coord(node1['cell'])
    goal_pos = cell_2_coord(node2['cell'])

    neighbors = [(1, 1), (-1, -1), (1, -1), (-1, 1), (1, 0), (0, 1), (-1, 0), (0, -1)]

    close_set = set()
    came_from = {}
    gscore = {start_pos: 0}
    fscore = {start_pos: (goal_pos[0] - start_pos[0]) ** 2 + (goal_pos[1] - start_pos[1]) ** 2}
    oheap = []

    heappush(oheap, (fscore[start_pos], start_pos))

    while oheap:

        current = heappop(oheap)[1]

        if current == goal_pos:
            data = []
            while current in came_from:
                data.append(current)
                current = came_from[current]
            return True

        close_set.add(current)
        for i, j in neighbors:
            neighbor = current[0] + i, current[1] + j
            tentative_g_score = gscore[current] + (neighbor[0] - current[0]) ** 2 + (neighbor[1] - current[1]) ** 2
            if 0 <= neighbor[0] < map.shape[0]:
                if 0 <= neighbor[1] < map.shape[1]:
                    if map[neighbor[0]][neighbor[1]] in [-1, 1, 2]:
                        continue
                else:
                    # array bound y walls
                    continue
            else:
                # array bound x walls
                continue

            if neighbor in close_set and tentative_g_score >= gscore.get(neighbor, 0):
                continue

            if tentative_g_score < gscore.get(neighbor, 0) or neighbor not in [i[1] for i in oheap]:
                came_from[neighbor] = current
                gscore[neighbor] = tentative_g_score
                fscore[neighbor] = tentative_g_score + (goal_pos[0] - neighbor[0]) ** 2 + (goal_pos[1] - neighbor[1]) ** 2
                heappush(oheap, (fscore[neighbor], neighbor))

    return False


def get_map_nodes(map_data):
    edges = get_edges(map_data['cells'])
    # for edge in edges.items():
    #     print(edge)
    nodes = {}
    for direction, edge in edges.items():
        ok_cells = [[3, 4, 10], [6, 7, 8], [4, 5, 6], [8, 9, 10]][['n', 's', 'e', 'w'].index(direction)]
        # print(direction, edge)
        node_start = None
        edge_id = 0
        for i in range(len(edge)):
            if node_start is None and edge[i] in ok_cells:
                node_start = i
            if node_start is not None and (edge[i] not in ok_cells or i == len(edge) - 1):
                nodes[str(uuid.uuid4())] = {
                    'map_id': map_data['id'],
                    'edge_id': edge_id,
                    'coord': map_data['coord'],
                    'center': int((i - node_start - 1) // 2 + node_start),
                    'cell': edge_cell_to_map_cell(int((i - node_start - 1) / 2 + node_start), direction),
                    'direction': direction,
                    'neighbours': [],
                    'not_neighbours': []
                }
                edge_id += 1
                node_start = None
    return nodes


def add_intra_neighbours(map_nodes, cells):
    map = cells_2_map(cells)
    for start_node_id, start_node in map_nodes.items():
        for end_node_id, end_node in map_nodes.items():
            if end_node_id not in start_node['neighbours'] and end_node_id not in start_node['not_neighbours'] and start_node_id != end_node_id:
                if path_exists_between_nodes(map, start_node, end_node):
                    start_node['neighbours'].append(end_node_id)
                    end_node['neighbours'].append(start_node_id)
                else:
                    start_node['not_neighbours'].append(end_node_id)
                    end_node['not_neighbours'].append(start_node_id)


def add_extra_neighbours(current_nodes, neighbour_nodes):
    if len(current_nodes):
        pairs = dict(zip(list(current_nodes.keys()), list(neighbour_nodes.keys())))
        for current_node_id, neighbour_node_id in pairs.items():
            if current_node_id not in neighbour_nodes[neighbour_node_id]['neighbours']:
                current_nodes[current_node_id]['neighbours'].append(neighbour_node_id)
                neighbour_nodes[neighbour_node_id]['neighbours'].append(current_node_id)


def fetch_map(map_info, coord, worldmap):
    maps = []
    for map in map_info:
        if map['coord'] == coord and map['worldMap'] == worldmap:
            maps.append(map)
    if len(maps) == 1 and maps[0] is not None:
        return maps[0]
    elif len(maps) > 1:
        for map in maps:
            if map['hasPriorityOnWorldMap']:
                return map


def delete_node(node_id, graph, coord_2_nodes):
    # print('Removing {} from graph'.format(graph[node_id]))
    del graph[node_id]
    for node in graph.values():
        if node_id in node['neighbours']:
            node['neighbours'].remove(node_id)
        if node_id in node['not_neighbours']:
            node['not_neighbours'].remove(node_id)

    for node_id_list in coord_2_nodes.values():
        if node_id in node_id_list:
            node_id_list.remove(node_id)


def trim_edge(current_nodes, neighbour_nodes, graph, coord_2_nodes):
    if len(current_nodes) > len(neighbour_nodes):
        coords = current_nodes[list(current_nodes.keys())[0]]['coord']
        direction = current_nodes[list(current_nodes.keys())[0]]['direction']

        if len(neighbour_nodes) == 0:
            for node_id in current_nodes.keys():
                delete_node(node_id, graph, coord_2_nodes)
        else:
            max_tries, tries = 100, 0
            while len(current_nodes) > len(neighbour_nodes) and tries < max_tries:
                tries += 1
                node_id_1 = list(current_nodes.keys())[randint(0, len(list(current_nodes.keys())) - 1)]
                node_id_2 = list(current_nodes.keys())[randint(0, len(list(current_nodes.keys())) - 1)]
                if node_id_1 != node_id_2 and node_id_1 in graph[node_id_2]['neighbours']:
                    delete_node(node_id_1, graph, coord_2_nodes)
                    del current_nodes[node_id_1]
            if tries == max_tries:
                raise Exception('Unable to make map {} bijective with {} neighbour'.format(coords, direction))
                pass


def create_map_nodes(map_data):
    if map_data is not None:
        nodes = get_map_nodes(map_data)
        add_intra_neighbours(nodes, map_data['cells'])
        return nodes
    return {}


def build_graph(map_info, worldmap, bbox):
    start = time.time()
    x_min, y_min, x_max, y_max = bbox
    coord_2_nodes, graph = {}, {}

    # Building initial graph without inter-map connections
    coords = [(x, y) for x in range(x_min, x_max + 1) for y in range(y_min, y_max + 1)]

    with Pool(cpu_count() - 1) as p:
        nodes_list = p.map(create_map_nodes, [(fetch_map(map_info, '{};{}'.format(coord[0], coord[1]), worldmap)) for coord in coords])
    graph = nodes_list[0]
    for node in nodes_list[1:]:
        graph.update(node)

    # Trimming graph

    # Manual part (some nodes just don't make sense...)
    nodes_removed_manually = {
        '-15;10': [195],
        '13;27': [111]
    }
    nodes_to_delete = []
    for key, node in graph.items():
        if node['coord'] in nodes_removed_manually.keys():
            if node['cell'] in nodes_removed_manually[node['coord']]:
                nodes_to_delete.append(key)
    for node_id in nodes_to_delete:
        delete_node(node_id, graph, coord_2_nodes)


    # Automated part
    for x in range(x_min, x_max + 1):
        for y in range(y_min, y_max + 1):
            if '{};{}'.format(x, y) in coord_2_nodes.keys():
                # North
                if '{};{}'.format(x, y - 1) in coord_2_nodes.keys():
                    current_map_nodes_ids = coord_2_nodes['{};{}'.format(x, y)]
                    current_nodes = {node_id: graph[node_id] for node_id in current_map_nodes_ids if graph[node_id]['direction'] == 'n'}

                    neighbour_map_nodes_ids = coord_2_nodes['{};{}'.format(x, y - 1)]
                    neighbour_nodes = {node_id: graph[node_id] for node_id in neighbour_map_nodes_ids if graph[node_id]['direction'] == 's'}

                    trim_edge(current_nodes, neighbour_nodes, graph, coord_2_nodes)

                # South
                if '{};{}'.format(x, y + 1) in coord_2_nodes.keys():
                    current_map_nodes_ids = coord_2_nodes['{};{}'.format(x, y)]
                    current_nodes = {node_id: graph[node_id] for node_id in current_map_nodes_ids if graph[node_id]['direction'] == 's'}

                    neighbour_map_nodes_ids = coord_2_nodes['{};{}'.format(x, y + 1)]
                    neighbour_nodes = {node_id: graph[node_id] for node_id in neighbour_map_nodes_ids if graph[node_id]['direction'] == 'n'}

                    trim_edge(current_nodes, neighbour_nodes, graph, coord_2_nodes)

                # West
                if '{};{}'.format(x - 1, y) in coord_2_nodes.keys():
                    current_map_nodes_ids = coord_2_nodes['{};{}'.format(x, y)]
                    current_nodes = {node_id: graph[node_id] for node_id in current_map_nodes_ids if graph[node_id]['direction'] == 'w'}

                    neighbour_map_nodes_ids = coord_2_nodes['{};{}'.format(x - 1, y)]
                    neighbour_nodes = {node_id: graph[node_id] for node_id in neighbour_map_nodes_ids if graph[node_id]['direction'] == 'e'}

                    trim_edge(current_nodes, neighbour_nodes, graph, coord_2_nodes)

                # East
                if '{};{}'.format(x + 1, y) in coord_2_nodes.keys():
                    current_map_nodes_ids = coord_2_nodes['{};{}'.format(x, y)]
                    current_nodes = {node_id: graph[node_id] for node_id in current_map_nodes_ids if graph[node_id]['direction'] == 'e'}

                    neighbour_map_nodes_ids = coord_2_nodes['{};{}'.format(x + 1, y)]
                    neighbour_nodes = {node_id: graph[node_id] for node_id in neighbour_map_nodes_ids if graph[node_id]['direction'] == 'w'}

                    trim_edge(current_nodes, neighbour_nodes, graph, coord_2_nodes)

    # Building inter-map connections
    for x in range(x_min, x_max + 1):
        for y in range(y_min, y_max + 1):
            if '{};{}'.format(x, y) in coord_2_nodes.keys():
                # North
                if '{};{}'.format(x ,y - 1) in coord_2_nodes.keys():
                    current_map_nodes_ids = coord_2_nodes['{};{}'.format(x, y)]
                    current_nodes = {node_id: graph[node_id] for node_id in current_map_nodes_ids if graph[node_id]['direction'] == 'n'}

                    neighbour_map_nodes_ids = coord_2_nodes['{};{}'.format(x, y - 1)]
                    neighbour_nodes = {node_id: graph[node_id] for node_id in neighbour_map_nodes_ids if graph[node_id]['direction'] == 's'}

                    add_extra_neighbours(current_nodes, neighbour_nodes)

                # South
                if '{};{}'.format(x, y + 1) in coord_2_nodes.keys():
                    current_map_nodes_ids = coord_2_nodes['{};{}'.format(x, y)]
                    current_nodes = {node_id: graph[node_id] for node_id in current_map_nodes_ids if graph[node_id]['direction'] == 's'}

                    neighbour_map_nodes_ids = coord_2_nodes['{};{}'.format(x, y + 1)]
                    neighbour_nodes = {node_id: graph[node_id] for node_id in neighbour_map_nodes_ids if graph[node_id]['direction'] == 'n'}

                    add_extra_neighbours(current_nodes, neighbour_nodes)
                # West
                if '{};{}'.format(x - 1, y) in coord_2_nodes.keys():
                    current_map_nodes_ids = coord_2_nodes['{};{}'.format(x, y)]
                    current_nodes = {node_id: graph[node_id] for node_id in current_map_nodes_ids if graph[node_id]['direction'] == 'w'}

                    neighbour_map_nodes_ids = coord_2_nodes['{};{}'.format(x - 1, y)]
                    neighbour_nodes = {node_id: graph[node_id] for node_id in neighbour_map_nodes_ids if graph[node_id]['direction'] == 'e'}

                    add_extra_neighbours(current_nodes, neighbour_nodes)
                # East
                if '{};{}'.format(x + 1, y) in coord_2_nodes.keys():
                    current_map_nodes_ids = coord_2_nodes['{};{}'.format(x, y)]
                    current_nodes = {node_id: graph[node_id] for node_id in current_map_nodes_ids if graph[node_id]['direction'] == 'e'}

                    neighbour_map_nodes_ids = coord_2_nodes['{};{}'.format(x + 1, y)]
                    neighbour_nodes = {node_id: graph[node_id] for node_id in neighbour_map_nodes_ids if graph[node_id]['direction'] == 'w'}

                    add_extra_neighbours(current_nodes, neighbour_nodes)

    # print(json.dumps(graph))
    print(len(graph.keys()), 'maps factorized in', time.time() - start)
    print('Graph has {} nodes'.format(len(graph)))
    return graph


def to_image(map, nodes, coords, scaling_factor):
    for y in range(len(map)):
        for x in range(len(map[0])):
            if map[y, x] > 2:
                map[y, x] = 3
    for node in nodes.values():
        if node['coord'] == coords:
            map[cell_2_coord(node['cell'])] = 4
    big_map = np.kron(map, np.ones((scaling_factor, scaling_factor))).astype(int)
    plt.imshow(big_map)
    plt.show()


def generate():
    print('Generating pathfinder graph')
    assets = os.listdir(os.path.join(os.path.dirname(__file__), '../definitive_output'))
    map_info_files = [asset for asset in assets if asset.startswith('map_info')]

    map_info = []
    for file in map_info_files:
        with open(os.path.join(os.path.dirname(__file__), '../definitive_output', file), 'r', encoding='utf8') as f:
            map_info += json.load(f)

    graph = build_graph(map_info, 1, (-40, -67, 27, 51))
    graph.update(build_graph(map_info, 2, (-3, -6, 5, 1)))
    graph.update(build_graph(map_info, -1, (-40, -67, 27, 51)))

    n_splits = ceil(len(json.dumps(graph)) / 5000000)
    for i in range(n_splits):
        with open(os.path.abspath(os.path.join(os.path.dirname(__file__), '../definitive_output/pathfinder_graph_{}.json'.format(i))), 'w', encoding='utf8') as f:
            json.dump(dict(list(graph.items())[i * (len(graph.keys()) // n_splits): (i + 1) * (len(graph.keys()) // n_splits)]), f, ensure_ascii=False)
    print('Pathfinder graph generated')
    return graph


if __name__ == '__main__':
    map_info = []
    for i in range(5):
        with open('../definitive_output/map_info_{}.json'.format(i), 'r') as f:
            map_info += json.load(f)
    graph = {}
    for i in range(2):
        with open('../definitive_output/pathfinder_graph_{}.json'.format(i), 'r') as f:
            graph.update(json.load(f))

    graph = generate()
    pos = '13;27'
    for key, node in graph.items():
        if node['coord'] == pos:
            print(key, node)
    map = cells_2_map(fetch_map(map_info, pos, 1)['cells'])
    to_image(map, graph, pos, 1)


