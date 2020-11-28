from enum import Enum
class NetworkMessageType(Enum):
    Ready = 1
    RequestImage = 2
    AnswerImage = 3
    StopImage = 4
    TurnRobot = 5
    Unexpected = 6
    GameOver = 7
