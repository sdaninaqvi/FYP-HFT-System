#This code cleans the data for Binance BTCUSDT data.
#It loads through the 1 second data for the year 2023. It then cleans it and turns into time series data.

import pandas as pd
import os
import requests
import numpy as np
from datetime import datetime

def DataToBeDownloaded(DownloadPathway, PathLocation, NameOfFile):

   #Function checks if file exists and if not then downloads it from Binance site.
        if not os.path.exists(PathLocation):
            print(f"File is being downloaded: {NameOfFile}")
            #This downloads file from site
            response = requests.get(DownloadPathway)

            if response.status_code == 200:
            #File has to be opened in the binary format to be written.
                with open(PathLocation, 'wb') as file:
                    file.write(response.content)

            else:
                print(f"File couldn't be downloaded. Error with status code or code. Check code or file location. {NameOfFile}. Status code is: {response.status_code}")

        else:
            print(f"File already has been created hence this can be ignored  : {NameOfFile}")


def DataCleaner(PathOfFile, CleanedDataLocation):
# This function cleans a single days data and saves it

    #Column names need to be listed down otherwise the data will be all over the place and a mess.

    NamesOfColumns = ['OpenTime', 'Open', 'High', 'Low', 'Close', 'Volume', 'CloseTime', 'QuoteAssetVolume', 'NumberOfTrades', 'TakerBuyBaseAssetVolume', 'TakerBuyQuoteAssetVolume', 'ignore']

    #DataFrame allows spreadsheet of code to be created and allows panda to read CSV files.

    df = pd.read_csv(PathOfFile, names=NamesOfColumns, header=None)

    #DataFrame now initially holds the data as a mess. The data needs to be sorted into date and time format.
    #The unit is set to milliseconds as that's the data that is being used. OpenTime is the column holding the data
    #pd.to_datetime changes that column into datetime format.

    df['OpenTime'] = pd.to_datetime(df['OpenTime'], unit='ms')

    #The next instruction sets the row numbers to be the datetime values. Inplace allows pandas to change the dataframe rather than make a new one.
    df.set_index('OpenTime', inplace=True)

    #Only the open, high, low, close and volume columns are needed for the analysis.
    df = df[['Open', 'High', 'Low', 'Close', 'Volume', 'TakerBuyBaseAssetVolume']]

    #The data will be scanned through using the for loop and turns them into numbers to later be able to be used for calculations.
    for column in df.columns:
        df[column] = pd.to_numeric(df[column], errors='coerce')

    #The data now needs to be scanned for any gaps and errors.
    #The df.fillna() function fills the gaps with the previous value.

    df.ffill(inplace=True)
    #The data should now be cleaned.

    print(df.isnull().sum())

    #Data being stored as csv file.
    df.to_csv(CleanedDataLocation)

    print(f"Data is being saved to: {CleanedDataLocation}")
    


def FullProcess():
#Loops through all dates one by one to first be downloaded and then cleaned and stored in processed data folder.

#Creates list of dates to download
    DatesToDownload= pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')


#Loops through each date    
    for date in DatesToDownload:
        DateInYMD= date.strftime('%Y-%m-%d')
        print(f"\n-- Starting the full data clean for date: {DateInYMD} ")
#List of all the pathways and where to download from.
        NameOfFile= f'BTCUSDT-1s-{DateInYMD}.zip'
        PathOfRawData= f'C:/Users/nhnaq/Desktop/Project/Data/Raw Data/BTCUSDT-1s-{NameOfFile}.zip'
        PathOfProcessedData= f'C:/Users/nhnaq/Desktop/Project/Data/Processed Data + TBBAV/BTCUSDT-1s-{DateInYMD}_Cleaned.csv'
        DownloadPathway= f'https://data.binance.vision/data/spot/daily/klines/BTCUSDT/1s/{NameOfFile}'

        DataToBeDownloaded(DownloadPathway, PathOfRawData, NameOfFile)

#Checks if the file for the raw data has been downloaded and then begins to clean
        if os.path.exists(PathOfRawData):
            print(f"\n Data for {DateInYMD} has been downloaded successfully. Starting data cleaning.")
            DataCleaner(PathOfRawData, PathOfProcessedData)
#If the data has not been downloaded then it will automatically skip this data
        else:
            print(f"\n Data for {DateInYMD} couldn't be downloaded.Skipping data cleaning for this date.")

    
    print("\n All dates fully downloaded and cleaned. Check processed data folder manually for each day")

#Full process can start
FullProcess()
#C:\Users\nhnaq\Desktop\Project\Data\Processed Data + TBBAV
#Had to ammend code to add TBBAV
