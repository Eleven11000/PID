import math
import time
import pickle
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

def ReLU(x):
	return x * (x > 0)

class VdynLonPlant():
	
	def run(self, toq, v):
		if toq > 0:
			E = np.array([toq, 0, v])
			E = np.expand_dims(np.expand_dims(E, axis=-1), 0)
			P = model.predict(E)
		else:
			E = np.array([0, abs(toq), v])
			E = np.expand_dims(np.expand_dims(E, axis=-1), 0)
			P = model.predict(E)
		return P

	def as_signal_dict(self, E):
		signals = ['positivetorque', 'negativetorque', 'wheelbasedvehiclespeed']

		sigdict = {}
		sigdict['transmissionactualgearratio'] = 8
		sigdict['roadinclination'] = 0
		sigdict['grosscombinationvehicleweight'] = 20000

		for n, s in enumerate(signals):
			sigdict[s] = E[:, n, -1]
		return sigdict
	
	def fwd_transmission_block(self, e):
		ptorq 		= e['positivetorque']
		gear_ratio 	= e['transmissionactualgearratio']		
		
		T_w = ptorq * gear_ratio * iFD * etaT		
		
		return T_w

	def fwd_chassis_block(self, e):
		T_w 	= e['T_w']
		ntorq 	= e['negativetorque']
		alpha 	= e['roadinclination']
		prev_v	= e['wheelbasedvehiclespeed']
		m_v 	= e['grosscombinationvehicleweight']
		time_step = 1/10 # sampling rate: 10Hz
		
		# Max torque from transmission minus ntorq torque
		T_w_drive = T_w - ntorq #/ 100 * T_b_max
		# aerodynamic resistance
		Fa = 0
		#Rolling resistance		
		Fr = 0 
		#slope resistance		
		Fg = m_v * g * np.sin(np.arctan(alpha/100))
		#drag force, total resistance force
		Fd = Fa + Fr + Fg
		# calculating traction force from torque
		Ft = T_w_drive / r_w
		a_cc = (Ft - Fd) / m_v
		pred_v = a_cc * time_step + prev_v
		pred_v = ReLU(pred_v)
		
		return pred_v

	def predict(self, E):
		e = self.as_signal_dict(E)
		
		e['T_w'] = self.fwd_transmission_block(e)
		P   = self.fwd_chassis_block(e)
		# P   = np.expand_dims(np.expand_dims(P, axis=-1), 0)
		
		return P

if __name__ == "__main__":
	model = VdynLonPlant()
	E = np.array([5000, 0, 32])
	E = np.expand_dims(np.expand_dims(E, axis=-1), 0)
	P = model.predict(E)
