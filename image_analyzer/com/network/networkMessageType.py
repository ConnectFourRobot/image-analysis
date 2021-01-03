from enum import Enum
class NetworkMessageType(Enum):
    Register = 0
    RequestImage = 1
    AnswerImage = 2
    StopImage = 3
    TurnRobot = 4
    Unexpected = 5
    GameOver = 6
