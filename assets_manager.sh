#!/bin/bash

cd /home/docker/AssetsManager
git reset --hard HEAD
git pull
python3.7 raw_transformer/assets_transformer.py /home/docker/.config/Ankama/zaap/dofus
python3.7 assets_uploader.py
cd /home/docker