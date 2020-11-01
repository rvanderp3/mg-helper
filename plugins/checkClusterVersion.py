from .xmgPlugin import XmgPlugin
from transforms.logLevel import LogLevel
class CheckForClusterVersion(XmgPlugin):
    def __init__(self,accessor):
        super(CheckForClusterVersion,self).__init__("Cluster Version Operator",accessor)
    cvo = {}
    parsedData = None
    available = False
    
    def getStatus(self):
        status = "> Cluster Version <\n"
        status = status + "Update Channel: " + self.accessor.getValueFromObj(self.parsedData,"spec","channel") + "\n"
        status = status + "Cluster ID: " + self.accessor.getValueFromObj(self.parsedData,"spec","clusterID") + "\n"
        if "availableUpdates" in self.parsedData["status"] and self.parsedData["status"]["availableUpdates"] is not None:
            for availableUpdate in self.parsedData["status"]["availableUpdates"]:
                status = status + "Available Update: " + self.accessor.getValueFromObj(availableUpdate,"version") + "\n"
        status = status + "Cluster Version Available: "
        if "available" in self.cvo:
            status = status + str(self.cvo["available"])
        else:
            status = status + "Unknown"
        if "desired" in self.parsedData["status"]:            
            status = status + "\nDesired Version: " + self.accessor.getValueFromObj(self.parsedData["status"],"desired","version")
        return status

    def run( self ):    
        entries = self.accessor.getEntriesFromPath("cluster-scoped-resources/config.openshift.io/clusterversions") 
        self.logWithoutResource(LogLevel.LEVEL_INFO,str(len(entries)) + " versions found to verify")    
        warned = False
        self.cvo = {}
        self.cvo["failing"] = False
        self.cvo["available"] = True

        for entry in entries:
            content =  self.accessor.getFileContent(entry)
            data = self.accessor.parseYaml(content)
            self.parsedData = data
            conditions=self.accessor.getValueFromObj(data,"status","conditions")
            if conditions != None:
                if self.arrayHasValue(conditions,"type","Failing","status","True"):
                    self.logWithoutResource(LogLevel.LEVEL_WARNING,"is failing")   
                    self.cvo["failing"] = False
                    warned = True
                if self.arrayHasValue(conditions,"type","Available","status","False"):
                    self.logWithKCS(LogLevel.LEVEL_WARNING,"is not available","411111")   
                    self.cvo["available"] = False
                    warned = True      
        
        if warned:
            summary = "Available\tFailing\n"
            summary = summary + "------------------------------------------\n"                
            available = self.cvo["available"]
            failing = self.cvo["failing"]
            summary = summary + str(available) + "\t\t" + str(failing) + "\n"
            self.setSummary(summary)
