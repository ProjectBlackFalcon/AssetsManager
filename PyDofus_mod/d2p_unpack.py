import io, sys, os, json
from pydofus.d2p import D2PReader, InvalidD2PFile
from pydofus.swl import SWLReader, InvalidSWLFile

# python d2p_pack.py (all files in input folder)
# folder output: ./output/{all files}.d2p

path_input = "./input/"
path_output = os.path.join(os.path.dirname(__file__), "./output/")


def unpack(files_paths='./input/', output=os.path.abspath(os.path.join(os.path.dirname(__file__), "../raw_transformer/partially_unpacked_maps/"))):
    path_output = output

    for file_path in files_paths:
        file_name = file_path.split('/')[-1]
        d2p_file = open(file_path, "rb")

        try:
            os.stat(path_output + "/" + file_name[:-4])
        except:
            os.makedirs(path_output + "/" + file_name[:-4])

        print("D2P Unpacker for " + file_name)

        try:
            d2p_reader = D2PReader(d2p_file, False)
            d2p_reader.load()
            for name, specs in d2p_reader.files.items():
                # print("extract file " + file_name + "/" + name)

                try:
                    os.stat(path_output + "/" + file_name[:-4] + "/" + os.path.dirname(name))
                except:
                    os.makedirs(path_output + "/" + file_name[:-4] + "/" + os.path.dirname(name))

                if "swl" in name:
                    pass
                    # This is broken

                    # swl = io.BytesIO(specs["binary"])
                    # swl_reader = SWLReader(swl)
                    #
                    # swf_output = open(path_output + "/" + file_name[:-4] + "/" + name.replace("swl", "swf"), "wb")
                    # json_output = open(path_output + "/" + file_name[:-4] + "/" + name.replace("swl", "json"), "w")
                    #
                    # swf_output.write(swl_reader.SWF)
                    # swl_data = {'version':swl_reader.version, 'frame_rate':swl_reader.frame_rate, 'classes':swl_reader.classes}
                    # json.dump(swl_data, json_output, indent=4)
                    #
                    # swf_output.close()
                    # json_output.close()
                else:
                    file_output = open(path_output + "/" + file_name[:-4] + "/" + name, "wb")
                    file_output.write(specs["binary"])
                    file_output.close()
                pass
        except InvalidD2PFile:
            pass
