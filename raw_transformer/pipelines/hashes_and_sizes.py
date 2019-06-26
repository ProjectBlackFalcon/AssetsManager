import hashlib
import json
import os
from math import ceil


def generate_file_md5(path, blocksize=2**20):
    m = hashlib.md5()
    with open(path, "rb") as f:
        while True:
            buf = f.read(blocksize)
            if not buf:
                break
            m.update(buf)
    return m.hexdigest()


def generate(dof_root_dir):
    output = {}
    for root, dirs, files in os.walk(dof_root_dir):
        for file in files:
            file_path = os.path.join(root, file)
            output[file.replace('.', '')] = {
                'md5': generate_file_md5(file_path),
                'size': os.path.getsize(file_path)
            }

    n_splits = ceil(len(json.dumps(output)) / 10000000)
    for i in range(n_splits):
        with open(os.path.abspath(os.path.join(os.path.dirname(__file__), '../definitive_output/hashes_and_sizes_{}.json'.format(i))), 'w', encoding='utf8') as f:
            json.dump(dict(list(output.items())[i * (len(output.keys()) // n_splits): (i + 1) * (len(output.keys()) // n_splits)]), f, ensure_ascii=False)
