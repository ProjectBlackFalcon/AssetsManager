import sys, json
from pydofus.dlm import DLM, InvalidDLMFile

# python dlm_unpack.py file.dlm
# file output: file.json


def unpack_dlm(file):
    dlm_input = open(file, "rb")

    dlm = DLM(dlm_input, "649ae451ca33ec53bbcbcc33becf15f4")
    data = dlm.read()
    dlm_input.close()
    return data

