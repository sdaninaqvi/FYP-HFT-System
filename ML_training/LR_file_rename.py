import os
import re

lr_dir = r'C:\Users\sdani\Desktop\Daniyal\Project\FPGA_final_backup\HLS_IP\lr_f3_hls_new2\firmware'

# Files to process
files_to_fix = [
    os.path.join(lr_dir, 'lr_predict.cpp'),
    os.path.join(lr_dir, 'lr_predict.h'),
]

# Also process all files in weights/ folder
weights_dir = os.path.join(lr_dir, 'weights')
if os.path.exists(weights_dir):
    for fname in os.listdir(weights_dir):
        if fname.endswith('.h'):
            files_to_fix.append(os.path.join(weights_dir, fname))

# Replacements (order matters!)
replacements = [
    (r'\bw4\b', 'lr_w4'),
    (r'\bb4\b', 'lr_b4'),
    (r'\bw3\b', 'lr_w3'),
    (r'\bb3\b', 'lr_b3'),
    (r'\bw2\b', 'lr_w2'),
    (r'\bb2\b', 'lr_b2'),
    (r'\bs4\b', 'lr_s4'),
    (r'\bs3\b', 'lr_s3'),
    (r'\bs2\b', 'lr_s2'),
]

print("Fixing LR symbol collisions...")

for filepath in files_to_fix:
    if not os.path.exists(filepath):
        continue
        
    print(f"Processing: {filepath}")
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Apply replacements
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)
    
    # Write back
    with open(filepath, 'w') as f:
        f.write(content)
    
    print(f"  ✓ Done")

# Also rename weight files themselves
if os.path.exists(weights_dir):
    for fname in os.listdir(weights_dir):
        if fname in ['w2.h', 'b2.h', 'w3.h', 'b3.h', 'w4.h', 'b4.h', 's2.h', 's3.h', 's4.h']:
            old_path = os.path.join(weights_dir, fname)
            new_fname = 'lr_' + fname
            new_path = os.path.join(weights_dir, new_fname)
            os.rename(old_path, new_path)
            print(f"Renamed: {fname} → {new_fname}")

print("\n✅ All done! Re-run synthesis now.")