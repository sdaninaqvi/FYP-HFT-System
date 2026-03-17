import pandas as pd
import numpy as np
import os
import tensorflow as tf
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.regularizers import l2
import joblib
import random
# 1. Lock down Python's hash environment
os.environ['PYTHONHASHSEED'] = '0'

# 2. Lock down the random number generators
SEED = 42
random.seed(SEED)
np.random.seed(SEED)
tf.random.set_seed(SEED)
# === CONFIGURATION ===
data_location = r'C:\Users\sdani\Desktop\Daniyal\Project\Data\Processed Data + TBBAV' 
model_location = r'C:\Users\sdani\Desktop\Daniyal\Project\Trained Data'
os.makedirs(model_location, exist_ok=True)

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
            print("Files combined limit reached")
            break
    
    combined_df = pd.concat(dataframes)
    combined_df['OpenTime'] = pd.to_datetime(combined_df['OpenTime'])
    combined_df.set_index('OpenTime', inplace=True) 
    return combined_df  

def finance_features(df):
    print("Generating Features...")
    
    # === F3 FEATURES ===
    df['Microprice'] = (df['Close']) - ((df['High'] + df['Low']) / 2)
    df['High_low_spread'] = (df['High'] - df['Low']) / df['Close']
    df['moving_average_10'] = df['Close'].rolling(window=10).mean()

    # === F13 FEATURES ===
    df['ma_12'] = df['Close'].rolling(window=12).mean()
    df['ma_26'] = df['Close'].rolling(window=26).mean()
    df['MACD'] = df['ma_12'] - df['ma_26']
    df['ROC_5'] = df['Close'].pct_change(periods=5)
    df['ROC_10'] = df['Close'].pct_change(periods=10)
    
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / (loss + 1e-9)
    df['Relative_strength_index'] = 100 - (100 / (1 + rs))
    
    df['std_20'] = df['Close'].rolling(window=20).std()
    df['ma_20'] = df['Close'].rolling(window=20).mean()
    df['Bollinger_Pos'] = (df['Close'] - df['ma_20']) / (2 * df['std_20'] + 1e-9)
    
    df['high_low'] = df['High'] - df['Low']
    df['high_close'] = abs(df['High'] - df['Close'].shift(1))
    df['low_close'] = abs(df['Low'] - df['Close'].shift(1))
    df['true_range'] = df[['high_low', 'high_close', 'low_close']].max(axis=1)
    df['ATR'] = df['true_range'].rolling(window=14).mean()
    
    df['volume_ma_10'] = df['Volume'].rolling(window=10).mean()
    df['volume_ratio'] = df['Volume'] / (df['volume_ma_10'] + 1e-9)
    df['Buy_volume_ratio'] = df['TakerBuyBaseAssetVolume'] / (df['Volume'] + 1e-9)
    df['Order_flow_imbalance'] = df['TakerBuyBaseAssetVolume'] - (df['Volume'] - df['TakerBuyBaseAssetVolume'])
    
    df['price_velocity'] = df['Close'].diff()
    df['price_acceleration'] = df['price_velocity'].diff()
    
    # TARGET
    df['Target'] = (df['Close'].shift(-1) > df['Close']).astype(int)
    
    df = df.dropna()
    return df

def train_all_four_models(df):
    # DEFINE FEATURE SETS
    f3_features = ['Microprice', 'High_low_spread', 'moving_average_10']
    
    f13_features = [
        'Microprice', 'High_low_spread', 'moving_average_10',
        'MACD', 'ROC_5', 'ROC_10', 'Relative_strength_index',
        'Bollinger_Pos', 'ATR',
        'volume_ratio', 'Buy_volume_ratio', 'Order_flow_imbalance',
        'price_acceleration'
    ]

    print(f"Training on {len(df)} samples.")

    # PREPARE DATA
    X_f3 = df[f3_features]
    X_f13 = df[f13_features]
    y = df['Target']
    
    X_f3 = X_f3.replace([np.inf, -np.inf], np.nan).dropna()
    X_f13 = X_f13.replace([np.inf, -np.inf], np.nan).dropna()
    
    common_index = X_f3.index.intersection(X_f13.index)
    X_f3, X_f13, y = X_f3.loc[common_index], X_f13.loc[common_index], y.loc[common_index]
    
    split_point = int(len(X_f3) * 0.7)
    
    X_f3_train, X_f3_test = X_f3[:split_point], X_f3[split_point:]
    X_f13_train, X_f13_test = X_f13[:split_point], X_f13[split_point:]
    y_train, y_test = y[:split_point], y[split_point:]

    # --- MODEL 1: Keras LR F3 (Replaces Sklearn) ---
    print("\n--- MODEL 1: LR F3 (Keras Version) ---")
    scaler_f3 = StandardScaler()
    X_f3_train_scaled = scaler_f3.fit_transform(X_f3_train)
    X_f3_test_scaled = scaler_f3.transform(X_f3_test)
    
    # A single Dense layer with sigmoid IS Logistic Regression
    lr_f3 = Sequential([
        Dense(1, input_shape=(3,), activation='sigmoid')
    ])
    lr_f3.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    lr_f3.fit(X_f3_train_scaled, y_train, epochs=50, batch_size=2048, verbose=0)
    
    _, acc_lr_f3 = lr_f3.evaluate(X_f3_test_scaled, y_test, verbose=0)
    print(f"Accuracy: {acc_lr_f3:.4f}")
    
    # Save as H5
    lr_f3.save(os.path.join(model_location, 'lr_f3.h5'))
    joblib.dump(scaler_f3, os.path.join(model_location, 'scaler_f3.pkl'))
    np.save(os.path.join(model_location, 'X_test_f3.npy'), X_f3_test_scaled[:100])

    # --- MODEL 2: Keras LR F13 (Replaces Sklearn) ---
    print("\n--- MODEL 2: LR F13 (Keras Version) ---")
    scaler_f13 = StandardScaler()
    X_f13_train_scaled = scaler_f13.fit_transform(X_f13_train)
    X_f13_test_scaled = scaler_f13.transform(X_f13_test)
    
    lr_f13 = Sequential([
        Dense(1, input_shape=(13,), activation='sigmoid')
    ])
    lr_f13.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    lr_f13.fit(X_f13_train_scaled, y_train, epochs=50, batch_size=2048, verbose=0)
    
    _, acc_lr_f13 = lr_f13.evaluate(X_f13_test_scaled, y_test, verbose=0)
    print(f"Accuracy: {acc_lr_f13:.4f}")
    
    # Save as H5
    lr_f13.save(os.path.join(model_location, 'lr_f13.h5'))
    joblib.dump(scaler_f13, os.path.join(model_location, 'scaler_f13.pkl'))

    # --- MODEL 3: MLP F3 (Small Net) ---
    print("\n--- MODEL 3: MLP F3 (Small Net) ---")
    mlp_f3 = Sequential([
        Dense(8, input_shape=(3,), activation='relu'),
        Dense(4, activation='relu'),
        Dense(1, activation='sigmoid')
    ])
    mlp_f3.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    mlp_f3.fit(X_f3_train_scaled, y_train, epochs=15, batch_size=4096, verbose=0)
    _, acc_mlp_f3 = mlp_f3.evaluate(X_f3_test_scaled, y_test, verbose=0)
    print(f"Accuracy: {acc_mlp_f3:.4f}")
    mlp_f3.save(os.path.join(model_location, 'mlp_f3.h5'))

    # --- MODEL 4: MLP F13 (The Heavyweight) ---
    print("\n--- MODEL 4: MLP F13 (Optimized) ---")
    mlp_f13 = Sequential([
        Dense(16, input_shape=(13,), activation='relu', kernel_regularizer=l2(0.0001)),
        Dropout(0.1), 
        Dense(8, activation='relu', kernel_regularizer=l2(0.0001)),
        Dense(1, activation='sigmoid')
    ])
    
    opt = tf.keras.optimizers.Adam(learning_rate=0.001)
    mlp_f13.compile(optimizer=opt, loss='binary_crossentropy', metrics=['accuracy'])
    
    callback = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)
    
    mlp_f13.fit(X_f13_train_scaled, y_train, 
                validation_split=0.1, 
                epochs=30, 
                batch_size=2048, 
                callbacks=[callback],
                verbose=1)
    
    _, acc_mlp_f13 = mlp_f13.evaluate(X_f13_test_scaled, y_test, verbose=0)
    print(f"Accuracy: {acc_mlp_f13:.4f}")
    mlp_f13.save(os.path.join(model_location, 'mlp_f13.h5'))
    np.save(os.path.join(model_location, 'X_test_f13.npy'), X_f13_test_scaled[:100])

    # --- SUMMARY ---
    print("\n" + "="*40)
    print(f"Setup A (F3+LR Keras):   {acc_lr_f3:.4f}")
    print(f"Setup B (F13+LR Keras):  {acc_lr_f13:.4f}")
    print(f"Setup C (F3+MLP Keras):  {acc_mlp_f3:.4f}")
    print(f"Setup D (F13+MLP Keras): {acc_mlp_f13:.4f}")
    print("="*40)

if __name__ == "__main__":
    df = combine_data(data_location)
    df = finance_features(df)
    train_all_four_models(df)