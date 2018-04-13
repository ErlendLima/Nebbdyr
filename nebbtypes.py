# -*- coding: utf-8 -*-

from enum import Enum, unique


@unique
class Type(Enum):
    NUMBER = 0
    FUNCTION = 1
    STRING = 2
    LIST = 3
    TUPLE = 4
    DICTIONARY = 5
    NONE = 6

    @classmethod
    def type(cls, var):
        if isinstance(var, (float, int)):
            return cls.NUMBER
        if isinstance(var, str):
            return cls.STRING
        if isinstance(var, list):
            return cls.LIST
        if isinstance(var, tuple):
            return cls.TUPLE
        if isinstance(var, dict):
            return cls.DICT
        if isinstance(var, type(lambda x: x)):
            return cls.FUNCTION
        if isinstance(var, type(None)):
            return cls.NONE
        else:
            print("Uncategorized type", type(var))
            return type(var)
