from enum import Enum
class NetworkMessageType(Enum):
    Register = 0
    MakeImage = 1
    SendImage = 2
    StopAnalysis = 3
    MonitorHumanInterference = 4
    UnexpectedInterference = 5
    GameOver = 6
    NoCameraFound = 253
    Error = 254
    NoInteractionDetected = 127
    CaptureInteractionHeartbeat = 128

