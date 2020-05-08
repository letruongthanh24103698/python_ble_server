####****************************Request library****************************####
from estimate_dis import estimate_dis
import json
####***********************************************************************####
class server:
    def __init__(self,value_json):
        #init variable
        self.last_gateway_sum={} #float(os.environ['last_gateway_sum'])
        self.last_gateway_count={} #float(os.environ['last_gateway_count'])

        self.gateway={}
        self.gateway_sum={}
        self.gateway_count={}

        self.tag_kal={} #float(os.environ['tag_kal'])
        self.pathloss_kal={} #float(os.environ['pathloss_kal'])

        for datas in value_json['Gateway']['value']:
            data=value_json['Gateway']['value'][datas]
            self.gateway[data['Mac']]=data['last']
            self.gateway_sum[data['Mac']]=data['sum']
            self.gateway_count[data['Mac']]=data['count']
            self.last_gateway_sum[data['Mac']]=data['sum'][4]
            self.last_gateway_count[data['Mac']]=data['count'][4]
        
        for datas in value_json['Tag']['value']:
            data=value_json['Tag']['value'][datas]
            self.tag_kal[data['Mac']]=data['Last_kal']

        for datas in value_json['Pathloss']['value']:
            data=value_json['Pathloss']['value'][datas]
            self.pathloss_kal[data['Mac']]=data['Last_kal']

        #init estimate
        P=value_json['kalman']['P']
        K=value_json['kalman']['K']
        Q=value_json['kalman']['Q']
        R=value_json['kalman']['R']
        self.est=estimate_dis(P,K,Q,R)

####**********************************main**********************************####

    def process(self,req_json,value_json):
        #calculate
        for datas in req_json['data']:
            data=req_json['data'][datas]
            if req_json['name']=='gateway_home':
                cnt=0
                if data['Mac'] in self.gateway:
                    for value in data['value']:
                        self.gateway[data['Mac']][cnt]=value
                        self.gateway_sum[data['Mac']][cnt]=self.last_gateway_sum[data['Mac']]+value
                        self.gateway_count[data['Mac']][cnt]=self.last_gateway_count[data['Mac']]+1
                        self.last_gateway_sum[data['Mac']]=self.gateway_sum[data['Mac']][cnt]
                        self.last_gateway_count[data['Mac']]=self.gateway_count[data['Mac']][cnt] 
                        cnt=cnt+1
            elif req_json['name']=='tag_home':
                cnt=0
                if data['Mac'] in self.tag_kal:
                    for value in data['value']:
                        if self.tag_kal[data['Mac']]==0:
                            self.tag_kal[data['Mac']]=value-(self.gateway[data['Mac']][cnt]-self.gateway_sum[data['Mac']][cnt]/self.gateway_count[data['Mac']][cnt])
                        else:
                            R_correct=value-(self.gateway[data['Mac']][cnt]-self.gateway_sum[data['Mac']][cnt]/self.gateway_count[data['Mac']][cnt])
                            self.tag_kal[data['Mac']]=self.est.estimate(R_correct,self.tag_kal[data['Mac']])
                            
                        cnt=cnt+1
            elif req_json['name']=='pathloss_home':
                cnt=0
                if data['Mac'] in self.pathloss_kal:
                    for value in data['value']:
                        if self.pathloss_kal[data['Mac']]==0:
                            self.pathloss_kal[data['Mac']]=value-(self.gateway[data['Mac']][cnt]-self.gateway_sum[data['Mac']][cnt]/self.gateway_count[data['Mac']][cnt])
                        else:
                            R_correct=value-(self.gateway[data['Mac']][cnt]-self.gateway_sum[data['Mac']][cnt]/self.gateway_count[data['Mac']][cnt])
                            self.pathloss_kal[data['Mac']]=self.est.estimate(R_correct,self.pathloss_kal[data['Mac']])
                            
                        cnt=cnt+1

        return self.create_json(value_json)
####************************************************************************####

    def create_json(self,value_json):
        for datas in value_json['Gateway']["value"]:
            data=value_json['Gateway']["value"][datas]
            value_json['Gateway']["value"][datas]['count']=self.gateway_count[data['Mac']]
            value_json['Gateway']["value"][datas]['sum']=self.gateway_sum[data['Mac']]
            value_json['Gateway']["value"][datas]['last']=self.gateway[data['Mac']]

        for datas in value_json['Tag']["value"]:
            data=value_json['Tag']["value"][datas]
            value_json['Tag']["value"][datas]['Last_kal']=self.tag_kal[data['Mac']]

        for datas in value_json['Pathloss']["value"]:
            data=value_json['Pathloss']["value"][datas]
            value_json['Pathloss']["value"][datas]['Last_kal']=self.pathloss_kal[data['Mac']]

        value_json['kalman']['P']=self.est.P
        value_json['kalman']['K']=self.est.K
        value_json['kalman']['Q']=self.est.Q
        value_json['kalman']['R']=self.est.R
        return json.dumps(value_json)
                     
