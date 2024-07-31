class Word:
    
    def __init__(self, *args):
        self.text = args[0] if len(args) > 0 else ''
        self.snippet = args[1] if len(args) > 1 else ''
        self.parts_of_speech = args[2] if len(args) > 2 else ''