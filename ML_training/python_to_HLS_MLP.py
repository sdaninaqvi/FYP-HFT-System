import hls4ml
import tensorflow as tf
import numpy as np
import os

model_path='Trained Data/keras_mlp_April_2023.h5'
output_folder='FPGA_project_MLP'
FPGA_board='xc7a35tcpg236-1'

print("Loading Keras Model")
model=tf.keras.models.load_model(model_path)

config=hls4ml.utils.config_from_keras_model(model, granularity='name')

#Note to self: Update quantisation to test difference later from AP_fixed<16,6>
for layer in config['LayerName']:
    config['LayerName'][layer]['Precision']= 'ap_fixed<16,6>'
    #Anything above splits the area up, takes longer to do calculations
    config['LayerName'][layer]['ReuseFactor']= 1 

print (f'Converting to C++')
hls_model=hls4ml.converters.convert_from_keras_model(model, hls_config=config, output_dir=output_folder, part=FPGA_board)

#Crashed code
#print("Compiling")
#hls_model.compile()

#print("Verifying accuracy")
#x_test=np.random.rand(1,12)
#y_keras=model.predict(x_test)
#y_hls=hls_model.predict(x_test)

print (f"\n File generated in {output_folder}")
