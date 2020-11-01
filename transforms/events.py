import collections
from .logLevel import LogLevel
class Events:
    __instance = None
    events = []
    level = LogLevel.valueOf(LogLevel.LEVEL_WARNING)
    @staticmethod 
    def getInstance():
       if Events.__instance == None:
          Events()
       return Events.__instance
       
    def __init__(self):
       if Events.__instance != None:
          raise Exception("This constructor is private - use getInstance() to retrieve an instance of this class")
       else:
          Events.__instance = self

    def setLogLevel(self,level):
        if isinstance(level,int):
            self.level = level
        else:
            self.level = LogLevel.valueOf(level)

    def makeEntry(self,level,source,description):
        entry = {}
        entry["level"] = level
        entry["source"] = source
        entry["description"] = description
        return entry
    
    def addWithoutResource(self,level,source,description):
        if LogLevel.valueOf(level) <= self.level: 
            self.events.append(self.makeEntry(level,source,description))

    def addWtihKCS(self,level,source,description,kcs):
        if LogLevel.valueOf(level) > self.level: 
            return
        kcses = []
        if isinstance(kcs,list) == False:
            kcses.append(kcs)
        else:
            kcses = kcs
        entry = self.makeEntry(level,source,description)
        entry["kcs"] = kcses
        self.events.append(entry)

    def addWtihURL(self,level,source,description,url):
        if LogLevel.valueOf(level) > self.level: 
            return
        urls = []
        if isinstance(url,list) == False:            
            urls.append(url)            
        else:
            urls = url
        entry = self.makeEntry(level,source,description)
        entry["url"] = urls
        self.events.append(entry)

    def getEvents(self):
        return self.events
    