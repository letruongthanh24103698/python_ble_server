import json
import sys
from server import server


#with open('req_json.txt') as json_file:
#    req_json=json.load(json_file)

#with open('value_json.txt') as json_file:
#    value_json=json.load(json_file)

#get data from node.js
req_json_str=sys.argv[1]
value_json_str=sys.argv[2]

#parse data from string to json
req_json=json.loads(req_json_str)
value_json=json.loads(value_json_str)

#process data
sv=server(value_json)
data=sv.process(req_json,value_json)
print(data)
del sv
del data
