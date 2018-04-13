# -*- coding: utf-8 -*-


class Expr:
    def accept(self, visitor):
        return visitor.visit(self)


class Stmt:
    pass
