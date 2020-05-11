####****************************Request library****************************####
from estimate_dis import estimate_dis
import json
import math
import sys
####***********************************************************************####
class server:
    def __init__(self,value_json):
        #init variable
        self.last_gateway_sum={} #float(os.environ['last_gateway_sum'])
        self.last_gateway_count={} #float(os.environ['last_gateway_count'])
        self.check_none=1
        self.check_enough=0
        self.gateway_kal={}
        self.last_gateway_kal={}

        self.gateway={}
        self.gateway_sum={}
        self.gateway_count={}
        
        #2020.04.09
        #self.calib=[-53.66,-49.05,-49.38,-48.27,-48.16,-47.13,-48.66,-48.08,-47.23,-47.01,-50.23,-49.68,-49.77,-50.09,-50.27,-53.15,-53.55,-50.71,-50.44,-51.03,-51.35,-53.04,-54.29,-57.70,-59.09,-61.35,-56.310,-62.53,-63.99,-61.23,-57.24,-54.44,-54.94,-54.12,-53.980,-53.780,-53.66]
        #2020.04.10
        #self.calib=[-53.66,-54.22,-50.87,-49.13,-49.00,-49.20,-50.61,-50.47,-53.21,-52.29,-53.13,-56.51,-58.53,-60.72,-59.02,-57.52,-55.22,-53.60,-50.44,-51.03,-51.35,-53.04,-54.29,-57.70,-59.09,-61.35,-56.310,-62.53,-63.99,-61.23,-57.24,-54.44,-54.94,-54.12,-53.980,-53.780,-53.66]
        #2020.04.14=[-00.10,-00.20,-00.30,-00.40,-00.50,-00.60,-00.70,-00.80,-00.90,-01.00,-01.10,-01.20,-01.30,-01.40,-01.50,-01.60,-01.70,-01.80
        self.calib=[-43.24,-42.75,-42.66,-42.59,-42.72,-43.29,-44.07,-44.39,-46.08,-49.23,-55.39,-54.95,-56.89,-56.68,-51.45,-48.19,-46.31,-46.27,-47.70,-51.03,-51.35,-53.04,-54.29,-57.70,-59.09,-61.35,-56.310,-62.53,-63.99,-61.23,-57.24,-54.44,-54.94,-54.12,-53.980,-53.780,-53.66]
        #self.calib= [-43.24,-42.75,-42.66,-42.59,-42.72,-43.29,-44.07,-45.39,-49.23,-48.06,-55.39,-54.95,-56.89,-56.68,-51.45,-48.19,-46.31,-46.27,-47.70,-51.03,-51.35,-53.04,-54.29,-57.70,-59.09,-61.35,-56.310,-62.53,-63.99,-61.23,-57.24,-54.44,-54.94,-54.12,-53.980,-53.780,-53.66]

        ##begin test adjust rssi
        ##
        #self.adj={}
        self.adjust={}
        #self.adj['ac:23:3f:a2:16:59']=0.029
        #self.adj['ac:23:3f:a2:16:93']=0
        #self.adj['ac:23:3f:a2:16:c2']=-3.476
        #self.adj['ac:23:3f:a2:16:c0']=0
        ##
        ##end test adjust rssi

        ##begin hard set angle beacon
        ##
        self.angle_beacon={}
        self.angle_beacon['ac:23:3f:a2:16:59']=110
        self.angle_beacon['ac:23:3f:a2:16:93']=185
        self.angle_beacon['ac:23:3f:a2:16:c2']=195
        self.angle_beacon['ac:23:3f:a2:16:c0']=280

        self.location={}
        self.tag_kal={} #float(os.environ['tag_kal'])
        self.pathloss_kal={} #float(os.environ['pathloss_kal'])
        self.dis_pathloss={}
        self.dis_tag={}
        self.location_pathloss={}
        self.beacon=[]
        self.last_tag_location=None

        self.delta=value_json['Delta'].copy()

        for gateway in value_json['Gateway']:
            for datas in gateway['value']:
                data=gateway['value'][datas].copy()
                self.gateway[data['Mac']]=data['last']
                self.gateway_sum[data['Mac']]=data['sum']
                self.gateway_count[data['Mac']]=data['count']
                self.last_gateway_sum[data['Mac']]=data['sum'][4]
                self.last_gateway_count[data['Mac']]=data['count'][4]
                self.gateway_kal[data['Mac']]=data['kalman']
                self.last_gateway_kal[data['Mac']]=data['kalman'][4]
                if data['count'][4]>2000:
                    self.check_enough=1
        
        for datas in value_json['Tag']['value']:
            data=value_json['Tag']['value'][datas].copy()
            self.tag_kal[data['Mac']]=data['Last_kal']
            self.dis_tag[data['Mac']]=0
        if not (value_json['Tag']['location'] is None):
            self.last_tag_location=value_json['Tag']['location'].copy()
            self.check_none=0

        for pathloss in value_json['Pathloss']:
            self.location_pathloss=pathloss['location'].copy()
            for datas in pathloss['value']:
                data=pathloss['value'][datas].copy()
                self.adjust[data['Mac']]=0
                self.pathloss_kal[data['Mac']]=data['Last_kal']
                self.location[data['Mac']]=data['location']
                self.dis_pathloss[data['Mac']]=self.calculate_path_dis(data['location'],pathloss['location'])

        #init estimate
        P=value_json['kalman']['P']
        K=value_json['kalman']['K']
        Q=value_json['kalman']['Q']
        R=value_json['kalman']['R']
        self.est=estimate_dis(P,K,Q,R)

        self.rssi1m=value_json['kalman']['RSSI1m']
        
        #self.Recalculate_Adjust(self.last_tag_location,self.location_pathloss,self.location,self.angle_beacon)
        #print(self.adjust)
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
                        
                        if self.last_gateway_kal[data['Mac']]==0:
                            self.gateway_kal[data['Mac']][cnt]=value
                        else:
                            self.gateway_kal[data['Mac']][cnt]=self.est.estimate(value,self.last_gateway_kal[data['Mac']])
                        self.last_gateway_kal[data['Mac']]=self.gateway_kal[data['Mac']][cnt]
                        cnt=cnt+1
                        
            elif req_json['name']=='pathloss_home':
                cnt=0
                if data['Mac'] in self.pathloss_kal:
                    for value in data['value']:
                        if self.pathloss_kal[data['Mac']]==0:
                            self.pathloss_kal[data['Mac']]=value#-(self.gateway[data['Mac']][cnt]-self.gateway_kal[data['Mac']][cnt])#self.gateway_sum[data['Mac']][cnt]/self.gateway_count[data['Mac']][cnt])
                        else:
                            R_correct=value#-(self.gateway[data['Mac']][cnt]-self.gateway_kal[data['Mac']][cnt])#self.gateway_sum[data['Mac']][cnt]/self.gateway_count[data['Mac']][cnt])
                            if value==0:
                                R_correct=self.pathloss_kal[data['Mac']]
                            self.pathloss_kal[data['Mac']]=self.est.estimate(R_correct,self.pathloss_kal[data['Mac']])
                        cnt=cnt+1

            elif req_json['name']=='tag_home':
                cnt=0
                if data['Mac'] in self.tag_kal:
                    for value in data['value']:
                        if self.tag_kal[data['Mac']]==0:
                            self.tag_kal[data['Mac']]=value#-(self.gateway[data['Mac']][cnt]-self.gateway_kal[data['Mac']][cnt])#.gateway_sum[data['Mac']][cnt]/self.gateway_count[data['Mac']][cnt])
                        else:
                            R_correct=value#-(self.gateway[data['Mac']][cnt]-self.gateway_kal[data['Mac']][cnt])#self.gateway_sum[data['Mac']][cnt]/self.gateway_count[data['Mac']][cnt])
                            if value==0:
                                R_correct=self.tag_kal[data['Mac']]
                            self.tag_kal[data['Mac']]=self.est.estimate(R_correct,self.tag_kal[data['Mac']])
                        cnt=cnt+1
                    #self.dis_tag[data['Mac']]=self.calculate_tag_dis(self.rssi1m,self.tag_kal[data['Mac']],self.pathloss_kal[data['Mac']],self.dis_pathloss[data['Mac']],self.adjust[data['Mac']])
                                       

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
        ret_json['json']=[value_json,self.tag_kal,self.pathloss_kal,self.location,self.delta,self.calib,self.location_pathloss,self.last_tag_location,self.rssi1m,self.angle_beacon]
        
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
    def calculate_tag_dis(self,rssi1m,rssi_tag,rssi_path,dis_path,adjust):
        pathloss_exp=(rssi_path-rssi1m)/(10*math.log10(dis_path))
        if rssi_tag<rssi_path:
            temp=1
        else:
            temp=-1
        dis_tag=10**(((rssi_tag+adjust)-rssi1m)/(10*pathloss_exp))
        return dis_tag
####************************************************************************####

####*************************calculate adjust rssi *************************####
    def Recalculate_Adjust(self,loc_tag,loc_path,loc_beacon,angle_beacon):
        for index in loc_beacon:
            if (self.check_none==0 and self.check_enough==1):
                angle_p=self.calculate_angle(loc_path,loc_beacon[index],angle_beacon[index])
                angle_t=self.calculate_angle(loc_tag,loc_beacon[index],angle_beacon[index])
                point1=int(angle_p/10)
                point2=point1+1
                r_calib_p=((angle_p-point1*10)/10)*(self.calib[point2]-self.calib[point1])+self.calib[point1]
                tmp=self.calculate_path_dis(loc_path,loc_beacon[index])
                r_calib_p=math.log10(tmp)/math.log10(3.0)*(r_calib_p+45.5)-45.5
                #print(r_calib_p)

                point1=int(angle_t/10)
                point2=point1+1
                r_calib_t=((angle_t-point1*10)/10)*(self.calib[point2]-self.calib[point1])+self.calib[point1]
                tmp=self.calculate_path_dis(loc_tag,loc_beacon[index])
                r_calib_t=math.log10(tmp)/math.log10(3.0)*(r_calib_t+45.5)-45.5
                #print(r_calib_t)

                self.adjust[index]=-r_calib_t+r_calib_p
            else:
                self.adjust[index]=0
    
####************************************************************************####

####****************************calculate angle ****************************####
    def calculate_angle(self,loc_target,loc_ref,angle_ref):
        a2=0
        b2=-1
        a1=(loc_target['lon']-loc_ref['lon'])/self.delta['lon']
        b1=(loc_target['lat']-loc_ref['lat'])/self.delta['lat']

        cos_=(a1*a2+b1*b2)/(math.sqrt(a1**2+b1**2)*math.sqrt(a2**2+b2**2))
        phy=math.acos(cos_)/2/math.pi*360

        if loc_target['lon']<loc_ref['lon']:
            phy=360-phy
        phy=(phy-angle_ref)%360
        #print(phy)
        return phy
####************************************************************************####
