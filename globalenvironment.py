from environment import Environment
from token import Token
from tokentype import TokenType
from attributes import Attribute
from errors import RuntimeException


class CoreFunction:
    def arity(self):
        return self._arity


class GlobalEnvironment(Environment):
    def __init__(self, *args):
        super(GlobalEnvironment, self).__init__(*args)
        self.define_globals()

    def define_global(self, name, value, attributes=[]):
        token = self.global_token(name)
        self.define(token, value, attributes+[Attribute.CORE])

    def global_token(self, lexeme):
        return Token(TokenType.IDENTIFIER, lexeme, None, "core")

    def define_global_var(self, lexeme):
        token = self.global_token(lexeme)
        self.define(token, None, [Attribute.CORE, Attribute.UNSTABLE,
                                  Attribute.MUTABLE])

    def define_globals(_self):
        class fun_list(CoreFunction):
            _arity = 5

            def call(self, interpreter, arguments):
                return [*arguments]

        class fun_tostr(CoreFunction):
            _arity = 1

            def call(self, interpreter, arguments):
                return str(*arguments)

        class fun_tonum(CoreFunction):
            _arity = 1

            def call(self, interpreter, arguments):
                try:
                    return float(*arguments)
                except TypeError as err:
                    raise RuntimeException(_self.global_token("tonumber"),
                                           "Invalid argument type for tonumber")

        class fun_len(CoreFunction):
            _arity = 1

            def call(self, interpreter, arguments):
                try:
                    return len(*arguments)
                except TypeError as err:
                    raise RuntimeException(_self.global_token("len"),
                                           "Invalid argument type for len.")

        _self.define_global("list", fun_list())
        _self.define_global("tostring", fun_tostr())
        _self.define_global("tonumber", fun_tonum())
        _self.define_global("len", fun_len())

        [_self.define_global_var(var) for var in
        ["elements", "mass", "localomp"]]

