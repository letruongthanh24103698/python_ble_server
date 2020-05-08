#declare library
import numpy as np
import random
import math
import json
import time


#class definition
class Particles:
    def __init__(self,Radius,ref_pos):
        dis = random.uniform(0,Radius)
        angle = random.uniform(0,360)
        x_rand = ref_pos[0] + float(dis*math.sin(angle))
        y_rand = ref_pos[1] + float(dis*math.cos(angle))
    #format [[x, y], fitness, [[pbestx, pbesty], fitbest], [Vx, Vy], w]
        self.pos=np.array([x_rand,y_rand])
        self.fitness=10000000
        self.pbest_pos=np.array([x_rand,y_rand])
        self.pbest_fit=10000000
        self.V=np.array([[0], [0]])
        self.w=0

class location:
    def __init__(self,dis_tag,ble_location,delta,angle_p,calib,rssi_p,rssi_t):
        #print(dis_tag)
        self.Confined_Area_Radius = 3.0
        self.Number_Of_Swarm = 300
        self.Iteration = 1000
        self.delta = delta
        self.angle_p=angle_p
        self.calib=calib
        self.rssi_p=rssi_p
        self.rssi_t=rssi_t
        self.rssi_t_temp=self.rssi_t.copy()
        #print(self.rssi_t_temp)
        #print(angle_p)
        self.ble_location=ble_location
        self.calib=calib
        self.dis_best=None

        self.angle_59=100
        self.angle_93=175
        self.angle_c2=190
        self.angle_c0=280

        #testing informations
        #RSSI=[] #format [ToBeacon, RML_mean, RML, RNL]
        #RSSI.append([0, -70, -68, -78])
        #RSSI.append([1, -70, -69, -77])
        #RSSI.append([2, -70, -70, -80])
        #RSSI.append([3, -70, -71, -82])

        #data
        self.distance = []
        self.node_locations = [] #format [x y z]
        #self.node_locations.append([0,  0, 0]) #Beacon 0
        #self.node_locations.append([20, 0, 0]) #Beacon 1
        #self.node_locations.append([0, 20, 0]) #Beacon 2
        #self.node_locations.append([20,20, 0]) #Beacon 3
        cnt=0;
        self.pos={}

        # chuyen sang met. x.lon, y.lat
        for idx in ble_location:
            self.node_locations.append([float(ble_location[idx]['lon'])/delta['lon'], float(ble_location[idx]['lat'])/delta['lat'], float(ble_location[idx]['alt'])/delta['alt']])
            self.pos[idx]=cnt
            cnt=cnt+1
        #print(self.node_locations)
        for idx in dis_tag:
            self.distance.append([self.pos[idx], dis_tag[idx]])
            cnt=cnt+1
     
        #parameter
        self.c1=1.2
        self.c2=1.2
        self.r1=-0.5
        self.r2=0.5
        self.wmax=0.8
        self.wmin=0.3

        #variable
        self.Z_MLE=[]
        self.swarm=[]
        self.gbest_pos=np.array([[0], [0]])
        self.gbest_fit=10000000
        
    def cal_dis(self,a,b):
        tmp=math.sqrt(a**2+b**2)
        return tmp

    def adjust(self,angle_p,dis_p,angle_t,dis_t,calib):
        #print(angle_p)
        #print(angle_t)
        point1=int(angle_p/10)
        point2=point1+1;
        r_calib_p=((angle_p-point1*10)/10)*(calib[point2]-calib[point1])+calib[point1]
        #r_calib_p=math.log10(dis_p)/math.log10(2)*(r_calib_p+40)-40
        #r_calib_p=dis_p/2*r_calib_p
        
        point1=int(angle_t/10)
        point2=point1+1;
        r_calib_t=((angle_t-point1*10)/10)*(calib[point2]-calib[point1])+calib[point1]
        #r_calib_t=math.log10(dis_t)/math.log10(2)*(r_calib_t+40)-40
        #r_calib_t=dis_t/2*r_calib_t
        
        #print(r_calib_p)
        #print(r_calib_t)
        temp=-r_calib_t+r_calib_p
        #print(temp)
        return temp

    #localization by MLE and get confined area of PSO
    def MLE(self):
        A=[]
        b=[]
        for index in range(0,len(self.distance),1):
            ref = self.distance[index]
            num_ref = ref[0]
            for k in range(0,len(self.distance),1):
                temp = self.distance[k]
                num = temp[0]
                A1 = 2*(self.node_locations[num][0] - self.node_locations[num_ref][0])
                A2 = 2*(self.node_locations[num][1] - self.node_locations[num_ref][1])
                A.append([A1, A2])

                b_temp= self.node_locations[num][0]**2 - self.node_locations[num_ref][0]**2 \
                    + self.node_locations[num][1]**2 - self.node_locations[num_ref][1]**2 \
                    + temp[1]**2 - ref[1]**2
                b.append([b_temp])

        #print(A)
        #print(b)
        A_transpose = np.transpose(A)
        temp = np.dot(A_transpose,A)
        temp1 = np.linalg.inv(temp)
        temp2 = np.dot(temp1,A_transpose)
        self.Z_MLE = np.dot(temp2,b)
        self.Z_MLE = np.array([[4.53],[2.43]])

        print(self.Z_MLE)

    def recalculate_dis(self,x,y):
        a2=0
        b2=-1
        ret={}
        ret['lon']=x
        ret['lat']=y
        #print("B")
        #print(x)
        #print(y)
        #59
        a1=ret['lon']-self.ble_location['ac:23:3f:a2:16:59']['lon']
        b1=ret['lat']-self.ble_location['ac:23:3f:a2:16:59']['lat']

        cos_=(a1*a2+b1*b2)/(math.sqrt(a1**2+b1**2)*math.sqrt(a2**2+b2**2))
        phy=math.acos(cos_)/2/math.pi*360

        if ret['lon']<self.ble_location['ac:23:3f:a2:16:59']['lon']:
            phy=360-phy

        phy=(phy-self.angle_59)%360

        self.rssi_t_temp['ac:23:3f:a2:16:59']=self.rssi_t['ac:23:3f:a2:16:59']+self.adjust(self.angle_p['ac:23:3f:a2:16:59'],6.37,phy,self.cal_dis(a1,b1),self.calib)
        

        #93
        a1=ret['lon']-self.ble_location['ac:23:3f:a2:16:93']['lon']
        b1=ret['lat']-self.ble_location['ac:23:3f:a2:16:93']['lat']

        cos_=(a1*a2+b1*b2)/(math.sqrt(a1**2+b1**2)*math.sqrt(a2**2+b2**2))
        phy=math.acos(cos_)/2/math.pi*360

        if ret['lon']<self.ble_location['ac:23:3f:a2:16:93']['lon']:
            phy=360-phy

        phy=(phy-self.angle_93)%360
        #print(phy)

        self.rssi_t_temp['ac:23:3f:a2:16:93']=self.rssi_t['ac:23:3f:a2:16:93']+self.adjust(self.angle_p['ac:23:3f:a2:16:93'],7.04,phy,self.cal_dis(a1,b1),self.calib)


        #c2
        a1=ret['lon']-self.ble_location['ac:23:3f:a2:16:c2']['lon']
        b1=ret['lat']-self.ble_location['ac:23:3f:a2:16:c2']['lat']

        cos_=(a1*a2+b1*b2)/(math.sqrt(a1**2+b1**2)*math.sqrt(a2**2+b2**2))
        phy=math.acos(cos_)/2/math.pi*360

        if ret['lon']<self.ble_location['ac:23:3f:a2:16:c2']['lon']:
            phy=360-phy

        phy=(phy-self.angle_c2)%360

        self.rssi_t_temp['ac:23:3f:a2:16:c2']=self.rssi_t['ac:23:3f:a2:16:c2']+self.adjust(self.angle_p['ac:23:3f:a2:16:c2'],7.39,phy,self.cal_dis(a1,b1),self.calib)


        #c0
        a1=ret['lon']-self.ble_location['ac:23:3f:a2:16:c0']['lon']
        b1=ret['lat']-self.ble_location['ac:23:3f:a2:16:c0']['lat']

        cos_=(a1*a2+b1*b2)/(math.sqrt(a1**2+b1**2)*math.sqrt(a2**2+b2**2))
        phy=math.acos(cos_)/2/math.pi*360

        if ret['lon']<self.ble_location['ac:23:3f:a2:16:c0']['lon']:
            phy=360-phy

        phy=(phy-self.angle_c0)%360

        self.rssi_t_temp['ac:23:3f:a2:16:c0']=self.rssi_t['ac:23:3f:a2:16:c0']+self.adjust(self.angle_p['ac:23:3f:a2:16:c0'],5.41,phy,self.cal_dis(a1,b1),self.calib)

        self.distance_temp=[]
        

        p_exp=(self.rssi_p['ac:23:3f:a2:16:59']+40)/(10*math.log10(6.37))
        if self.rssi_t_temp['ac:23:3f:a2:16:59']>(-40+11.76*p_exp):  
            dis=10**((self.rssi_t_temp['ac:23:3f:a2:16:59']+40)/(10*p_exp))
        else:
            dis=100000000
        idx='ac:23:3f:a2:16:59'
        self.distance_temp.append([self.pos[idx], dis])

        p_exp=(self.rssi_p['ac:23:3f:a2:16:93']+40)/(10*math.log10(7.04))
        if self.rssi_t_temp['ac:23:3f:a2:16:93']>(-40+11.76*p_exp):   
            dis=10**((self.rssi_t_temp['ac:23:3f:a2:16:93']+40)/(10*p_exp))
        else:
            dis=100000000
        idx='ac:23:3f:a2:16:93'
        self.distance_temp.append([self.pos[idx], dis])

        p_exp=(self.rssi_p['ac:23:3f:a2:16:c2']+40)/(10*math.log10(7.39))
        if self.rssi_t_temp['ac:23:3f:a2:16:c2']>(-40+11.76*p_exp):
            dis=10**((self.rssi_t_temp['ac:23:3f:a2:16:c2']+40)/(10*p_exp))
        else:
            dis=100000000
        idx='ac:23:3f:a2:16:c2'
        self.distance_temp.append([self.pos[idx], dis])

        p_exp=(self.rssi_p['ac:23:3f:a2:16:c0']+40)/(10*math.log10(5.41))
        #print("a")
        #print((-40+11.76*p_exp))
        #print(self.rssi_t_temp['ac:23:3f:a2:16:c0'])
        #print(self.rssi_t_temp['ac:23:3f:a2:16:c0']>(-40+11.76*p_exp))
        if self.rssi_t_temp['ac:23:3f:a2:16:c0']>(-40+11.76*p_exp):   
            dis=10**((self.rssi_t_temp['ac:23:3f:a2:16:c0']+40)/(10*p_exp))
        else:
            dis=100000000
        idx='ac:23:3f:a2:16:c0'
        #print(dis)
        self.distance_temp.append([self.pos[idx], dis])

        #print(self.distance_temp)

        
    

    #Evaluate fitness
    def eval_fitness(self,x,y,best):
        fitness=0
        self.recalculate_dis(x,y)
        for k in self.distance_temp:
            #print(k[1])
            if self.tmp==1:
                print(k[1])
                print(math.sqrt((x-self.node_locations[k[0]][0])**2 +(y-self.node_locations[k[0]][1])**2))
                print('---')
            if k[1]< 10000000:
                #fitness = fitness + (k[1]-math.sqrt((x-self.node_locations[k[0]][0])**2 +(y-self.node_locations[k[0]][1])**2))**2
                fitness = fitness + abs(k[1]-math.sqrt((x-self.node_locations[k[0]][0])**2 +(y-self.node_locations[k[0]][1])**2))
            else:
                return[10000000, best]
        if best>fitness:
            best_ = fitness
        else:
            best_=best
        return [fitness, best_]

    #validate fitness and update pbest gbest
    def validate(self):
        #print(self.gbest_pos)
        for k in range(0,len(self.swarm),1):
            particle=self.swarm[k]
            [fit, fitbest] = self.eval_fitness(particle.pos[0],particle.pos[1],particle.pbest_fit)
            if fitbest==fit:
                self.swarm[k].pbest_pos=particle.pos
                self.swarm[k].pbest_fit=fitbest
                if self.gbest_fit > fitbest:
                    self.gbest_pos=particle.pos
                    self.gbest_fit=fitbest
                    self.dis_best=self.distance_temp
                    


    #update pos and velo
    def update(self,step):
        for k in range(0,self.Number_Of_Swarm,1):
            particle=self.swarm[k]
            Z_curr=particle.pos
            V_curr=particle.V
            pbest_curr=particle.pbest_pos
            w_curr= particle.w
            V_next = w_curr*V_curr + self.c1*self.r1*(pbest_curr-Z_curr) \
                 + self.c2*self.r2*(self.gbest_pos-Z_curr)
        
            Z_next = Z_curr +V_next;
            #print(self.gbest_pos)
            w_curr= self.wmax- step*(self.wmax-self.wmin)/float(self.Iteration)
            temp=math.sqrt((Z_next[0]-self.Z_MLE[0])**2 + (Z_next[1]-self.Z_MLE[1])**2)
            if temp<=self.Confined_Area_Radius:
                self.swarm[k].pos=Z_next
            self.swarm[k].V=V_next
            self.swarm[k].w=w_curr;
    
            
    #main
    def estimate(self):
        self.tmp=0
        self.MLE()

        #generate swarm
        for k in range(0,self.Number_Of_Swarm,1):
            particle=Particles(self.Confined_Area_Radius, self.Z_MLE)
            self.swarm.append(particle)

        step = 0;
        while step < self.Iteration:
            step = step+1
            self.validate()
            self.update(step)

        ret={}
        ret['lat']=float(self.gbest_pos[1])*self.delta['lat']
        ret['lon']=float(self.gbest_pos[0])*self.delta['lon']
        ret['alt']=0*self.delta['alt']
        #return json.dumps(ret)
        print(self.dis_best)
        print(self.gbest_fit)
        self.distance_temp=self.dis_best
        self.tmp=1
        [a,b]=self.eval_fitness(self.gbest_pos[0],self.gbest_pos[1],100000)
        print(a)
        print(b)
        return ret
        
 

    
    




































                  
