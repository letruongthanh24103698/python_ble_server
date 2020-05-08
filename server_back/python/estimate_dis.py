from KMF import KMF
import math

class estimate_dis:
    def __init__(self,P,K,Q,R):
        self.P=P
        self.K=K
        self.Q=Q
        self.R=R

    def estimate(self,R_correct, R_kal_last_est):
        kmf=KMF()
        self.P, self.K, last_est = kmf.estimate(R_correct, self.P, self.K, self.Q, self.R, R_kal_last_est)
        return last_est

    def kalman(self, R_gateway_mean, R_gateway_last, R_last, last_est, initiate):
        delta=R_gateway_last-R_gateway_mean
        if initiate==1:
            last_est=R_last-delta
        else:
            R_correct=R_last-delta
            last_est=self.estimate(R_correct, last_est)
        return last_est

    def calculate(self, R_tag, R_pathloss, dis_pathloss):
        pathloss=-(R_pathloss+59)/(10*math.log10(dis_pathloss))
        distance=10**((-59-R_tag)/(10*pathloss))
        return distance
