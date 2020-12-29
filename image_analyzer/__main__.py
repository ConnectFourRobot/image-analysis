import numpy as np
import argparse

from image_analyzer.com.network.tcpClient import TcpClient
from image_analyzer.com.network.networkMessageType import NetworkMessageType
from image_analyzer.com.message import Message

# Sign up, Type 0, no payload | out
# Ready, Type 1, no payload | out

# Analyse Gameboard: type 2, no payload | in
# Game situation: type 3, payload is array | out
# Stop analysing: type 4, no payload | in
# Robot turn: type 5, no payload | in
# Player is interferring with Robot moving: type 6, no payload | out
# Game over: type 7, no payload | in

# Errors: types 254 descending

# Set up argument parsing

parser = argparse.ArgumentParser(description="Image Analysis Service")
parser.add_argument("--height", "-H", dest="height", type=int, help="Height of the Connect Four board (int).")  # stores value in args.height
parser.add_argument("--width", "-W", dest="width", type=int, help="Width of the Connect Four board (int).")     # stores value in args.width
parser.add_argument("--ip", "-i", dest="ip", type=str, help="Target ip address (str).")                         # stores value in args.ip
parser.add_argument("--port", "-p", dest="port", type=int, help="Target port (int).")                           # stores value in args.port

args = parser.parse_args()

def main():
    # Connect to broker
    broker = TcpClient(address=args.ip, port=args.port)

    # Register with broker
    broker.send(type = NetworkMessageType.Register, payload = None)

    # Send ready message
    broker.send(type = NetworkMessageType.Ready, payload = None)

    isRunning: bool = True

    while(isRunning == True):
        # Check for incoming message
        inc_message: Message = broker.read()
        if inc_message.type == NetworkMessageType.RequestImage:
            ## send array
            dummy_array = np.zeros((6,7), dtype = np.uint8, order = 'C')
            dummy_data = bytearray(dummy_array.data)
            #broker.send(type = NetworkMessageType.AnswerImage, size = 98, payload = dummy_data)
            out_msg: Message = Message(type = NetworkMessageType.AnswerImage, size = 98, payload = dummy_data)
            broker.__socket.send(out_msg)
        elif inc_message.type == NetworkMessageType.StopImage:
            ## stop taking pictures
            print("Not implemented yet.")
        elif inc_message.type == NetworkMessageType.TurnRobot:
            ## watch for human interaction, then send abort
            #broker.send(type = NetworkMessageType.Unexpected, size = 0, payload = None)
            out_msg: Message = Message(type = NetworkMessageType.Unexpected, size = 0, payload = None)
            broker.__socket.send(out_msg)
        elif inc_message.type == NetworkMessageType.GameOver:
            ## game is over, exit while loop
            isRunning == False
        else:
            continue

if __name__ == '__main__':
    main()