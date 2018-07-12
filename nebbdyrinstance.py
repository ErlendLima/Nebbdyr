from errors import RuntimeException

class NebbdyrInstance:
    def __init__(self, klasse):
        self.klasse = klasse
        self.fields = {}

    def __str__(self):
        return self.klasse.name + " instance"

    def get(self, name):
        if name in self.fields:
            return self.fields[name]

        method = self.klasse.find_method(self, name.lexeme)
        if method is not None:
            return method

        raise RuntimeException(name, f"Undefined property {name.lexeme}.")

    def set(self, name, value):
        self.fields[name] = value
