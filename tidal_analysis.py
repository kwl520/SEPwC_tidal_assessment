# import the modules you need here
import argparse
import datetime
import glob
import math
import os
import pytz
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
import pytest
import uptide
import wget
from scipy import stats

def read_tidal_data(filename):
    """
    Reads tidal data from multiple files in a directory, 
    processes it, and returns a pandas DataFrame.
   
    Parameters
    ----------
    filename : str
        The path to the text file containing the tidal data.

    Raises
    ------
    FileNotFoundError
        If the specified 'filename' cannot be found or does not exist.

    Returns
    -------
    data : pandas DataFrame
        The DataFrame will include processed tidal data, 
        with a DatetimeIndex and a 'Sea Level' column.
            Non- numeric entries (e.g. 'M', 'N' and 'T') will be converted to NaN.
    """
    # Check if file exists. If not, raise error message.
    if not os.path.exists(filename):
        raise FileNotFoundError(f'Error: File not found: {filename}')
    # Define expected column names
    column_names = ['Cycle', 'Date', 'Time', 'Sea Level', 'Residual']
    parse_dates={'Datetime': ['Date', 'Time']}
    # Specify non-numerical values that should be converted to NaN.
    na_values=['M', 'N', 'T']
    #Read the csv file data into a pandas DataFrame.
    data = pd.read_csv(filename, sep=r'\s+', skiprows=11, header = None, names=column_names, na_values=na_values)
    # Combine 'Date_Col' and 'Time' into a single string,
    # convert this into a datetime object,
    # and then set the 'Datetime' column as the DataFrame's index.
    data['Datetime'] = pd.to_datetime(data['Date'] + ' ' + data['Time'])
    data.set_index('Datetime', inplace=True)
    data['Sea Level'] = pd.to_numeric(data['Sea Level'], errors='coerce')
    return data

def extract_single_year_remove_mean(year, data):
    """
    Extracts 'Sea Level' data for a specific year from the DataFrame, then removes the mean.
    
    Parameters
    ----------
    year : integer
        The year for which to extract and process data.
    data : pd.DataFrame
       The source DataFrame containing 'Sea Level' data.

    Returns
    -------
    year_data : pandas.DataFrame
        A new DataFrame containing 'Sea Level' data for the specified year, 
        with its mean removed from the data. 
    """
    # Construct the start and end date strings and then,
    # extract data from DatetimeIndex,
    # and calculate the mean from every 'Sea Level' value in the DataFrame
    year_string_start = str(year)+"0101"
    year_string_end = str(year)+"1231"
    year_data = data.loc[year_string_start:year_string_end, ['Sea Level']]
    # remove mean to oscillate around zero
    mmm = np.mean(year_data['Sea Level'])
    year_data['Sea Level'] -= mmm
    return year_data

# Code from Gemini
def extract_section_remove_mean(start, end, data):
    """
    Extracts a specific time section of 'Sea Level' data from a DataFrme,
    and removes the mean of that section.
    
    Parameters
    ----------
    start : string
        The start date for the section in "YYYYMMDD" format.
    end : string
        The end date for the section in "YYYYMMDD" format.
    data : pandas DataFrame
        The source DataFrame containing 'Sea Level' data with a DatetimeIndex.

    Returns
    -------
    pandas DataFrame
    A new DataFrame containing the extracted 'Sea Level' data, 
    with its mean removed.
    """
    start_dt = pd.to_datetime(start, format='%Y%m%d')
    end_dt = pd.to_datetime(end, format='%Y%m%d') + pd.Timedelta(days=1) - pd.Timedelta(hours=1)
    extracted_section = data.loc[start_dt:end_dt].copy()
   
    if 'Sea Level' not in extracted_section.columns:
        raise ValueError("The 'Sea Level' column is missing in the provided data.")      
    section_mean = extracted_section['Sea Level'].mean()
    extracted_section['Sea Level'] -= section_mean
    return extracted_section


def join_data(data1, data2):
    """
     Combines two pandas DataFrames containing time-series data into one DataFrame. 
      
     Parameters
     ----------
     data1 : pandas Dataframe
         The first DataFrame to join. Expected to have a DatetimeIndex.
     data2 : pandas Dataframe
         The second DataFrame to join. Expected to have a DatetimeIndex.

     Returns
     -------
     pandas DataFrame
         A new DataFrame, combining all rows from data1 and data2, 
         and sorting them chronologically through their DatetimeIndex.
     """
    # Create a list with two DataFrames to be concatenated, 
    # stacking the DataFrames and ordering them chronologically.
    combined_data = [data1, data2]
    return pd.concat(combined_data).sort_index()
    
def sea_level_rise(data):
    """
    Calculates the slope and p-value of sea level rise using linear regression.
    
    Parameters
    ----------
    data : pandas.DataFrame
    A DataFrame containing at least 'Date' (as strings like 'YYYY-MM-DD'
    or 'YYYYMMDD'), 'Time' (as strings like 'HH:MM:SS'), and 'Sea Level' (float).

    Returns
    -------
    tuple: (slope, p_value) from the linear regression (two floats).
    """
    # Ensure 'Sea Level' is float and drop NaNs from it first
    df_clean = data.dropna(subset=['Sea Level'])
    df_clean['Combined_DateTime'] = pd.to_datetime(
    df_clean['Date'].astype(str) + ' ' + df_clean['Time'].astype(str),
    format='%Y/%m/%d %H:%M:%S',
    errors='coerce'
    )
    # Drop rows where datetime conversion failed
    df_clean = df_clean.dropna(subset=['Combined_DateTime'])   
    # Convert datetime objects to Matplotlib dates (floats) for linear regression
    x = mdates.date2num(df_clean['Combined_DateTime'].dt.to_pydatetime()) 
    y = df_clean['Sea Level'].values
    slope, _, _, p_value, _ = stats.linregress(x, y)
    return slope, p_value

def tidal_analysis(data, constituents, start_datetime):
    """
    Performs a tidal analysis on sea level data to extract amplitudes and phases
    for specified tidal constituents.

    Parameters
    ----------
    data : pandas DataFrame
        A DataFrame containing time series data, with a 'Sea Level' column and a 
        DatetimeIndex
    constituents : list of strings
       A list of tidal constituent names ('M2' and 'S2')
    start_datetime : datetime.datetime
        The exact datetime object representing the start time of the analysis period.

    Returns
    -------
    A tuple containing the calculated amplitudes and phases. 
    """
    # Drop rows where 'Sea Level' data is missing (NaN)
    data = data.dropna(subset=['Sea Level']).copy()
    #Initialises an Uptide Tides object, specifiying constituents and initial time
    tide = uptide.Tides(['M2', 'S2'])
    tide.set_initial_time(start_datetime)
    seconds_since = (
        data.index.astype('int64').to_numpy()/1e9
    ) - start_datetime.timestamp()
   # Extracts 'Sea Level] column values as a NumPy array
    sea_level_values = data['Sea Level'].to_numpy()
    amp, pha = uptide.harmonic_analysis(
        tide, 
        sea_level_values,
    seconds_since
    )
    return amp, pha
  
def get_longest_contiguous_data(data):


    return 


"""def find_txt_files(directory):
    return glob.glob(os.path.join(directory, '*.txt'))"""

if __name__ == '__main__':

  
    """
    parser = argparse.ArgumentParser(
    prog="UK Tidal analysis",
    description="Calculate tidal constiuents and RSL from tide gauge data",
    epilog="Copyright 2024, Jon Hill"
    )
       
   parser.add_argument("directory", default='/data',
   help="the directory containing txt files with data")
   parser.add_argument('-v', '--verbose',
   action='store_true',
   default=False,
   help="Print progress")
   
   args = parser.parse_args()
   dirname = args.directory
   verbose = args.verbose
   """
    dirname = 'data'
    verbose = False
  
    
   # glob dir to grab all *.txt files
    filelist = glob.glob(os.path.join(dirname, '**/*.txt'), recursive = True)
   
    if filelist:
        main_data = read_tidal_data(filelist[0])
        for single_file in filelist[1:]:
            data = read_tidal_data(single_file)
            main_data = join_data(main_data, data)
                