import numpy as np
import argparse
import sys

from image_analyzer.com.network.tcpClient import TcpClient
from image_analyzer.com.network.networkMessageType import NetworkMessageType
from image_analyzer.com.message import Message

def main(args):
    # Connect to broker
    broker = TcpClient(address=args.ip, port=args.port)

    # Register with broker
    broker.send(type = NetworkMessageType.Register, payload = None)

    isRunning: bool = True

    while(isRunning == True):
        # Operation handling is done in this loop
        isRunning == False

    sys.exit(0)

if __name__ == '__main__':
    # Set up argument parsing

    parser = argparse.ArgumentParser(description="Image Analysis Service")
    parser.add_argument("--height", "-H", dest="height", type=int, help="Height of the Connect Four board (int).", default=6)  # stores value in args.height
    parser.add_argument("--width", "-W", dest="width", type=int, help="Width of the Connect Four board (int).", default=7)     # stores value in args.width
    parser.add_argument("--ip", "-i", dest="ip", type=str, help="Target ip address (str).", default="127.0.0.1")               # stores value in args.ip
    parser.add_argument("--port", "-p", dest="port", type=int, help="Target port (int).", default=7777)                        # stores value in args.port

    main(parser.parse_args())
