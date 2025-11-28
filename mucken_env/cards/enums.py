from enum import IntEnum


class GameType(IntEnum):
    MUCK = 2
    WENZ = 1
    GEIER = 0

class Color(IntEnum):
    SCHELLE = 0
    HERZ = 1
    BLATT = 2
    EICHEL = 3


    def __str__(self):
        return self.name

class Face(IntEnum):
    NEUN = 0
    UNTER = 2
    OBER = 3
    KOENIG = 4
    ZEHN = 10
    ASS = 11

    def __str__(self):
        return self.name