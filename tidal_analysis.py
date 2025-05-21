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

now = datetime.datetime.now()
print(now)

def read_tidal_data(filename):
    if not os.path.exists (filename):
        raise FileNotFoundError (f'Error: No .txt files found in the directory: {dirname}')
    else:
        main_data = read_tidal_data(filelist[0])
        for single_file in filelist[1:]:
            data = read_tidal_data(single_file)
            main_data = join_data(data, main_data)
    data = pd.read_csv(filename, sep=r'\s+', skiprows=11)
    print(data.index[0])
    (names = column_names,ArithmeticError
    parse_dates={'Datetime': ['Date', 'Time']}, 
    index_col='Datetime',                    
    na_values=['M', 'N', 'T'])
    
    print('Original DataFrame:')
    print(df)
    df.rename(columns={'old_'})
    
    
    def test_missing_file_raises_filenotfound():
        'Tests that the read_tidal_data rasies FileNotFoundError'
        with pytest.raises(FileNotFoundError):
            read_tidal_data('missing_file.dat')
    return data

#assert 'Sea Level' in columns
#Check for M, N and T data: should be Nan
#Error if file not found
  

def extract_single_year_remove_mean(year, data):
    return

def read_tidal_data(filename):
        with open(filename, 'r') as f:
            return f.readlines()
        return 



def extract_section_remove_mean(start, end, data):


    return 


def join_data(data1, data2):
    
    return 



def sea_level_rise(data):

                                                     
    return 


def tidal_analysis(data, constituents, start_datetime):


    return 


def get_longest_contiguous_data(data):


    return 


def find_txt_files(directory):
    return glob.glob(os.path.join(directory, '*.txt'))

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
                     prog="UK Tidal analysis",
                     description="Calculate tidal constiuents and RSL from tide gauge data",
                     epilog="Copyright 2024, Jon Hill"
                     )

    parser.add_argument("directory",
                    help="the directory containing txt files with data")
    parser.add_argument('-v', '--verbose',
                    action='store_true',
                    default=False,
                    help="Print progress")

    args = parser.parse_args()
    dirname = args.directory
    verbose = args.verbose
 
# Defining dirname 
dirname = os.path.dirname(__file__)
    
# glob dir to grab all *.txt files
filelist = glob.glob(os.path.join(dirname, '*.txt'))
main_data = read_tidal_data(filelist[0])
for single_file in filelist[1:]:
    data = read_tidal_data(single_file)
    main_data = join_data(data, main_data)
    

        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
    

