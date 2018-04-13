# -*- coding: utf-8 -*-

from environment import Environment
from errors import Return


class NebbdyrFunction:
    def __init__(self, declaration, closure):
        self.declaration = declaration
        self.closure = closure

    def call(self, interpreter, arguments):
        environment = Environment(self.closure)
        for i, parameter in enumerate(self.declaration.parameters):
            environment.define(parameter, arguments[i])
        try:
            interpreter.execute_block(self.declaration.body, environment)
        except Return as return_value:
            return return_value.value

    def Nebbdyr_function(self, declaration):
        self.declaration = declaration

    def arity(self):
        return len(self.declaration.parameters)

    def to_string(self):
        return "<fn " + self.declaration.name.lexeme + ">"
