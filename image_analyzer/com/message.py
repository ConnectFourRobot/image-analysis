class Message:
    def __init__(self, messageType, size: int, payload = None):
        self.messageType = messageType
        self.size = size
        self.payload = payload