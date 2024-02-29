import json
from datetime import datetime

def get_timestamp(item):
    return datetime.strptime(item[1], '%Y-%m-%d %H:%M:%S')

def serialize_shirts(shirts_list):
    return json.dumps([{
        'id': shirt.id,
        'shirt': shirt.shirt,
        'shirt_name': shirt.shirt_name
    } for shirt in shirts_list])