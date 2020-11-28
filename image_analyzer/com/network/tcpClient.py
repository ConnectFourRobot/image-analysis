import socket
import sys

from image_analyzer.com.network.networkMessageType import NetworkMessageType
from image_analyzer.com.message import Message

class TcpClient:
    def __init__(self, address: str, port):
        # Create a TCP/IP socket
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (address, port)
        self.__socket.connect(server_address)

    def send(self, type: NetworkMessageType, payload: bytearray = None) -> None:
        # Size of payload
        size: int = 0
        if payload is not None:
            size = len(payload)
        message = bytearray([type.value, size])
        if payload is not None:
            message.extend(payload)
        self.__socket.send(message)
    
    def read(self) -> Message:
        type: NetworkMessageType = NetworkMessageType(self.__socket.recv(1)[0])
        size: int = 0
        # Read messages will never have a payload and thus no size, maybe return error message if there is a size / payload?
        #if size > 0:
        #    return Error
        return Message(type, size)
    
    def __del__(self):
        self.__socket.close()