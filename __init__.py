from BotServer import main_app
from BotServer import initCode


def getApp():
    print("Calling init code")
    initCode()
    print("Code initialization has successfully completed")
    return main_app
