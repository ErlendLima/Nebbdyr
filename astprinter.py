# -*- coding: utf-8 -*-

from expr import *
from token import Token
from tokentype import TokenType


class AstPrinter:
    def print(self, expr):
        return expr.accept(self)

    def visit_binary_expr(self, expr):
        return self.parenthesize(expr.operator.lexeme, expr.left, expr.right)

    def visit_grouping_expr(self, expr):
        return self.parenthesize("group", expr.expression)

    def visit_literal_expr(self, expr):
        return str(expr.value)

    def visit_unary_expr(self, expr):
        return self.parenthesize(expr.operator.lexeme, expr.right)

    def parenthesize(self, name, *args):
        text = " ".join(expr.accept(self) for expr in args)
        return "({name} {text})".format(**locals())


if __name__ == '__main__':
    expression = Binary(
        Unary(
            Token(TokenType.MINUS, "-", None, 1),
            Literal(123)),
        Token(TokenType.STAR, "*", None, 1),
        Grouping(
            Literal(45.67)))

    printer = AstPrinter()
    print(printer.print(expression))
