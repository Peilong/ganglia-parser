#!/usr/bin/python
#
# filter zero metrics out of the collected metrics files
#
import urllib2
import re
import sys
import json
from pprint import pprint
import matplotlib.pyplot as plt
import ConfigParser
import string
import decimal
import datetime
import os
from os import listdir
from os.path import isfile, join, isdir
import shutil
from optparse import OptionParser    
import calendar

def filter_dir(metricdir, metric):
    global filtered_dir
    onlyfile = [ f for f in listdir(metricdir) if isfile(join(metricdir,f)) ]
    #onlyfile contains all metric files, 
    # then we look only the chosen metric file
    for fn in onlyfile:
        fn_pattern = '.*'+metric+'.*.json'
        #print fn_pattern
        pattern = re.compile(fn_pattern)
        result = pattern.findall(fn)
        if len(result) != 0:
            #print "***"+fn
            jsonfile_fullname = metricdir+"/"+fn
            if filter_metric(jsonfile_fullname, metric):
                # create metric subdirectory now to avoid creating 
                # metric directory too early, then realizing json files are empty
                filtered_metric_dir = filtered_dir+metric+"/"
                #print filtered_metric_dir
                if not os.path.exists(filtered_metric_dir):
                    os.makedirs(filtered_metric_dir)
                if option_copypng:
                    # save png file
                    origin_pngfile_fullname = jsonfile_fullname.replace("json","png")
                    # copy png file to filtered_dir
                    shutil.copy2(origin_pngfile_fullname, filtered_metric_dir+"/")
                else: 
                    # filter time span
                    # print "calling generate_png_time"
                    newpng_fullname = filtered_metric_dir+fn.replace("json","png")
                    generate_png_time( jsonfile_fullname, newpng_fullname, 
                                      timestart_ts, option_timeduration)

def generate_png_time(jsonfilename, pngfilename,
                      timestart, timeduration):
    global g_metric
    json_data_file=open(jsonfilename)
    jsondata = json.load(json_data_file)
    # json data not empty
    # check if all zero
    tmpx=[]
    tmpy=[]
    rawdata = jsondata[0]['datapoints']
    for i in xrange (0, len(rawdata)-2):
        #print "raw timestamp=", rawdata[i][1]
        #print "timestart=", timestart
        if rawdata[i][1] >= timestart and rawdata[i][1] <= timestart+timeduration:
            tmpx.append(rawdata[i][1]-timestart)
            tmpy.append(rawdata[i][0])
    json_data_file.close()
    #print tmpx
    #print tmpy
    #plot png
    plt.figure()
    plt.clf()
    # extract host name
    ### Regular experssion matching to grab the node internal IP
    p = re.compile('ip-\w{1,3}-\w{1,3}-\w{1,3}-\w{1,3}\.ec2\.internal')
    r = p.findall(jsonfilename)
    #print r[0]
    plt.title(r[0])   
    plt.plot(tmpx, tmpy, 'k')
    plt.ylabel(metric)
    plt.xlabel('Time in s ( start time = '+option_timestart+' )')
    plt.savefig(pngfilename)

                        
# check if the json data file is empty or contains only zeros
# True -> has non-zero values
# False -> not interesting
def filter_metric(jsonfile, metric):
    #
    json_data_file=open(jsonfile)
    
    jsondata = json.load(json_data_file)
    #pprint(data)
    # check if json file is empty or contains "null"
    if jsondata == None:
        return False
    # json data not empty
    # check if all zero
    rawdata = jsondata[0]['datapoints']
    #print "len(rawdata)=", len(rawdata)
    for i in xrange (0, len(rawdata)-2):
        if rawdata[i][0] != 0:
            json_data_file.close()
            return True
    json_data_file.close()
    return False

if len (sys.argv) < 2:
    print 'Usage: python metricsFilter.py filter.conf'
    sys.exit(2)
else:
    filename = sys.argv[-1]

parser = OptionParser()
parser.add_option("-c", "--copypng", dest="copypng", action="store_true", default=False)
#parser.add_option("-ts", "--timestart", dest="timestart", action="store", 
#		  type="int", help="time span start in milliseconds", default="0")
#parser.add_option("-ts", "--timeend", dest="timeend", action="store", 
#		  type="int", help="time span end in milliseconds", default="0")

(options, args) = parser.parse_args()

option_copypng = options.copypng
#option_timestart = options.timestart
#option_timeend = options.timeend

### Header
print '-'*45
print ' *** Ganglia Metrics Filter ***'
print ''
print ' Usage: python metricsFilter.py filter.conf'
print '-'*45

### Configuration file parser
cf = ConfigParser.ConfigParser()    
cf.read(filename)

# metrics is comma separated list
metrics = cf.get("option","metrics")
option_timestart = cf.get("option","time_start")
# convert seconds to milliseconds
option_timeduration = int(cf.get("option","time_duration"))
#option_timeend = int(cf.get("option","time_end")

timestart_dt = datetime.datetime.strptime (option_timestart, "%Y/%m/%d %H:%M:%S")
timestart_ts = calendar.timegm (timestart_dt.timetuple())

mypath="./"
onlydir = [ f for f in listdir(mypath) if isdir(join(mypath,f)) ]
# locate metrics-xxxxx directory
for fns in onlydir :
    ### Regular experssion matching to grab metrics dir
    pattern = re.compile('^metrics-*')
    result = pattern.findall(fns)
    if len(result) != 0:
        print fns
        filtered_dir = "filtered-"+fns+"/"
        if not os.path.exists(filtered_dir):
            os.makedirs(filtered_dir)
        # do filter
        # get all the metrics one by one
        for metric in metrics.split(','):
            print "Filtering metric \""+metric+"\" in directory "+fns
            g_metric = metric
            filter_dir(fns, metric)

### Final printout message
print '+'*45
print '[SUCCESS] .JSON and .PNG files are filtered!'
print '+'*45
