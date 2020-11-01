from .xmgPlugin import XmgPlugin
from transforms.logLevel import LogLevel

class CheckForClusterOperator(XmgPlugin):
    def __init__(self,accessor):
        super(CheckForClusterOperator,self).__init__("Cluster Operator",accessor)

    operatorSummary = {}

    def getStatus(self):
        return "> Cluster Operators <\n" + self.buildOperatorTable(self.operatorSummary)

    def buildOperatorTable(self,operators):
        summary = "Version\tAvailable\tProgressing\tDegraded\tNamespace\n"
        summary = summary + "--------------------------------------------------------------------------------\n"                
        for operatorName in self.operatorSummary:
            operatorStatus = self.operatorSummary[operatorName]
            available = operatorStatus["available"]
            degraded = operatorStatus["degraded"]
            progressing = operatorStatus["progressing"]
            version = operatorStatus["version"]
            summary = summary + str(version) + "\t\t" + str(available) + "\t\t" + str(progressing) + "\t\t" + str(degraded) + "\t\t"+ operatorName + "\n"
        return summary

    def run( self ):    
        entries = self.accessor.getEntriesFromPath("cluster-scoped-resources/config.openshift.io/clusteroperators") 
        self.logWithoutResource(LogLevel.LEVEL_INFO,str(len(entries)) + " Operators found to verify")    
        warned=False
        self.operatorSummary = {}
        for entry in entries:
            content =  self.accessor.getFileContent(entry)
            data = self.accessor.parseYaml(content)
            opname=self.accessor.getValueFromObj(data,"metadata","name")
            self.logWithoutResource(LogLevel.LEVEL_INFO,"Checking"+opname)      
            conditions=self.accessor.getValueFromObj(data,"status","conditions")
            versions=self.accessor.getValueFromObj(data,"status","versions")
            operatorStatus = {}
            if versions != None:
                operatorStatus["version"] = self.arrayGetValue(versions,"name","operator","version")
            else:
                operatorStatus["version"] = "----"

            if conditions != None:                
                operatorStatus["degraded"] = False
                operatorStatus["available"] = True
                operatorStatus["progressing"] = False
                if self.arrayHasValue(conditions,"type","Degraded","status","True"):
                    self.logWithoutResource(LogLevel.LEVEL_WARNING,"Operator ["+opname + "] is degraded")    
                    operatorStatus["degraded"]=True
                    warned = True
                if self.arrayHasValue(conditions,"type","Available","status","False"):
                    self.logWithoutResource(LogLevel.LEVEL_WARNING,"Operator ["+opname + "] is not available")    
                    operatorStatus["available"] = False
                    warned = True
                if self.arrayHasValue(conditions,"type","Progressing","status","True"):                    
                    operatorStatus["progressing"] = True

                self.operatorSummary[opname] = operatorStatus
        if warned:
            filteredNamespaces = {}
            for operatorName in self.operatorSummary:
                operatorStatus = self.operatorSummary[operatorName]
                available = operatorStatus["available"]
                degraded = operatorStatus["degraded"]
                if available and degraded == False:
                    continue       
                filteredNamespaces[operatorName] = self.operatorSummary[operatorName]     
            self.setSummary(self.buildOperatorTable(filteredNamespaces))
