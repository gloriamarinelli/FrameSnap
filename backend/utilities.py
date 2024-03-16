import json
from datetime import datetime

def get_timestamp(item):
    return datetime.strptime(item[1], '%Y-%m-%d %H:%M:%S')

def serialize_paints(paints_list):
    return json.dumps([{
        'id': paint.id,
        'paint': paint.paint,
        'paint_name': paint.paint_name,
        'paint_year': paint.paint_year
    } for paint in paints_list])