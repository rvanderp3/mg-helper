from .xmgPlugin import XmgPlugin
from transforms.tracker import Tracker
from transforms.logLevel import LogLevel
import time
import glob
import queue
import threading

queueLock = threading.Lock()
exitFlag = 0

class updateFileThread (threading.Thread):
    ipMap = {}
    q = None
    def __init__(self, threadID, name,q, ipMap):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.ipMap = ipMap
        self.q = q
        
    def run(self):        
        while exitFlag == 0:
            queueLock.acquire()
            qEmpty = self.q.empty()
            if qEmpty == False:
                filename = self.q.get()
            queueLock.release()
            if qEmpty:
                return            
            with open(filename) as file:
                s = file.read()
            for key in self.ipMap:                
                s = s.replace(key+":", self.ipMap[key]+":")
            with open(filename, "w") as file:
                file.write(s)
    

class ReplacePodIps(XmgPlugin):    
    workQueue = None
    threads = []
    def __init__(self,accessor):
        super(ReplacePodIps,self).__init__("Pod IP mapping",accessor)

    def printStatus( self, count, of, message):
        print("[Processed "+str(count) +"/"+str(of) + " | " + message + "                                                                      ", end="\r", flush=True)
    def run( self ):    
        
        ipMap = { }        
        entries = self.accessor.getDirsFromPath("namespaces") 
        print("Loading IP addresses for known services and pod in ["+str(len(entries))+"] namespaces")        
        count = 1
        for entry in entries:                                            
            services = self.accessor.getFileContent(entry+"/core/services.yaml")
            if services is not None:
                serviceObj = self.accessor.parseYaml(services)      
                for item in serviceObj["items"]:                
                    name = item["metadata"]["name"]
                    spec = item["spec"]
                    if "clusterIP" in spec:
                        clusterIP = spec["clusterIP"]
                        if clusterIP == "None":
                            continue
                        ipMap[clusterIP] = "[svc:"+name+"@"+clusterIP+"]"
                        self.printStatus(count, len(entries), "Found service: " + ipMap[clusterIP])
            pods = self.accessor.getDirsFromPath(entry+"/pods") 
            for pod in pods:
                podfiles=self.accessor.getEntriesFromPath(pod) 
                for podfile in podfiles:
                    content = self.accessor.getFileContent(podfile)
                    data = self.accessor.parseYaml(content)
                    podname=self.accessor.getValueFromObj(data,"metadata","name")
                    nodeName=self.accessor.getValueFromObj(data,"spec","nodeName")
                    podIP=self.accessor.getValueFromObj(data,"status","podIP")
                    if podIP == "":
                        continue
                    ipMap[podIP] = "["+nodeName +"/"+podname+"@"+podIP+"]"
                    self.printStatus(count, len(entries), "Found pod: " + ipMap[podIP])   
            count = count + 1                 
        
        podFiles = glob.iglob(self.accessor.filename+'/**/current.log',recursive=True)
        workQueue = queue.Queue()
        
        for filepath in podFiles:
            workQueue.put(filepath)

        for threadID in range(0,4):
            thread = updateFileThread(threadID, "Thread " + str(threadID), workQueue, ipMap)
            thread.start()
            self.threads.append(thread)            

        podsStartCount = podsLeft = workQueue.qsize()
        # Wait for queue to empty
        print("Updating pod logs to reflect service/pod name in addition to the raw IP")
        while not workQueue.empty():            
            if workQueue.qsize() != podsLeft:
                podsLeft = workQueue.qsize()
                
                self.printStatus(podsStartCount-podsLeft, podsStartCount, "Updating logs")
            time.sleep(1)

        # Wait for all threads to complete
        for t in self.threads:
            t.join()
