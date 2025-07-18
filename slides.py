from enum import Enum, auto

class InstallerSlide(Enum):
    WELCOME = auto()
    LOCATION = auto()
    KEYBOARD = auto()
    PARTITIONING = auto()
    USERS = auto()
    DESKTOP = auto()
    SUMMARY = auto()
    INSTALL = auto()
    FINISH = auto()
