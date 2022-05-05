import torch
import numpy as np
 
iFD = 3.61 # Final drive
etaT = 0.9 # Transmission efficiency 
r_w = 0.49 # radius of wheel [m]
T_b_max = 6000 # Max brake torque [Nm]
cd = 0.36 #0.7 # drag coefficient
rho = 1.2 # Density of air [kg/m^3]
A_f = 10 # Frontal area of vehicle [m^2]
m_v = 50000 # Vehicle mass [kg]
g = 9.81 # Gravity of acceleration [m/s^2]
fr = 0.0056 # Rolling resistance coefficient
 
ptorq = # see below
ntorq = # see below
gear_ratio 	= #you can put in fixed value
alpha 	= #you can put in fixed value
prev_v	= # can start at 0
m_v = #you can put in fixed value
time_step = # time between the measured signaldata, usually 0.1 or 0.01 seconds
 
def fwd_transmission_block(self, e):	    
    T_w = ptorq * gear_ratio * iFD * etaT		
    
    return T_w
 
def fwd_chassis_block(self, e):
    
    # Max torque from transmission minus ntorq torque
    T_w_drive = T_w - ntorq 
    #slope resistance
    Fg = m_v * g * torch.sin(torch.arctan(alpha/100))
    #drag force, total resistance force
    Fd = Fg
    # calculating traction force from torque
    Ft = T_w_drive / r_w
    pred_a = (Ft - Fd) / m_v
    pred_v = pred_a * time_step + prev_v
    pred_dist = pred_v * time_step
 
    return pred_v, pred_a, pred_dist
# how to get positive and negative tourqe
# make dict with the tourqe and get it from there
e = {}
ptorq   = e['positivetorque']
ntorq 	= e['negativetorque']
 
def predict(self, E, is_normalized=True):
    e = self.as_signal_dict(E)
    
    e['T_w'] = self.fwd_transmission_block(e)
    V, A, D = self.fwd_chassis_block(e)
 
    return V, A, D
