# -*- coding: utf-8 -*-

import datetime

from attributes import Attribute
from environment import Environment
from errors import BreakException, ContinueException, Return, RuntimeException, IndexException
from nebbdyrfunction import NebbdyrFunction
from nebbdyrclass import NebbdyrClass
from nebbdyrinstance import NebbdyrInstance
from tokentype import TokenType as TT
from globalenvironment import GlobalEnvironment


class Interpreter:
    def __init__(self, nebbdyr):
        self.nebbdyr = nebbdyr
        self.globals = GlobalEnvironment()
        self.environment = self.globals
        self.locals = {}

    def interpret(self, statements):
        try:
            if not isinstance(statements, list):
                self.execute(statements)
            else:
                for statement in statements:
                    self.execute(statement)
        except RuntimeException as exc:
            self.nebbdyr.runtime_error(exc)
        except IndexException as exc:
            self.nebbdyr.runtime_error(exc)

    def evaluate(self, expr):
        return expr.accept(self)

    def execute(self, stmt):
        return stmt.accept(self)

    def resolve(self, expr, depth):
        self.locals[expr] = depth

    def execute_block(self, statements, environment):
        previous = self.environment
        try:
            self.environment = environment
            if not isinstance(statements, list):
                self.execute(statements)
            else:
                for statement in statements:
                    self.execute(statement)
        finally:
            self.environment = previous

    def visit_block_stmt(self, stmt):
        self.execute_block(stmt.statements, Environment(self.environment))

    def visit_class_stmt(self, stmt):
        self.environment.define(stmt.name, None)

        methods = {}
        for method in stmt.methods:
            function = NebbdyrFunction(method, self.environment)
            methods[method.name.lexeme] = function

        klasse = NebbdyrClass(stmt.name.lexeme, methods)
        self.environment.assign(stmt.name, klasse)
        return None

    def visit_expression_stmt(self, stmt):
        self.evaluate(stmt.expression)

    def visit_function_stmt(self, stmt):
        function = NebbdyrFunction(stmt, self.environment)
        self.environment.define(stmt.name, function, (Attribute.FUNCTION))

    def visit_if_stmt(self, stmt):
        if self.is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.then_branch)
        elif stmt.else_branch is not None:
            self.execute(stmt.else_branch)
        return None

    def visit_print_stmt(self, stmt):
        value = self.evaluate(stmt.expression)
        print(self.stringify(value))

    def visit_return_stmt(self, stmt):
        value = self.evaluate(stmt.value) if stmt.value is not None else None
        raise Return(value)

    def visit_var_stmt(self, stmt):
        value = None
        if stmt.initializer is not None:
            value = self.evaluate(stmt.initializer)
        self.environment.define(stmt.name, value)

    def visit_mut_stmt(self, stmt):
        value = None
        if stmt.initializer is not None:
            value = self.evaluate(stmt.initializer)
        self.environment.define(stmt.name, value, [Attribute.MUTABLE])

    def visit_unstable_stmt(self, stmt):
        value = None
        if stmt.initializer is not None:
            value = self.evaluate(stmt.initializer)
        self.environment.define(stmt.name, value, [Attribute.UNSTABLE,
                                                   Attribute.MUTABLE])

    def visit_while_stmt(self, stmt):
        while self.is_truthy(self.evaluate(stmt.condition)):
            try:
                self.execute(stmt.body)
            except BreakException:
                break
            except ContinueException:
                pass

    def visit_break_stmt(self, stmt):
        raise BreakException()

    def visit_continue_stmt(self, stmt):
        raise ContinueException()

    def visit_assign_expr(self, expr):
        value = self.evaluate(expr.value)

        distance = self.locals.get(expr)
        if distance is not None:
            self.environment.assign_at(distance, expr.name, value)
        else:
            self.globals.assign(expr.name, value)
        return value

    def visit_literal_expr(self, expr):
        return expr.value

    def visit_logical_expr(self, expr):
        left = self.evaluate(expr.left)
        if expr.operator.type == TT.OR:
            if self.is_truthy(left):
                return left
        else:
            if not self.is_truthy(left):
                return left

        return self.evaluate(expr.right)

    def visit_set_expr(self, expr):
        object = self.evaluate(expr.object)

        if not isinstance(object, NebbdyrInstance):
            raise RuntimeError(expr.name, "Only instances have fields.")

        value = self.evaluate(expr.value)
        object.set(expr.name, value)

    def visit_grouping_expr(self, expr):
        return self.evaluate(expr.expression)

    def visit_unary_expr(self, expr):
        right = self.evaluate(expr.right)

        if expr.operator.type == TT.MINUS:
            self.check_number_operand(expr.operator, right)
            return -right
        elif expr.operator.type == TT.BANG:
            return not self.is_truthy(right)

        # Increment and decrement operators
        elif expr.operator.type == TT.PLUSPLUS:
            self.check_number_operand(expr.operator, right)
            distance = self.locals.get(expr)
            if distance is not None:
                self.environment.assign_at(distance, expr.right.name, right+1)
            else:
                self.globals.assign(expr.right.name, right+1)
            return right + 1
        elif expr.operator.type == TT.MINUSMINUS:
            self.check_number_operand(expr.operator, right)
            distance = self.locals.get(expr)
            if distance is not None:
                self.environment.assign_at(distance, expr.right.name, right-1)
            else:
                self.globals.assign(expr.right.name, right-1)
            return right - 1

        # Unreachable

    def visit_listconstructor_expr(self, expr):
        start = self.evaluate(expr.start)
        if not isinstance(start, (int, float)):
            raise RuntimeException(expr.token, "Start must be iterable.")

        next_is_none = False
        if expr.next is not None:
            next = self.evaluate(expr.next)
            if not isinstance(next, (int, float)):
                raise RuntimeException(expr.token, "Next must be iterable.")
        else:
            next_is_none = True

        stop = self.evaluate(expr.stop)
        if not isinstance(stop, (int, float)):
            raise RuntimeException(expr.token, "Stop must be iterable.")

        if next_is_none:
            return list(range(start, stop+1))
        else:
            return list(range(start, stop+1, next-start))

    def visit_variable_expr(self, expr):
        return self.lookup_variable(expr.name, expr)

    def lookup_variable(self, name, expr):
        distance = self.locals.get(expr)
        if distance is not None:
            return self.environment.get_at(distance, name)
        else:
            return self.globals.get(name)

    def visit_list_expr(self, expr):
        return [self.evaluate(e) for e in expr.expression]

    def check_number_operand(self, operator, operand):
        # Can't use isinstance since bools are of instance int
        if not type(operand) in (int, float):
            raise RuntimeException(operator, "Operand must be a number.")

    def visit_binary_expr(self, expr):
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)

        if expr.operator.type == TT.MINUS:
            self.check_number_operands(expr.operator, left, right)
            return left - right
        elif expr.operator.type == TT.SLASH:
            self.check_number_operands(expr.operator, left, right)
            if right == 0:
                raise RuntimeException(expr.operator,
                                       "Attempted to divide by zero.")
            return left/right
        elif expr.operator.type == TT.STAR:
            self.check_number_operands(expr.operator, left, right)
            return left*right
        elif expr.operator.type == TT.PLUS:
            # Allow both float+float and str+str
            if type(left) == type(right):
                return left + right
            # Case of int + float
            if (isinstance(left, (int, float)) and
               isinstance(right, (int, float))):
                return left + right
            raise RuntimeException(expr.operator,
                                   "Operands must both be numbers or strings.")
        elif expr.operator.type == TT.GREATER:
            if left is False or right is False:
                return False
            self.check_number_operands(expr.operator, left, right)
            return right if left > right else False
        elif expr.operator.type == TT.GREATER_EQUAL:
            if left is False or right is False:
                return False
            self.check_number_operands(expr.operator, left, right)
            return right if left >= right else False
        elif expr.operator.type == TT.LESS:
            if left is False or right is False:
                return False
            self.check_number_operands(expr.operator, left, right)
            return right if left < right else False
        elif expr.operator.type == TT.LESS_EQUAL:
            if left is False or right is False:
                return False
            self.check_number_operands(expr.operator, left, right)
            return right if left <= right else False
        elif expr.operator.type == TT.BANG_EQUAL:
            return right if not self.is_equal(left, right) else False
        elif expr.operator.type == TT.EQUAL:
            return right if self.is_equal(left, right) else False
        elif expr.operator.type == TT.HAT:
            self.check_number_operands(expr.operator, left, right)
            return left**right

        # Unreachable

    def visit_call_expr(self, expr):
        callee = self.evaluate(expr.callee)

        arguments = []
        for argument in expr.arguments:
            argument = self.evaluate(argument)
            arguments.append(argument)

        if len(arguments) != callee.arity():
            raise RuntimeException(expr.paren, "Expected " + str(callee.arity()) +
                                   " arguments, but got " + str(len(arguments))
                                   + ".")
        try:
            return callee.call(self, arguments)
        except Exception as e:
            raise e
            raise RuntimeException(expr.paren, "Can only call functions")

    def visit_index_expr(self, expr):
        def is_valid(collection, index):
            if not isinstance(collection, (list)):
                raise IndexException(expr.paren, f"Can not index type '{type(collection)}'.")
            if len(collection) <= index:
                col = str(collection)
                if(len(collection) > 4):
                    col = (f'[{collection[0]}, {collection[1]}, ..., '
                           f'{collection[-2]}, {collection[-1]}]')

                raise IndexException(expr.paren, f"Index {index} is out of bounds of collection {col} of length {len(collection)}.")

        collection = self.evaluate(expr.collection)

        indicies = []
        for index in expr.indicies:
            index = self.evaluate(index)
            indicies.append(index)

        indicies = [int(i) for i in indicies]
        if len(indicies) == 1:
            is_valid(collection, indicies[0])
            return collection[indicies[0]]
        else:
            for index in indicies:
                is_valid(collection, index)
            return [collection[i] for i in indicies]

    def visit_lambda_expr(self, expr):
        function = NebbdyrFunction(expr, self.environment)
        return function

    def visit_get_expr(self, expr):
        object = self.evaluate(expr.object)
        if isinstance(object, NebbdyrInstance):
            return object.get(expr.name)

        raise RuntimeException(expr.name, "Only instances have properties")

    def check_number_operands(self, operator, left, right):
        if not isinstance(left, (float, int)):
            raise RuntimeException(
                operator, "Left operand '{}' must be number.".format(
                    self.stringify(left)))
        if not isinstance(right, (float, int)):
            raise RuntimeException(
                operator, "Right operand '{}' must be number.".format(
                    self.stringify(right)))

    def is_truthy(self, object):
        # Inherit Python's definitions of True and False
        return True if object or (object is 0) else False

    def is_equal(self, left, right):
        # none is not equal to anything
        if left is None and right is None:
            return False
        return left == right

    def stringify(self, object):
        if object is None:
            return "none"
        if object is True:
            return "true"
        if object is False:
            return "false"
        return str(object)
