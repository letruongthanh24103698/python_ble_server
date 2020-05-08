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
        x_rand = ref_pos[0] + dis*math.sin(angle)
        y_rand = ref_pos[1] + dis*math.cos(angle)
    #format [[x, y], fitness, [[pbestx, pbesty], fitbest], [Vx, Vy], w]
        self.pos=np.array([x_rand,y_rand])
        self.fitness=0
        self.pbest_pos=np.array([0,0])
        self.pbest_fit=10000000
        self.V=np.array([[0], [0]])
        self.w=0

class location:
    def __init__(self,dis_pathloss,ble_location):
        self.Confined_Area_Radius = 2.0
        self.Number_Of_Swarm = 100
        self.Iteration = 1000

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
        pos={}
        for idx in ble_location:
            self.node_locations.append([ble_location[idx]['lat'], ble_location[idx]['lon'], ble_location[idx]['alt']])
            pos[idx]=cnt
            cnt=cnt+1
        for idx in dis_pathloss:
            self.distance.append([pos[idx], dis_pathloss[idx]])
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
        self.gbest_pos=np.array([0, 0])
        self.gbest_fit=10000000

    #localization by MLE and get confined area of PSO
    def MLE(self):
        ref = self.distance[random.randint(0,len(self.distance)-1)]
        num_ref = ref[0]
        A=[]
        b=[]
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

        print(A)
        A_transpose = np.transpose(A)
        temp = np.dot(A_transpose,A)
        print(temp)
        temp1 = np.linalg.inv(temp)
        temp2 = np.dot(temp1,A_transpose)
        self.Z_MLE = np.dot(temp2,b)

    #print(Z_MLE)
    

    #Evaluate fitness
    def eval_fitness(self,x,y,best):
        fitness=0
        for k in self.distance:
            fitness = fitness + (k[1]-((x-self.node_locations[k[0]][0])**2 \
                                   +(y-self.node_locations[k[0]][1])**2)**(1/2))**2
        
        if best>fitness:
            best_ = fitness
        else:
            best_=best
        return [fitness, best_]

    #validate fitness and update pbest gbest
    def validate(self):
        for k in range(0,len(self.swarm),1):
            particle=self.swarm[k]
            [fit, fitbest] = self.eval_fitness(particle.pos[0],particle.pos[1],particle.pbest_fit)
            if fitbest==fit:
                self.swarm[k].pbest_pos=particle.pos
                self.swarm[k].pbest_fit=fitbest
                if self.gbest_fit > fitbest:
                    self.gbest_pos=particle.pos
                    self.gbest_fit=fitbest


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
            w_curr= self.wmax- step*(self.wmax-self.wmin)/self.Iteration
            temp=((Z_next[0]-self.Z_MLE[0])**2 + (Z_next[1]-self.Z_MLE[1])**2)**(1/2)
            if temp<=self.Confined_Area_Radius:
                self.swarm[k].pos=Z_next
            self.swarm[k].V=V_next
            self.swarm[k].w=w_curr;
    
            
    #main
    def estimate(self):
        time.perf_counter()
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
        ret['lat']=float(self.gbest_pos[0])
        ret['lon']=float(self.gbest_pos[1])
        ret['alt']=0
        return json.dumps(ret)
        
 

    
    




































                  
