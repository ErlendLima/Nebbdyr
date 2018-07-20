# -*- coding: utf-8 -*-

from tokentype import TokenType as TT
from expr import (Binary, Grouping, Literal, Unary,
                  Variable, Assign, Logical, Call,
                  List, Get, Set, Index, Lambda, ListConstructor)
import stmt

from errors import ParseException


class Parser:
    def __init__(self, nebbdyr, tokens):
        self.nebbdyr = nebbdyr
        self.tokens = tokens
        self.loop_level = 0
        self.current = 0

    def parse(self):
        statements = []
        while not self.is_at_end():
            statements.append(self.declaration())
        return statements

    def expression(self):
        return self.assignment()

    def declaration(self):
        try:
            if self.match(TT.CLASS):
                return self.class_declaration()
            if self.match(TT.FUN):
                return self.function("function")
            if self.match(TT.VAR):
                return self.var_declaration()
            if self.match(TT.MUT):
                return self.mut_declaration()
            if self.match(TT.UNSTABLE):
                return self.unstable_declaration()
            return self.statement()
        except ParseException:
            self.synchronize()
            return None

    def class_declaration(self):
        name = self.consume(TT.IDENTIFIER, "Expect class name.")
        self.consume(TT.COLON, "Expect newline after class name.")
        self.consume(TT.NEWLINE, "Expect newline after ':'.")
        self.consume(TT.INDENT, "Expect indent after class name.")

        methods = []
        while not self.check(TT.DEDENT) and not self.is_at_end():
            methods.append(self.function("method"))

        self.consume(TT.DEDENT, "Expect dedent after class body.")
        return stmt.Class(name, methods)

    def statement(self):
        if self.match(TT.FOR):
            return self.for_statement()
        if self.match(TT.IF):
            return self.if_statement()
        if self.match(TT.PRINT):
            return self.print_statement()
        if self.match(TT.WHILE):
            return self.while_statement()
        if self.match(TT.RETURN):
            return self.return_statement()
        if self.match(TT.INDENT):
            return stmt.Block(self.block())
        if self.match(TT.BREAK):
            return self.break_statement()
        if self.match(TT.CONTINUE):
            return self.continue_statement()
        return self.expression_statement()

    def for_statement(self):
        next = self.consume(TT.IDENTIFIER, "Expect variable name.")
        self.consume(TT.IN, "Expect 'in' after variable name.")
        collection = self.consume(TT.IDENTIFIER, "Expect collection to iterate over.")
        self.consume(TT.COLON, "Expect ':' to end 'for'.")
        self.consume(TT.NEWLINE, "Expect newline after ':'.")

        # self.consume(TT.LEFT_PAREN, "Expect '(' after 'for'.")
        # if self.match(TT.SEMICOLON):
        #     initializer = None
        # elif self.match(TT.VAR):
        #     initializer = self.var_declaration()
        # else:
        #     initializer = self.expression_statement()

        # condition = None
        # if not self.check(TT.SEMICOLON):
        #     condition = self.expression()
        # self.consume(TT.SEMICOLON, "Expect ';' after loop condition")

        # increment = None
        # if not self.check(TT.RIGHT_PAREN):
        #     increment = self.expression()
        # self.consume(TT.RIGHT_PAREN, "Expect ')' after for clauses.")
        iterator = stmt.Mut('')

        body = self.statement()
        body = stmt.Block([body, Assign(iterator, collection)])
        body = stmt.While(None, body)
        body = stmt.Block([stmt.Unstable(iterator, None), body])

        # if increment is not None:
        #     body = stmt.Block([body, stmt.Expression(increment)])

        # if condition is None:
        #     condition = Literal(True)
        # body = stmt.While(condition, body)

        # if initializer is not None:
        #     body = stmt.Block([initializer, body])

        return body

    def if_statement(self):
        condition = self.expression()
        self.consume(TT.COLON, "Expect ':' after if condition.")
        self.consume(TT.NEWLINE, "Expect newline after ':'.")
        then_branch = self.statement()

        else_branch = None
        if self.match(TT.ELSE):
            self.consume(TT.COLON, "Expect ':' after if condition.")
            self.consume(TT.NEWLINE, "Expect newline after ':'.")
            else_branch = self.statement()

        return stmt.If(condition, then_branch, else_branch)

    def print_statement(self):
        value = self.expression()

        if not self.is_at_end():
            self.consume(TT.NEWLINE, "Expect newline after value.")
        return stmt.Print(value)

    def return_statement(self):
        keyword = self.previous()
        value = None
        if not self.check(TT.NEWLINE):
            value = self.expression()

        if not self.is_at_end():
            self.consume(TT.NEWLINE, "Expect newline after return value.")
        return stmt.Return(keyword, value)

    def var_declaration(self):
        name = self.consume(TT.IDENTIFIER, "Expect variable name.")

        initalizer = None
        if self.match(TT.ASSIGNMENT):
            initalizer = self.expression()
            if self.match(TT.COMMA):
                initalizer = List([initalizer, *self.inner_list().expression])

        if not self.is_at_end():
            self.consume(TT.NEWLINE, "Expect newline after variable initialization")
        return stmt.Var(name, initalizer)

    def mut_declaration(self):
        self.consume(TT.VAR, "Expect 'var' keyword after 'mut'.")
        name = self.consume(TT.IDENTIFIER, "Expect variable name.")

        initalizer = None
        if self.match(TT.ASSIGNMENT):
            initalizer = self.expression()
            if self.match(TT.COMMA):
                initalizer = List([initalizer, *self.inner_list().expression])

        self.consume(TT.NEWLINE, "Expect newline after variable declaration")
        return stmt.Mut(name, initalizer)

    def unstable_declaration(self):
        if self.match(TT.MUT):
            self.consume(TT.VAR, "Expect 'var' after keyword 'mut'.")
        else:
            self.consume(TT.VAR, "Expect 'var' after keyword 'unstable'.")
        name = self.consume(TT.IDENTIFIER, "Expect variable name.")

        initalizer = None
        if self.match(TT.ASSIGNMENT):
            initalizer = self.expression()
            if self.match(TT.COMMA):
                initalizer = List([initalizer, *self.inner_list().expression])

        self.consume(TT.NEWLINE, "Expect newline after variable declaration.")
        return stmt.Unstable(name, initalizer)

    def while_statement(self):
        condition = self.expression()
        self.consume(TT.COLON, "Expect ':' after while condition.")
        self.consume(TT.NEWLINE, "Expect newline after ':'.")

        try:
            self.loop_level += 1
            body = self.statement()
            return stmt.While(condition, body)
        finally:
            self.loop_level -= 1

    def break_statement(self):
        if self.loop_level <= 0:
            raise ParseException(self.previous(),
                                 "'break' statement must be inside a loop.")
        self.consume(TT.NEWLINE, "Expect newline after 'break' statement.")
        return stmt.Break()

    def continue_statement(self):
        if self.loop_level <= 0:
            raise ParseException(self.previous(),
                                 "'continue' statement must be inside a loop.")
        self.consume(TT.NEWLINE, "Expect newline after 'continue' statement.")
        return stmt.Continue()

    def expression_statement(self):
        expr = self.expression()
        if not self.is_at_end():
            self.consume(TT.NEWLINE, "Expect newline after expression.")
        return stmt.Expression(expr)

    def function(self, kind):
        name = self.consume(TT.IDENTIFIER, "Expect " + kind + " name.")
        self.consume(TT.LEFT_PAREN, "Expect '(' after " + kind + " name.")
        parameters = []
        if not self.check(TT.RIGHT_PAREN):
            parameters.append(self.consume(TT.IDENTIFIER,
                                           "Expect parameter name."))
            while self.match(TT.COMMA):
                parameters.append(self.consume(TT.IDENTIFIER,
                                               "Expect parameter name."))
                if len(parameters) >= 5:
                    self.error(self.peek(),
                               "Cannot have more than 5 parameters.")
        self.consume(TT.RIGHT_PAREN, "Expect ')' after parameters")
        self.consume(TT.COLON, "Expect ':' before " + kind + " body.")
        self.consume(TT.NEWLINE, "Expect newline after ':'.")
        self.consume(TT.INDENT, "Expect indent after ':'.")
        body = self.block()
        return stmt.Function(name, parameters, body)

    def lambda_declaration(self):
        # Parentheses are optional
        using_paren = False
        if self.check(TT.LEFT_PAREN):
            using_paren = True
            self.advance()
        # self.consume(TT.LEFT_PAREN, "Expect '(' after \\.")
        parameters = []
        if not (self.check(TT.RIGHT_PAREN) or self.check(TT.COLON)):
            parameters.append(self.consume(TT.IDENTIFIER,
                                           "Expect parameter name."))
            while self.match(TT.COMMA):
                parameters.append(self.consume(TT.IDENTIFIER,
                                               "Expect parameter name."))
                if len(parameters) >= 5:
                    self.error(self.peek(),
                               "Cannot have more than 5 parameters.")
        if using_paren:
            self.consume(TT.RIGHT_PAREN, "Expect ')' after parameters")
        self.consume(TT.COLON, "Expect ':' before lambda body.")
        body = self.expression()
        body = stmt.Return(self.previous(), body)

        return Lambda(parameters, body)

    def block(self):
        statements = []

        while not self.check(TT.DEDENT) and not self.is_at_end():
            statements.append(self.declaration())

        self.consume(TT.DEDENT, "Expect dedentation after block.")
        return statements

    def assignment(self):
        expr = self.logical_or()
        if self.match(TT.ASSIGNMENT):
            equals = self.previous()
            value = self.assignment()
            if self.match(TT.COMMA):
                value = List([value, *self.inner_list().expression])

            if isinstance(expr, Variable):
                name = expr.name
                return Assign(name, value)
            elif isinstance(expr, Get):
                return Set(expr.object, expr.name, value)

            self.error(equals, "Invalid assignment target.")

        return expr

    def logical_or(self):
        expr = self.logical_and()

        while self.match(TT.OR):
            operator = self.previous()
            right = self.logical_and()
            expr = Logical(expr, operator, right)

        return expr

    def logical_and(self):
        expr = self.equality()

        while self.match(TT.AND):
            operator = self.previous()
            right = self.equality()
            expr = Logical(expr, operator, right)

        return expr

    def equality(self):
        expr = self.comparison()
        while self.match(TT.BANG_EQUAL, TT.EQUAL):
            operator = self.previous()
            right = self.comparison()
            expr = Binary(expr, operator, right)

        return expr

    def comparison(self):
        expr = self.addition()
        while self.match(TT.GREATER, TT.GREATER_EQUAL, TT.LESS, TT.LESS_EQUAL):
            operator = self.previous()
            right = self.addition()
            expr = Binary(expr, operator, right)
        return expr

    def addition(self):
        expr = self.list_construction()
        while self.match(TT.MINUS, TT.PLUS):
            operator = self.previous()
            right = self.list_construction()
            expr = Binary(expr, operator, right)

        return expr

    def inner_list(self):
        expr = [self.expression()]
        # Case for 1,1..10
        if self.match(TT.ELLIPSIS):
            token = self.previous()
            stop = self.expression()
            return ListConstructor(expr[0], None, stop, token)

        while self.match(TT.COMMA):
            expr.append(self.expression())
            if len(expr) == 2:
                if self.match(TT.ELLIPSIS):
                    token = self.previous()
                    stop = self.multiplication()
                    return ListConstructor(expr[0], expr[1],
                                           stop, token)
        return List(expr)

    def list_construction(self):
        if self.match(TT.LEFT_BRACKET):
            list = self.inner_list()
            self.consume(TT.RIGHT_BRACKET, "Expect ']' to close list.")
            return list
        expr = self.multiplication()
        return expr

    def multiplication(self):
        expr = self.exponentiation()
        while self.match(TT.SLASH, TT.STAR):
            operator = self.previous()
            right = self.exponentiation()
            expr = Binary(expr, operator, right)

        return expr

    def exponentiation(self):
        expr = self.unary()
        while self.match(TT.HAT):
            operator = self.previous()
            right = self.unary()
            expr = Binary(expr, operator, right)

        return expr

    def unary(self):
        if self.match(TT.BANG, TT.MINUS, TT.PLUSPLUS, TT.MINUSMINUS):
            operator = self.previous()
            right = self.unary()
            if operator.type in (TT.PLUSPLUS, TT.MINUSMINUS):
                if not isinstance(right, Variable):
                    self.error(operator, "Invalid assignment target.")
            return Unary(operator, right)

        return self.call()

    def finish_call(self, callee):
        arguments = []
        if not self.check(TT.RIGHT_PAREN):
            arguments.append(self.expression())
            while self.match(TT.COMMA):
                if len(arguments) >= 5:
                    self.error(self.peek(),
                               "Cannot have more than 5 arguments")
                arguments.append(self.expression())
        paren = self.consume(TT.RIGHT_PAREN, "Expect ')' after arguments.")

        return Call(callee, paren, arguments)

    def call(self):
        expr = self.indexation()
        while True:
            if self.match(TT.LEFT_PAREN):
                expr = self.finish_call(expr)
            elif self.match(TT.DOT):
                name = self.consume(TT.IDENTIFIER,
                                    "Expect property name after '.'.")
                expr = Get(expr, name)
            else:
                break
        return expr

    def indexation(self):
        expr = self.primary()
        while True:
            if self.match(TT.LEFT_BRACKET):
                expr = self.finish_indexation(expr)
            else:
                break
        return expr

    def finish_indexation(self, collection):
        indicies = []
        if not self.check(TT.RIGHT_BRACKET):
            indicies.append(self.expression())
            while self.match(TT.COMMA):
                indicies.append(self.expression())
        paren = self.consume(TT.RIGHT_BRACKET, "Expect ']' after indicies.")

        return Index(collection, paren, indicies)

    def primary(self):
        if self.match(TT.LEFT_PAREN):
            expr = self.expression()
            self.consume(TT.RIGHT_PAREN, "Expect ')' after expression.")
            return Grouping(expr)

        if self.match(TT.FALSE):
            return Literal(False)
        if self.match(TT.TRUE):
            return Literal(True)
        if self.match(TT.NONE):
            return Literal(None)

        if self.match(TT.INT, TT.FLOAT, TT.STRING):
            return Literal(self.previous().literal)

        if self.match(TT.IDENTIFIER):
            return Variable(self.previous())

        if self.match(TT.LAMBDA):
            return self.lambda_declaration()

        raise self.error(self.peek(), "Expected expression.")

    def match(self, *types):
        for type in types:
            if self.check(type):
                self.advance()
                return True

        return False

    def consume(self, type, message):
        if self.check(type):
            return self.advance()
        raise self.error(self.peek(), message)

    def check(self, token_type):
        if self.is_at_end():
            if not token_type == TT.DEDENT:
                return False
        return self.peek().type == token_type

    def advance(self):
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def is_at_end(self):
        return (self.peek().type == TT.EOF or
                (self.peek().type == TT.DEDENT
                 and self.peek_next().type == TT.EOF))

    def peek(self):
        return self.tokens[self.current]

    def peek_next(self):
        return self.tokens[self.current+1]

    def previous(self):
        return self.tokens[self.current-1]

    def error(self, token, message):
        self.nebbdyr.error(token, message)
        return ParseException()

    def synchronize(self):
        self.advance()

        # Discard tokens until a probable statement boundary
        while not self.is_at_end():
            # Does not consider the possibility of being inside a group
            if self.previous().type == TT.NEWLINE:
                return

            if self.peek().type in {TT.FUN, TT.VAR, TT.FOR, TT.IF,
                                    TT.WHILE, TT.PRINT, TT.RETURN, TT.MUT}:
                return

            self.advance()
