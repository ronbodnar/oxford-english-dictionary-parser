import json
import copy

class Word:
    
    def __init__(self, *args):
        self.text = args[0] if len(args) > 0 else ''
        self.snippet = args[1] if len(args) > 1 else ''
        self.parts_of_speech = args[2] if len(args) > 2 else ''
        
    def toJSON(self):
        dump = copy.deepcopy(self)
        del dump.snippet
        del dump.parts_of_speech
        return json.dumps(dump, default=lambda o: o.__dict__, indent=4)