#!/usr/bin/env python3
import os
import argparse
import textwrap

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import datetime

# rewrite create_plot.py
# first need to load csv file(s) and then plot them
# this script will be called by the main script

# I want to either pass an directory of csv files or a single file as an argument
# if a directory is passed, I want to loop over all files in the directory
# if a single file is passed, I want to just load that file

# For deciding which files to load, I will use the argparse module
# I will use the pandas module to load the csv files
# I will use the matplotlib module to plot the data

def argument_parser():
    parser = argparse.ArgumentParser(
        prog="create_plot.py",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent('''\
            This script will create a plot from one or more csv files.
            You can pass either a directory of csv files or a single csv file.
            If a directory is passed, all csv files from the same BTS will be plotted.
            If there are multiple BTSs in the directory, these will be grouped and plotted separately.
            '''),
        epilog=textwrap.dedent('''\
            Examples:
            create_plot.py -d data/
            create_plot.py -f data.csv
            ''')
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-d", "--directory", help="Directory containing csv files")
    group.add_argument("-f", "--file", help="Single csv file")
    # add optional argument to specify the time interval to group by
    parser.add_argument("-iv", "--interval", dest="interval", type=int, help="Time interval in minutes to group by"                          
                                                                              " [default=%(default)r]", default=3)
    return parser

def sort_csv_by_bts(directory)->dict:
    # file names will have the following format tshark_944.2M_262_2_0x10c3_0x23a1_1717511213
    # read all csv files in the directory with the same frequency, mcc, mnc, lac, and cell_id
    # into a pandas dataframe, then save the dataframe as new csv file
    # and return the dataframes
    # list of files in the directory
    files = os.listdir(directory)
    # filter out only csv files
    files = [file for file in files if file.endswith(".csv")]
    # create a list to store the dataframes
    dataframes = {}
    same_bts = {}
    for file in files:
        # Extract the frequency, mcc, mnc, lac, and cell_id from the file name
        # and use these as the keys to group the dataframes
        # frequency, mcc, mnc, lac, cell_id = file.split("_")[1:6]
        # key = (frequency, mcc, mnc, lac, cell_id)

        frequency, _, provider, lac = file.split("_")[1:5]
        key = f"{frequency}_{provider}_{lac}"
        same_bts.setdefault(key, []).append(file)
    for key, files in same_bts.items():
        # read all csv files into a pandas dataframe
        df = pd.concat([pd.read_csv(os.path.join(directory, file)) for file in files], ignore_index=True)
        dataframes[key] = df
    # for key, df in dataframes.items():
    #     # save the dataframe as a new csv file
    #     df.to_csv(f"{directory}/new_{key}.csv", index=False)
    return dataframes

def clean_data(df)->pd.DataFrame:
    try:
        df["frame.time"] = pd.to_datetime(df["frame.time"], format='%b %d, %Y %H:%M:%S.%f CEST')
    except ValueError:
        try:
            df["frame.time"] = pd.to_datetime(df["frame.time"], format='%b %d, %Y %H:%M:%S.%f BST')
        except ValueError:
            df["frame.time"] = pd.to_datetime(df["frame.time"], format='%b %d, %Y %H:%M:%S.%f CET')
            
    df.rename(columns={"gsm_a.rr.algorithm_identifier": "algorithm", "frame.number": "frame_number",
                    "frame.time": "timestamp"}, inplace=True)
    # Create new column a5_1, a5_3 and a5_4 for A5/1, A5/3 and A5/4 respectively with integer values
    df["a5_1"] = np.where(df["algorithm"] == 0, 1, 0)
    df["a5_3"] = np.where(df["algorithm"] == 2, 1, 0)
    df["a5_4"] = np.where(df["algorithm"] == 3, 1, 0)
    # Drop columns we don't need anymore
    df.drop(columns=["algorithm", "frame_number"], inplace=True, axis=1)
    return df
    

def main():
    args = argument_parser().parse_args()
    # Mapping of MNC to provider
    provider_dict = {"1": "Telekom ", "2": "O2", "3": "Vodafone"}
    if args.directory:
        dataframes = sort_csv_by_bts(args.directory)
        
    else:
        dataframes = {}
        file = os.path.basename(args.file)
        df = pd.read_csv(file)
        frequency, _, provider, lac = file.split("_")[1:5]
        key = f"{frequency}_{provider}_{lac}"
        dataframes[key] = df
        
    for key, df in dataframes.items():
        df = clean_data(df)
        if args.directory:
            df.to_csv(f"{args.directory}/cleaned_{key}.csv", index=False)
        else:
            df.to_csv(f"cleaned_{key}.csv", index=False)
    
    # Group by timestamp and sum the values of a5_1, a5_3 and a5_4 and timeinterval of x minutes
    for key, df in dataframes.items():
        provider = provider_dict[key.split("_")[1]]
        if args.directory:
            pd.read_csv(f"{args.directory}/cleaned_{key}.csv")
        else:
            df = pd.read_csv(f"cleaned_{key}.csv")
        
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors='coerce')
        df.set_index("timestamp", inplace=True)
        resampled_data = df.resample(f'{args.interval}T').sum()
        plt.figure()
        plt.gcf().set_size_inches(20, 8)
        plt.plot(resampled_data.index.to_numpy(), resampled_data['a5_1'].to_numpy(), marker='o', linestyle='-')
        plt.plot(resampled_data.index.to_numpy(), resampled_data['a5_3'].to_numpy(), marker='o', linestyle='-', color='red')
        plt.plot(resampled_data.index.to_numpy(), resampled_data['a5_4'].to_numpy(), marker='o', linestyle='-', color='green')
        plt.title(f'Algorithm Occurrences for {provider} BTS in Euskirchen, LAC: {key.split("_")[2]} / Total Samples: {len(df)}')
        plt.xlabel('Time')
        plt.ylabel(f'Number of Cipher Mode Commands in {args.interval} minute intervals')
        plt.xticks(resampled_data.index, resampled_data.index.strftime("%d:%m_%H:%M:%S"), rotation=45)
        # Change size of xticks to make them more readable
        plt.tick_params(axis='x', which='major', labelsize=8)
        # Show only 10 xticks
        plt.locator_params(axis='x', nbins=20)
        plt.legend(['A5/1', 'A5/3', 'A5/4'])
        plt.grid(True)
        #plt.show()
        if args.directory:
            plt.savefig(f"{args.directory}/{key}.png")
        else:
            plt.savefig(f"{key}.png")
    
    
if __name__ == "__main__":
    main()