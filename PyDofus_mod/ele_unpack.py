import sys, json
from pydofus.ele import ELE, InvalidELEFile


def unpack_ele(file):
    with open(file, "rb") as f:
        ele = ELE(f)
        data = ele.read()

    data_stripped = {}
    for element_id, values in data['elements_map'].items():
        if dict(values)['type'] == 0:
            data_stripped[element_id] = dict(values)['gfx_id']

    with open('elem2gfx.json', "w") as f:
        json.dump(data_stripped, f, indent=2)
