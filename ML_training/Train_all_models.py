import pandas as pd
import numpy as np
import os
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score
import joblib
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense


data_location= r'C:\Users\sdani\Desktop\Daniyal\Project\Data\Processed Data + TBBAV' #This needs to be updated each time i want a different set of data to be used.
model_location= r'C:\Users\sdani\Desktop\Daniyal\Project\Trained Data'

os.makedirs(model_location, exist_ok=True)


def combine_data (data_location):
    #since files currently split by day this combines them together
    dataframes= []
    file_count=90
    for filename in os.listdir(data_location):
        if filename.endswith('.csv'):
            file_location= os.path.join(data_location, filename)
            df= pd.read_csv(file_location)
            dataframes.append(df)
            file_count +=1

        if file_count>=119: #update each time
            print("30 files combined")
            break
    
    combined_df = pd.concat(dataframes)

    combined_df['OpenTime'] = pd.to_datetime(combined_df['OpenTime'])
    combined_df.set_index('OpenTime', inplace=True) 
    return combined_df  

def finance_features(df):
    df ['Mid_price_log_return']= np.log(df['Close']/ df['Close'].shift(1))
    df ['High_low_spread']= (df['High'] - df['Low'])/ df['Close']
    #Relative Strength Index (RSI) feature
    diff_between_close= df['Close'].diff()
    gain_for_rsi= diff_between_close.clip(lower=0)
    loss_for_rsi= -1* diff_between_close.clip(upper=0)
    rolling_gain= gain_for_rsi.rolling(window=14).mean()
    rolling_loss= loss_for_rsi.rolling(window=14).mean()
    relative_strength= rolling_gain/ (rolling_loss +1e-9)   
    df ['moving_average_10']= df['Close'].rolling(window=10).mean()
    df ['moving_average_30']= df['Close'].rolling(window=30).mean()
    df ['moving_average_60']= df['Close'].rolling(window=60).mean()
    df ['Relative_strength_index']= 100.0 - (100.0/(1.0 + relative_strength))
    df ['Buy_volume_ratio']= df['TakerBuyBaseAssetVolume']/ df['Volume']
    df ['Order_flow_imbalance']= df['TakerBuyBaseAssetVolume']-(df['Volume']-df['TakerBuyBaseAssetVolume'])
    df ['Vol_weighted_avg_price']= (((df['High'])+ df['Low'] + df['Close'])/3)
    df ['Amihud_illiquidity_ratio']= df['Mid_price_log_return'].abs()/ df['Volume']
    df ['Microprice']= (df['Close'])- ((df['High']+df['Low'])/2)
    p=(np.sign(df['Mid_price_log_return'])+1)/2
    df ['Entropy_of_returns']= -p*np.log2(p+1e-9)+(1-p)*np.log2(1-p+1e-9)
    df['Target'] = (df['Close'].shift(-1) > df['Close']).astype(int)
    
    df= df.dropna()
    return df

def train_all_four_models(df):
    #Four models to be trained.
    #Fast path relies on add/sub functions. Slow path uses RSI loops and intensive variances to show area-latency trade off

    f3_features = ['Microprice', 'High_low_spread', 'moving_average_10']
    f13_features = ['Mid_price_log_return', 'High_low_spread', 'moving_average_10', 'moving_average_30', 'moving_average_60', 'Relative_strength_index', 'Buy_volume_ratio', 'Order_flow_imbalance', 'Vol_weighted_avg_price', 'Amihud_illiquidity_ratio', 'Microprice', 'Entropy_of_returns', 'Volume']

   # Prepare data
    X_f3 = df[f3_features]
    X_f13 = df[f13_features]
    y = df['Target']
    
    # Clean data
    X_f3 = X_f3.replace([np.inf, -np.inf], np.nan).dropna()
    X_f13 = X_f13.replace([np.inf, -np.inf], np.nan).dropna()
    
    # Use common index
    common_index = X_f3.index.intersection(X_f13.index)
    X_f3 = X_f3.loc[common_index]
    X_f13 = X_f13.loc[common_index]
    y = y.loc[common_index]
    
    # Split (70-30)
    split_point = int(len(X_f3) * 0.7)
    
    X_f3_train, X_f3_test = X_f3[:split_point], X_f3[split_point:]
    X_f13_train, X_f13_test = X_f13[:split_point], X_f13[split_point:]
    y_train, y_test = y[:split_point], y[split_point:]


  # ==========================================
    # MODEL 1: LR with F3
    # ==========================================
    print("\n" + "="*50)
    print("MODEL 1: Logistic Regression with F3 (3 features)")
    print("="*50)
    
    scaler_f3 = StandardScaler()
    X_f3_train_scaled = scaler_f3.fit_transform(X_f3_train)
    X_f3_test_scaled = scaler_f3.transform(X_f3_test)
    
    lr_f3 = LogisticRegression(max_iter=500, random_state=42)
    lr_f3.fit(X_f3_train_scaled, y_train)
    
    acc_lr_f3 = lr_f3.score(X_f3_test_scaled, y_test)
    print(f"Test Accuracy: {acc_lr_f3:.4f}")
    
    # Save
    joblib.dump(lr_f3, os.path.join(model_location, 'lr_f3.pkl'))
    joblib.dump(scaler_f3, os.path.join(model_location, 'scaler_f3.pkl'))
    np.save(os.path.join(model_location, 'X_test_f3.npy'), X_f3_test_scaled[:100])
    np.save(os.path.join(model_location, 'y_test_f3.npy'), y_test[:100].values)
    
    # ==========================================
    # MODEL 2: LR with F13
    # ==========================================
    print("\n" + "="*50)
    print("MODEL 2: Logistic Regression with F13 (13 features)")
    print("="*50)
    
    scaler_f13 = StandardScaler()
    X_f13_train_scaled = scaler_f13.fit_transform(X_f13_train)
    X_f13_test_scaled = scaler_f13.transform(X_f13_test)
    
    lr_f13 = LogisticRegression(max_iter=500, random_state=42)
    lr_f13.fit(X_f13_train_scaled, y_train)
    
    acc_lr_f13 = lr_f13.score(X_f13_test_scaled, y_test)
    print(f"Test Accuracy: {acc_lr_f13:.4f}")
    
    # Save
    joblib.dump(lr_f13, os.path.join(model_location, 'lr_f13.pkl'))
    joblib.dump(scaler_f13, os.path.join(model_location, 'scaler_f13.pkl'))
    np.save(os.path.join(model_location, 'X_test_f13.npy'), X_f13_test_scaled[:100])
    np.save(os.path.join(model_location, 'y_test_f13.npy'), y_test[:100].values)
    
    # ==========================================
    # MODEL 3: MLP with F3
    # ==========================================
    print("\n" + "="*50)
    print("MODEL 3: MLP with F3 (3 features)")
    print("="*50)
    
    mlp_f3 = Sequential([
        Dense(8, input_shape=(3,), activation='relu', name='hidden1'),
        Dense(4, activation='relu', name='hidden2'),
        Dense(1, activation='sigmoid', name='output')
    ])
    
    mlp_f3.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    mlp_f3.fit(X_f3_train_scaled, y_train, epochs=10, batch_size=2048, verbose=1)
    
    _, acc_mlp_f3 = mlp_f3.evaluate(X_f3_test_scaled, y_test, verbose=0)
    print(f"Test Accuracy: {acc_mlp_f3:.4f}")
    
    # Save
    mlp_f3.save(os.path.join(model_location, 'mlp_f3.h5'))
    
    # ==========================================
    # MODEL 4: MLP with F13
    # ==========================================
    print("\n" + "="*50)
    print("MODEL 4: MLP with F13 (13 features)")
    print("="*50)
    
   mlp_f13 = Sequential
([
        # Layer 1: 64 Neurons (Was 16) - Capture broad patterns
        Dense(64, input_shape=(13,), activation='relu', name='hidden1'),
        
        # Layer 2: 32 Neurons (Was 8) - Refine features
        Dense(32, activation='relu', name='hidden2'),
        
        # Layer 3: 16 Neurons (New Layer) - Deep reasoning
        Dense(16, activation='relu', name='hidden3'),
        
        # Output
        Dense(1, activation='sigmoid', name='output')
    ])
    mlp_f13.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    mlp_f13.fit(X_f13_train_scaled, y_train, epochs=10, batch_size=2048, verbose=1)
    
    _, acc_mlp_f13 = mlp_f13.evaluate(X_f13_test_scaled, y_test, verbose=0)
    print(f"Test Accuracy: {acc_mlp_f13:.4f}")
    
    # Save
    mlp_f13.save(os.path.join(model_location, 'mlp_f13.h5'))
    
    # ==========================================
    # SUMMARY
    # ==========================================
    print("\n" + "="*50)
    print("SUMMARY OF ALL MODELS")
    print("="*50)
    print(f"Setup A (F3+LR):   Accuracy = {acc_lr_f3:.4f}")
    print(f"Setup B (F13+LR):  Accuracy = {acc_lr_f13:.4f}")
    print(f"Setup C (F3+MLP):  Accuracy = {acc_mlp_f3:.4f}")
    print(f"Setup D (F13+MLP): Accuracy = {acc_mlp_f13:.4f}")
    
    # Save summary
    summary = pd.DataFrame({
        'Setup': ['A', 'B', 'C', 'D'],
        'Features': ['F3', 'F13', 'F3', 'F13'],
        'Model': ['LR', 'LR', 'MLP', 'MLP'],
        'Accuracy': [acc_lr_f3, acc_lr_f13, acc_mlp_f3, acc_mlp_f13],
        'Latency_Cycles': [0, 0, 0, 0],  # Fill in after synthesis
        'LUT': [0, 0, 0, 0],
        'DSP': [0, 0, 0, 0]
    })
    summary.to_csv(os.path.join(model_location, 'model_summary.csv'), index=False)
    
    return summary

if __name__ == "__main__":
    # Load and prepare data
    print("Loading data...")
    df = combine_data(data_location)
    df = finance_features(df)
    
    # Train all models
    summary = train_all_four_models(df)
    
    print("\n All models trained and saved!")
    print(f" Location: {model_location}")