import json
import sys
import math
from ble import location
def cal_exponent(a,b):
    tmp=math.sqrt(a**2+b**2)
    return math.log10(tmp)/math.log10(3.0)

def cal_dis(a,b):
    tmp=math.sqrt(a**2+b**2)
    return tmp

def adjust(angle_p,dis_p,angle_t,dis_t,calib):
    print(angle_p)
    print(angle_t)
    point1=int(angle_p/10)
    point2=point1+1;
    r_calib_p=((angle_p-point1*10)/10)*(calib[point2]-calib[point1])+calib[point1]
    r_calib_p=math.log10(dis_p)/math.log10(2)*(r_calib_p+r1m)-r1m
    #r_calib_p=dis_p/1.5*r_calib_p
    
    point1=int(angle_t/10)
    point2=point1+1;
    r_calib_t=((angle_t-point1*10)/10)*(calib[point2]-calib[point1])+calib[point1]
    r_calib_t=math.log10(dis_t)/math.log10(2)*(r_calib_t+r1m)-r1m
    #r_calib_t=dis_t/1.5*r_calib_t
    
    print(r_calib_p)
    print(r_calib_t)
    temp=-r_calib_t+r_calib_p;
    print(temp)
    return temp

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

exponent={}
r1m=40

r1m_adjust={}

ret_p={}
ret_p['lat']=6.33
ret_p['lon']=2.43
ret_p['alt']=0

r_c0_p=-46.98828572026394#-47.83
r_c0_t=-50.854751281258835#-50.53#-51.03

r_c2_p=-52.83809273589799#-52.24
r_c2_t=-50.57386987229817#-49.87#-49.37

r_93_p=-59.5327248914018#-58.63
r_93_t=-52.527280758818634#-51.85#-51.35

r_59_p=-52.89392475331768#-54.46
r_59_t=-54.49153060739368#-54.19

p_c0=r_c0_p
t_c0=r_c0_t

p_c2=r_c2_p
t_c2=r_c2_t

p_93=r_93_p
t_93=r_93_t

p_59=r_59_p
t_59=r_59_t

a2=0;
b2=-1

angle_59=100
angle_93=200
angle_c2=190
angle_c0=280

#59
a1=ret_p['lon']-loc_json['ac:23:3f:a2:16:59']['lon']
b1=ret_p['lat']-loc_json['ac:23:3f:a2:16:59']['lat']
print(a1)
print(b1)
cos_=(a1*a2+b1*b2)/(math.sqrt(a1**2+b1**2)*math.sqrt(a2**2+b2**2))
phy=math.acos(cos_)/2/math.pi*360

if ret_p['lon']<loc_json['ac:23:3f:a2:16:59']['lon']:
    phy=360-phy

phy=(phy-angle_59)%360
#print(phy)

p_a_59=phy
exponent['ac:23:3f:a2:16:59']=cal_exponent(a1,b1)
r1m_adjust['59']=0#adjust(phy,6.37,0,1.0,calib_json)/2.5
print("------------------")


#93
a1=ret_p['lon']-loc_json['ac:23:3f:a2:16:93']['lon']
b1=ret_p['lat']-loc_json['ac:23:3f:a2:16:93']['lat']

cos_=(a1*a2+b1*b2)/(math.sqrt(a1**2+b1**2)*math.sqrt(a2**2+b2**2))
phy=math.acos(cos_)/2/math.pi*360

if ret_p['lon']<loc_json['ac:23:3f:a2:16:93']['lon']:
    phy=360-phy

phy=(phy-angle_93)%360
#print(phy)

p_a_93=phy
exponent['ac:23:3f:a2:16:93']=cal_exponent(a1,b1)
r1m_adjust['93']=0#adjust(phy,7.04,0,1.0,calib_json)/2.5
print("------------------")


#c2
a1=ret_p['lon']-loc_json['ac:23:3f:a2:16:c2']['lon']
b1=ret_p['lat']-loc_json['ac:23:3f:a2:16:c2']['lat']

cos_=(a1*a2+b1*b2)/(math.sqrt(a1**2+b1**2)*math.sqrt(a2**2+b2**2))
phy=math.acos(cos_)/2/math.pi*360

if ret_p['lon']<loc_json['ac:23:3f:a2:16:c2']['lon']:
    phy=360-phy

phy=(phy-angle_c2)%360
#print(phy)

p_a_c2=phy
exponent['ac:23:3f:a2:16:c2']=cal_exponent(a1,b1)
r1m_adjust['c2']=0#adjust(phy,7.39,0,1.0,calib_json)/2.5
print("------------------")

#c0
a1=ret_p['lon']-loc_json['ac:23:3f:a2:16:c0']['lon']
b1=ret_p['lat']-loc_json['ac:23:3f:a2:16:c0']['lat']

cos_=(a1*a2+b1*b2)/(math.sqrt(a1**2+b1**2)*math.sqrt(a2**2+b2**2))
phy=math.acos(cos_)/2/math.pi*360

if ret_p['lon']<loc_json['ac:23:3f:a2:16:c0']['lon']:
    phy=360-phy

phy=(phy-angle_c0)%360
#print(phy)

p_a_c0=phy
exponent['ac:23:3f:a2:16:c0']=cal_exponent(a1,b1)
r1m_adjust['c0']=0#adjust(phy,5.41,0,1.0,calib_json)/2.5
print("------------------")

print(r1m_adjust)

result=[]
ret={}
    
for index in range(0,50,1):
    print("dis----------")
    p_exp=(p_59+r1m-r1m_adjust['59'])/(10*math.log10(6.37))
    dis_json['ac:23:3f:a2:16:59']=10**((t_59+r1m)/(10*p_exp))
    print(dis_json['ac:23:3f:a2:16:59'])

    p_exp=(p_93+r1m-r1m_adjust['93'])/(10*math.log10(7.04))
    dis_json['ac:23:3f:a2:16:93']=10**((t_93+r1m)/(10*p_exp))
    print(dis_json['ac:23:3f:a2:16:93'])

    p_exp=(p_c2+r1m-r1m_adjust['c2'])/(10*math.log10(7.39))
    dis_json['ac:23:3f:a2:16:c2']=10**((t_c2+r1m)/(10*p_exp))
    print(dis_json['ac:23:3f:a2:16:c2'])

    p_exp=(p_c0+r1m-r1m_adjust['c0'])/(10*math.log10(5.41))
    dis_json['ac:23:3f:a2:16:c0']=10**((t_c0+r1m)/(10*p_exp))
    print(dis_json['ac:23:3f:a2:16:c0'])

    print("end----------")
    
    loc=location(dis_json,loc_json,delta_json)
    ret=loc.estimate()
    result.append(ret)
    print(ret)
    ##
    ret['lon']=2.43
    ret['lat']=4.53

    #59
    a1=ret['lon']-loc_json['ac:23:3f:a2:16:59']['lon']
    b1=ret['lat']-loc_json['ac:23:3f:a2:16:59']['lat']

    cos_=(a1*a2+b1*b2)/(math.sqrt(a1**2+b1**2)*math.sqrt(a2**2+b2**2))
    phy=math.acos(cos_)/2/math.pi*360

    if ret['lon']<loc_json['ac:23:3f:a2:16:59']['lon']:
        phy=360-phy

    phy=(phy-angle_59)%360

    t_59=r_59_t+adjust(p_a_59,6.37,phy,cal_dis(a1,b1),calib_json)#* exponent['ac:23:3f:a2:16:59']
    print(t_59)
    
    print("------------------")

    #93
    a1=ret['lon']-loc_json['ac:23:3f:a2:16:93']['lon']
    b1=ret['lat']-loc_json['ac:23:3f:a2:16:93']['lat']

    cos_=(a1*a2+b1*b2)/(math.sqrt(a1**2+b1**2)*math.sqrt(a2**2+b2**2))
    phy=math.acos(cos_)/2/math.pi*360

    if ret['lon']<loc_json['ac:23:3f:a2:16:93']['lon']:
        phy=360-phy

    phy=(phy-angle_93)%360

    t_93=r_93_t+adjust(p_a_93,7.04,phy,cal_dis(a1,b1),calib_json)#* exponent['ac:23:3f:a2:16:93']
    print(t_93)
    
    print("------------------")

    #c2
    a1=ret['lon']-loc_json['ac:23:3f:a2:16:c2']['lon']
    b1=ret['lat']-loc_json['ac:23:3f:a2:16:c2']['lat']

    cos_=(a1*a2+b1*b2)/(math.sqrt(a1**2+b1**2)*math.sqrt(a2**2+b2**2))
    phy=math.acos(cos_)/2/math.pi*360

    if ret['lon']<loc_json['ac:23:3f:a2:16:c2']['lon']:
        phy=360-phy

    phy=(phy-angle_c2)%360

    t_c2=r_c2_t+adjust(p_a_c2,7.39,phy,cal_dis(a1,b1),calib_json)#* exponent['ac:23:3f:a2:16:c2']
    print(t_c2)
    
    print("------------------")

    #c0
    a1=ret['lon']-loc_json['ac:23:3f:a2:16:c0']['lon']
    b1=ret['lat']-loc_json['ac:23:3f:a2:16:c0']['lat']

    cos_=(a1*a2+b1*b2)/(math.sqrt(a1**2+b1**2)*math.sqrt(a2**2+b2**2))
    phy=math.acos(cos_)/2/math.pi*360

    if ret['lon']<loc_json['ac:23:3f:a2:16:c0']['lon']:
        phy=360-phy

    phy=(phy-angle_c0)%360

    t_c0=r_c0_t+adjust(p_a_c0,5.41,phy,cal_dis(a1,b1),calib_json)#* exponent['ac:23:3f:a2:16:c0']
    print(t_c0)
    
    print("------------------")
result_json=json.dumps(result)
with open('result.txt','w') as json_file:
    json_file.write(result_json)
    json_file.close()

