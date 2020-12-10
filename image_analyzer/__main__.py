import sys

from image_analyzer.com.network.tcpClient import TcpClient
from image_analyzer.com.network.networkMessageType import NetworkMessageType

def main():
    # Connect to broker
    broker = TcpClient(address=sys.argv[1], port=sys.argv[2])

    # Send ready message
    broker.send(NetworkMessageType.Ready)

if __name__ == '__main__':
    main()