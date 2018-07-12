from nebbdyrinstance import NebbdyrInstance

class NebbdyrClass:
    def __init__(self, name, methods):
        self.name = name
        self.methods = methods

    def find_method(self, instance, name):
        if name in self.methods:
            return self.methods[name]

    def __str__(self):
        return self.name

    def call(self, interpreter, arguments):
        instance = NebbdyrInstance(self)
        return instance

    def arity(self):
        return 0
