from dataclasses import dataclass

@dataclass
class Record:
  ''' Class for db records '''
  id: int               # sequential number
  user_id: int          # user that sent this record
  date_ts: int          # when record was done
  happiness: float      # happiness 1-10
  comment: str          # a comment for record

  def __init__(self):
    self.id = 0
    self.user_id = ''
    self.date_ts = ''
    self.happiness = 0
    self.comment = ''

  def set_id(self, id: int):
    self.id = int(id)

  def set_user_id(self, user_id: int):
    self.user_id = int(user_id)

  def set_date_ts(self, date_ts: int):
    self.date_ts = int(date_ts)

  def set_happiness(self, happiness: int):
    self.happiness = float(happiness)

  def set_comment(self, comment: str):
    self.comment = str(comment)

  def get_dict(self):
    dict = {}
    dict['user_id'] = int(self.user_id)
    dict['date_ts'] = int(self.date_ts)
    dict['happiness'] = int(self.happiness)
    dict['comment'] = int(self.comment)
    return dict

  def get_obj_from_dict(self, dict):
    obj = Record()
    obj.set_id(dict['id'])
    obj.set_user_id(dict['user_id'])
    obj.set_date_ts(dict['date_ts'])
    obj.set_happiness(dict['happiness'])
    obj.set_comment(dict['comment'])
    return obj