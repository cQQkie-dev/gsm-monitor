#!/usr/bin/env python3
import os
import subprocess
import argparse
import textwrap

import numpy as np
import pandas as pd
import logging
import seaborn as sns
import matplotlib.pyplot as plt
import datetime


def argument_parser():
    parser = argparse.ArgumentParser(description=textwrap.dedent('''\
                                     Write GSM Cipher Mode Command packets to a file and optionally
                                     compares the appearance of A5/1 and A5/3 ciphers over time.
                                     For valid argument format of frequency and gain args, see 'grgsm_livemon -h'.
                                     Requires tshark and grgsm_livemon to be installed.
                                     Consult the README for more information.
                                    '''), formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument(
        "-f", "--fc", dest="frequency", type=str, help="GSM frequency in Hz [default=%(default)r]", default="933.4e6")
    parser.add_argument(
        "-d", "--dur", dest="duration", type=int, help=f"Duration of the capture in seconds [default=%(default)rs]",
        default=1800)
    parser.add_argument(
        "-o", "--output", dest="output", help="Output file name [default=%(default)r]", default="capture.csv")
    parser.add_argument(
        "--format", dest="fileformat", type=str, help="Output file format, either 'csv' or 'json' "
                                                      "[default=%(default)r]", default="csv")
    parser.add_argument(
        "-g", "--gain", dest="gain", help="Set gain [default=%(default)r]", default=30)
    parser.add_argument("-a", "--analyze", dest="analyze", type=bool, help="Analyze the output"
                                                                           " file [default=%(default)r]", default=False)
    parser.add_argument("-iv", "--interval", dest="interval", type=int, help="Time interval in minutes to group by"                          
                                                                             " [default=%(default)r]", default=3)
    parser.add_argument("-i", "--input", dest="input", type=str, help='''Input file name to analyze, must be .csv
or .json recorded with this script 
[default=%(default)r]
     ''', default=None)
    return parser


args = argument_parser().parse_args()

tshark_args_csv = [
    "tshark", "-i", "lo", "-f", "udp", "-a", f"duration:{args.duration}", "-w", "-", "|",
    "tshark",
    "-r", "-",  # Read from stdin
    "-l",  # Flush output for each packet
    "-T", "fields",  # Output as fields
    "-Y", "gsm_a.rr.algorithm_identifier",  # Filter for Cipher Mode Command A5/1 (==0) and A5/3 (==2)
    "-e", "gsm_a.rr.algorithm_identifier",  # Output algorithm identifier
    "-e", "frame.number",  # Output frame number
    "-e", "frame.time",  # Output frame time
    "-E", "header=y",  # Output header
    "-E", "separator=,",  # Output separator
    "-E", "quote=d",  # Output quote
    "-E", "occurrence=f",  # Output occurrence
    ">", args.output  # Write to file
]

tshark_args_json = [
    "tshark", "-i", "lo", "-f", "udp", "-a", f"duration:{args.duration}", "-w", "-", "|",
    "tshark",
    "-r", "-",  # Read from stdin
    "-l",  # Flush output for each packet
    "-Y", "gsm_a.rr.algorithm_identifier",  # Filter for Cipher Mode Command A5/1 (==0) and A5/3 (==2)
    "-T", "ek",  # Output as JSON
    "-e", "gsm_a.rr.algorithm_identifier",  # Output algorithm identifier
    "-e", "frame.number",  # Output frame number
    "-e", "frame.time",  # Output frame time
    ">", args.output  # Write to file
]
logging_format = "%(asctime)s: %(message)s"
#logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")

if args.output and not args.input:
    logging.info(f"Writing to file at {os.getcwd()}/{args.output}")
    if args.fileformat == "csv":
        logging.info("Capturing...")
        p_tshark = subprocess.Popen(" ".join(tshark_args_csv), shell=True)
    elif args.fileformat == "json":
        logging.info("Capturing...")
        p_tshark = subprocess.Popen(" ".join(tshark_args_json), shell=True)
    else:
        print("File format must be either 'csv' or 'json'!")
        exit(1)

    logging.info("Monitoring...")
    p_grgsm = subprocess.Popen(["grgsm_livemon", "-f", args.frequency])

    p_tshark.wait()
    logging.info("Done capturing. Exiting...")
    p_grgsm.kill()
    logging.info("Done monitoring. Exiting...")

if args.analyze:
    if args.input:
        file = os.path.basename(args.input)
    elif args.ouput:
        file = os.path.basename(args.output)
    logging.info("Analyzing...")
    # Read csv file into dataframe
    df = pd.read_csv(file)
    ## Split file ending from file name
    file = file.split(".")[0]
    # Clean up dataframe
    df["frame.time"] = pd.to_datetime(df["frame.time"], format='%b %d, %Y %H:%M:%S.%f CET')
    # Rename columns
    df.rename(columns={"gsm_a.rr.algorithm_identifier": "algorithm", "frame.number": "frame_number",
                       "frame.time": "timestamp"}, inplace=True)
    # Create new column a5_1 and a5_3 for A5/1 and A5/3 respectively with integer values
    df["a5_1"] = np.where(df["algorithm"] == 0, 1, 0)
    df["a5_3"] = np.where(df["algorithm"] == 2, 1, 0)
    # Drop columns we don't need anymore
    df.drop(columns=["algorithm", "frame_number"], inplace=True, axis=1)
    # Write out cleaned dataframe
    df.to_csv(f"{os.getcwd()}/cleaned_{file}.csv", index=False)
    # Group by timestamp and sum the values of a5_1 and a5_3 and timeinterval of x minutes
    df_grouped = df.groupby(pd.Grouper(key='timestamp', freq=f'{args.interval}T')).sum().reset_index(drop=False, inplace=False)
    df_grouped.to_csv(f"{os.getcwd()}/interval_{file}.csv", index=False)
    logging.info("Done analyzing.")
    #sns.lineplot(data=df)
    # show header of df_grouped
    #print(df_grouped.head(5))
    #melt_df = pd.melt(df_grouped, ['timestamp'])
    #print(melt_df.head(5))
    #print(melt_df.tail(5))
    # Plotting cumulative sum of A5/1 and A5/3 over time in chosen intervals
    sns.lineplot(x="timestamp", y="value", hue="variable", data=pd.melt(df_grouped, ['timestamp']))
    #plt.show()
    plt.title(f"Cumulative sum of Cipher Mode Commands in {args.interval} minute intervals")
    plt.xlabel("Time from Nov 14 to Nov 21 (each in the morning)")
    plt.ylabel("No. of CMCs")
    # Change figure size to make it more readable
    plt.gcf().set_size_inches(13, 8)
    # Set xticks to timestamps using hour:minute:second format
    plt.xticks(df_grouped["timestamp"], df_grouped["timestamp"].dt.strftime("%d:%m_%H:%M:%S"), rotation=45)
    # Change size of xticks to make them more readable
    plt.tick_params(axis='x', which='major', labelsize=6)
    # Show only 10 xticks
    plt.locator_params(axis='x', nbins=20)
    # choose same color for legend and lines and place legend in plot
    plt.legend(labels=["A5/1", "A5/3"], loc="upper right")
    # Label color for legend symbols, use same color as lines
    plt.gca().get_legend().legend_handles[0].set_color('blue')
    plt.gca().get_legend().legend_handles[1].set_color('orange')
    # change legend handle size to default
    plt.gca().get_legend().legend_handles[0]._sizes = [6]
    plt.gca().get_legend().legend_handles[1]._sizes = [6]
    # add a grid
    plt.grid()
    #plt.show()


    # Save plot to file
    logging.info(f"Saving plot to file at {os.getcwd()}/{file}.png")
    # Save plot to file with high dpi
    plt.savefig(f"plot_{file}.png", dpi=600)




    # Plotting percentage of A5/1 and A5/3 of all Cipher Mode Commands over time in chosen intervals
    df_grouped["a5_1_percentage"] = df_grouped["a5_1"] / (df_grouped["a5_1"] + df_grouped["a5_3"])
    df_grouped["a5_3_percentage"] = df_grouped["a5_3"] / (df_grouped["a5_1"] + df_grouped["a5_3"])
    df_grouped.drop(columns=["a5_1", "a5_3"], inplace=True, axis=1)
    #print(df_grouped.head(5))
    # Make new plot only showing the percentages
    plt.clf()
    sns.lineplot(x="timestamp", y="a5_1_percentage", data=df_grouped)
    plt.title(f"Percentage of A5/1 and A5/3 of all Cipher Mode Commands in {args.interval} minute intervals")
    plt.xlabel("Time from Nov 14 to Nov 21 (each in the morning)")
    plt.ylabel("Percentage")
    plt.xticks(df_grouped["timestamp"], df_grouped["timestamp"].dt.strftime("%d:%m_%H:%M:%S"), rotation=45)
    plt.tick_params(axis='x', which='major', labelsize=6)
    plt.locator_params(axis='x', nbins=20)
    plt.grid()
    plt.savefig(f"plot_percentage_{file}.png")

