# -*- coding: utf-8 -*-

from enum import Enum, unique


@unique
class FunctionType(Enum):
    NONE = 0
    FUNCTION = 1


@unique
class VariableState(Enum):
    DECLARED = 0
    DEFINED = 1
    USED = 2
    CORE = 3


class Resolver:
    def __init__(self, interpreter, nebbdyr):
        self.interpreter = interpreter
        self.nebbdyr = nebbdyr
        self.scopes = [{}]
        for name in self.interpreter.globals.values:
            self.scopes[0][name] = VariableState.CORE
        self.current_function = FunctionType.NONE

    def visit_block_stmt(self, stmt):
        self.begin_scope()
        self.resolve(stmt.statements)
        self.end_scope()

    def visit_class_stmt(self, stmt):
        self.declare(stmt.name)
        self.define(stmt.name)

    def visit_expression_stmt(self, stmt):
        self.resolve(stmt.expression)

    def visit_function_stmt(self, stmt):
        self.declare(stmt.name)
        self.define(stmt.name)

        self.resolve_function(stmt, FunctionType.FUNCTION)

    def visit_if_stmt(self, stmt):
        self.resolve(stmt.condition)
        self.resolve(stmt.then_branch)
        if stmt.else_branch is not None:
            self.resolve(stmt.else_branch)

    def visit_print_stmt(self, stmt):
        self.resolve(stmt.expression)

    def visit_return_stmt(self, stmt):
        if self.current_function != FunctionType.FUNCTION:
            self.nebbdyr.error(stmt.keyword,
                               "Cannot return from top-level code.")

        if stmt.value is not None:
            self.resolve(stmt.value)

        return None

    def visit_while_stmt(self, stmt):
        self.resolve(stmt.condition)
        self.resolve(stmt.body)

    def visit_continue_stmt(self, stmt):
        return

    def visit_break_stmt(self, stmt):
        return

    def visit_var_stmt(self, stmt):
        self.declare(stmt.name)
        if stmt.initializer is not None:
            self.resolve(stmt.initializer)
        self.define(stmt.name)

    def visit_mut_stmt(self, stmt):
        self.declare(stmt.name)
        if stmt.initializer is not None:
            self.resolve(stmt.initializer)
        self.define(stmt.name)

    def visit_unstable_stmt(self, stmt):
        self.declare(stmt.name)
        if stmt.initializer is not None:
            self.resolve(stmt.initializer)
        self.define(stmt.name)

    def visit_assign_expr(self, expr):
        self.resolve(expr.value)
        self.resolve_local(expr, expr.name, False)

    def visit_binary_expr(self, expr):
        self.resolve(expr.left)
        self.resolve(expr.right)

    def visit_call_expr(self, expr):
        self.resolve(expr.callee)

        for argument in expr.arguments:
            self.resolve(argument)

    def visit_grouping_expr(self, expr):
        self.resolve(expr.expression)

    def visit_literal_expr(self, expr):
        return

    def visit_logical_expr(self, expr):
        self.resolve(expr.left)
        self.resolve(expr.right)

    def visit_unary_expr(self, expr):
        self.resolve(expr.right)

    def visit_variable_expr(self, expr):
        if (len(self.scopes) > 0 and
            expr.name.lexeme in self.scopes[-1] and
            self.scopes[-1][expr.name.lexeme] == VariableState.DECLARED):
            self.nebbdyr.error(expr.name, "Cannot read local variable in its own initializer.")

        self.resolve_local(expr, expr.name, True)

    def resolve(self, statements):
        if isinstance(statements, (list, tuple)):
            for statement in statements:
                self.resolve(statement)
        else:
            statements.accept(self)

    def resolve_function(self, function, type):
        enclosing_function = self.current_function
        self.current_function = type

        self.begin_scope()
        for param in function.parameters:
            self.declare(param)
            self.define(param)
        self.resolve(function.body)
        self.end_scope()

        self.current_function = enclosing_function

    def begin_scope(self):
        self.scopes.append(dict())

    def end_scope(self):
        scope = self.scopes.pop()
        for name, state in scope.items():
            if state == VariableState.DECLARED:
                self.nebbdyr.error('', "Local variable '{}' is declared but not used.".format(name))
            elif state == VariableState.DEFINED:
                self.nebbdyr.error('', "Local variable '{}' is defined but not used.".format(name))

    def declare(self, name):
        if len(self.scopes) == 0:
            return

        scope = self.scopes[-1]

        if name.lexeme in scope:
            if scope[name.lexeme] == VariableState.CORE:
                self.nebbdyr.error(name, "Cannot redefine core variable")
            else:
                self.nebbdyr.error(name,
                                   "A variable with this name already declared in this scope.")
        scope[name.lexeme] = VariableState.DECLARED

    def define(self, name):
        if len(self.scopes) == 0:
            return

        self.scopes[-1][name.lexeme] = VariableState.DEFINED

    def resolve_local(self, expr, name, is_read):
        for i in range(len(self.scopes)-1, -1, -1):
            if name.lexeme in self.scopes[i]:
                self.interpreter.resolve(expr, len(self.scopes)-1-i)

                if is_read and self.scopes[i][name.lexeme] != VariableState.CORE:
                    self.scopes[i][name.lexeme] = VariableState.USED
                return

        # Not found. Assume it is global
