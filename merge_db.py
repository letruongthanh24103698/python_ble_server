import pymongo
import json

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb1 = myclient["iFactory"]
mydb2 = myclient["iFactory2"]
mycol1 = mydb1["rtlsbletest"]
mycol2 = mydb2["rtlsbletest"]

cursor=mycol2.find({},{"_id":0},no_cursor_timeout=True)

for data in cursor:
    x=mycol1.insert_one(data)