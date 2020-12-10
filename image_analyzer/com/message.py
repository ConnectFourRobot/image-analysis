class Message:
    def __init__(self, type, size: int, payload = None):
        self.type = type
        self.size = size
        self.payload = payload