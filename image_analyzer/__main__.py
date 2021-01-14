import numpy as np
import argparse
import sys

from image_analyzer.image_functions import analyseImage, cameraCheck, detectHumanInteraction
from image_analyzer.com.network.tcpClient import TcpClient
from image_analyzer.com.network.networkMessageType import NetworkMessageType
from image_analyzer.com.message import Message

def main(args):
    # Connect to broker
    broker : TcpClient = TcpClient(address=args.ip, port=args.port)

    # Register with broker
    broker.send(messageType = NetworkMessageType.Register, payload = bytearray([23]))

    isRunning: bool = True

    # Check for open cameras
    cameraID = cameraCheck()
    if type(cameraID) == bool and not cameraID:
        # Log for no open camera found
        broker.send(messageType = NetworkMessageType.NoCameraFound, payload = bytearray([]))
        sys.exit()

    cameraID = 3

    while(isRunning == True):
        # Check for incoming message
        incomingMessage : Message = broker.read()
        if incomingMessage.messageType == NetworkMessageType.MakeImage:
            successFlag : bool = False
            for _ in range(10):
                payload : bytearray = analyseImage(cameraID = cameraID)
                if type(payload) == bool and not payload:
                    continue
                else:
                    print(payload)
                    broker.send(messageType = NetworkMessageType.SendImage, payload = payload)
                    successFlag = True
                    break
            # Send Error after 10 tries
            if not successFlag:
                broker.send(messageType = NetworkMessageType.Error, payload = bytearray([]))
        elif incomingMessage.messageType == NetworkMessageType.MonitorHumanInterference and args.hid:
            # Perform function until broker tells IA to stop
            while(broker.read().messageType != NetworkMessageType.StopAnalysis):
                # Check if change in picture is bigger than treshold
                if detectHumanInteraction(cameraID = cameraID):
                    # Send message to broker
                    broker.send(messageType = NetworkMessageType.UnexpectedInterference, payload = bytearray([]))
                else:
                    continue
        elif incomingMessage.messageType == NetworkMessageType.GameOver:
            print('game has been terminated, by Arnie')
            isRunning = False
        else:
            continue

    # Kill the service
    sys.exit(0)

if __name__ == '__main__':
    # Set up argument parsing

    parser = argparse.ArgumentParser(description="Image Analysis Service")
    parser.add_argument("--height", "-H", dest="height", type=int, help="Height of the Connect Four board (int). Default value is 6.", default=6)  # stores value in args.height
    parser.add_argument("--width", "-W", dest="width", type=int, help="Width of the Connect Four board (int). Default value is 7.", default=7)     # stores value in args.width
    parser.add_argument("--ip", "-i", dest="ip", type=str, help="Target ip address (str). Default ip is 127.0.0.1.", default="127.0.0.1")          # stores value in args.ip
    parser.add_argument("--port", "-p", dest="port", type=int, help="Target port (int). Default port is 7777.", default=7777)                      # stores value in args.port
    parser.add_argument("--human-interaction-detection", "-hid", dest="hid", type=bool, 
                        help="Toggle the human interaction detection (bool). Default is True.", default=True)                                      # stores value in args.hid

    main(parser.parse_args())
