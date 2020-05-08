import json
import sys
from server import server
from ble import location


with open('req_json.txt') as json_file:
    req_json=json.load(json_file)

with open('value_json.txt') as json_file:
    value_json=json.load(json_file)

#get data from node.js
#req_json_str=sys.argv[1]
#value_json_str=sys.argv[2]

#parse data from string to json
#req_json=json.loads(req_json_str)
#value_json=json.loads(value_json_str)

#process data
sv=server(value_json)
data=sv.process(req_json,value_json)
print(data)
del sv
del data

#ble_location={}
#dis_pathloss={}
#location_1={}
#location_1['lat']=1.34
#location_1['lon']=0.05
#location_1['alt']=0
#ble_location['a']=location_1
#dis_pathloss['a']=3.801

#location_2={}
#location_2['lat']=7.55
#location_2['lon']=11.66
#location_2['alt']=0
#ble_location['b']=location_2
#dis_pathloss['b']=23.773

#location_3={}
#location_3['lat']=1.05
#location_3['lon']=11.66
#location_3['alt']=0
#ble_location['c']=location_3
#dis_pathloss['c']=7.369

#location_4={}
#location_4['lat']=7.55
#location_4['lon']=1.50
#location_4['alt']=0
#ble_location['d']=location_4
#dis_pathloss['d']=22.647

#loc=location(dis_pathloss,ble_location)
#print(loc.estimate())
