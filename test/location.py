import json
import sys
from ble import location

#with open('req_json.txt') as json_file:
#    dis_json=json.load(json_file)

#with open('value_json.txt') as json_file:
#    loc_json=json.load(json_file)

#get data from node.js
dis_json_str=sys.argv[1]
loc_json_str=sys.argv[2]

#parse data from string to json
dis_json=json.loads(dis_json_str)
loc_json=json.loads(loc_json_str)

loc=location(dis_json,loc_json)
print(loc.estimate())


