from .events import Events

class Transform:
  events=None
  def __init__ (self):        
    self.events = Events.getInstance()

  def run(self):
    # override this method to implement desired transform
    pass

