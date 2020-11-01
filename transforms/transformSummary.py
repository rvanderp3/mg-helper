from .transform import Transform
from .logLevel import LogLevel
from plugins.xmgPlugin import XmgPlugin
import json
class TransformSummary(Transform):
    fullOutput=None
    def __init__(self,fullOutput):
        Transform.__init__(self)
        self.fullOutput = fullOutput
 
    def run(self):
        if self.fullOutput == None:
            print("\n\n------------------------------------------")        
            print("**** Analysis results ****")        
            print("------------------------------------------\n")        
            for plugin in XmgPlugin.getPlugins():
                summary = plugin.getSummary()
                if summary != None:
                    print ("> Plugin: " + plugin.getName())
                    print (summary+"\n")
            
            print("\n\nOnly plugins which recorded potential issues are shown in the summary. ")
            print("\nFor additional details, use -f <plugin name>")
        else:
            print("\n\n------------------------------------------")        
            print("**** Plugin Events ****")        
            print("------------------------------------------\n")        
            for event in self.events.getEvents():            
                if event["source"] == self.fullOutput and event["level"] == LogLevel.LEVEL_WARNING or event["level"] == LogLevel.LEVEL_ERROR:
                    print(" > "+event["description"])
                    if "kcs" in event:
                        print("Knowledge articles: ")
                        for kcs in event["kcs"]:
                            print(" - https://access.redhat.com/articles/" + kcs)
                            print("")
                    if "url" in event:
                        print("Linked Documentation: ")
                        for url in event["url"]:
                            print(" - " + url)   
                            print("")
                                     