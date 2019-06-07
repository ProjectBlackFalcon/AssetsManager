import os
import json
from pydofus.d2o import D2OReader, InvalidD2OFile

# python d2o_unpack.py (all files in input folder)
# folder output: ./output/{all files}

path_output = os.path.join(os.path.dirname(__file__), "../raw_transformer/output/")


def unpack(files_paths='./input/'):
    print(path_output)
    for file_path in files_paths:
        file_name = file_path.split('/')[-1]
        d2p_file = open(file_path, "rb")

        print("D2O Unpacker for " + file_name)

        try:
            d2o_reader = D2OReader(d2p_file)
            d2o_data = d2o_reader.get_objects()

            json_output = open(path_output + file_name.replace("d2o", "json"), "w", encoding='utf8')
            json.dump(d2o_data, json_output, indent=4, ensure_ascii=False)
            json_output.close()

        except InvalidD2OFile:
            pass
        d2p_file.close()
