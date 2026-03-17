import tensorflow as tf
import hls4ml
import os

# Load your trained MLP model
model_location = r'C:\Users\sdani\Desktop\Daniyal\Project\Trained Data'
mlp_f13 = tf.keras.models.load_model(os.path.join(model_location, 'mlp_f13.h5'))

print("Model loaded successfully")
print(f"Model layers: {len(mlp_f13.layers)}")

# ============================================
# CRITICAL: RESOURCE-CONSTRAINED CONFIG
# ============================================
config = hls4ml.utils.config_from_keras_model(mlp_f13, granularity='name')

# Strategy: Resource (not Latency!)
config['Model']['Strategy'] = 'Resource'

# ReuseFactor: How many operations share one multiplier
# Higher = fewer resources, more cycles
config['Model']['ReuseFactor'] = 32  # Good balance for your FPGA

# Precision: Use 32-bit (you changed from 16-bit)
config['Model']['Precision'] = 'ap_fixed<32,18>'

# Individual layer configs (optional - for fine-tuning)
for layer in config['LayerName'].keys():
    config['LayerName'][layer]['ReuseFactor'] = 32
    config['LayerName'][layer]['Precision'] = 'ap_fixed<32,18>'

print("\n=== HLS4ML Configuration ===")
print(f"Strategy: {config['Model']['Strategy']}")
print(f"ReuseFactor: {config['Model']['ReuseFactor']}")
print(f"Precision: {config['Model']['Precision']}")

# ============================================
# CONVERT TO HLS
# ============================================
output_dir = r'C:\Users\sdani\Desktop\Daniyal\Project\FPGA_final_backup\HLS_IPA\mlp_f13_resource_32_reuse_16AP'

hls_model = hls4ml.converters.convert_from_keras_model(
    mlp_f13,
    hls_config=config,
    output_dir=output_dir,
    part='xc7a35tcpg236-1',  # Your Artix-7 part
    clock_period=10,  # 100 MHz
    io_type='io_parallel'  # Parallel I/O for speed
)

print(f"\n HLS model generated in: {output_dir}")

# ============================================
# BUILD (COMPILE C++)
# ============================================
print("\nBuilding HLS model...")
hls_model.build(csim=False, synth=True, export=True)

print("\n Check synthesis report for resources.")
print(f"Location: {output_dir}/myproject_prj/solution1/syn/report/")