import json
import sys

try:
    with open('config.json', 'r') as jsonfile:
        data = json.load(jsonfile)
except IOError:
    sys.exit('Finalizando Execução')

csv_patch = data['csv_patch'].encode('unicode_escape')
auvo_api_url = data['auvo_api_url']
auvo_api_key = data['auvo_api_key']
auvo_api_token = data['auvo_api_token']
log_enabled = data['log_enabled']
debug_enabled = data['debug_enabled']
log_when = data['log_when']
log_interval = data['log_interval']
log_max_files = data['log_max_files']