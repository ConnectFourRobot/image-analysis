import configparser
import serial

from image_analyzer.com.network.tcpClient import TcpClient
from image_analyzer.com.network.networkMessageType import NetworkMessageType

def main():
    # Connect to broker
    broker = TcpClient(address="127.0.0.1", port=7777)

    # Send ready message
    broker.send(1)

if __name__ == '__main__':
    print("Hello World")