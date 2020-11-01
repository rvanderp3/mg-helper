from .transform import Transform
import yaml

class TransformYaml(Transform):
    def __init__(self):
        Transform.__init__(self)
 
    def run(self):
        print (yaml.dump(self.events.getEvents()))