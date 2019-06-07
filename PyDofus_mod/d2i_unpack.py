import sys, json
import os
from pydofus.d2i import D2I, InvalidD2IFile

# python d2i_unpack.py file.d2i
# file output: file.json

path_input = "./input/"
path_output = os.path.join(os.path.dirname(__file__), "./output/")


def unpack(files_paths='./input/'):
    for file_path in files_paths:
        file_name = file_path.split('/')[-1]
        d2i_file = open(file_path, "rb")

        print("D2O Unpacker for " + file_name)

        try:
            d2i_reader = D2I(d2i_file)
            d2i_data = d2i_reader.read()

            json_output = open(path_output + file_name.replace("d2i", "json"), "w", encoding='utf8')
            json.dump(d2i_data, json_output, indent=4, ensure_ascii=False)
            json_output.close()

        except InvalidD2IFile:
            pass
        d2i_file.close()
