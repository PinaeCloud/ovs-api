# coding=utf-8

import json

def parse_list(data):
    if not data:
        return None

    data = data.strip()
    try:
        return json.loads(data)
    except:
        if data.startswith('[') and data.endswith(']'):
            data = data[1:len(data)-1]
            return [i.strip() for i in data.split(',') if i.strip()]

def parse_dict(data):
    if not data:
        return None
    
    d = {}
    data = data.strip()
    try:
        return json.loads(data)
    except:
        if data.startswith('{') and data.endswith('}'):
            data = data[1:len(data)-1]
            for i in data.split(','):
                if '=' in i:
                    k, v = i.split('=')
                    v = v.strip()
                    if v.startswith('"') and v.endswith('"'):
                        v = v[1:len(v)-1]
                    d[k.strip()] = v
    return d
