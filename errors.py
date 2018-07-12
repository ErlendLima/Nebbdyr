# -*- coding: utf-8 -*-


class RuntimeException(Exception):
    def __init__(self, token, *args, **kwargs):
        self.token = token
        self.msg = args[0]
        Exception.__init__(self, *args, **kwargs)


class ParseException(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class BreakException(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class ContinueException(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class Return(Exception):
    def __init__(self, value, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)
        self.value = value


class MutableException(Exception):
    def __init__(self, msg, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)
        self.msg = msg


class StableException(Exception):
    def __init__(self, msg, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)
        self.msg = msg


class IndexException(Exception):
    def __init__(self, token, *args, **kwargs):
        self.token = token
        self.msg = args[0]
        Exception.__init__(self, *args, **kwargs)
