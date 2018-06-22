from nebbdyrinstance import NebbdyrInstance

class NebbdyrClass:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def call(self, interpreter, arguments):
        instance = NebbdyrInstance(self)
        return instance

    def arity(self):
        return 0
