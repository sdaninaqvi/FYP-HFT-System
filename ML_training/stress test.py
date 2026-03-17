import pandas as pd
import numpy as np
import os
import joblib
import tensorflow as tf
from sklearn.metrics import accuracy_score
from tensorflow.keras.models import load_model

# === CONFIG ===
data_location = r'C:\Users\sdani\Desktop\Daniyal\Project\Data\Processed Data + TBBAV' 
model_location = r'C:\Users\sdani\Desktop\Daniyal\Project\Trained Data'

def combine_data(data_location):
    dataframes = []
    file_count = 0
    print("Reading CSV files...")
    for filename in os.listdir(data_location):
        if filename.endswith('.csv'):
            file_location = os.path.join(data_location, filename)
            df = pd.read_csv(file_location)
            dataframes.append(df)
            file_count += 1
        if file_count >= 30: 
            break
    
    combined_df = pd.concat(dataframes)
    combined_df['OpenTime'] = pd.to_datetime(combined_df['OpenTime'])
    combined_df.set_index('OpenTime', inplace=True) 
    return combined_df  

def finance_features(df):
    print("Generating Features...")
    # 1. Microprice 
    df['Microprice'] = (df['Close']) - ((df['High'] + df['Low']) / 2)
    # 2. High-Low Spread 
    df['High_low_spread'] = (df['High'] - df['Low']) / df['Close']
    # 3. SMA-10 
    df['moving_average_10'] = df['Close'].rolling(window=10).mean()
    # 4. MACD 
    df['ma_12'] = df['Close'].rolling(window=12).mean()
    df['ma_26'] = df['Close'].rolling(window=26).mean()
    df['MACD'] = df['ma_12'] - df['ma_26']
    # 5. ROC-5 
    df['ROC_5'] = df['Close'].pct_change(periods=5)
    # 6. ROC-10 
    df['ROC_10'] = df['Close'].pct_change(periods=10)
    # 7. RSI 
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / (loss + 1e-9)
    df['Relative_strength_index'] = 100 - (100 / (1 + rs))
    # 8. Bollinger Pos 
    df['std_20'] = df['Close'].rolling(window=20).std()
    df['ma_20'] = df['Close'].rolling(window=20).mean()
    df['Bollinger_Pos'] = (df['Close'] - df['ma_20']) / (2 * df['std_20'] + 1e-9)
    # 9. ATR 
    df['high_low'] = df['High'] - df['Low']
    df['high_close'] = abs(df['High'] - df['Close'].shift(1))
    df['low_close'] = abs(df['Low'] - df['Close'].shift(1))
    df['true_range'] = df[['high_low', 'high_close', 'low_close']].max(axis=1)
    df['ATR'] = df['true_range'].rolling(window=14).mean()
    # 10. Volume Ratio 
    df['volume_ma_10'] = df['Volume'].rolling(window=10).mean()
    df['volume_ratio'] = df['Volume'] / (df['volume_ma_10'] + 1e-9)
    # 11. Buy Volume Ratio 
    df['Buy_volume_ratio'] = df['TakerBuyBaseAssetVolume'] / (df['Volume'] + 1e-9)
    # 12. Order Flow Imbalance 
    df['Order_flow_imbalance'] = df['TakerBuyBaseAssetVolume'] - (df['Volume'] - df['TakerBuyBaseAssetVolume'])
    # 13. Price Acceleration 
    df['price_velocity'] = df['Close'].diff()
    df['price_acceleration'] = df['price_velocity'].diff()
    # TARGET
    df['Target'] = (df['Close'].shift(-1) > df['Close']).astype(int)
    # Clean NaN
    df = df.dropna()
    return df

def run_stress_test():
    # 1. LOAD DATA
    df = combine_data(data_location)
    df = finance_features(df)
    
    # 2. DEFINE FEATURES
    f3_features = ['Microprice', 'High_low_spread', 'moving_average_10']
    
    f13_features = [
        'Microprice', 'High_low_spread', 'moving_average_10',
        'MACD', 'ROC_5', 'ROC_10', 'Relative_strength_index',
        'Bollinger_Pos', 'ATR', 'volume_ratio', 'Buy_volume_ratio',
        'Order_flow_imbalance', 'price_acceleration'
    ]

    # 3. LOAD SCALERS & MODELS
    print("Loading Scalers and Models...")
    # Scalers are still loaded with joblib (assuming they were saved that way)
    scaler_f3 = joblib.load(os.path.join(model_location, 'scaler_f3.pkl'))
    scaler_f13 = joblib.load(os.path.join(model_location, 'scaler_f13.pkl'))
    
    # === CRITICAL CHANGE: LOAD LR AS KERAS MODEL ===
    # Assuming you saved it as 'lr_f3.h5' or 'lr_f3.keras'
    lr_f3 = load_model(os.path.join(model_location, 'lr_f3.h5')) 
    mlp_f13 = load_model(os.path.join(model_location, 'mlp_f13.h5'))

    # 4. PREPARE TEST DATA (Last 30%)
    split_point = int(len(df) * 0.7)
    test_df = df[split_point:].copy()
    y_true = test_df['Target']

    # 5. GENERATE PREDICTIONS
    print("Running Predictions...")
    
    # F3 Predictions
    X_f3 = test_df[f3_features]
    X_f3_scaled = scaler_f3.transform(X_f3)
    
    # === CRITICAL CHANGE: PROCESS LR PREDICTIONS LIKE MLP ===
    # Keras returns probabilities, so we must round them > 0.5
    pred_lr_raw = lr_f3.predict(X_f3_scaled, verbose=0)
    pred_lr = (pred_lr_raw > 0.5).astype(int).flatten()
    
    # F13 Predictions
    X_f13 = test_df[f13_features]
    X_f13_scaled = scaler_f13.transform(X_f13)
    
    pred_mlp_raw = mlp_f13.predict(X_f13_scaled, verbose=0)
    pred_mlp = (pred_mlp_raw > 0.5).astype(int).flatten()

    # 6. SEGMENT BY VOLATILITY
    # High Volatility = Top 20% of High_low_spread
    threshold = test_df['High_low_spread'].quantile(0.80)
    
    high_vol_mask = test_df['High_low_spread'] > threshold
    low_vol_mask = ~high_vol_mask

    print(f"\n=== STRESS TEST RESULTS ({len(test_df)} samples) ===")
    
    # --- LOW VOLATILITY ---
    acc_lr_low = accuracy_score(y_true[low_vol_mask], pred_lr[low_vol_mask])
    acc_mlp_low = accuracy_score(y_true[low_vol_mask], pred_mlp[low_vol_mask])
    
    print(f"\n[Low Volatility (80% of data)]")
    print(f"LR-F3 Accuracy:   {acc_lr_low:.4f}")
    print(f"MLP-F13 Accuracy: {acc_mlp_low:.4f}")
    print(f"Difference:       {(acc_mlp_low - acc_lr_low)*100:.2f}%")

    # --- HIGH VOLATILITY ---
    acc_lr_high = accuracy_score(y_true[high_vol_mask], pred_lr[high_vol_mask])
    acc_mlp_high = accuracy_score(y_true[high_vol_mask], pred_mlp[high_vol_mask])
    
    print(f"\n[High Volatility (Top 20%)]")
    print(f"LR-F3 Accuracy:   {acc_lr_high:.4f}")
    print(f"MLP-F13 Accuracy: {acc_mlp_high:.4f}")
    print(f"Difference:       {(acc_mlp_high - acc_lr_high)*100:.2f}%")

    # --- FINAL VERDICT ---
    if acc_mlp_high > acc_lr_high:
        print("\n✅ POSITIVE RESULT: MLP is better in High Volatility.")
        print(f"   Gap is {acc_mlp_high - acc_lr_high:.4f}. This justifies the adaptive switch.")
    else:
        print("\n⚠️ NEGATIVE RESULT: MLP did not beat LR in high volatility.")
        print("   Stick to the 'Efficiency/Diminishing Returns' narrative.")

if __name__ == "__main__":
    run_stress_test()