import json
import sys
import math
from ble import location

with open('req_json.txt') as json_file:
    dis_json=json.load(json_file)

with open('value_json.txt') as json_file:
    loc_json=json.load(json_file)
    
with open('delta_json.txt') as json_file:
    delta_json=json.load(json_file)
    
#get data from node.js
#dis_json_str=sys.argv[1]
#loc_json_str=sys.argv[2]
#delta_json_str=sys.argv[3]

#parse data from string to json
#dis_json=json.loads(dis_json_str)
#loc_json=json.loads(loc_json_str)
#delta_json=json.loads(delta_json_str)

with open('calib_json.txt') as json_file:
    calib_json=json.load(json_file)

ret_p={}
ret_p['lat']=6.33
ret_p['lon']=2.43
ret_p['alt']=0

r_c0_p=-48.991#-47.83
r_c0_t=-51.645#-50.53#-51.03

r_c2_p=-52.995#-52.24
r_c2_t=-50.243#-49.87#-49.37

r_93_p=-58.694#-58.63
r_93_t=-51.736#-51.85#-51.35

r_59_p=-53.800#-54.46
r_59_t=-55.563#-54.19

p_c0=r_c0_p
t_c0=r_c0_t

p_c2=r_c2_p
t_c2=r_c2_t

p_93=r_93_p
t_93=r_93_t

p_59=r_59_p
t_59=r_59_t

rssi_p={}
rssi_p['ac:23:3f:a2:16:59']=r_59_p
rssi_p['ac:23:3f:a2:16:93']=r_93_p
rssi_p['ac:23:3f:a2:16:c2']=r_c2_p
rssi_p['ac:23:3f:a2:16:c0']=r_c0_p

rssi_t={}
rssi_t['ac:23:3f:a2:16:59']=r_59_t
rssi_t['ac:23:3f:a2:16:93']=r_93_t
rssi_t['ac:23:3f:a2:16:c2']=r_c2_t
rssi_t['ac:23:3f:a2:16:c0']=r_c0_t

a2=0;
b2=-1

angle_59=100
angle_93=185
angle_c2=190
angle_c0=280

#59
a1=ret_p['lon']-loc_json['ac:23:3f:a2:16:59']['lon']
b1=ret_p['lat']-loc_json['ac:23:3f:a2:16:59']['lat']

cos_=(a1*a2+b1*b2)/(math.sqrt(a1**2+b1**2)*math.sqrt(a2**2+b2**2))
phy=math.acos(cos_)/2/math.pi*360

if ret_p['lon']<loc_json['ac:23:3f:a2:16:59']['lon']:
    phy=360-phy

phy=(phy-angle_59)%360
p_a_59=phy


#93
a1=ret_p['lon']-loc_json['ac:23:3f:a2:16:93']['lon']
b1=ret_p['lat']-loc_json['ac:23:3f:a2:16:93']['lat']

cos_=(a1*a2+b1*b2)/(math.sqrt(a1**2+b1**2)*math.sqrt(a2**2+b2**2))
phy=math.acos(cos_)/2/math.pi*360

if ret_p['lon']<loc_json['ac:23:3f:a2:16:93']['lon']:
    phy=360-phy

phy=(phy-angle_93)%360

p_a_93=phy


#c2
a1=ret_p['lon']-loc_json['ac:23:3f:a2:16:c2']['lon']
b1=ret_p['lat']-loc_json['ac:23:3f:a2:16:c2']['lat']

cos_=(a1*a2+b1*b2)/(math.sqrt(a1**2+b1**2)*math.sqrt(a2**2+b2**2))
phy=math.acos(cos_)/2/math.pi*360

if ret_p['lon']<loc_json['ac:23:3f:a2:16:c2']['lon']:
    phy=360-phy

phy=(phy-angle_c2)%360

p_a_c2=phy

#c0
a1=ret_p['lon']-loc_json['ac:23:3f:a2:16:c0']['lon']
b1=ret_p['lat']-loc_json['ac:23:3f:a2:16:c0']['lat']

cos_=(a1*a2+b1*b2)/(math.sqrt(a1**2+b1**2)*math.sqrt(a2**2+b2**2))
phy=math.acos(cos_)/2/math.pi*360

if ret_p['lon']<loc_json['ac:23:3f:a2:16:c0']['lon']:
    phy=360-phy

phy=(phy-angle_c0)%360

p_a_c0=phy

angle_pathloss={}
angle_pathloss['ac:23:3f:a2:16:59']=p_a_59
angle_pathloss['ac:23:3f:a2:16:93']=p_a_93
angle_pathloss['ac:23:3f:a2:16:c2']=p_a_c2
angle_pathloss['ac:23:3f:a2:16:c0']=p_a_c0

print(angle_pathloss)

result=[]

    
for index in range(0,1,1):
    p_exp=(p_59+40)/(10*math.log10(6.37))
    dis_json['ac:23:3f:a2:16:59']=10**((t_59+40)/(10*p_exp))

    p_exp=(p_93+40)/(10*math.log10(7.04))
    dis_json['ac:23:3f:a2:16:93']=10**((t_93+40)/(10*p_exp))

    p_exp=(p_c2+40)/(10*math.log10(7.39))
    dis_json['ac:23:3f:a2:16:c2']=10**((t_c2+40)/(10*p_exp))

    p_exp=(p_c0+40)/(10*math.log10(5.41))
    dis_json['ac:23:3f:a2:16:c0']=10**((t_c0+40)/(10*p_exp))

    print(dis_json)
    
    loc=location(dis_json,loc_json,delta_json,angle_pathloss,calib_json,rssi_p,rssi_t)
    ret=loc.estimate()
    result.append(ret)
    print(ret)


