import time
import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model

model = load_model('Trained Data/keras_MLP_April_2023.h5')

#This creates a single tick so that it can simulate a packet of 13 features
single_tick=np.random.rand(1,12).astype(np.float32)

#This calibrates and makes sure the system is ready for trade
for _ in range(100):
    model.predict(single_tick, verbose=0)

#Timer allows the latency to be measured in nanoseconds
start_time=time.perf_counter_ns()

loops=1000
for _ in range(loops):
    decision=model.predict(single_tick, verbose=0)
    #This acts as the trade being predicted then checked if worth

#Timer allows latency to be measured in nanoseconds
end_time= time.perf_counter_ns()

average_latency_ns = ((end_time - start_time)/ loops)
print (f"The latency for the PC averages to be {average_latency_ns: .4f} nanoseconds")

