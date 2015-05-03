# graph_airrecorder
graphing AirRecorder output of "show ap arm rf-summary"

 This will graph the output of an IAP rf-summary command, using air-recorder to obtain the raw data.
 launch air-recorder with the following air-recorder command:
 java -jar AirRecorder-1.2.16-release.jar --instant --protocol ssh -u <username> -t 20 -m -c commands.txt <ap_ip_address>
 with only the following in commands.txt file in same directory:
 125,show ap arm rf-summary

 Each column in the output represents 5 seconds (for total of 2 minutes)
 The command is run every 125 seconds to avoid duplicate data.
 The longer you let air-recorder run, the more data will be graphed.
 Since I'm averaging 2-minute intervals, this may mask "spikes" and is aimed at analyzing
 rf-summary output over long periods of time.

The only python dependency is matplotlib.

Linux: sudo apt-get install python-matplotlib

OSX: pip, macports etc.

Windows: untested
