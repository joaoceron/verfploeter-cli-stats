#!/usr/bin/env python3
###############################################################################
# Verfploeter CLI 
# Thu Jul  4 13:43:19 UTC 2019
# @copyright sand-project.nl - Joao Ceron - ceron@botlog.org
###############################################################################

###############################################################################
### Python modules
import os
import sys
import pandas as pd
import argparse
import threading
import queue as queue
import time 
from argparse import RawTextHelpFormatter
from os import linesep
import imp
import logging

###############################################################################
### Program settings
verbose = False
version = 0.5
program_name = os.path.basename(__file__)
###############################################################################
### Subrotines


#------------------------------------------------------------------------------
def set_log_level(level=None):
    """Sets the log level of the notebook. Per default this is 'INFO' but
    can be changed.
    :param level: level to be passed to logging (defaults to 'INFO')
    :type level: str
    """
    imp.reload(logging)
#    logging.basicConfig(format='%(filename)s - %(asctime)s :  %(levelname)8s - %(message)s', "%Y-%m-%d %H:%M:%S",
#                        level=level)

#    formatter = logging.Formatter("%(asctime)s;%(levelname)s;%(message)s",
#                                          "%Y-%m-%d %H:%M:%S")

    logging.basicConfig(
	    level=logging.DEBUG,
	    format='%(asctime)s.%(msecs)03d %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S',
     )

#------------------------------------------------------------------------------
def parser_args ():

    #parser = argparse.ArgumentParser(prog=program_name, usage='%(prog)s [options]', formatter_class=RawTextHelpFormatter)
    parser = argparse.ArgumentParser(prog=program_name, usage='%(prog)s [options]')
    parser.add_argument("--version", help="print version and exit", action="store_true")
    parser.add_argument("-v","--verbose", help="print info msg", action="store_true")
    parser.add_argument("-d","--debug", help="print debug info", action="store_true")
    parser.add_argument("-q","--quiet", help="ignore animation", action="store_true")
    parser.add_argument('-f','--file', nargs='?', help="Verfploeter measurement output file")
    parser.add_argument("-n","--normalize", help="remove inconsistency from the measurement dataset", action="store_true")

    parser.add_argument('-s','--source', nargs='?', help="Verfploeter source pinger node")
    parser.add_argument('-b','--bgp', nargs='?', help="BGP status")


    # TODO
    parser.add_argument("--stats", dest="stat",  choices=["load", "block", "country"], default="load",
	help="show stats from the vp measurement. Potential options:" + linesep +
	        linesep.join("    " + name for name in ["load (default)", "block", "country"]))

    return parser

#------------------------------------------------------------------------------
# ## remove inconsistency and add metadata field
def check_metadata_from_df(ret,df):
  
    # remove inconsistency
    df = df[df['destination_address'] == df['meta_source_address']]
    df = df[df['source_address'] == df['meta_destination_address']]
    df['src_net'] =  df.source_address.str.extract('(\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.)\\d{1,3}')+"0"
    df.drop_duplicates(subset="src_net",keep='first', inplace=True)
    ret.put(df)

#------------------------------------------------------------------------------
# print loading animation
def animated_loading(flag):

    if (flag == 0 ):
        msg = "loading dataframe     "
        chars = "▁▂▃▄▅▆▇█▇▆▅▄▃▁"
    if (flag == 1 ):
        chars = "◢ ◣ ◤ ◥"
        msg = "removing incosistency "
    if (flag == 2):
        chars = "▖▘▝▗"
        msg = "inserting metadata    "
    if (flag == 3):
        chars = "⣾⣽⣻⢿⡿⣟⣯⣷"
        msg = "saving dataframe      "
    os.system('setterm -cursor off')

    for char in chars:

        sys.stdout.write('\r'+msg+''+char)
        time.sleep(.1)
        sys.stdout.flush()
#    os.system('setterm -cursor on')

#------------------------------------------------------------------------------
# load the dataframe 
def load_df (ret,file):

	print ("reading the dataframe") if (args.verbose) else 0
	df = pd.read_csv(file, sep=",", index_col=False, low_memory=False, skiprows=0)
	ret.put(df) 

#------------------------------------------------------------------------------
# add metadata
def insert_metadata(ret,df,args):

    # add extra metadata info
    # origin = node that has started the ping process
    # bgp = current bgp announces
    df['origin'] = args.source
    df['bgp'] = args.bgp
    ret.put(df) 

#------------------------------------------------------------------------------
# call metadata insertion
def add_metadata(df,args):

    ## check for metadata and pre-processing tasks
    print ("inserting dataframe metadata") if (args.verbose) else 0
    ret = queue.Queue()
    the_process = threading.Thread(name='process', target=insert_metadata, args=(ret,df,args))
    the_process.start()
    while the_process.isAlive():
    	animated_loading(2) if not (args.quiet) else 0
    the_process.join()
    df = ret.get()

    # fix formating
    if (not args.quiet) or (not args.debug) or (not args.verbose):
        print ("\r                      ")

    return(df)

#------------------------------------------------------------------------------
# plot the graph
def bar(row):
    percent = int(row['percent'])
    bar_chunks, remainder = divmod(int(percent * 8 / increment), 8)
    count = str(row['counts'])
    label = row['index']
    percent = str(percent)

    bar = '█' * bar_chunks
    if remainder > 0:
        bar += chr(ord('█') + (8 - remainder))
    # If the bar is empty, add a left one-eighth block
    bar = bar or  '▏'
    print ("{} | {} - {}%  {}".format( label.rjust(longest_label_length), count.rjust(longest_count_length),percent.rjust(3), bar ))
    return ()

#------------------------------------------------------------------------------
# save df - threading
def save_df(ret,args,df):
    outputfile = str(args.file.split(".")[:-1][0])+"-csv.norm.gz"
    df.to_csv(outputfile,index=False, compression="gzip")
    ret.put(outputfile)


#------------------------------------------------------------------------------
# load the dataframe and remove inconsistency
def init_load(args):

    file = args.file
    ## load dataframe
    print ("reading the dataframe - file {}".format(file)) if (args.verbose) else 0
    ret = queue.Queue()
    the_process = threading.Thread(name='process', target=load_df, args=(ret,file))
    the_process.start()
    while the_process.isAlive():
    	animated_loading(0) if not (args.quiet) else 0
    the_process.join()
    df = ret.get()
    
    ## check for metadata and pre-processing tasks
    print ("checking dataframe metadata\n") if (args.verbose) else 0
    ret = queue.Queue()
    the_process = threading.Thread(name='process', target=check_metadata_from_df, args=(ret,df))
    the_process.start()
    while the_process.isAlive():
    	animated_loading(1) if not (args.quiet) else 0
    
    the_process.join()
    df = ret.get()
    
    # rename columns
    df.rename( columns={'send_receive_time_diff':'rtt',
                        'source_address_country': 'country',
                        'source_address_asn': 'asn',
                        'client_id': 'catchment',
                       }
              ,inplace=True)
    df = df.drop(columns=['source_address','destination_address','meta_source_address',\
                'meta_destination_address','task_id','transmit_time','receive_time'])
    
    return (df)


#------------------------------------------------------------------------------
# check parameters
def evaluate_args():
    parser = parser_args()
    args = parser.parse_args()

    if (args.debug):
        set_log_level('DEBUG')
        logging.debug(args)

    if (args.version):
        print (version)
        sys.exit(0)
    
    if (args.verbose):
        verbose=True
        print (args)
    
    if (args.file):
        file = args.file
        if not (os.path.isfile(file)):
            print ("file not found: {}".format(file))
            sys.exit(0)
    
    else:
        print ("You have to define the filename")
        parser.print_help()
        sys.exit(0)

    return (args)

###############################################################################
### Main Process

args = evaluate_args()

# prepare dataset to sent to bq
if (args.normalize):

    if (not args.bgp) or (not args.source):
        print ("\n\tTo normalize the measurement file you should add \"--bgp and --origin\" ")
        print ("\t\tvp-cli.py -v -n -f data.csv -b \"us-was-anycast01: 145.90.8.0/24; \" -s  us-was-anycast01\n")
        if (args.bgp==None):
            print ("\tBGP policy not defined.")

        if (args.source==None):
            print ("\tSource (pinger) is not defined.")
        sys.exit(0)
        
#-------
df = init_load(args)

if (args.normalize):
    df = add_metadata(df,args)


    ## check for metadata and pre-processing tasks
    print ("saving normalized file\n") if (args.verbose) else 0
    logging.debug('msg: saving normalized file')

    ret = queue.Queue()
    the_process = threading.Thread(name='process', target=save_df, args=(ret,args,df))
    the_process.start()
    while the_process.isAlive():
    	animated_loading(3) if not (args.quiet) else 0
    
    the_process.join()
    outputfile = ret.get()
    print ("\r{}                 ".format(outputfile))
    sys.exit(0)

else:
    print('\rdataframe processing ... done!\n')

# new stats df 
s = df.catchment
counts = s.value_counts()
percent100 = s.value_counts(normalize=True).mul(100).round(1).astype(int)
df_summary = pd.DataFrame({'counts': counts, 'percent': percent100}).reset_index()

# print ascii bar chart
max_value = df_summary.percent.max()
increment = max_value / 25
longest_label_length = len(df_summary['index'].max())
longest_count_length = len(df_summary['counts'].max().astype(str))

ret  = df_summary.apply(bar, axis=1)
sys.exit(0)
