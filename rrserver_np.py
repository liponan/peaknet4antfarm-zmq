import zmq
import sys
import os
sys.path.append(os.path.abspath("/reg/neh/home/liponan/ai/peaknet4antfarm"))
import pandas as pd
import numpy as np
import glob
import re
import h5py
import time
import psana
import torch
from peaknet.Peaknet import Peaknet
from peaknet.peaknet_utils import *
from antfarm_utils import *

n_validate = 60 # period of validation 

### Peaknet setup ###

net = Peaknet()
net.loadCfg( "/reg/d/psdm/cxi/cxic0415/res/liponan/peaknet4antfarm/newpeaksv10-asic.cfg" )
net.init_model()
net.model
print("done model setup")

#####################

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5556")

while True:
    #  Wait for next request from client
    message = socket.recv_pyobj()
    grads, delta = message # 'messsage' always has two components
    print("Received request. delta:", delta) # let's not to print out the grads
    if delta > 0: # delta = 
        net.set_optimizer(adagrad=True) # number of images trained in the last iteration
        net.updateGrad(grads=grads, delta=delta, useGPU=False)
        net.optimize()
    print("imgs seen:", net.model.seen)
    if net.model.seen % n_validate == 0 and net.model.seen > 0:
        socket.send_pyobj(["validate", net.model])
    else:
        socket.send_pyobj(["train", net.model])
