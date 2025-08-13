
class Tool:
  def __init__(self, name : str):
    self.name = name
  
  def execute(self, user_query : str):
    raise NotImplementedError