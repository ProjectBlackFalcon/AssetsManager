import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'PyDofus_mod')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'raw_transformer')))
import argparse
import os

import d2o_unpack
import d2i_unpack
import d2p_unpack
import ele_unpack

from pipelines import named_recipes
from pipelines import id_2_hdv
from pipelines import id_2_name
from pipelines import id_2_type
from pipelines import effect_id_2_name
from pipelines import rune_2_id
from pipelines import equipments
from pipelines import maps_unpacker
from pipelines import itemid_to_itemiconid
from pipelines import fmable_stats
from pipelines import pathfinder_graph

# parser = argparse.ArgumentParser(description='Assets Transformer')
# parser.add_argument('dofusdir', type=str, help='Dofus root directory')
# root = parser.parse_args().dofusdir

root = 'input'
files_paths = {'d2i': [], 'd2o': [], 'd2p': [], 'ele': []}
files = os.walk(root)
for root, dirs, files in files:
    for file in files:
        if file.endswith('d2i'):
            files_paths['d2i'].append(root + '/' + file)
        if file.endswith('d2o'):
            files_paths['d2o'].append(root + '/' + file)
        if file.endswith('d2p'):
            files_paths['d2p'].append(root + '/' + file)
        if file.endswith('ele'):
            files_paths['ele'].append(root + '/' + file)

d2o_unpack.unpack(files_paths=files_paths['d2o'])  # Items, Recipes, Effects...
d2p_unpack.unpack(files_paths=files_paths['d2p'])
d2i_unpack.unpack(files_paths=files_paths['d2i'])  # i18n_fr
ele_unpack.unpack(files_paths=files_paths['ele'])

maps_unpacker.generate_map_info()
pathfinder_graph.generate()
itemid_to_itemiconid.generate()
named_recipes.generate()
id_2_hdv.generate()
id_2_name.generate()
id_2_type.generate()
effect_id_2_name.generate()
rune_2_id.generate()
equipments.generate()
fmable_stats.generate()

'python raw_transformer\assets_transformer.py raw_transformer\input'
