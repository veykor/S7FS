#!/usr/bin/python3

'''
S7FS is an interface develop over python3 that convert a memory block from/to snap7 protocol from/to binary files
All right reserved to veykor(https://github.com/veykor)
Version:1.02
Change below uppercast variables you can to modify the essential parameter for api control.
'''
import snap7, time, signal
from vcommon import *

SERVERPORT = 102
DBINSIZE = 255#bytes
DBOUTSIZE = 255
DBINADDRESS = 1
DBOUTADDRESS = 2


#CAUTION!!! HIGHLY CRITIC!! PLACE NEXT FILES TO TMPFS DIRECTORY FOR HIGH READ/WRITE RATE
#IF YOU IGNORE THIS WARNING YOU CAN TO REDUCE HARD DISK LIFE
#care with files name to prevent possible system files collisions
DBINFILE='/run/dataIn.bgn' #bgn extension isn't relevant, are pure binary files
DBOUTFILE='/run/dataOut.bgn' 

server=''
loopctl=0

def svUnsetup():
	global server
	if isinstance(server, str):
		return
	logger(LOGLVLINFO,'Server will be closed')
	server.stop()
	server.destroy()
	logger(LOGLVLINFO,'Server closed')
	
def safeClose(signum, frame):
	global loopctl
	loopctl=1
	

def svSetup():
	logger(LOGLVLINFO,'Creating server')
	serverTemplate = snap7.server.Server()
	dbTemplate = snap7.types.wordlen_to_ctypes[snap7.types.S7WLByte]
	dbIn = (dbTemplate*DBINSIZE)() #from out to host
	dbOut = (dbTemplate*DBOUTSIZE)() #from host to out
	serverTemplate.register_area(snap7.types.srvAreaDB, DBINADDRESS, dbIn)
	serverTemplate.register_area(snap7.types.srvAreaDB, DBOUTADDRESS, dbOut)
	write_binary_file(DBOUTFILE, bytes(DBOUTSIZE)) #create file for read
	return (serverTemplate, dbIn, dbOut);

def __main__():
	global loopctl
	global server
	error=0
	signal.signal(signal.SIGTERM, safeClose)
	signal.signal(signal.SIGINT, safeClose)
	server, dbIn, dbOut = svSetup()
	server.start(SERVERPORT)
	logger(LOGLVLINFO,f"Server created: localhost:{SERVERPORT}, rack 0, slot 0")
	logger(LOGLVLINFO,f"Available DBs: DBIN:{DBINADDRESS}, DBOUT:{DBOUTADDRESS}")
	while loopctl < 1:
		event = server.pick_event()
		if event:
			logger(LOGLVLINFO, server.event_text(event))
			
			dataOut = read_binary_file(DBOUTFILE)[:DBOUTSIZE] #ignore data out of range
			dbOut[:len(dataOut)] = dataOut[:]
			
			dataIn = bytearray(DBINSIZE);
			dataIn[:] = dbIn[:]
			write_binary_file(DBINFILE, bytes(dataIn))
		time.sleep(0.01)
	svUnsetup
try:
	__main__()
except KeyboardInterrupt:
	svUnsetup()
except:
	logger(LOGLVLERROR, 'Error not handling', LOGTRACE)
	svUnsetup()
