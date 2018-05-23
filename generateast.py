#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse


def define_ast(output_dir, base_name, types):
    path = "{output_dir}/{base_name}.py".format(**locals())
    with open(path, 'w') as output:
        output.print = lambda x: output.write(str(x)+'\n')
        output.print("from expression import Expr, Stmt\n\n")

        for type in types:
            class_name = type.split(":")[0].strip()
            fields = type.split(":")[1].strip()
            define_type(output, base_name, class_name, fields)
            output.print('')


def define_type(writer, base_name, class_name, fields):
    writer.print("class {}({}):".format(
        class_name, str.capitalize(base_name)))
    if len(fields) > 0:
        writer.print("    def __init__(self, {fields}):".format(**locals()))
        for field in [f.strip() for f in fields.split(',')]:
            writer.print("        self.{field} = {field}".format(**locals()))
        writer.print('')

    # Visitor pattern
    writer.print("    def accept(self, visitor):")
    writer.print("        return visitor.visit_{}_{}(self)".format(
        str.lower(class_name), str.lower(base_name)))
    writer.print('')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate AST')
    parser.add_argument('output_dir', metavar='output directory')
    args = parser.parse_args()

    define_ast(args.output_dir, "expr", ["Assign : name, value",
                                         "Binary : left, operator, right",
                                         "Call : callee, paren, arguments",
                                         "Lambda : parameters, body",
                                         "Grouping : expression",
                                         "List : expression",
                                         "Literal : value",
                                         "Logical : left, operator, right",
                                         "Unary : operator, right",
                                         "Variable : name"])
    define_ast(args.output_dir, "stmt", ["Block : statements",
                                         "Class : name, methods",
                                         "Expression : expression",
                                         "Function : name, parameters, body",
                                         "If : condition, then_branch, else_branch",
                                         "Print : expression",
                                         "Return : keyword, value",
                                         "Var : name, initializer",
                                         "Mut : name, initializer",
                                         "Unstable : name, initializer",
                                         "While : condition, body",
                                         "Break : ",
                                         "Continue : "])
