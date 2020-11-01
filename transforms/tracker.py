class Tracker:
    namespaces = {}
    
    def getTrackedData(self):
        return self.namespaces
        
    def getSummaryString(self,header,*fields):
        summary = header
        summary = summary + "\n-------------------------------------------------\n"
        namespaces = self.namespaces
        hasEntries = False
        for namespace in namespaces:
            namespaceObj = namespaces[namespace]
            nonZero=False
            nsString = ""
            for field in fields:
                if field in namespaceObj:
                    events = namespaceObj[field]                
                    if events > 0:
                        nsString = nsString + str(events) + "\t\t"
                        nonZero = True
                        hasEntries = True
                    else:
                        nsString = nsString + "-\t\t"
                else:
                    nsString = nsString + "-\t\t"
            if nonZero:
                summary = summary + nsString + "\t"+namespace + "\n"
        if hasEntries == False:
            summary = None
        return summary
    
    def add(self, namespace, field, amount):
        objCounter = None
        if namespace != None:            
            if namespace in self.namespaces:
                objCounter = self.namespaces[namespace]                        
            else:                        
                objCounter = {}
                self.namespaces[namespace] = objCounter
        if objCounter != None:
            if field in objCounter:
                objCounter[field] = objCounter[field] + amount
            else:
                objCounter[field] = 0


    def increment(self, namespace, field):
        self.add(namespace,field,1)