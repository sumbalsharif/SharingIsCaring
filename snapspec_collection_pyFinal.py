import ugradio
import snap_spec #note this is installed on the rpi attached to the SNAP spectrometer
import threading
from astropy.io import fits
from astropy.table import Table, Column
import numpy as np
import matplotlib.pyplot as plt
import os
import argparse
import time

parser = argparse.ArgumentParser()
parser.add_argument('--prefix', '-p', help='this will append to the start of the filenames. these should include info about the data')
parser.add_argument('--len_obs', '-l', help='How long you want the observation to last in seconds (for now).')

args = parser.parse_args()

prefix=args.prefix
len_obs=int(args.len_obs)

spec = snap_spec.snap.UGRadioSnap() #create the interface
spec.initialize(mode='corr') #initialize interface to cross-correlate signals

count = 0
data = []
storage_count = []
time_track = []
running = True
def run_vis(spec): #watching the milk on the stove
	global count
	global data
	global storage_count
	global time_track
	global running

	while running:
		if count == 0: #First case
			d = spec.read_data() #read the data
			data_name = list(d.keys())[0]
			data.append(d[data_name]) #append data to l
			count = d['acc_cnt'] #reassign count to output
			print(count)
			storage_count.append(count)
			time_track.append(d['time']) #append the time to time_track
		else: #all other cases
			d = spec.read_data(count)
			data_name = list(d.keys())[0]
			data.append(d[data_name])
			count = d['acc_cnt']
			print(count)
			storage_count.append(count)
			time_track.append(d['time'])


#this function takes a prefix argument and every ten vis it pulls, it writes to a new fits file
def writeto(prefix):
	#getting global variables
	global count
	global data
	global storage_count
	global time_track
	global running

	track_files=0 #Updates every time a new file is written
	while running: #This checks if running is still true
		if len(storage_count) > 10:
			counts,times,stored = storage_count[:10], time_track[:10], data[:10] #assigns the data I want to store to new, local variables
			#deletes the data from the global storage variables that is now being stored and written
			del storage_count[:10]
			del time_track[:10]
			del data[:10]
			#possibly change names to care about the date and time?
			names = np.array([f'countnum{i}' for i in counts]) #creates column names for the fits file
			tab = Table(stored, names=names, meta={'times':times,'acc_cnts':counts}) #creates an astropy Table object with the data, names asthe column names, and meta data that stores the times and acc_cnt numbers
			tab.write(f'{prefix}_{track_files}.fits')
			print(f'file number {track_files} has been written!')
			track_files += 1
def tracktime(): #Sleeps until it's time to shut off, then flips the running variable to False
	global running
	global len_obs

	time.sleep(len_obs)
	running= False
#initializes threads, resurrects daemons, sets daemons loose
reading = threading.Thread(target=run_vis, args=(spec,))
writing = threading.Thread(target=writeto, args=(prefix,))
tracking = threading.Thread(target=tracktime)
reading.set_daemon = True
writing.set_daemon = True
tracking.set_daemon=True
reading.start()
writing.start()
tracking.start()
