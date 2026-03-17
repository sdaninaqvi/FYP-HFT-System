import pandas as pd
import numpy as np
import os
import joblib #Stores trained model to file
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import StandardScaler


data_location= r'C:\Users\nhnaq\Desktop\Daniyal\Project\Data\Processed Data + TBBAV' #This needs to be updated each time i want a different set of data to be used.
model_location= r'C:\Users\nhnaq\Desktop\Daniyal\Project\Trained Data'

os.makedirs(model_location, exist_ok=True)


def combine_data (data_location):
    #since files currently split by day this combines them together
    dataframes= []
    file_count=0
    for filename in os.listdir(data_location):
        if filename.endswith('.csv'):
            file_location= os.path.join(data_location, filename)
            df= pd.read_csv(file_location)
            dataframes.append(df)
            file_count +=1

        if file_count>=30: #update each time
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
    df ['relative_strength']= rolling_gain/ rolling_loss
    df ['moving_average_10']= df['Close'].rolling(window=10).mean()
    df ['moving_average_30']= df['Close'].rolling(window=30).mean()
    df ['moving_average_60']= df['Close'].rolling(window=60).mean()
    df ['Relative_strength_index']= 100.0 - (100.0/(1.0 + df['relative_strength']))
    df ['Buy_volume_ratio']= df['TakerBuyBaseAssetVolume']/ df['Volume']
    df ['Order_flow_imbalance']= df['TakerBuyBaseAssetVolume']-(df['Volume']-df['TakerBuyBaseAssetVolume'])
    df ['Vol_weighted_avg_price']= (((df['High'])+ df['Low'] + df['Close'])/3)
    df ['Amihud_illiquidity_ratio']= df['Mid_price_log_return'].abs()/ df['Volume']
    df ['Microprice']= (df['Close'])- ((df['High']+df['Low'])/2)
    p=(np.sign(df['Mid_price_log_return'])+1)/2
    df ['Entropy_of_returns']= -p*np.log(p+1e-9)-(1-p)*np.log(1-p+1e-9)
    df['Target'] = (df['Close'].shift(-1) > df['Close']).astype(int)
    
    df
    df= df.dropna()
    return df

def train_model(df, dataset_name=('default')):

    featureslist=['Mid_price_log_return', 'High_low_spread', 'relative_strength', 'moving_average_10', 'moving_average_30', 'moving_average_60', 'Relative_strength_index', 'Buy_volume_ratio', 'Order_flow_imbalance', 'Vol_weighted_avg_price', 'Amihud_illiquidity_ratio', 'Microprice', 'Entropy_of_returns']

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

    print("Training LR model")
    lr=LogisticRegression(max_iter=500)
    lr.fit(x_train_scaled, y_train)

    training_predictions= lr.predict(x_train_scaled)
    training_accuracy= accuracy_score(y_train, training_predictions)
    print (f'Training accuracy is {training_accuracy: .5f}')
    
    testing_predictions= lr.predict(x_test_scaled)
    testing_accuracy=accuracy_score(y_test, testing_predictions)

    print(f"\n Test accuracy is: {testing_accuracy: .5f}")
    print(classification_report(y_test, testing_predictions))

    model_filename= f'logistic_regression_model{dataset_name}.pkl'
    scaler_filename= f'scaler{dataset_name}.pkl'

    joblib.dump(lr, os.path.join(model_location, model_filename))
    joblib.dump(scaler, os.path.join(model_location, scaler_filename))
    print("\n \n \nModel and scaler saved to {model_location}")

    return lr, scaler

if __name__ == "__main__":
    df=combine_data(data_location)

    df=finance_features(df)

    model, scaler= train_model(df, dataset_name= "jan_2023") #update to new date each time
