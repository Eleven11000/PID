import ivPID.PID as PID
import time
import matplotlib.pyplot as plt
import numpy as np
#from scipy.interpolate import spline
from scipy.interpolate import BSpline, make_interp_spline #  Switched to BSpline
from model import VdynLonPlant

glob_total_time = 100
MAX_Toq = 50000

def generate_target_v_list(*args):
    '''
    arg: [target_v, t] ...
    '''
    global glob_total_time 
    sorted_list = sorted(args, key=lambda x:x[1])
    sorted_list.insert(0,[0, 0])
    sorted_list.append([sorted_list[-1][0], glob_total_time])
    target_time_list = list()
    target_v_list = list()
    pre_point = sorted_list[0]
    for point in sorted_list[1:]:
        for i in range(pre_point[1], point[1]):
            target_time_list.append(i)
            target_v_list.append(pre_point[0])
        pre_point = point
    return target_v_list, target_time_list

def run_model(model: VdynLonPlant, toq, v):
    if toq > 0:
        if toq > MAX_Toq:
            toq = MAX_Toq
        E = np.array([toq, 0, v])
        E = np.expand_dims(np.expand_dims(E, axis=-1), 0)
        P = model.predict(E)
    else:
        if toq < -MAX_Toq:
            toq = -MAX_Toq
        E = np.array([0, abs(toq), v])
        E = np.expand_dims(np.expand_dims(E, axis=-1), 0)
        P = model.predict(E)
    return P[0]

def run_pid(P, I, D, total_time):
    pid = PID.PID(P, I, D)
    pid.SetPoint=0.0
    pid.setSampleTime(0.01)
    global glob_total_time 
    glob_total_time = total_time

    feedback = 0
    target_v_list, target_time_list = generate_target_v_list([20,1],[60,20])
    feedback_list = []

    model = VdynLonPlant()
    previous_v = 0

    for i in target_time_list:
        pid.SetPoint = target_v_list[i]
        pid.update(feedback)
        output = pid.output
        if pid.SetPoint > 0:
            feedback = run_model(model, output, previous_v)
        time.sleep(0.02)

        previous_v = feedback if feedback > 0 else 0
        feedback_list.append(feedback)

    target_time_list_sm = np.array(target_time_list)
    v_time_list = np.linspace(target_time_list_sm.min(), target_time_list_sm.max(), 300)

    # Using make_interp_spline to create BSpline
    helper_x3 = make_interp_spline(target_time_list, feedback_list)
    v = helper_x3(v_time_list)

    plot(target_v_list, target_time_list, v, v_time_list, total_time)

def plot(target_v, target_v_time_list, v, v_time_list, total_time):
    plt.plot(v_time_list, v)
    plt.plot(target_v_time_list, target_v)
    plt.xlim((0, total_time))
    plt.xlabel('time (s)')
    plt.ylabel('PID (PV)')
    plt.title('TEST PID')
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    run_pid(3500, 0, 0.01, total_time=50)