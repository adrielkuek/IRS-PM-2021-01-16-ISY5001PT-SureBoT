from botserver import main_app
from botserver import initCode


def getApp():
    print("Calling init code")
    initCode()
    print("Code initialization has successfully completed")
    return main_app
