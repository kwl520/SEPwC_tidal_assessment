'Copyright 2025, Lois Cole'
# import the modules you need here
import argparse
import datetime
import glob
import os
import pytz
import matplotlib.dates as mdates
import pandas as pd
import uptide
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
    # Define expected column names.
    column_names = ['Cycle', 'Date', 'Time', 'Sea Level', 'Residual']
    # Specify non-numerical values that should be converted to NaN.
    na_values=['M', 'N', 'T']
    # Read the csv file data into a pandas DataFrame.
    data = pd.read_csv(filename, sep=r'\s+', skiprows=11, header = None,
                       names=column_names, na_values=na_values)
    # Combine 'Date' and 'Time' into a single string,
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
    # Construct the start and end date strings,
    # and then extract data from DatetimeIndex,
    # and calculate the mean from every 'Sea Level' value in the DataFrame.
    year_data = data.loc[str(year), ['Sea Level']].copy()
    year_data['Sea Level'] -= year_data['Sea Level'].mean()
    return year_data

# Code from Gemini
def extract_section_remove_mean(start, end, data):
    """
    Extracts a specific time section of 'Sea Level' data from a DataFrame,
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
    # Convert start and end date strings to datetime.
    start_dt = pd.to_datetime(start, format='%Y%m%d')
    end_dt = pd.to_datetime(end, format='%Y%m%d') + pd.Timedelta(days=1) - pd.Timedelta(hours=1)
    extracted_section = data.loc[start_dt:end_dt].copy()
    if 'Sea Level' not in extracted_section.columns:
        raise ValueError("The 'Sea Level' column is missing in the provided data.")
    # Remove the mean from 'Sea Level' data.
    extracted_section['Sea Level'] -= extracted_section['Sea Level'].mean()
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
    # Ensure 'Sea Level' is float and drop NaNs from it first.
    df_clean = data.dropna(subset=['Sea Level']).copy()
    df_clean['Combined_DateTime'] = pd.to_datetime(
    df_clean['Date'].astype(str) + ' ' + df_clean['Time'].astype(str),
    format='%Y/%m/%d %H:%M:%S',
    errors='coerce'
    )
    # Drop rows where datetime conversion failed.
    df_clean = df_clean.dropna(subset=['Combined_DateTime'])
    # Convert datetime objects to Matplotlib dates (floats) for linear regression.
    x = mdates.date2num(df_clean.index.to_pydatetime())
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
        DatetimeIndex.
    constituents : list of strings
       A list of tidal constituent names ('M2' and 'S2')
    start_datetime : datetime.datetime
        The exact datetime object representing the start time of the analysis period.

    Returns
    -------
    A tuple containing the calculated amplitudes and phases. 
    """
    _ = datetime.datetime
    # Drop rows where 'Sea Level' data is missing (NaN).
    data = data.dropna(subset=['Sea Level']).copy()
    _ = pytz.utc
    # Initialises an Uptide Tides object, specifiying constituents and initial time.
    data.index = data.index.tz_localize('utc')
    tide = uptide.Tides(constituents)
    tide.set_initial_time(start_datetime)
    seconds_since = (
        data.index.astype('int64').to_numpy()/1e9
    ) - start_datetime.timestamp()
    # Extracts 'Sea Level' column values as a NumPy array.
    sea_level_values = data['Sea Level'].to_numpy()
    amp, pha = uptide.harmonic_analysis(
        tide,
        sea_level_values,
    seconds_since
    )
    return amp, pha

def get_longest_contiguous_data(data):
    """
    Identifies and returns the longest contiguous segment of data
    from the input DataFrame.
    The segment starts at the beginning of the DataFrame and ends
    just before the first encountered NaN or invalid data point.
    
    Parameters
    ----------
    data : pandas.DataFrame
        Input DataFrame expected to have a DatetimeIndex and a 'Sea Level' column.
    
    Returns
    -------
    pandas.DataFrame
        The longest contiguous segment of the input DataFrame where 'Sea Level' is not NaN.
        Returns an empty DataFrame if the input is empty or contains no valid contiguous segments.
     """
    nan_indices = data['Sea Level'].isna()
    if nan_indices.any():
        # Get the index of the first True (first NaN).
        first_nan_idx_in_series = nan_indices[nan_indices].index[0]
        # Get the positional integer index of this NaN in the DataFrame's index.
        stop_idx_loc = data.index.get_loc(first_nan_idx_in_series)
        # Slice the DataFrame up to (but not including) this position.
        return data.iloc[:stop_idx_loc]
    return data.copy()

if __name__ == '__main__':
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
    input_directory = args.directory
    is_verbose = args.verbose
    # Ensure the directory exists
    if not os.path.isdir(input_directory):
        print(f"Error: Directory not found: {input_directory}")

    filelist = glob.glob(os.path.join(input_directory, '**/*.txt'), recursive=True)
    # Code from gemini.
    if is_verbose:
        print(f"Found {len(filelist)} data files. Compiling...")
    # Store dataframes in a dictionary, grouped by their locations.
    location_data = {}
    # Iterate through each file in the provided list.
    for file_path in filelist:
        try:
            current_df = read_tidal_data(file_path)
            if not current_df.empty:
                # Extract and format location name from the file path.
                location_name = os.path.basename(os.path.dirname(file_path)
                ).replace('_data.txt', '').capitalize()

                if location_name not in location_data:
                    location_data[location_name] = []
                location_data[location_name].append(current_df)

                if is_verbose:
                    print(f"Successfully read {file_path} for {location_name}.")
            # Warn if the DataFrame is empty.
            elif is_verbose:
                print(f"Warning: No valid data in {file_path}. Skipping.")
        # Handle specific exceptions during file processing.
        except FileNotFoundError as e:
            print(f"Error: File not found: {file_path}. {e}")
        except pd.errors.EmptyDataError:
            print(f"Error: {file_path} is empty or contains no data. Skipping.")
        except (pd.errors.ParserError, ValueError, KeyError) as e:
            print(f"Error: Malformed data in {file_path}. Details: {e}. Skipping.")

    # Process and print data for each location.
    for location, dfs in location_data.items():
        print(f"\n{'='*50}") # Separator for clarity
        print(f"--- Analysis for {location} ---")
        print(f"{'='*50}")

        # 1. Compiled Tidal Data Summary (Moved inside the loop)
        compiled_data = pd.concat(dfs).sort_index() if dfs else pd.DataFrame()
        print("\n--- Compiled Tidal Data Summary ---")
        if len(compiled_data) > 10: # Print head and tail for large dataframes
            print(compiled_data.head())
            print("...")
            print(compiled_data.tail())
        else: # Print entire dataframe if small
            print(compiled_data)
        print(f"Data range: {compiled_data.index.min().strftime('%Y-%m-%d %H:%M:%S')} to"
              "{compiled_data.index.max().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total data points: {len(compiled_data)}")
        print("---------------------------------")

        # 2. Sea Level Rise
        slope_val, p_value_val = sea_level_rise(compiled_data)
        if slope_val is not None and p_value_val is not None:
            print("\n--- Sea Level Rise ---")
            print(f"Calculated Sea Level Rise Slope for {location}: {slope_val:.6e} units/time")
            print(f"P-value for Sea Level Rise for {location}: {p_value_val:.4f}")

        # 3. Longest Contiguous Period of Data
        longest_contiguous_df = get_longest_contiguous_data(compiled_data)
        print("\n--- Longest Contiguous Period of Data ---")
        if not longest_contiguous_df.empty:
            start_date = longest_contiguous_df.index.min().strftime('%Y-%m-%d %H:%M:%S')
            end_date = longest_contiguous_df.index.max().strftime('%Y-%m-%d %H:%M:%S')
            duration = longest_contiguous_df.index.max() - longest_contiguous_df.index.min()
            print(f"For {location}:")
            print(f"  Start: {start_date}")
            print(f"  End: {end_date}")
            print(f"  Duration: {duration}")
            print(f"  Number of data points: {len(longest_contiguous_df)}")
