import hls4ml
import tensorflow as tf
import os

# Updated paths to go UP one level to find 'Trained Data'
# Or use the absolute path you used in your training script
model_dir = r'C:\Users\sdani\Desktop\Daniyal\Project\Trained Data'
output_base = r'C:\Users\sdani\Desktop\Daniyal\Project\FPGA_final_backup\HLS_IP'

# 1. Convert the Fast Path (LR)
lr_path = os.path.join(model_dir, 'lr_f3.h5')
print(f"Loading LR from: {lr_path}")
model_lr = tf.keras.models.load_model(lr_path)

config_lr = hls4ml.utils.config_from_keras_model(model_lr)
config_lr['Model']['WeightTablePrefix'] = 'lr_'
hls_model_lr = hls4ml.converters.convert_from_keras_model(
    model_lr, 
    hls_config=config_lr, 
    output_dir=os.path.join(output_base, 'lr_f3_hls_new2'), 
    part='xc7a35tcpg236-1',
    project_name='lr_predict'
)
hls_model_lr.build(reset=True, csim=False, synth=False)

# 2. Convert the Slow Path (MLP)
mlp_path = os.path.join(model_dir, 'mlp_f13.h5')
print(f"Loading MLP from: {mlp_path}")
model_mlp = tf.keras.models.load_model(mlp_path)

config_mlp = hls4ml.utils.config_from_keras_model(model_mlp, granularity='name')

config_mlp['Model']['Strategy'] = 'Resource'
config_mlp['Model']['ReuseFactor'] = 16

for layer in config_mlp['LayerName'].keys():
    config_mlp['LayerName'][layer]['Strategy'] = 'Resource'
    config_mlp['LayerName'][layer]['ReuseFactor'] = 16

hls_model_mlp = hls4ml.converters.convert_from_keras_model(
    model_mlp, 
    hls_config=config_mlp, 
    output_dir=os.path.join(output_base, 'mlp_f13_hls'), 
    part='xc7a35tcpg236-1'
)
hls_model_mlp.build(reset=True, csim=False, synth=False)

print("\nSUCCESS: All C++ files generated in HLS_IP folder.")