import joblib
import numpy as np

lr = joblib.load(r'C:\Users\sdani\Desktop\Daniyal\Project\Trained Data\lr_f3.pkl')

print("LR Weights:")
print(lr.coef_[0])  # Should be 3 values
print("\nLR Bias:")
print(lr.intercept_[0])  # Should be 1 value
