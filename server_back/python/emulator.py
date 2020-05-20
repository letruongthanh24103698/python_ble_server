from bson import json_util
from bson.codec_options import CodecOptions
import pytz
import pymongo
import json
from datetime import datetime
from process import process
from location import location_

restart=0
amount=0

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["iFactory"]
mycol = mydb["rtlsbletest"]
colRes = mydb['result']
colResOne=mydb['rtls']
init_json={}

if restart==1:
    colRes.delete_many({})
    with open('init.txt') as json_file:
        init_json=json.load(json_file)
else:
    tmp=colRes.find()
    amount=tmp.count()
    tmp.close()
    tmp=colResOne.find_one({},{'_id':0})
    init_json=tmp

result={}
count=0


cursor=mycol.find({},{'_id':0},no_cursor_timeout=True)
cnt=0
for data in cursor:
    #print(data)
    count=count+1

    if count>amount:
        x=data['data']
        with open('process_req.txt','w') as json_file:
            json.dump(x,json_file)
        with open('process_value.txt','w') as json_file:
            json.dump(init_json,json_file)
        tmp=json.loads(process())
        init_json=tmp['json'][0].copy()
        if x['name']=='tag_home' and cnt>50:
            with open('location_tag.kal.txt','w') as json_file:
                json.dump(tmp['json'][1],json_file)
            with open('location_pathloss.kal.txt','w') as json_file:
                json.dump(tmp['json'][2],json_file)
            with open('location_loc.txt','w') as json_file:
                json.dump(tmp['json'][3],json_file)
            with open('location_delta.txt','w') as json_file:
                json.dump(tmp['json'][4],json_file)
            with open('location_calib.txt','w') as json_file:
                json.dump(tmp['json'][5],json_file)
            with open('location_pathloss.loc.txt','w') as json_file:
                json.dump(tmp['json'][6],json_file)
            with open('location_tag.loc.txt','w') as json_file:
                json.dump(tmp['json'][7],json_file)
            with open('location_R1m.txt','w') as json_file:
                json.dump(tmp['json'][8],json_file)
            with open('location_angle.ble.txt','w') as json_file:
                json.dump(tmp['json'][9],json_file)

            delta=tmp['json'][4]
            tmp=json.loads(location_())
            #print(tmp)
            init_json['Tag']['location']=tmp[0].copy()
            temp=tmp[0].copy()
            if not (tmp[0] is None):
                temp['lat']=temp['lat']/delta['lat']
                temp['lon']=temp['lon']/delta['lon']
            print(temp)

            for idx in init_json['Tag']['value']:
                init_json['Tag']['value'][idx]['distance']=tmp[1][init_json['Tag']['value'][idx]['Mac']]

        result['rssi_mean']=init_json.copy()
        result['createtime']=data['createtime']
        res=result.copy()
        colRes.insert(res)
        colResOne.delete_many({})
        colResOne.insert(init_json.copy())

    cnt=cnt+1


