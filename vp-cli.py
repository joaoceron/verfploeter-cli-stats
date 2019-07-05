#!/usr/bin/env python3
###############################################################################
# cli view interface
# Thu Jul  4 13:43:19 UTC 2019
# @copyright sand-project.nl - Joao Ceron - ceron@botlog.org
###############################################################################

###############################################################################
### Python modules
import glob
import os
import sys
import pandas as pd
import argparse
import threading
import queue as queue
import time 

###############################################################################
### Program settings
verbose = False
version = 0.2

###############################################################################
### Subrotines

#------------------------------------------------------------------------------
def parser_args ():

    parser = argparse.ArgumentParser(prog='vp-viz.py', usage='%(prog)s [options]')
    parser.add_argument("--version", help="print version and exit", action="store_true")
    parser.add_argument("-v","--verbose", help="print debug infos", action="store_true")
    parser.add_argument('-f','--file', nargs='?', help="Verfploeter output file")
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

    chars = "/-|-\\"
    for char in chars:
        if (flag==1):
	        sys.stdout.write('\r'+'processing dataframe ...  '+char)
        else:
	        sys.stdout.write('\r'+'loading dataframe ...  '+char)
        time.sleep(.1)
        sys.stdout.flush()

#------------------------------------------------------------------------------
# load the dataframe 
def load_df (ret,file):

	print ("reading the dataframe") if (args.verbose) else 0
	df = pd.read_csv(file, sep=",", index_col=False, low_memory=False, skiprows=0)
	ret.put(df) 

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


###############################################################################
### Main Process

parser = parser_args()
args = parser.parse_args()

if (args.version):
    print (version)
    sys.exit(0)

if (args.verbose):
    verbose=True
    print (args)

if (args.file):
    file = args.file
else:
    print ("You have to define the filename")
    parser.print_help()
    sys.exit(0)


## load dataframe
print ("reading the dataframe - file {}".format(file)) if (args.verbose) else 0
ret = queue.Queue()
the_process = threading.Thread(name='process', target=load_df, args=(ret,file))
the_process.start()
while the_process.isAlive():
	animated_loading(0)
the_process.join()
df = ret.get()

## check for metadata and pre-processing tasks
print ("checking dataframe metadata") if (args.verbose) else 0
ret = queue.Queue()
the_process = threading.Thread(name='process', target=check_metadata_from_df, args=(ret,df))
the_process.start()
while the_process.isAlive():
	animated_loading(1)
print('\rprocessing dataframe ... done!\n')

the_process.join()
df = ret.get()

# rename columns
df.rename( columns={'send_receive_time_diff':'rtt',
                    'source_address_country': 'country',
                    'source_address_asn': 'asn',
                    'client_id': 'node',
                   }
          ,inplace=True)
df = df.drop(columns=['source_address','destination_address','meta_source_address',\
            'meta_destination_address','task_id','transmit_time','receive_time'])

# new stats df 
s = df.node
counts = s.value_counts()
percent100 = s.value_counts(normalize=True).mul(100).round(1).astype(int)
df_summary = pd.DataFrame({'counts': counts, 'percent': percent100}).reset_index()

# print ascii bar chart
max_value = df_summary.percent.max()
increment = max_value / 25
longest_label_length = len(df_summary['index'].max())
longest_count_length = len(df_summary['counts'].max().astype(str))

ret  = df_summary.apply(bar, axis=1)
print ("")
