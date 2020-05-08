from flask import Flask
from bson import json_util
from bson.codec_options import CodecOptions
import pytz
import pymongo
import json


app = Flask(__name__)

@app.route('/newalg/getall')
def getall():
    with open('result.txt') as json_file:
        datas=json.load(json_file)
    
    response = app.response_class(
        response=json.dumps(datas, indent=4, default=json_util.default),
        status=200,
        mimetype='application/json'
    )
    
    return response

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
