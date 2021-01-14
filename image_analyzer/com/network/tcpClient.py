import socket

from image_analyzer.com.network.networkMessageType import NetworkMessageType
from image_analyzer.com.message import Message

class TcpClient:
    def __init__(self, address: str, port):
        # Create a TCP/IP socket
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (address, port)
        try:
            self.__socket.connect(server_address)
        except socket.error as e:
            # Log e.errno Error Number
            pass


    def send(self, messageType: NetworkMessageType, payload: bytearray = None):
        # Size of payload
        size: int = 0
        if payload is not None:
            size = len(payload)
        message = bytearray([messageType.value, size])
        if payload is not None:
            message.extend(payload)
        try:
            self.__socket.sendall(message)
        except socket.error as e:
            # Log e.errno Error Number
            return False
        else:
            return True
    
    def read(self) -> Message:
        try:
            messageType: NetworkMessageType = NetworkMessageType(self.__socket.recv(1)[0])
            size: int = self.__socket.recv(1)[0]
            payload = None
            if size > 0:
                payload = self.__socket.recv(size)
        except socket.error as e:
            # Log e.errno Error Number
            return False
        else:
            return Message(messageType, size, payload)
    
    def __del__(self):
        self.__socket.close()