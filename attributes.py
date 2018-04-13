# -*- coding: utf-8 -*-

from enum import Enum, unique


@unique
class Attribute(Enum):
    MUTABLE = 0
    FUNCTION = 1
    UNSTABLE = 2
    CORE = 3
