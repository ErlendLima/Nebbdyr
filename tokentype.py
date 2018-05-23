#!/usr/bin/env python
# -*- coding: utf-8 -*-

from enum import Enum, unique


@unique
class TokenType(Enum):
    # Single-character tokens
    LEFT_PAREN = 1
    RIGHT_PAREN = 2
    LEFT_BRACE = 3
    RIGHT_BRACE = 4
    LEFT_BRACKET = 38
    RIGHT_BRACKET = 39
    COMMA = 5
    DOT = 6
    MINUS = 7
    PLUS = 8
    SEMICOLON = 9
    COLON = 37
    SLASH = 10
    STAR = 11
    PYCALL = 41
    NEWLINE = 42
    INDENT = 44
    DEDENT = 45
    LAMBDA = 49

    # One or two character tokens
    BANG = 12
    BANG_EQUAL = 13
    EQUAL = 14
    ASSIGNMENT = 15
    GREATER = 16
    GREATER_EQUAL = 17
    LESS = 18
    LESS_EQUAL = 19
    ELLIPSIS = 48

    # Literals
    IDENTIFIER = 20
    STRING = 21
    INT = 22
    FLOAT = 53

    # Keywords
    AND = 23
    ELSE = 24
    FALSE = 25
    FUN = 26
    FOR = 27
    IF = 28
    NONE = 29
    OR = 30
    PRINT = 31
    RETURN = 32
    TRUE = 33
    MUT = 34
    WHILE = 35
    IN = 36
    ENSURE = 40
    VAR = 43
    BREAK = 46
    CONTINUE = 47
    CLASS = 51
    UNSTABLE = 52

    EOF = 50
