import json
import sys
from ble import location

def location_():
    with open('location_tag.kal.txt') as json_file:
        tag_json=json.load(json_file)

    with open('location_pathloss.kal.txt') as json_file:
        pathloss_json=json.load(json_file)
        
    with open('location_delta.txt') as json_file:
        delta_json=json.load(json_file)

    with open('location_loc.txt') as json_file:
        loc_json=json.load(json_file)

    with open('location_calib.txt') as json_file:
        calib_json=json.load(json_file)

    with open('location_pathloss.loc.txt') as json_file:
        pathloss_loc_json=json.load(json_file)

    with open('location_tag.loc.txt') as json_file:
        tag_loc_json=json.load(json_file)

    with open('location_R1m.txt') as json_file:
        R1m_json=json.load(json_file)

    with open('location_angle.ble.txt') as json_file:
        angle_ble_json=json.load(json_file)
        
    #get data from node.js
    #dis_json_str=sys.argv[1]
    #loc_json_str=sys.argv[2]
    #delta_json_str=sys.argv[3]

    #parse data from string to json
    #dis_json=json.loads(dis_json_str)
    #loc_json=json.loads(loc_json_str)
    #delta_json=json.loads(delta_json_str)

    loc=location(tag_json, pathloss_json, loc_json, delta_json, calib_json, pathloss_loc_json, tag_loc_json, angle_ble_json, R1m_json)
    tmp=loc.estimate()
    return tmp


