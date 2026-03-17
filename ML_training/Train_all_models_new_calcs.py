import pandas as pd
import numpy as np
import os
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score
import joblib
import tensorflow as tf
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization, Input, Concatenate

data_location = r'C:\Users\sdani\Desktop\Daniyal\Project\Data\Processed Data + TBBAV'
model_location = r'C:\Users\sdani\Desktop\Daniyal\Project\Trained Data'
os.makedirs(model_location, exist_ok=True)

def combine_data(data_location):
    """USE ALL FILES - NOT JUST 30"""
    dataframes = []
    for filename in os.listdir(data_location):
        if filename.endswith('.csv'):
            file_location = os.path.join(data_location, filename)
            df = pd.read_csv(file_location)
            dataframes.append(df)
    
    print(f"Total files combined: {len(dataframes)}")
    combined_df = pd.concat(dataframes)
    combined_df['OpenTime'] = pd.to_datetime(combined_df['OpenTime'])
    combined_df.set_index('OpenTime', inplace=True)
    return combined_df

def finance_features(df):
    # Base features
    df['Mid_price_log_return'] = np.log(df['Close'] / df['Close'].shift(1))
    df['High_low_spread'] = (df['High'] - df['Low']) / df['Close']
    
    # Moving averages
    df['moving_average_10'] = df['Close'].rolling(window=10).mean()
    df['moving_average_30'] = df['Close'].rolling(window=30).mean()
    df['moving_average_60'] = df['Close'].rolling(window=60).mean()
    
    # RSI
    diff = df['Close'].diff()
    gain = diff.clip(lower=0).rolling(window=14).mean()
    loss = (-diff.clip(upper=0)).rolling(window=14).mean()
    rs = gain / (loss + 1e-9)
    df['Relative_strength_index'] = 100.0 - (100.0 / (1.0 + rs))
    
    # Volume features
    df['Buy_volume_ratio'] = df['TakerBuyBaseAssetVolume'] / df['Volume']
    df['Order_flow_imbalance'] = df['TakerBuyBaseAssetVolume'] - (df['Volume'] - df['TakerBuyBaseAssetVolume'])
    df['Vol_weighted_avg_price'] = ((df['High'] + df['Low'] + df['Close']) / 3)
    df['Amihud_illiquidity_ratio'] = df['Mid_price_log_return'].abs() / df['Volume']
    df['Microprice'] = df['Close'] - ((df['High'] + df['Low']) / 2)
    
    # MACD
    df['ma_12'] = df['Close'].rolling(window=12).mean()
    df['ma_26'] = df['Close'].rolling(window=26).mean()
    df['MACD'] = df['ma_12'] - df['ma_26']
    df['MACD_signal'] = df['MACD'].rolling(window=9).mean()
    df['MACD_hist'] = df['MACD'] - df['MACD_signal']
    
    # Bollinger
    df['std_20'] = df['Close'].rolling(window=20).std()
    df['ma_20'] = df['Close'].rolling(window=20).mean()
    df['Bollinger_Position'] = (df['Close'] - df['ma_20']) / (2 * df['std_20'] + 1e-9)
    
    # Momentum
    df['ROC_5'] = df['Close'].pct_change(periods=5)
    df['ROC_10'] = df['Close'].pct_change(periods=10)
    
    # ATR
    df['high_low'] = df['High'] - df['Low']
    df['high_close'] = abs(df['High'] - df['Close'].shift(1))
    df['low_close'] = abs(df['Low'] - df['Close'].shift(1))
    df['true_range'] = df[['high_low', 'high_close', 'low_close']].max(axis=1)
    df['ATR'] = df['true_range'].rolling(window=14).mean()
    
    # Volume
    df['volume_ma_10'] = df['Volume'].rolling(window=10).mean()
    df['volume_ratio'] = df['Volume'] / (df['volume_ma_10'] + 1e-9)
    
    # Price derivatives
    df['price_velocity'] = df['Close'].diff()
    df['price_acceleration'] = df['price_velocity'].diff()
    
    # === NUCLEAR: INTERACTION FEATURES ===
    df['RSI_Volume'] = df['Relative_strength_index'] * df['volume_ratio']
    df['Bollinger_MACD'] = df['Bollinger_Position'] * df['MACD_hist']
    df['ATR_ROC'] = df['ATR'] * df['ROC_5']
    df['Volume_Flow'] = df['volume_ratio'] * df['Buy_volume_ratio']
    df['Accel_Bollinger'] = df['price_acceleration'] * df['Bollinger_Position']
    df['MACD_RSI'] = df['MACD_hist'] * (df['Relative_strength_index'] / 100)
    
    # === NUCLEAR: NON-LINEAR TERMS ===
    df['RSI_squared'] = (df['Relative_strength_index'] / 100) ** 2
    df['Bollinger_squared'] = df['Bollinger_Position'] ** 2
    df['MACD_squared'] = df['MACD_hist'] ** 2
    
    # === NUCLEAR: TEMPORAL FEATURES ===
    df['hour'] = df.index.hour
    df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
    df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
    
    df['Target'] = (df['Close'].shift(-1) > df['Close']).astype(int)
    df = df.dropna()
    return df

def focal_loss(gamma=2.0, alpha=0.25):
    def focal_loss_fixed(y_true, y_pred):
        epsilon = tf.keras.backend.epsilon()
        y_pred = tf.keras.backend.clip(y_pred, epsilon, 1. - epsilon)
        cross_entropy = -y_true * tf.math.log(y_pred)
        weight = alpha * tf.pow((1 - y_pred), gamma)
        loss = weight * cross_entropy
        return tf.reduce_mean(loss)
    return focal_loss_fixed

def train_all_four_models(df):
    f3_features = ['Microprice', 'High_low_spread', 'moving_average_10']
    
    f13_features = [
        # Core
        'Microprice', 'High_low_spread', 'moving_average_10',
        # Momentum
        'MACD_hist', 'ROC_5', 'ROC_10', 'Relative_strength_index',
        # Volatility
        'Bollinger_Position', 'ATR',
        # Volume
        'volume_ratio', 'Buy_volume_ratio', 'Order_flow_imbalance',
        # Advanced
        'price_acceleration',
        # INTERACTIONS (MLP advantage)
        'RSI_Volume', 'Bollinger_MACD', 'ATR_ROC',
        'Volume_Flow', 'Accel_Bollinger', 'MACD_RSI',
        # NON-LINEAR
        'RSI_squared', 'Bollinger_squared', 'MACD_squared',
        # TEMPORAL
        'hour_sin', 'hour_cos'
    ]
    
    print(f"F3 features: {len(f3_features)}")
    print(f"F13+ features: {len(f13_features)}")
    
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
    
    # MODEL 1: LR F3
    print("\n" + "="*50)
    print("MODEL 1: LR F3")
    print("="*50)
    scaler_f3 = StandardScaler()
    X_f3_train_scaled = scaler_f3.fit_transform(X_f3_train)
    X_f3_test_scaled = scaler_f3.transform(X_f3_test)
    lr_f3 = LogisticRegression(max_iter=1000, random_state=42).fit(X_f3_train_scaled, y_train)
    acc_lr_f3 = lr_f3.score(X_f3_test_scaled, y_test)
    print(f"Test Accuracy: {acc_lr_f3:.4f}")
    joblib.dump(lr_f3, os.path.join(model_location, 'lr_f3.pkl'))
    joblib.dump(scaler_f3, os.path.join(model_location, 'scaler_f3.pkl'))
    
    # MODEL 2: LR F13
    print("\n" + "="*50)
    print("MODEL 2: LR F13")
    print("="*50)
    scaler_f13 = StandardScaler()
    X_f13_train_scaled = scaler_f13.fit_transform(X_f13_train)
    X_f13_test_scaled = scaler_f13.transform(X_f13_test)
    lr_f13 = LogisticRegression(max_iter=1000, random_state=42).fit(X_f13_train_scaled, y_train)
    acc_lr_f13 = lr_f13.score(X_f13_test_scaled, y_test)
    print(f"Test Accuracy: {acc_lr_f13:.4f}")
    joblib.dump(lr_f13, os.path.join(model_location, 'lr_f13.pkl'))
    joblib.dump(scaler_f13, os.path.join(model_location, 'scaler_f13.pkl'))
    
    # MODEL 3: MLP F3
    print("\n" + "="*50)
    print("MODEL 3: MLP F3")
    print("="*50)
    mlp_f3 = Sequential([
        Dense(8, input_shape=(3,), activation='relu'),
        Dense(4, activation='relu'),
        Dense(1, activation='sigmoid')
    ])
    mlp_f3.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    mlp_f3.fit(X_f3_train_scaled, y_train, epochs=20, batch_size=1024, verbose=0)
    _, acc_mlp_f3 = mlp_f3.evaluate(X_f3_test_scaled, y_test, verbose=0)
    print(f"Test Accuracy: {acc_mlp_f3:.4f}")
    mlp_f3.save(os.path.join(model_location, 'mlp_f3.h5'))
    
    # MODEL 4: MLP F13 (NUCLEAR)
    print("\n" + "="*50)
    print("MODEL 4: MLP F13 (NUCLEAR)")
    print("="*50)
    
    mlp_f13 = Sequential([
        Dense(64, input_shape=(len(f13_features),), activation='relu',
              kernel_regularizer=tf.keras.regularizers.l2(0.0005)),
        BatchNormalization(),
        Dropout(0.3),
        
        Dense(32, activation='relu',
              kernel_regularizer=tf.keras.regularizers.l2(0.0005)),
        BatchNormalization(),
        Dropout(0.3),
        
        Dense(16, activation='relu',
              kernel_regularizer=tf.keras.regularizers.l2(0.0005)),
        Dropout(0.2),
        
        Dense(1, activation='sigmoid')
    ])
    
    lr_schedule = tf.keras.optimizers.schedules.ExponentialDecay(
        initial_learning_rate=0.001,
        decay_steps=5000,
        decay_rate=0.96
    )
    
    opt = tf.keras.optimizers.Adam(learning_rate=lr_schedule)
    mlp_f13.compile(optimizer=opt, loss=focal_loss(gamma=2.0, alpha=0.25), metrics=['accuracy'])
    
    early_stop = tf.keras.callbacks.EarlyStopping(
        monitor='val_accuracy',
        patience=7,
        restore_best_weights=True,
        mode='max'
    )
    
    reduce_lr = tf.keras.callbacks.ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.5,
        patience=4,
        min_lr=0.00001
    )
    
    history = mlp_f13.fit(
        X_f13_train_scaled, y_train,
        validation_split=0.15,
        epochs=100,
        batch_size=512,
        callbacks=[early_stop, reduce_lr],
        verbose=1
    )
    
    _, acc_mlp_f13 = mlp_f13.evaluate(X_f13_test_scaled, y_test, verbose=0)
    print(f"Test Accuracy: {acc_mlp_f13:.4f}")
    mlp_f13.save(os.path.join(model_location, 'mlp_f13.h5'))
    
    # Summary
    print("\n" + "="*60)
    print("FINAL RESULTS")
    print("="*60)
    print(f"A (F3+LR):   {acc_lr_f3:.4f}")
    print(f"B (F13+LR):  {acc_lr_f13:.4f}")
    print(f"C (F3+MLP):  {acc_mlp_f3:.4f}")
    print(f"D (F13+MLP): {acc_mlp_f13:.4f}")
    print(f"\nGAP (D - A): {(acc_mlp_f13 - acc_lr_f3):.4f} ({100*(acc_mlp_f13 - acc_lr_f3):.2f}%)")
    
    summary = pd.DataFrame({
        'Setup': ['A', 'B', 'C', 'D'],
        'Accuracy': [acc_lr_f3, acc_lr_f13, acc_mlp_f3, acc_mlp_f13]
    })
    summary.to_csv(os.path.join(model_location, 'model_summary.csv'), index=False)
    return summary

if __name__ == "__main__":
    print("Loading ALL data...")
    df = combine_data(data_location)
    print(f"Total samples: {len(df)}")
    
    print("\nEngineering features...")
    df = finance_features(df)
    print(f"Samples after feature engineering: {len(df)}")
    
    summary = train_all_four_models(df)
    print("\n✅ All models trained!")