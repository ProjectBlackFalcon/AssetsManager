#!/bin/bash

cd /home/docker/AssetsManager
git reset --hard HEAD
git pull
python3.7 raw_transformer/assets_transformer.py $1
python3.7 raw_transformer/assets_uploader.py
cd /home/docker