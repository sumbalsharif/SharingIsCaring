import ugradio
import snap_spec
import numpy as np
import matplotlib.pyplot as plt
import astropy
import time
import glob
import argparse 

parser = argparse.ArgumentParser()
parser.add_argument('--filename', '-f', help='name to give file')
parser.add_argument('--timedelay', '-t', help='time delay in seconds')

#parser to name files more conviniently
args = parser.parse_args()
file = args.filename
timedelay = args.timedelay
timedelay = int(timedelay)

#Creating an empty dictionary for the point number (1st point, 2nd point, etc.) and corresponding Julian Date. 
julian_dates = {}
num = 0

#Providing an interface for controlling the pointing of the two telescopes that constitute the interferometer.
ifm = ugradio.interf.Interferometer()

try:
    while True:
            #Get the initial Julian date. This sill be continously updated. 
            jd = ugradio.timing.julian_date() 
            julian_dates.update({num:jd})
            
            #Get the altitude and azimuth of the sun at the given Julian date and correct for precession of Equinox 
            ra, dec = ugradio.coord.sunpos(jd = jd)
            ra, dec = ugradio.coord.precess(ra = ra, dec = dec, jd=jd)
            
            #Coverting from equitorial coordinates to topocentric.
            alt, az = ugradio.coord.get_altaz(ra = ra, dec = dec, jd=jd)  
            
            #We must have conditional pointing for the pointing to ensure... she does not break her neck.
            if az <= 90:
                ifm.point(az=az+180, alt=alt+90)
            if az >= 300:
                ifm.point(az=az-180, alt=alt+90)
            else: 
                ifm.point(alt, az)
                
            #Will print to statement everytime she updates. 
            print("Mashallah, she is pointing to the sun. Alhamdulillah")
            
            #Now will introdue the time delay we set beorore updating the Julian Date and updating the pointing number. 
            time.sleep(timedelay)
            num += 1
            
# To stop running the script, press Ctrl+C
except KeyboardInterrupt:
    print("You stopped stalking the sun! no longer activly pointing.")
    #Once active poriting is terminated, will 
    np.savez('{}.npz'.format(file), dates=julian_dates)
