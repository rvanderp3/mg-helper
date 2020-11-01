from .xmgPlugin import XmgPlugin
from transforms.logLevel import LogLevel
class CheckForNodes(XmgPlugin):
    def __init__(self,accessor):
        super(CheckForNodes,self).__init__("Node Status",accessor)

    nodes=[]

    def getStatus(self):
        status="\n> Nodes <\n"
        status = status + "Memory(GB)\tCores\tVersion\t\t\tRole\tName\n"
        status = status + "------------------------------------------------------------------\n"
        for node in self.nodes:
            status = status + str(node["memory"]) + "\t\t" + str(node["cpus"]) + "\t" + str(node["version"]) + "\t" + str(node["role"]) + "\t" + node["name"] + "\n"
            status = self.appendFlagSummary(node,status)
        return status

    def appendFlagSummary(self, node, text):
        conditions = ""
        if node["ready"] == False:
            conditions = " ^ Not Ready\n"
        if node["disk-pressure"] == True:
            conditions = conditions + " ^ Has Disk Pressure\n"
        if node["memory-pressure"] == True:
            conditions = conditions + " ^ Has Memory Pressure\n"
        if node["pid-pressure"] == True:
            conditions = conditions + " ^ Has PID Pressure\n"
        if conditions != "":
            text = text + conditions
        return text

    def run( self ):    
        entries = self.accessor.getEntriesFromPath("cluster-scoped-resources/core/nodes") 
        self.logWithoutResource(LogLevel.LEVEL_INFO,str(len(entries)) + " Nodes found to verify")
        nodes = []
        warned = False       
        for entry in entries:                         
            content = self.accessor.getFileContent(entry)
            out = self.accessor.parseYaml(content)
            nodename=self.accessor.getValueFromObj(out,"metadata","name")
            self.logWithoutResource(LogLevel.LEVEL_INFO,"Checking ["+nodename+"]")
            node = {}
            node["memory-pressure"] = node["disk-pressure"] = node["pid-pressure"] = False
            node["ready"] = True

            # Check node statuses
            if "status" in out:
                status = out["status"]
                if "conditions" in status:                    
                    if self.arrayHasValue(status["conditions"],"type","Ready","status","False"):
                        warned = True
                        node["ready"] = False
                        self.logWithoutResource(LogLevel.LEVEL_WARNING,"Node["+nodename+"] is not ready")
                    if self.arrayHasValue(status["conditions"],"type","MemoryPressure","status","True"):
                        warned = True
                        node["memory-pressure"] = True
                        self.logWithURL(LogLevel.LEVEL_WARNING,"Node["+nodename+"] has MemoryPressure","https://docs.openshift.com/container-platform/3.11/admin_guide/out_of_resource_handling.html#out-of-resource-scheduler")
                    if self.arrayHasValue(status["conditions"],"type","DiskPressure","status","True"):
                        node["disk-pressure"] = True
                        warned = True
                        self.logWithURL(LogLevel.LEVEL_WARNING,"Node["+nodename+"] has DiskPressure","https://docs.openshift.com/container-platform/3.11/admin_guide/out_of_resource_handling.html#out-of-resource-scheduler")
                    if self.arrayHasValue(status["conditions"],"type","PIDPressure","status","True"):
                        warned = True
                        node["pid-pressure"] = True
                        self.logWithoutResource(LogLevel.LEVEL_WARNING,"Node["+nodename+"] has PIDPressure")
            
            # Check minimum requirements
            minRAMGB = 16
            minCPUs = 4
            resourceUrl = "https://docs.openshift.com/container-platform/4.1/installing/installing_bare_metal/installing-bare-metal.html#minimum-resource-requirements_installing-bare-metal"
            if self.accessor.getValueFromObj(out,"metadata","labels","node-role.kubernetes.io/master") != None:
                minRAMGB = 16
                minCPUs = 4
            elif self.accessor.getValueFromObj(out,"metadata","labels","node-role.kubernetes.io/worker") != None:
                minRAMGB = 8
                minCPUs = 2
            capacity = self.accessor.getValueFromObj(out,"status","capacity","memory")
            cpus = self.accessor.getValueFromObj(out,"status","capacity","cpu")            
            if capacity != None:                
                try:
                    # capacity is represented in Ki                  
                    capacity = capacity[0:-2]
                    capacity = int(capacity) / (1000*1000)                
                    if capacity < minRAMGB:
                        warned = True
                        self.logWithURL(LogLevel.LEVEL_WARNING,"Node has insufficient physical memory["+nodename+"]. Found ["+str(capacity)+"GiB], requires ["+str(minRAMGB)+"GiB]",resourceUrl)
                except:
                    self.logWithoutResource(LogLevel.LEVEL_WARNING,"Unable to get physical memory capacity for ["+nodename+"]")
            if cpus != None:                
                try:
                    # capacity is represented in Ki                  
                    cpus = int(cpus)                
                    if cpus < minCPUs:
                        warned = True
                        self.log(LogLevel.LEVEL_WARNING,"Node has insufficient CPU capacity["+nodename+"]. Found ["+str(cpus)+"], requires ["+str(minCPUs)+"]",resourceUrl)
                except:
                    self.logWithoutResource(LogLevel.LEVEL_WARNING,"Unable to get physical memory capacity for ["+nodename+"]")
            
            node["name"] = nodename
            node["memory"] = capacity
            node["cpus"] = cpus
            node["version"] = self.accessor.getValueFromObj(out,"status","nodeInfo","kubeletVersion")        
            node["role"] = ""    
            if self.accessor.getValueFromObj(out,"metadata","labels","node-role.kubernetes.io/master") != None:
                node["role"] = "master"
            if self.accessor.getValueFromObj(out,"metadata","labels","node-role.kubernetes.io/worker") != None:
                node["role"] = "worker"
            
            node["warned"] = True
            nodes.append(node)
            self.nodes.append(node)
        if warned:
            summary = "Insufficient\n"
            summary = summary + "resources\tMemory(GB)\tCores\tName\n"
            summary = summary + "------------------------------------------------------------------\n"
            for node in nodes:
                summary = summary + str(node["warned"]) + "\t\t" + str(node["memory"]) + "\t\t" + str(node["cpus"]) + "\t" + node["name"] + "\n"
                summary = self.appendFlagSummary(node,summary)
                self.setSummary(summary)