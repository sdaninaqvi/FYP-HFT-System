import tensorflow as tf
import hls4ml
import os

# Load your trained MLP model
model_location = r'C:\Users\sdani\Desktop\Daniyal\Project\Trained Data'
mlp_f13 = tf.keras.models.load_model(os.path.join(model_location, 'mlp_f13.h5'))

print("Model loaded successfully")
print(f"Model layers: {len(mlp_f13.layers)}")

# ============================================
# CRITICAL: PURE-SPEED HFT CONFIG
# ============================================
config = hls4ml.utils.config_from_keras_model(mlp_f13, granularity='name')

# 1. Global Model Settings
config['Model']['Strategy'] = 'Resource'
config['Model']['ReuseFactor'] = 32
config['Model']['Precision'] = 'ap_fixed<16,6>'

# 2. Safely apply constraints ONLY to layers that do math (Dense layers)
for layer in config['LayerName'].keys():
    # Set precision globally for all layers to ensure no 32-bit leaks
    config['LayerName'][layer]['Precision'] = 'ap_fixed<16,6>'
    
    # Only force ReuseFactor and Strategy on layers with weights/multipliers
    if 'dense' in layer.lower():
        config['LayerName'][layer]['Strategy'] = 'Resource'
        config['LayerName'][layer]['ReuseFactor'] = 32

print("\n=== HLS4ML Configuration ===")
print(f"Strategy: {config['Model']['Strategy']}")
print(f"ReuseFactor: {config['Model']['ReuseFactor']}")
print(f"Precision: {config['Model']['Precision']}")

# ============================================
# CONVERT TO HLS
# ============================================
# Renamed output dir so you don't confuse it with the old broken one
output_dir = r'C:\Users\sdani\Desktop\Daniyal\Project\FPGA_final_backup_vivado\HLS_IPA\mlp_f13_Resource_rf1_16bit_32_reusefactor'

hls_model = hls4ml.converters.convert_from_keras_model(
    mlp_f13,
    hls_config=config,
    output_dir=output_dir,
    part='xc7a35tcpg236-1',  # Your Artix-7 part
    clock_period=10,  # 100 MHz (10ns)
    io_type='io_parallel'  # Parallel I/O for maximum speed
)

print(f"\n HLS model generated in: {output_dir}")

# ============================================
# BUILD (COMPILE C++)
# ============================================
print("\nBuilding HLS model (This will take a few minutes)...")
hls_model.build(csim=False, synth=True, export=True)

print("\n✓ Build Complete!")
print("Check synthesis report for positive slack and cycles.")
print(f"Location: {output_dir}/myproject_prj/solution1/syn/report/myproject_csynth.rpt")