import json
import sys
from ble import location

def location_():
    with open('location_req.txt') as json_file:
        dis_json=json.load(json_file)

    with open('location_value.txt') as json_file:
        loc_json=json.load(json_file)
        
    with open('location_delta.txt') as json_file:
        delta_json=json.load(json_file)
        
    #get data from node.js
    #dis_json_str=sys.argv[1]
    #loc_json_str=sys.argv[2]
    #delta_json_str=sys.argv[3]

    #parse data from string to json
    #dis_json=json.loads(dis_json_str)
    #loc_json=json.loads(loc_json_str)
    #delta_json=json.loads(delta_json_str)

    loc=location(dis_json,loc_json,delta_json)
    tmp=loc.estimate()
    return tmp


