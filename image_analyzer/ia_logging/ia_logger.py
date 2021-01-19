import logging
import os
import time

def settingUp():
    # This function creates the directory if it does not already exist
    path = os.getcwd()
    path = path + "/logs/ia/"
    if not os.path.exists(path):
        os.makedirs(path)

    logging.basicConfig(level=logging.INFO, format="%(asctime)s :: %(message)s", filename="./logs/ia/debug" + str(int(time.time())) + ".log")

def loggingIt(text : str):
    logging.info(text)