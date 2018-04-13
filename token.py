# -*- coding: utf-8 -*-


class Token:
    """
    A bundle containing the raw lexeme along with other things the
    scanner learned about it
    """
    def __init__(self, type, lexeme, literal, line):
        self.type = type
        self.lexeme = lexeme
        self.literal = literal
        self.line = line

    def __repr__(self):
        return "{} {} {}".format(self.type, self.lexeme, self.literal)
