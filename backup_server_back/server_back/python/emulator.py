from bson import json_util
from bson.codec_options import CodecOptions
import pytz
import pymongo
import json
from datetime import datetime
from process import process
from location import location_

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["iFactory"]
mycol = mydb["rtlsbletest"]
colRes = mydb['result1']
colRes.delete_many({})
result={}

with open('init.txt') as json_file:
    init_json=json.load(json_file)
cursor=mycol.find({},{"_id":0,"createtime":0},no_cursor_timeout=True)
cnt=0
for data in cursor:
    x=data['data']
    with open('process_req.txt','w') as json_file:
        json.dump(x,json_file)
    with open('process_value.txt','w') as json_file:
        json.dump(init_json,json_file)
    tmp=json.loads(process())
    init_json=tmp['json'][0]
    if x['name']=='tag_home' and cnt>500:
        with open('location_req.txt','w') as json_file:
            json.dump(tmp['json'][1],json_file)
        with open('location_value.txt','w') as json_file:
            json.dump(tmp['json'][2],json_file)
        with open('location_delta.txt','w') as json_file:
            json.dump(tmp['json'][3],json_file)
        delta=tmp['json'][3]
        tmp=json.loads(location_())
        #print(tmp)
        init_json['Tag']['location']=tmp.copy()
        temp=tmp.copy()
        temp['lat']=temp['lat']/delta['lat']
        temp['lon']=temp['lon']/delta['lon']
        print(temp)
    result['rssi_mean']=init_json.copy()
    result['createtime']=datetime.utcnow()
    res=result.copy()
    colRes.insert(res)
    cnt=cnt+1


