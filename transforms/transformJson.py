from .transform import Transform
import json

class TransformJson(Transform):
    def __init__(self):
        Transform.__init__(self)
 
    def run(self):
        print (json.dumps(self.events.getEvents()))