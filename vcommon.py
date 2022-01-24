import time, sys, traceback, inspect, re

LOGLEVEL = 1
LOGERRORLEVEL = 2

LOGLEVELS = ['DEBUG', 'INFO', 'WARN', 'ERROR']
LOGTRACE = True
LOGLVLDEBUG=0
LOGLVLINFO=1
LOGLVLWARN=2
LOGLVLERROR=3

def strMultireplace(strIn, listOfTuplesReplacers):
	strOut=strIn
	for replacer in listOfTuplesReplacers:
		strOut=strOut.replace(replacer[0], replacer[1])
	return strOut

def getStrMilliseconds():
	return str(round(time.time()%1,3))[1:]

def getTimeFormatted():
	return time.strftime('%Y-%m-%dT%H:%M:%S')
	
def getTimeFormattedWithMilliseconds():
	return time.strftime(f'%Y-%m-%dT%H:%M:%S{getStrMilliseconds()}')

def getTimeFormattedForFile():
	return time.strftime('%Y-%m-%dT%H-%M-%S')

def formatExecData(stackExecData):
	functionRoute=''
	for execData in stackExecData:
		context = execData.code_context
		if context != None:
			functionRoute += re.sub(r'\t+','', execData.code_context[0].replace('\n','')) + ' => '
		else:
			functionRoute += str(execData.function) + ' => ' 
	return functionRoute[0:-4]

def getFunctionRoute():
	stackExecData = inspect.stack()[:2:-1] #exclude log function for function route
	return formatExecData(stackExecData)	

def loggerTraceback(enableTb, outToStderr=False): #traceback enable and select out (stdout or stderr)
	if enableTb==True:
		tb=sys.exc_info()
		if outToStderr==True:
			traceback.print_exception(tb[0], tb[1], tb[2], file=sys.stderr)
		else:
			traceback.print_exception(tb[0], tb[1], tb[2])
	return

def logger(level, msg, logtb=False):
	if level < LOGLEVEL:
		return
	msgLog=getTimeFormattedWithMilliseconds() + "\t[" + LOGLEVELS[level] + "]\t"  + msg
	print(msgLog)
	loggerTraceback(logtb)
	if level >= LOGERRORLEVEL: #write to stderr
		print(msgLog, file=sys.stderr)
		loggerTraceback(logtb, True)

def checkPositiveFlag(signalIn,preSignalIn):
	return signalIn and not preSignalIn and signalIn != None and preSignalIn != None
	
def checkNegativeFlag(signalIn,preSignalIn):
	return not signalIn and preSignalIn and signalIn != None and preSignalIn != None

def equalLists(listA,listB):
	return listA==listB

def listSubstract(listA,listB):
	lenListA=len(listA)
	listRes=[]
	if lenListA != len(listB):
		return listRes
	for i in range(lenListA):
		listRes.append(listA[i]-listB[i])
	return listRes

def boolArrayFormater(unformatBoolArray):
	uba = unformatBoolArray
	return (uba[:8]) if (len(uba) >= 8) else (uba + [False]*(8-len(uba)))

def byteToBoolArray(value):
	res = []
	for i in range(8):
		res.append(int.__and__(value,(1<<i)).__bool__())
	return res
	
def boolArrayToByte(boolArray):
	res = 0
	formatBoolArray = boolArrayFormater(boolArray)
	for i in range(8):
		res += formatBoolArray[i]*(1<<i)
	return res

def bytearrayToArrayBoolArray(values):
	res = []
	for byteValue in values:
		res.append(byteToBoolArray(byteValue))
	return res
	
def arrayBoolArrayToBytearray(arrayBoolArray):
	lenArray = len(arrayBoolArray)
	res = bytearray(lenArray)
	for i in range(lenArray):
		res[i] = boolArrayToByte(arrayBoolArray[i])
	return res

def read_file(filename):
	with open(filename) as f:
		c=f.read()
	f.close()
	return c

def write_file(filename, data):
	with open(filename, 'w') as f:
		f.write(data)
	f.close()

def read_binary_file(filename):
	with open(filename, 'rb') as f:
		c=f.read()
	f.close()
	return c

def write_binary_file(filename, data):
	with open(filename, 'wb') as f:
		f.write(data)
	f.close() 

def invertBooleanList(booleanList):
	res=[]
	for boolean in booleanList:
		res.append(not boolean)
	return res	

def getDictParamsClass(classIn):
	paramsDict = dict(classIn.__dict__)
	for classParam in ['__module__', '__dict__', '__weakref__', '__doc__']: 
		paramsDict.pop(classParam)
	return paramsDict
                        
def getDictMembersClass(classIn):
	paramsDict = getDictParamsClass(classIn)
	membersDict = {}
	for param in paramsDict.keys():
		if not callable(paramsDict[param]):
			membersDict[param] = paramsDict[param]
	return membersDict	

class FunctionNotFoundError(Exception):
	pass
	
class ImageReadError(Exception):
	pass


	
                
class timeMeasures:
	start = 0
	setup = 0
	loop = 0
	flag = 0
	preUnix = 0
	unix = 0
	unixDiff = 0
	
	def registerUnixTimestamp(self):
		self.preUnix = self.unix
		self.unix = time.time()
		self.unixDiff = self.unix-self.preUnix
		
	def getUnixDiff(self):
		return self.unixDiff
    
class tensorIO:
	inputs=None
	outputs=None
	test=None

class tensorRtParams:
	context = None
	stream = None
	shapes = tensorIO
	host = tensorIO
	
class fpsLimit:
	
	def __init__(self,fps):
		if fps <= 0:
			fps=10
		self.limit=1/fps
	
	def takeTime(self):
		self.ti=time.time()
	
	ti=0
	limit = 0
	ready=lambda self: ((self.ti+self.limit) < time.time())
	

class inferenceTensorRTSystem:
	INPUTSHISTORYSIZE=2
	filter=''
	tensorRt=tensorRtParams()
	times=timeMeasures()
	temp=False
	tempNum=0
	lastInferences=[]
	semiOperativeWatchdog=0
	dataRegisterBuffer={}
	
	def __init__(self, inputsInitValues):#posible quitar entrada argumento
		pass
	
	def semiOperativeWatchdogUpdate(self):
		self.semiOperativeWatchdog=time.time()
	
	def semiOperativeWatchdogCheck(self):
		return self.semiOperativeWatchdog < (time.time() - cdef.TIMESEMIOPERATIVEMINIMAL)
		
	def registerLastInference(self, inference):
		self.lastInferences.append(inference[0])
		if len(self.lastInferences) <= cdef.LASTINFERENCESLENGTH:
			return
		self.lastInferences = self.lastInferences[1:]
		logger(0,f'last inferences -> {self.lastInferences}')
			
		
	def setInference(self, inference):
		self.outputs.inferenceUnfiltered = inference
		self.registerLastInference(inference)
		logger(0,'Unfiltered Inference:'+ str(self.outputs.inferenceUnfiltered) + ' lastInferences:' + str(self.lastInferences))
		self.outputs.inference = self.filter.step(inference)
		self.outputs.updateHatch()
		

	def dataRegisterBufferLength(self):
		return len(self.dataRegisterBuffer)

	def checkDataRegisterBuffer(self):
		if self.dataRegisterBufferLength() != cdef.DATAREGISTERBUFFERLENGTH:
			logger(2,'twistlock evkent not registered')
			return False
		return True

	def writeDataRegisterBuffer(self):
		#with self.dataRegisterBuffer as drb:
		self.dataRegisterBuffer['timestamp'] = self.times.flag
		self.dataRegisterBuffer['engineversion'] = cdef.ENGINENAME
		self.dataRegisterBuffer['lastinferences'] = strMultireplace(str(self.lastInferences),cdef.TABLEAUREPLACERS)
		logger(0,f'Data registered {self.dataRegisterBuffer}')
			
	def clearDataRegisterBuffer(self):
		self.dataRegisterBuffer.clear()

	def registerFlagTimestamp(self):
		self.times.flag = getTimeFormatted()
		self.times.flagForFilename = getTimeFormattedForFile()
		self.times.registerUnixTimestamp()
	
	def setFilterParams(self, filterInputShape, filterSize): 
		self.filter = averagesListFilter(filterInputShape, filterSize)

	def neuralNetworkInference(self,imageInput):
		neuralNetworkInput = self.tensorRt.host.inputs
		neuralNetworkOutput = self.tensorRt.host.outputs
		context = self.tensorRt.context
		stream = self.tensorRt.stream
		neuralNetworkInput[:] = imageInput[:]
		context.execute_async_v2(bindings=[neuralNetworkInput.base.get_device_pointer(), neuralNetworkOutput.base.get_device_pointer()], stream_handle=stream.handle)
		stream.synchronize()
		self.setInference(list(neuralNetworkOutput))
		return list(neuralNetworkOutput)