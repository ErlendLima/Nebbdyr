#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
from scanner import Scanner
from token import Token
from tokentype import TokenType
from parser import Parser
from astprinter import AstPrinter
from interpreter import Interpreter
from resolver import Resolver


class Nebbdyr:
    def __init__(self):
        self.interpreter = Interpreter(self)
        self.hadError = False
        self.had_runtime_error = False

    def run_file(self, path):
        with open(path) as text:
            self.run(text.read())

        if self.hadError:
            print("Running failed.")

    def run_prompt(self):
        while True:
            self.run(input("> ")+"\n")
            self.hadError = False
            self.had_runtime_error = False

    def run(self, source):
        scanner = Scanner(source, self)
        tokens = scanner.scan_tokens()

        parser = Parser(self, tokens)
        statements = parser.parse()

        if self.hadError:
            return
        if self.had_runtime_error:
            return

        resolver = Resolver(self.interpreter, self)
        resolver.resolve(statements)

        if self.hadError:
            return

        self.interpreter.interpret(statements)

    def report(self, line, where, message, type):
        print("[line {line}] {type} Error{where}: {message}".format(
            **locals()))
        self.hadError = True

    def error(self, origin, message):
        if isinstance(origin, Token):
            if origin.type == TokenType.EOF:
                self.report(origin.line, " at end", message, "Parser")
            else:
                self.report(origin.line,
                            " at '{origin.lexeme}'".format(**locals()),
                            message, "Parser")
        else:
            self.report(origin, '', message, "Syntax")

    def runtime_error(self, error):
        print("[line {error.token.line}] {error}".format(error=error))
        self.had_runtime_error = True


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('script', nargs='?', default=None)
    args = parser.parse_args()
    nebb = Nebbdyr()
    if args.script is not None:
        nebb.run_file(args.script)
    else:
        nebb.run_prompt()
