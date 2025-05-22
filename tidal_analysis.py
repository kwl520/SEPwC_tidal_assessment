# import the modules you need here
import argparse
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import wget
import os
import numpy as np
import uptide
import pytz
import math
import glob
import datetime
import pytest


def read_tidal_data(filename):
    # Create error message if file not found
    if not os.path.exists(filename):
        raise FileNotFoundError(f'Error: File not found: {filename}')
    else:
        column_names = ['Date_Col', 'Time', 'Sea Level', 'Flag']
        parse_dates={'Datetime': ['Date_Col', 'Time']} #Combines 'Date_Col' and 'Time-Col' into a new 'Datetime' column      
        na_values=['M', 'N', 'T']
        data = pd.read_csv(filename, sep=r'\s+', skiprows=11, names=column_names, na_values=na_values)
        data['Datetime'] = pd.to_datetime(data['Date_Col'] + ' ' + data['Time'])
        data.set_index('Datetime', inplace=True)
        data['Sea Level'] = pd.to_numeric(data['Sea Level'], errors='coerce')
        """data = data.drop(columns=['Date_Col', 'Flag'], errors='ignore')"""
        return data
    def test_missing_file_raises_filenotfound():
        'Tests that the read_tidal_data rasies FileNotFoundError'
        with pytest.raises(FileNotFoundError):
            read_tidal_data('missing_file.dat')
    return data


def extract_single_year_remove_mean(year, data):
    

    return 


def extract_section_remove_mean(start, end, data):
    

    return 


def join_data(data1, data2):
   combined_data = [data1, data2]
   return pd.concat(combined_data).sort_index()


def sea_level_rise(data):

                                                     
    return 


def tidal_analysis(data, constituents, start_datetime):


    return 


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
   # Defining dirname 
    """dirname = os.path.dirname(__file__)
    print(dirname)
    """
    
   
   # glob dir to grab all *.txt files
    filelist = glob.glob(os.path.join(dirname, '**/*.txt'), recursive = True)
   
    if filelist:
       main_data = read_tidal_data(filelist[0])
       for single_file in filelist[1:]:
           data = read_tidal_data(single_file)
           main_data = join_data(main_data, data)
        
      
    
           

        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
    

