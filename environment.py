# -*- coding: utf-8 -*-

from errors import RuntimeException
from attributes import Attribute
from nebbtypes import Type


class Variable:
    def __init__(self, name, value, attributes):
        self.name = name
        self.value = value
        self.attributes = attributes
        self.defined = False if value is None else True

    def assign(self, value):
        if Attribute.MUTABLE in self.attributes:
            if Attribute.UNSTABLE not in self.attributes:
                if self.value is not None and Type.type(self.value) != Type.type(value):
                    raise RuntimeException(self.name, "Variable '{}' is type stable and can not change type to '{}'".format(self.name.lexeme, Type.type(value)))
            self.value = value
        elif self.defined:
            raise RuntimeException(self.name, "Variable '{}' is immutable and can not be redefined.".format(self.name.lexeme))
        self.defined = True


class Environment:
    def __init__(self, enclosing=None):
        self.values = {}
        self.enclosing = enclosing

    def define(self, name, value, attributes=[]):
        self.values[name.lexeme] = Variable(name, value, attributes)

    def get(self, name):
        if name.lexeme in self.values:
            if self.values[name.lexeme].defined:
                return self.values[name.lexeme].value
            else:
                raise RuntimeException(name, "Can not get value of unassigned variable '{}'.".format(name.lexeme))

        if self.enclosing is not None:
            return self.enclosing[name]

        raise RuntimeException(name, "Undefined variable '{}'.".format(
            name.lexeme))

    def get_at(self, distance, name):
        if self.ancestor(distance).values[name.lexeme].defined:
            return self.ancestor(distance).values[name.lexeme].value
        else:
            raise RuntimeException(name, "Can not get value of unassigned variable '{}'.".format(name.lexeme))

    def assign_at(self, distance, name, value):
        try:
            self.ancestor(distance).values[name.lexeme].assign(value)
        except RuntimeException as exc:
            raise RuntimeException(name, exc.msg)

    def ancestor(self, distance):
        environment = self
        for i in range(distance):
            environment = environment.enclosing

        return environment

    def __getitem__(self, key):
        return self.get(key)

    def assign(self, name, value):
        if name.lexeme in self.values:
            return self.values[name.lexeme].value
        else:
            if self.enclosing is not None:
                return self.enclosing.assign(name, value)
            raise RuntimeException(name, "Undefined variable '{}'.".format(name.lexeme))
