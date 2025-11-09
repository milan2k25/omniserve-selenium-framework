import json

def fetch_config(path):
    '''
    Params 
        path [string] : Location of config file . 
    '''
    with open(path,) as config:
        return json.load(config)