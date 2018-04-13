# -*- coding: utf-8 -*-

from tokentype import TokenType as TT
from token import Token


class Scanner:
    def __init__(self, source, runner):
        self.source = source
        self.runner = runner
        self.tokens = []
        self.indentation_stack = [0]
        self.start = 0
        self.current = 0
        self.line = 1
        self.keywords = {
            "and": TT.AND,
            "else": TT.ELSE,
            "false": TT.FALSE,
            "true": TT.TRUE,
            "for": TT.FOR,
            "fun": TT.FUN,
            "if": TT.IF,
            "none": TT.NONE,
            "or": TT.OR,
            "print": TT.PRINT,
            "return": TT.RETURN,
            "mut": TT.MUT,
            "while": TT.WHILE,
            "in": TT.IN,
            "ensure": TT.ENSURE,
            "var": TT.VAR,
            "break": TT.BREAK,
            "continue": TT.CONTINUE,
            "unstable": TT.UNSTABLE
        }

    def scan_tokens(self):
        while not self.is_at_end():
            # At the beginning of the next lexeme
            self.start = self.current
            self.scan_token()

        # Once all of the token are scanned, append dedents and EOF
        for indent in self.indentation_stack:
            if indent > 0:
                self.tokens.append(Token(TT.DEDENT, '', None, self.line))
        self.tokens.append(Token(TT.EOF, '', None, self.line))
        return self.tokens

    def scan_token(self):
        char = self.advance()

        # Check indentation
        if len(self.tokens) > 0 and self.tokens[-1].type == TT.NEWLINE and char != '\n':
            spaces = self.count_until_not(' ')
            if spaces % 4 != 0:
                self.runner.error(self.line,
                                  "Indentation must a multiplicative of 4.")
                return
            else:
                indentation = spaces // 4

                difference = indentation - self.indentation_stack[-1]

                if difference > 1:
                    self.runner.error(self.line,
                                      "Indentation too large. Expect {}, found {}".format(self.indentation_stack[-1]*4, spaces))
                elif difference == 1:
                    self.indentation_stack.append(indentation)
                    self.tokens.append(Token(TT.INDENT, '', None, self.line))
                elif difference == 0:
                    pass
                elif difference < 0:
                    while self.indentation_stack[-1] > indentation:
                        self.indentation_stack.pop()
                        self.tokens.append(Token(TT.DEDENT, '', None, self.line))

                while char == ' ':
                    char = self.advance()
                    self.start = self.current-1

        # Handle the char
        if char == '(':
            self.add_token(TT.LEFT_PAREN),
        elif char == ')':
            self.add_token(TT.RIGHT_PAREN)
        elif char == '{':
            self.add_token(TT.LEFT_BRACE)
        elif char == '}':
            self.add_token(TT.RIGHT_BRACE)
        elif char == ',':
            self.add_token(TT.COMMA)
        elif char == '.':
            if self.match('.'):
                self.add_token(TT.ELLIPSIS)
            else:
                self.add_token(TT.DOT)
        elif char == '-':
            self.add_token(TT.MINUS)
        elif char == '+':
            self.add_token(TT.PLUS)
        elif char == ';':
            self.add_token(TT.SEMICOLON)
        elif char == '*':
            self.add_token(TT.STAR)
        elif char == '=':
            self.add_token(TT.EQUAL)
        elif char == '[':
            self.add_token(TT.LEFT_BRACKET)
        elif char == ']':
            self.add_token(TT.RIGHT_BRACKET)
        elif char == '@':
            self.pycall()
        elif char == '/':
            self.add_token(TT.SLASH)
        elif char == '\\' or char == 'λ':
            self.add_token(TT.LAMBDA)
        # Comment
        elif char == '#':
            while self.peek() != '\n' and not self.is_at_end():
                self.advance()
        # Double lexemes
        elif char == ':':
            if self.match('='):
                self.add_token(TT.ASSIGNMENT)
            else:
                self.add_token(TT.COLON)
        elif char == '!':
            if self.match('='):
                self.add_token(TT.BANG_EQUAL)
            else:
                self.add_token(TT.BANG)
        elif char == '<':
            if self.match('='):
                self.add_token(TT.LESS_EQUAL)
            else:
                self.add_token(TT.LESS)
        elif char == '>':
            if self.match('='):
                self.add_token(TT.GREATER_EQUAL)
            else:
                self.add_token(TT.GREATER)
        # White space and friends
        elif char == ' ':
            if self.line == 1 and self.current == 0:
                self.runner.error(self.line, "White space is not allowed on the first line")
            else:
                pass
        elif char == '\t':
            self.runner.error(self.line, "Tabs are not allowed.")
        elif char == '\r':
            pass
        elif char == '\n':
            self.line += 1
            if (self.tokens[-1].type != TT.NEWLINE
                and self.tokens[-1].type != TT.DEDENT):
                self.add_token(TT.NEWLINE)
        # Literals
        elif char == '"':
            self.string()
        else:
            # Number literals
            if char.isnumeric():
                self.number()
            # Identifiers
            elif char.isalpha():
                self.identifier()
            else:
                self.runner.error(self.line,
                                  "Unexpected character '"+char+"'.")

    def identifier(self):
        while self.peek().isalnum():
            self.advance()

        # See if the identifier is a reserved word
        text = self.source[self.start:self.current]
        type = self.keywords.get(text, TT.IDENTIFIER)
        self.add_token(type)

    def number(self):
        while self.peek().isnumeric():
            self.advance()

        # Look for a fractional part
        if self.peek() == '.' and self.peek_next().isnumeric():
            # Consume the '.'
            self.advance()
            while self.peek().isnumeric():
                self.advance()

        self.add_token(TT.NUMBER, float(self.source[self.start:self.current]))

    def pycall(self):
        while self.peek() != '@' and not self.is_at_end():
            if self.peek() == '\n':
                self.line += 1
            self.advance()

        # Unterminated string
        if self.is_at_end():
            self.runner.error(self.line, "Unterminated pycall.")
            return

        self.advance()

        self.add_token(TT.PYCALL, self.source[self.start+1:self.current-1])

    def string(self):
        while self.peek() != '"' and not self.is_at_end():
            if self.peek() == '\n':
                self.line += 1
            self.advance()

        # Unterminated string
        if self.is_at_end():
            self.runner.error(self.line, "Unterminated string.")
            return

        # Closing '"'
        self.advance()

        # Trim '"'
        self.add_token(TT.STRING, self.source[self.start+1:self.current-1])

    def match(self, expected):
        if self.is_at_end():
            return False
        if self.source[self.current] != expected:
            return False
        self.current += 1
        return True

    def peek(self):
        return '\0' if self.is_at_end() else self.source[self.current]

    def peek_next(self):
        if self.current + 1 >= len(self.source):
            return '\0'
        return self.source[self.current+1]

    def count_until_not(self, char):
        if self.is_at_end():
            return 0
        position = self.current-1
        if self.source[position] != char:
            return 0
        while position < len(self.source) and self.source[position] == char:
            position += 1
        return position - self.current + 1

    def is_at_end(self):
        return self.current >= len(self.source)

    def advance(self):
        self.current += 1
        return self.source[self.current - 1]

    def add_token(self, type, literal=None):
        text = self.source[self.start:self.current]
        self.tokens.append(Token(type, text, literal, self.line))
