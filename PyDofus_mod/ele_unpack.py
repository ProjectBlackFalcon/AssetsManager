import sys, json
from pydofus.ele import ELE, InvalidELEFile


def unpack(files_paths):
    for file_path in files_paths:
        with open(file_path, "rb") as f:
            ele = ELE(f)
            data = ele.read()

        with open('output/elements.json', "w") as f:
            json.dump(data, f, indent=2)


if __name__ == '__main__':
    import os
    print(os.getcwd())
    unpack(['../raw_transformer/input/elements.ele'])
