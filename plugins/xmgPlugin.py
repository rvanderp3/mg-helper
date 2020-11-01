from transforms.events import Events
from transforms.logLevel import LogLevel
from utilities.importerHelper import ImporterHelper
import sys, inspect
from importlib import import_module
class XmgPlugin(object):
    warned = False
    events = Events.getInstance()
    enabled = False
    pluginList = []
    whitelistAbbreviation=""
    description=""
    name = ""
    group= "analysis"
    summary=None

    def __init__ (self,name,accessor):        
        self.name = name
        self.accessor = accessor

    def logWithKCS(self,level,description,kcs):
        if self.warned == False:
            if LogLevel.valueOf(level)<= LogLevel.valueOf(LogLevel.LEVEL_WARNING):
                self.warned=True
        self.events.addWtihKCS(level,self.name,description,kcs)

    def logWithURL(self,level,description,url):
        if self.warned == False:
            if LogLevel.valueOf(level)<= LogLevel.valueOf(LogLevel.LEVEL_WARNING):
                self.warned=True
        self.events.addWtihURL(level,self.name,description,url)

    def logWithoutResource(self,level,description):
        if self.warned == False:
            if LogLevel.valueOf(level)<= LogLevel.valueOf(LogLevel.LEVEL_WARNING):
                self.warned=True
        self.events.addWithoutResource(level,self.name,description)

    def run(self):
        pass

    def arrayGetValue(self,array,key,keyvalue,value):
        outval=None
        for val in array:
            if key in val:
                if val[key] != keyvalue:
                    continue
                if value in val:
                    outval = val[value]
        return outval   
        
    def arrayHasValue(self,array,key,keyvalue,value,matchvalue):
        value = self.arrayGetValue(array,key,keyvalue,value)
        return value != None and value == matchvalue

    def getName(self):
        return self.name
    
    def getGroup(self):
        return self.group

    # Extended by plugins to provide a summary output for the summary transformer
    def getSummary(self):
        return self.summary

    def setSummary(self, summary):
        self.summary = summary

    def getStatus(self):
        return None

    @staticmethod
    def getPlugins(): 
        return XmgPlugin.pluginList

    @staticmethod
    def enumeratePlugins(accessor,group="analysis",includeList=None,excludeList=None):
        XmgPlugin.pluginList = []
        if includeList != None:
            includeList = includeList.split(",")  

        if excludeList != None:
            excludeList = excludeList.split(",")        
        
        import plugins        
        moduleNames = ImporterHelper(plugins).get_modules()
        for moduleName in moduleNames:
            module = import_module("plugins."+moduleName)
            if module == None:
                continue
            for name, obj in inspect.getmembers(module):
                if name != "XmgPlugin" and inspect.isclass(obj) and issubclass(obj, XmgPlugin):                    
                    plugin = getattr(module,name)
                    plugin = plugin(accessor)
                    if plugin.group == group:
                        if includeList != None:                            
                            if (plugin.getName() in includeList) == False:                                
                                continue
                        if excludeList != None:
                            if plugin.getName() in excludeList:
                                continue
                        XmgPlugin.pluginList.append(plugin)
        return XmgPlugin.pluginList

    
