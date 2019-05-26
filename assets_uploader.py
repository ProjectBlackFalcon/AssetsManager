import json
import pymongo
import mongo
import os
import hashlib


def generate_file_md5(path, blocksize=2**20):
    m = hashlib.md5()
    with open(path, "rb" ) as f:
        while True:
            buf = f.read(blocksize)
            if not buf:
                break
            m.update(buf)
    return m.hexdigest()


client = pymongo.MongoClient(host=mongo.host, port=mongo.port, username=mongo.username, password=mongo.password)
assets_path = ['raw_transformer/definitive_output/' + file for file in os.listdir('raw_transformer/definitive_output/')] + \
              ['raw_transformer/static_data/' + file for file in os.listdir('raw_transformer/static_data/')]

for file_path in assets_path:
    if file_path.endswith('.json'):
        file = file_path.split('/')[-1]
        print(file)
        with open(file_path, 'r', encoding='utf8') as f:
            data = json.load(f)


        checksum = generate_file_md5(file_path)
        existing_version = client.blackfalcon.files.find_one({"filename": file.replace('.json', '')})
        if existing_version is not None:
            if existing_version['checksum_md5'] == checksum:
                print('{} is up to date'.format(file))
            else:
                print('Updating {}'.format(file))
                client.blackfalcon.files.find_one_and_replace({"filename": file.replace('.json', '')}, {'filename': file.replace('.json', ''), 'payload': data, 'checksum_md5': checksum})
        else:
            print('Creating {}'.format(file))
            client.blackfalcon.files.insert_one({'filename': file.replace('.json', ''), 'payload': data, 'checksum_md5': checksum})