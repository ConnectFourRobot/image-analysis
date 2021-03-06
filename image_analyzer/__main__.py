import numpy as np
import argparse
import sys
import time

from image_analyzer.image_functions import analyseImage, cameraCheck, detectHumanInteraction, getPicture
from image_analyzer.com.network.tcpClient import TcpClient
from image_analyzer.com.network.networkMessageType import NetworkMessageType
from image_analyzer.com.message import Message
from image_analyzer.ia_logging.ia_logger import settingUp, loggingIt

def main(args):
    # Setting up the logger
    settingUp()

    # Connect to broker
    try:
        broker : TcpClient = TcpClient(address=args.ip, port=args.port)
    except:
        # Log connection failed
        loggingIt("Failed to connect to broker.")
        sys.exit()
    
    # Register with broker
    msgConfirm = broker.send(messageType = NetworkMessageType.Register, payload = bytearray([23]))
    if not msgConfirm:
        loggingIt("Failed to send Register message to broker.")
        sys.exit()

    isRunning: bool = True

    # Check for open cameras
    cameraID = cameraCheck()
    if type(cameraID) == bool and not cameraID:
        # Log for no open camera found, no need for msgConfirm since sys.exit() is following anyways
        loggingIt("No open camera found.")
        broker.send(messageType = NetworkMessageType.NoCameraFound, payload = None)
        sys.exit()

    while(isRunning == True):
        # Check for incoming message
        incomingMessage : Message = broker.read()
        if type(incomingMessage) == bool and not incomingMessage:
            sys.exit()
        if incomingMessage.messageType == NetworkMessageType.MakeImage:
            successFlag : bool = False
            for _ in range(10):
                payload : bytearray = analyseImage(cameraID = cameraID)
                if type(payload) == bool and not payload:
                    continue
                else:
                    msgConfirm = broker.send(messageType = NetworkMessageType.SendImage, payload = payload)
                    if not msgConfirm:
                        loggingIt("Failed to send SendImage message to broker.")
                        sys.exit()
                    successFlag = True
                    break
            # Send Error after 10 tries
            if not successFlag:
                msgConfirm = broker.send(messageType = NetworkMessageType.Error, payload = None)
                if not msgConfirm:
                    loggingIt("Failed to send Error message to broker.")
                    sys.exit()
        elif incomingMessage.messageType == NetworkMessageType.MonitorHumanInterference and bool(args.hid):
            # Make the reference picture
            referencePicture = getPicture(cameraID = cameraID)
            # Perform function until broker tells IA to stop, no need to msgConfirm here since it will be checked inside the loop
            detectInteraction: bool = True
            while(detectInteraction):
                time.sleep(0.25)
                # Check if change in picture is bigger than treshold
                if detectHumanInteraction(referencePicture = referencePicture, cameraID = cameraID):
                    # Send message to broker
                    msgConfirm = broker.send(messageType = NetworkMessageType.UnexpectedInterference, payload = None)
                    if not msgConfirm:
                        loggingIt("Failed to send UnexpectedInterference message to broker.")
                        sys.exit()
                else:
                    msgConfirm = broker.send(messageType=NetworkMessageType.NoInteractionDetected, payload=None)
                    if not msgConfirm:
                        loggingIt("Failed to send NoInteractionDetected message to broker.")
                        sys.exit()

                msg: Message = broker.read()
                if msg.messageType == NetworkMessageType.StopAnalysis:
                    detectInteraction = False
                    break
                elif msg.messageType == NetworkMessageType.GameOver:
                    detectInteraction = False
                    isRunning = False
                    break
                elif msg.messageType == NetworkMessageType.CaptureInteractionHeartbeat:
                    # do nothing
                    continue
                else:
                    continue
        elif incomingMessage.messageType == NetworkMessageType.GameOver:
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
