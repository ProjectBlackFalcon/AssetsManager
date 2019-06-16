import json
import os


def generate():
    with open(os.path.abspath(os.path.join(os.path.dirname(__file__), '../output/Servers.json')), 'r') as f:
        servers = json.load(f)

    with open(os.path.abspath(os.path.join(os.path.dirname(__file__), '../output/i18n_fr.json')), 'r', encoding='utf8') as f:
        texts = json.load(f)['texts']

    output = {}
    for server in servers:
        try:
            output[texts[str(server['nameId'])].replace('.', '')] = server['id']
        except:
            print('Not found', server['nameId'])

    with open(os.path.abspath(os.path.join(os.path.dirname(__file__), '../definitive_output/server_2_id.json')), 'w', encoding='utf8') as f:
        json.dump(output, f, ensure_ascii=False)
