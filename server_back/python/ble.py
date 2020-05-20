#declare library
import numpy as np
import random
import math
import json
import time
import threading

#class definition
class Particles:
    def __init__(self,Radius,ref_pos):
        dis = random.uniform(0,Radius)
        angle = random.uniform(0,360)
        x_rand = ref_pos[0] + float(dis*math.sin(angle))
        y_rand = ref_pos[1] + float(dis*math.cos(angle))
    #format [[x, y], fitness, [[pbestx, pbesty], fitbest], [Vx, Vy], w]
        self.pos=np.array([x_rand,y_rand])
        self.fitness=1000
        self.pbest_pos=np.array([x_rand,y_rand])
        self.pbest_fit=1000
        self.V=np.array([[0], [0]])
        self.w=0

class location:
    def __init__(self, tag, pathloss, ble_location, delta, calib, pathloss_location, tag_location, angle_ble, r1m):
        #print(dis_pathloss)
        if (tag_location is None):
            self.Confined_Area_Radius = 10.0
            self.Number_Of_Swarm = 300
        else:
            self.Confined_Area_Radius = 10.0
            self.Number_Of_Swarm = 300
        self.Iteration = 100
        self.delta = delta.copy()
        self.calib=calib.copy()
        self.pathloss=pathloss.copy()
        self.tag=tag.copy()
        self.tag_temp=self.tag.copy()
        self.ble_location=ble_location.copy()
        self.pathloss_loc=pathloss_location.copy()
        self.angle_ble=angle_ble.copy()
        self.R1m=r1m
        self.tag_loc=None
        self.dis_best=None
        self.tag_best=None
        self.adjust_best=None
        self.adjust_value={}

        for idx in self.pathloss_loc:
            if not( tag_location is None):
                tag_location[idx]=tag_location[idx]/self.delta[idx]
            self.pathloss_loc[idx]=self.pathloss_loc[idx]/self.delta[idx]
            for i in self.ble_location:
                self.ble_location[i][idx]=self.ble_location[i][idx]/self.delta[idx]

        self.max=1000

        #data
        self.distance = []
        self.distance_pathloss ={}
        self.node_locations = []
        cnt=0
        pos={}

        # chuyen sang met. x.lon, y.lat
        for idx in ble_location:
            self.node_locations.append([float(ble_location[idx]['lon']), float(ble_location[idx]['lat']), float(ble_location[idx]['alt'])])
            pos[idx]=cnt
            cnt=cnt+1
        #print(self.node_locations)
        for idx in ble_location:
            a=(ble_location[idx]['lon']-self.pathloss_loc['lon'])
            b=(ble_location[idx]['lat']-self.pathloss_loc['lat'])
            self.distance_pathloss[idx]=self.cal_dis(a,b)
            cnt=cnt+1

        self.pos=pos

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
        self.gbest_fit=self.max

        #self.recalculate_dis(0,0)
        #self.distance_tag=self.distance_temp

        self.tag_loc=tag_location
        #for idx in self.tag:
        #    if self.tag[idx]<self.pathloss[idx]-1.0:
        #        self.tag[idx]=self.tag[idx]+0.5
        #    elif self.tag[idx]>self.pathloss[idx]+1.0:
        #        self.tag[idx]=self.tag[idx]-0.5

    def cal_dis(self,a,b):
        tmp=math.sqrt(a**2+b**2)
        return tmp

    #localization by MLE and get confined area of PSO
    def MLE(self):
        if self.tag_loc is None:
            #self.Z_MLE=np.array([ [0], [0] ])
            #return
            self.recalculate_dis(self.pathloss_loc['lon'],self.pathloss_loc['lat'])
            self.distance=self.distance_temp.copy()
            print(self.distance)

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
        else:
            self.Z_MLE=np.array([ [self.tag_loc['lon']], [self.tag_loc['lat']] ])
        #self.Z_MLE=np.array([ [2.43], [4.53] ])
        print(self.Z_MLE)

    def cal_angle(self,src,dst,angle):
        a2=0
        b2=-1
        a1=src['lon']-dst['lon']
        b1=src['lat']-dst['lat']

        cos_=(a1*a2+b1*b2)/(math.sqrt(a1**2+b1**2)*math.sqrt(a2**2+b2**2))
        phy=math.acos(cos_)/2/math.pi*360

        if src['lon']<dst['lon']:
            phy=360-phy

        phy=(phy-angle)%360
        return phy
    
    def adjust(self,angle_p,angle_t,calib):
        point1=int(angle_p/10)
        point2=point1+1
        r_calib_p=((angle_p-point1*10)/10)*(calib[point2]-calib[point1])+calib[point1]

        point1=int(angle_t/10)
        point2=point1+1
        r_calib_t=((angle_t-point1*10)/10)*(calib[point2]-calib[point1])+calib[point1]

        temp=(-r_calib_t+r_calib_p)*2
        return temp

    def recalculate_dis(self,x,y):
        ret={}
        ret['lon']=x
        ret['lat']=y
        self.distance_temp=[]
        #ret=self.pathloss_location
        ########################this line if for none adjust rssi########################
        self.tag_temp=self.tag.copy()
        ########################the code below is for adjust rssi########################
        for idx in self.ble_location:
            #angle_p=self.cal_angle(self.pathloss_loc,self.ble_location[idx],self.angle_ble[idx])
            #angle_t=self.cal_angle(ret,self.ble_location[idx],self.angle_ble[idx])
            #if not (self.tag_loc is None):
            #    self.adjust_value[idx]=self.adjust(angle_p,angle_t,self.calib)
            #    self.tag_temp[idx]=self.tag[idx]+self.adjust_value[idx]
            #else:
            #    self.tag_temp[idx]=self.tag[idx]

            p_exp=(self.pathloss[idx]-self.R1m)/(10.0*math.log10(self.distance_pathloss[idx]))
            if not (self.tag_loc is None):
                tmp=self.R1m+10*math.log10(20)*p_exp
                if self.tag_temp[idx]>tmp:
                    dis=10**((self.tag_temp[idx]-self.R1m)/(10.0*p_exp))
                else:
                    dis=self.max
            else:
                dis=10**((self.tag_temp[idx]-self.R1m)/(10.0*p_exp))

            self.distance_temp.append([self.pos[idx], dis])     
        #print(self.distance_temp)       



    #Evaluate fitness
    def eval_fitness(self,x,y,best):
        fitness=0
        self.recalculate_dis(x,y)
        #for k in self.distance_temp:
        #    if k[1]==self.max:
        #        return [self.max, best]
        for idx in range(0,len(self.distance_temp),1):
            k=self.distance_temp[idx]
            tmp1=abs(k[1]-math.sqrt((x-self.node_locations[k[0]][0])**2 \
                                   +(y-self.node_locations[k[0]][1])**2))

            #k=self.distance_tag[idx]
            #tmp2=abs(k[1]-math.sqrt((x-self.node_locations[k[0]][0])**2 \
            #                       +(y-self.node_locations[k[0]][1])**2))
            fitness=fitness + tmp1**2
        if best>fitness:
            best_ = fitness
        else:
            best_=best
        return [fitness, best_]

    #validate fitness and update pbest gbest
    def validate(self,start,stop):
        for k in range(start,stop,1):
            particle=self.swarm[k]
            [fit, fitbest] = self.eval_fitness(particle.pos[0],particle.pos[1],particle.pbest_fit)
            if fitbest==fit:
                self.swarm[k].pbest_pos=particle.pos
                self.swarm[k].pbest_fit=fitbest
                if self.gbest_fit > fitbest:
                    self.gbest_pos=particle.pos
                    self.gbest_fit=fitbest
                    self.dis_best=self.distance_temp.copy()
                    self.adjust_best=self.adjust_value.copy()
                    self.tag_best=self.tag_temp.copy()


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
        
            Z_next = Z_curr +V_next
            w_curr= self.wmax- step*(self.wmax-self.wmin)/float(self.Iteration)
            temp=math.sqrt((Z_next[0]-self.Z_MLE[0])**2 + (Z_next[1]-self.Z_MLE[1])**2)
            if temp<=self.Confined_Area_Radius:
                self.swarm[k].pos=Z_next
            self.swarm[k].V=V_next
            self.swarm[k].w=w_curr
    
            
    #main
    def estimate(self):
        self.MLE()

        #generate swarm
        for k in range(0,self.Number_Of_Swarm,1):
            particle=Particles(self.Confined_Area_Radius, self.Z_MLE)
            self.swarm.append(particle)

        #start timer
        #t = time.time()


        step = 0
        middle=(int)(len(self.swarm)/2.0)
        while step < self.Iteration:
            step = step+1
            #thread1=threading.Thread(target=self.validate, args=(0,middle,))
            #thread2=threading.Thread(target=self.validate,args=(middle,len(self.swarm)))
            #thread1.start()
            #thread2.start()
            #thread1.join()
            #thread2.join()
            self.validate(0,len(self.swarm))
            self.update(step)
        #print("done in:",time.time()-t)
        ret={}
        ret['lat']=float(self.gbest_pos[1])*self.delta['lat']
        ret['lon']=float(self.gbest_pos[0])*self.delta['lon']
        ret['alt']=0*self.delta['alt']
        #print(self.tag_best)
        #print(self.dis_best)
        #print(self.adjust_best)
        dis={}
        for idx in self.ble_location:
            #a=self.gbest_pos[0]-self.ble_location[idx]['lon']
            #b=self.gbest_pos[1]-self.ble_location[idx]['lat']
            #dis[idx]=self.cal_dis(a,b)
            if (self.dis_best is None):
                dis[idx]=0
            else:
                dis[idx]=self.dis_best[self.pos[idx]][1]
        result=[ret, dis]
        return json.dumps(result)
        
 

    
    




































                  
