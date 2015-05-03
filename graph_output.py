#!/usr/bin/env python

##############
# This will graph the output of an IAP rf-summary command, using air-recorder to obtain the raw data.
# launch air-recorder with the following air-recorder command:
# java -jar AirRecorder-1.2.16-release.jar --instant --protocol ssh -u admin -t 20 -m -c commands.txt 4.35.159.123
# with only the following in commands.txt file in same directory:
# 125,show ap arm rf-summary
#
# Each column in the output represents 5 seconds (for total of 2 minutes)
# The command is run every 125 seconds to avoid duplicate data.
# The longer you let air-recorder run, the more data will be graphed.
# Since I'm averaging 2-minute intervals, this may mask "spikes" and is aimed at analyzing
# rf-summary output over long periods of time.
##############

import os, sys, re, argparse
import matplotlib.pyplot as plt

# set up argument parsing
# by default, 2.4ghz radio is graphed only. If you specify 5, 2.4ghz will NOT be graphed. If you specify both 2.4 AND 5 both will be graphed.
to_graph_5g = 'n'
to_graph_24g = 'y'
parser = argparse.ArgumentParser(description='Graph radio counters of an IAP')
# const is the int (0 or 1) associated with the option, if you only call the option (by itself). 
# nargs and default specify the default value (0 or 1)
parser.add_argument('-2.4', nargs='?', const='1', type=int, help='Graph 2.4GHz radio counters. wifi:1 interface (Graphed by default)', default=1, required=False)
parser.add_argument('-5', nargs='?', const='1', type=int, help='Graph 5GHz radio counters. wifi:0 interface', default=0, required=False)
parser.add_argument('-f', '--filename', type=str, help='filename of air-recorder output', required=True)
args = vars(parser.parse_args())
if args['5'] == 1:
  to_graph_5g = 'y'
  to_graph_24g = 'n'

print "Usage:\ngraph-output.py [-2 -5] [input file]\n\nExample (2.4GHz counters)> python graph-output.py -f air-recorder-10.1.1.5.log\nExample (5GHz counters)> python graph-output.py -5 -f air-recorder-10.1.1.5.log\n\nDefault graph (if no option specified) is 2.4Ghz radio only (wifi:1)\n\n"

logfile = args['filename']
input_file = open(logfile).readlines()

def find_start():
  # Locate the start time of the output file for graph X axis label
  global start_time
  for line in input_file:
    time_search = re.search(r'(Current Time\s*:)(.*)', line, re.IGNORECASE)
    if time_search:
      start_time = time_search.group(2).rstrip()

def gather_data():
  global counters
  counters = []
  # collect all counters (since currently tuned channel displays retry % (:R:), use that as endpoint
  collector = []
  R_seen = 0
  Q_seen = 0

  for line in input_file:
    if ':Q:' in line:
      # reset the collector, in case Q was seen without R
      collector = ''
      Q_seen = 1

    # if Q was seen start adding to the collector list
    if Q_seen == 1:
      collector += line

    # once R is seen, add the collector list items to counters list, IF/ONLY IF Q was previously seen
    if ':R:' in line:
      R_seen = 1
      if Q_seen == 1 and R_seen == 1:
        counters.append(collector)
        # after adding the collector data to the counters list, reset both 'seens' to 0
        Q_seen = 0
        R_seen = 0

def create_lists_24g():
  # make some of the lists global for use in graphing function
    global Q_list_avg_24g
    global R_list_avg_24g
    global U_list_avg_24g
    Q_list = []
    Q_list_avg_24g = []
    R_list = []
    R_list_avg_24g = []
    U_list = []
    U_list_avg_24g = []
    for line in counters:
      Q_search_24g = re.search(r'((\s1|\s6|\s11)\:Q\:\s*)([0-9].*)', line, re.IGNORECASE)
      R_search = re.search(r'(\:R\:\s*)([0-9].*)', line, re.IGNORECASE)
      U_search = re.search(r'(\:U\:\s*)([0-9].*)', line, re.IGNORECASE)
      # if the 24g channel matches, the counters below that are naturally included for searching.
      # ie each list item includes the channel plus Q through R counters
      if Q_search_24g:
        quality = Q_search_24g.group(3).rstrip()
        Q_list.append(quality)
        if R_search:
          retries = R_search.group(2).rstrip()
          R_list.append(retries)
        if U_search:
         non_dot11 = U_search.group(2).rstrip()
         U_list.append(non_dot11)

  # split each list entry, average it, and put back into new list
    for item in Q_list:
      Q_split = item.split()
      #turn the strings into integers
      Q_split_ints = [int(i) for i in Q_split]
      #average the individuals
      Q_avg = sum(Q_split_ints)/len(Q_split_ints)
      Q_list_avg_24g.append(Q_avg)

    for item in R_list:
      R_split = item.split()
      R_split_ints = [int(i) for i in R_split]
      R_avg = sum(R_split_ints)/len(R_split_ints)
      R_list_avg_24g.append(R_avg)

    for item in U_list:
      U_split = item.split()
      U_split_ints = [int(i) for i in U_split]
      U_avg = sum(U_split_ints)/len(U_split_ints)
      U_list_avg_24g.append(U_avg)

def create_lists_5g():
    # make some of the lists global for use in graphing function
    global Q_list_avg_5g
    global R_list_avg_5g
    global U_list_avg_5g
    Q_list = []
    Q_list_avg_5g = []
    R_list = []
    R_list_avg_5g = []
    U_list = []
    U_list_avg_5g = []
    for line in counters:
      Q_search_5g = re.search(r'\s*((36|40|44|48|52|56|60|64|100|104|108|112|116|120|124|128|132|136|140|149|153|157|161|165)\:Q\:\s*)([0-9].*)', line, re.IGNORECASE)
      R_search = re.search(r'(\:R\:\s*)([0-9].*)', line, re.IGNORECASE)
      U_search = re.search(r'(\:U\:\s*)([0-9].*)', line, re.IGNORECASE)
      # if the 5g channel matches, the counters below that are naturally included for searching.
      # ie each list item includes the channel plus Q through R counters
      if Q_search_5g:
        quality = Q_search_5g.group(3).rstrip()
        Q_list.append(quality)
        if R_search:
          retries = R_search.group(2).rstrip()
          R_list.append(retries)
        if U_search:
          non_dot11 = U_search.group(2).rstrip()
          U_list.append(non_dot11)

    # split each list entry, average it, and put back into new list
    for item in Q_list:
      Q_split = item.split()
      #turn the strings into integers
      Q_split_ints = [int(i) for i in Q_split]
      #average the individuals
      Q_avg = sum(Q_split_ints)/len(Q_split_ints)
      Q_list_avg_5g.append(Q_avg)

    for item in R_list:
      R_split = item.split()
      R_split_ints = [int(i) for i in R_split]
      R_avg = sum(R_split_ints)/len(R_split_ints)
      R_list_avg_5g.append(R_avg)

    for item in U_list:
      U_split = item.split()
      U_split_ints = [int(i) for i in U_split]
      U_avg = sum(U_split_ints)/len(U_split_ints)
      U_list_avg_5g.append(U_avg)

def graph_5g():
    print "Building 5GHz radio graph..."
    #start the list_avg's at zero for x,y axis
    Q_list_avg_5g.insert(0,0)
    R_list_avg_5g.insert(0,0)
    U_list_avg_5g.insert(0,0)
    #create time (X axis)
    time_ticks = range(0, len(Q_list_avg_5g), 1)
    time_axis = [x*2 for x in time_ticks]
    #Plot graph's
    plt.plot(time_axis, Q_list_avg_5g, label="Qual.")
    plt.plot(time_axis,R_list_avg_5g, label="Retry %")
    plt.plot(time_axis,U_list_avg_5g, label="Non-.11")
    #add labels, legend and title
    plt.grid(True)
    plt.xlabel("Minutes. Start time: %s" % start_time)
    plt.ylabel("Calculated Data")
    plt.title("ARM RF-Summary over Time")
    plt.legend(loc="upper left")
    plt.ylim(0,100)
    plt.show()
    # Uncomment following line to save the graph in current directory.
    #plt.savefig("graph_5g.png")

def graph_24g():
    print "Building 2.4GHz radio graph..."
    #start the list_avg's at zero for x,y axis
    Q_list_avg_24g.insert(0,0)
    R_list_avg_24g.insert(0,0)
    U_list_avg_24g.insert(0,0)
    #create time (X axis)
    time_ticks = range(0, len(Q_list_avg_24g), 1)
    time_axis = [x*2 for x in time_ticks]
    #Plot graph's
    plt.plot(time_axis, Q_list_avg_24g, label="Qual.")
    plt.plot(time_axis,R_list_avg_24g, label="Retry %")
    plt.plot(time_axis,U_list_avg_24g, label="Non-.11")
    #add labels, legend and title
    plt.grid(True)
    plt.xlabel("Minutes. Start time: %s" % start_time)
    plt.ylabel("Calculated Data")
    plt.title("ARM RF-Summary over Time")
    plt.legend(loc="upper left")
    plt.ylim(0,100)
    plt.show()
    # Uncomment following line to save the graph in current directory.
    #plt.savefig("graph_24g.png")

find_start()
gather_data()

if to_graph_5g == 'y':
  create_lists_5g()
  graph_5g()

if to_graph_24g == 'y':
  create_lists_24g()
  graph_24g()

