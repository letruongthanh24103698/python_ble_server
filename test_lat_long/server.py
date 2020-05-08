####****************************Request library****************************####
from estimate_dis import estimate_dis
import json
import math
####***********************************************************************####
class server:
    def __init__(self,value_json):
        #init variable
        self.last_gateway_sum={} #float(os.environ['last_gateway_sum'])
        self.last_gateway_count={} #float(os.environ['last_gateway_count'])

        self.gateway={}
        self.gateway_sum={}
        self.gateway_count={}

        self.location={}
        self.tag_kal={} #float(os.environ['tag_kal'])
        self.pathloss_kal={} #float(os.environ['pathloss_kal'])
        self.dis_pathloss={}
        self.dis_tag={}

        self.delta=value_json['Delta'].copy()

        for gateway in value_json['Gateway']:
            for datas in gateway['value']:
                data=gateway['value'][datas].copy()
                self.gateway[data['Mac']]=data['last']
                self.gateway_sum[data['Mac']]=data['sum']
                self.gateway_count[data['Mac']]=data['count']
                self.last_gateway_sum[data['Mac']]=data['sum'][4]
                self.last_gateway_count[data['Mac']]=data['count'][4]
        
        for datas in value_json['Tag']['value']:
            data=value_json['Tag']['value'][datas].copy()
            self.tag_kal[data['Mac']]=data['Last_kal']
            self.dis_tag[data['Mac']]=0

        for pathloss in value_json['Pathloss']:
            for datas in pathloss['value']:
                data=pathloss['value'][datas].copy()
                self.pathloss_kal[data['Mac']]=data['Last_kal']
                self.location[data['Mac']]=data['location']
                self.dis_pathloss[data['Mac']]=self.calculate_path_dis(data['location'],pathloss['location'])

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
                    self.dis_tag[data['Mac']]=self.calculate_tag_dis(-55,self.tag_kal[data['Mac']],self.pathloss_kal[data['Mac']],self.dis_pathloss[data['Mac']])
                                       

        return self.create_json(value_json)
####************************************************************************####

####***************************create json**********************************####

    def create_json(self,value_json):
        for index in range(0,len(value_json['Gateway']),1):
            gateway=value_json['Gateway'][index].copy()
            for datas in gateway['value']:
                data=gateway["value"][datas].copy()
                gateway["value"][datas]['count']=self.gateway_count[data['Mac']]
                gateway["value"][datas]['sum']=self.gateway_sum[data['Mac']]
                gateway["value"][datas]['last']=self.gateway[data['Mac']]
            value_json['Gateway'][index]=gateway.copy()

        for datas in value_json['Tag']["value"]:
            data=value_json['Tag']["value"][datas].copy()
            value_json['Tag']["value"][datas]['Last_kal']=self.tag_kal[data['Mac']]
            value_json['Tag']["value"][datas]['distance']=self.dis_tag[data['Mac']]

        for index in range(0,len(value_json['Pathloss']),1):
            pathloss=value_json['Pathloss'][index].copy()
            for datas in pathloss['value']:
                data=pathloss["value"][datas].copy()
                pathloss["value"][datas]['Last_kal']=self.pathloss_kal[data['Mac']]
            value_json['Pathloss'][index]=pathloss.copy()

        value_json['kalman']['P']=self.est.P
        value_json['kalman']['K']=self.est.K
        value_json['kalman']['Q']=self.est.Q
        value_json['kalman']['R']=self.est.R

        ret_json={}
        ret_json['json']=[value_json,self.dis_tag,self.location,self.delta]
        
        return json.dumps(ret_json)
####************************************************************************####

####***********************calculate pathloss distance**********************####
    def calculate_path_dis(self,source,destination):
        d_lat=float(source['lat']-destination['lat'])/self.delta['lat']
        d_lon=float(source['lon']-destination['lon'])/self.delta['lon']
        d_alt=float(source['alt']-destination['alt'])/self.delta['alt']
        dis=math.sqrt(float(float(d_lat)**2+float(d_lon)**2+float(d_alt)**2))
        return dis
####************************************************************************####

####*************************calculate tag distance*************************####
    def calculate_tag_dis(self,rssi1m,rssi_tag,rssi_path,dis_path):
        pathloss_exp=(rssi_path-rssi1m)/(10*math.log10(dis_path))
        dis_tag=10**((rssi_tag-rssi1m)/(10*pathloss_exp))
        return dis_tag
####************************************************************************####
