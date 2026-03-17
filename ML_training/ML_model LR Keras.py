import pandas as pd
import numpy as np
import os
import joblib #Stores trained model to file
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Activation
from tensorflow.keras.optimizers import Adam
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report


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

def train_keras_model(df, dataset_name=('default')):

    featureslist=['Mid_price_log_return', 'High_low_spread', 'moving_average_10', 'moving_average_30', 'moving_average_60', 'Relative_strength_index', 'Buy_volume_ratio', 'Order_flow_imbalance', 'Vol_weighted_avg_price', 'Amihud_illiquidity_ratio', 'Microprice', 'Entropy_of_returns']

    x=df[featureslist]
    y=df['Target']

    x = x.replace([np.inf, -np.inf], np.nan)
    x = x.dropna()
    y = y[x.index]


    split_train_data=int(len(x)*0.7)
    x_train, x_test = x[:split_train_data], x[split_train_data:]
    y_train, y_test = y[:split_train_data], y[split_train_data:]
    
    scaler=StandardScaler()
    x_train_scaled= scaler.fit_transform(x_train)
    x_test_scaled= scaler.transform(x_test)

    joblib.dump(scaler, os.path.join(model_location, f'scaler_{dataset_name}.pkl'))

    print("Training LR model")
    LR_model= Sequential()
    LR_model.add(Dense(1, input_shape=(len(featureslist),), activation='sigmoid', name='output_layer'))
    LR_model.compile(optimizer=Adam(learning_rate=0.01), loss= 'binary_crossentropy', metrics=['accuracy'])
    LR_model.fit(x_train_scaled, y_train, epochs=20, batch_size=32, verbose=0)
    LR_predictions=(LR_model.predict(x_test_scaled)>0.5).astype("int32")
    print(f"LR Accuracy: {accuracy_score(y_test, LR_predictions): .4f}")

    LR_model.save(f'Trained Data/keras_LR_{dataset_name}.h5')

   

    return LR_model, scaler

if __name__ == "__main__":
    print("Script started")
    df=combine_data(data_location)

    df=finance_features(df)

    train_keras_model(df, dataset_name= "April_2023") #update to new date each time
  