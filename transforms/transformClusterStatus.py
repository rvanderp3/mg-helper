from .transform import Transform
from .logLevel import LogLevel
from plugins.xmgPlugin import XmgPlugin
import json
class TransformClusterStatus(Transform):
    fullOutput=None
    def __init__(self,fullOutput):
        Transform.__init__(self)
        self.fullOutput = fullOutput
 
    def run(self):
        print("\n\n")
        for plugin in XmgPlugin.getPlugins():
            summary = plugin.getStatus()
            if summary != None:
                print (summary+"\n")
        