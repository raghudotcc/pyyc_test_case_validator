"""Given an input file and a subset of python(as mentioned in 
the book 'python-to-x86'), verify that the program is valid.

Validation is two part:
1) Parse the program and check if the program has 
the correct AST nodes.
2) Execute the program and check if the program runs
without error.

Usage: python3 val.py --subset=<python-subset> \
                      --input_file=<file|dir> \
                      [--verbose]

Example: python3 val.py --subset=P0 --input=test.py
"""

from collections import deque
from pathlib import Path
from inspect import currentframe, getframeinfo
import ply.yacc as yacc
import ply.lex as lex
import ast
from ast import *
import subprocess
import argparse
import os
import re

subset_tbl = ['p0', 'p1', 'p2', 'p3']
python_exe = 'python3'
nodes = [
    [Module, Assign, Name,
     Constant, Expr, Call,
     UnaryOp, BinOp, USub,
     Add, Store, Load],  # < P0
    [List, Dict, Subscript,
     BoolOp, And, Or, Not,
     Eq, NotEq, Is,
     IfExp, Compare],  # < P1
    [Return, FunctionDef,
     Lambda, arguments, arg],  # < P2
    [If, While, ClassDef]  # < P3
]


def popen_result(popen):
    (out, err) = popen.communicate()
    retcode = popen.wait()
    if retcode != 0:
        if not (out is None):
            verboseprint(out)
        return False
    elif err:  # stderr is not empty or None
        return False
    else:
        return True

def validate(subset_func):
    """Decorator to get valid nodes from subset func, 
    walk the AST and verify if input prog has valid AST nodes."""
    def wrapper(prog):
        tree = ast.parse(prog)
        valid_nodes = subset_func(prog)
        for node in ast.walk(tree):
            if type(node) not in valid_nodes:
                verboseprint("Invalid node type: {}".format(type(node)))
                return False
        return True
    return wrapper


@validate
def p0(prog):
    return nodes[0]


@validate
def p1(prog):
    return nodes[0] \
        + nodes[1]


@validate
def p2(prog):
    return nodes[0] \
        + nodes[1] \
        + nodes[2]


@validate
def p3(prog):
    return nodes[0] \
        + nodes[1] \
        + nodes[2] \
        + nodes[3]


# create a dict containing the subset as key
# and the function with the same name as the value
dispatch_tbl = {subset: eval(subset) for subset in subset_tbl}


def is_valid_subset(subset):
    if subset.lower() not in subset_tbl:
        verboseprint("Invalid python subset."
                     " Supported subsets: {}".format(subset_tbl))
        return False
    return True


def traverse(subset, f):
    """validate the AST nodes using the validate decorator"""
    prog = f.read()
    return dispatch_tbl[subset.lower()](prog)


##########################
# Ply parser
##########################


def get_fileinfo():
    """Get the file name, function name and line number of the current frame."""
    cf = currentframe()
    filename = getframeinfo(cf).filename
    lineno = cf.f_back.f_lineno
    funcname = cf.f_back.f_code.co_name
    return Path(filename).stem, funcname, lineno


class Lexer:
    reserved = {
        'if': 'IF',
        'else': 'ELSE',
        'while': 'WHILE',
        'return': 'RETURN',
        'True': 'TRUE',
        'False': 'FALSE',
        'and': 'AND',
        'or': 'OR',
        'not': 'NOT',
        'is': 'IS',
        'lambda': 'LAMBDA',
        'def': 'DEF',
        'class': 'CLASS',
    }

    tokens = [
        'integer',
        'identifier',
        'ASSIGN',
        'EQ',
        'NE',
        'NEWLINE',
        'WHITESPACE',
        'COMMA',
        'PLUS',
        'MINUS',
        'EQUALS',
        'LPAREN',
        'RPAREN',
        'LBRACE',
        'RBRACE',
        'LBRACKET',
        'RBRACKET',
        'COLON',
        'SEMICOLON',
        'INDENT',
        'DEDENT',
        'ENDMARKER',
    ] + list(reserved.values())

    t_EQ = r'=='
    t_NE = r'!='
    t_COMMA = r','
    t_PLUS = r'\+'
    t_MINUS = r'-'
    t_ASSIGN = r'='
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_LBRACE = r'{'
    t_RBRACE = r'}'
    t_LBRACKET = r'\['
    t_RBRACKET = r'\]'
    t_COLON = r':'
    t_SEMICOLON = r';'
    t_ignore = ' \t'
    t_WHITESPACE = r'\s+'
    t_ignore_COMMENT = r'\#.*'

    def __init__(self):
        self.lexer = lex.lex(module=self)
        self.lexer.begin('INITIAL')

    def input(self, data):
        self.lexer.input(data)

    def token(self):
        return self.lexer.token()

    def t_identifier(self, t):
        r'[a-zA-Z_][a-zA-Z_0-9]*'
        t.type = Lexer.reserved.get(t.value, 'identifier')
        return t

    def t_integer(self, t):
        r'\d+'
        try:
            t.value = int(t.value)
        except ValueError:
            verboseprint(get_fileinfo(),
                         "Integer value too large {}".format(t.value))
            t.value = 0
        return t

    def t_NEWLINE(self, t):
        r'\n(?:\s*(?:[#].*)?\n)*\s*'
        t.value = len(t.value) - 1 - t.value.rfind('\n')
        return t

    def t_error(self, t):
        verboseprint(get_fileinfo(), "Unknown Symbol '{}'".format(t.value[0]))
        exit(1)


def _new_token(type):
    """Create a new token with the given type. Useful
    for creating indent/dedent tokens dynamically."""
    tok = lex.LexToken()
    tok.type = type
    tok.value = None
    tok.lineno = -1
    tok.lexpos = -1
    return tok


def DEDENT():
    return _new_token("DEDENT")


def INDENT():
    return _new_token("INDENT")


class IndentWrapper(object):

    def __init__(self, lexer):
        """Create a new wrapper given the lexer which is being wrapped"""
        self.lexer = lexer
        self.indent_stack = [0]
        self.token_queue = deque()
        self.eof_reached = False

    def input(self, *args, **kwds):
        self.lexer.input(*args, **kwds)

    def token(self):
        """Return the next token, or None if end of input has been reached"""
        if self.token_queue:
            return self.token_queue.popleft()
        if self.eof_reached:
            return None
        t = self.lexer.token()
        if t is None:
            self.eof_reached = True
            if len(self.indent_stack) > 1:
                t = DEDENT()
                for i in range(len(self.indent_stack) - 1):
                    self.token_queue.append(DEDENT())
                self.indent_stack = [0]
        elif t.type == "NEWLINE":
            if t.value > self.indent_stack[-1]:
                self.indent_stack.append(t.value)
                self.token_queue.append(INDENT())
            else:
                while t.value < self.indent_stack[-1]:
                    self.indent_stack.pop()
                    self.token_queue.append(DEDENT())
                if t.value != self.indent_stack[-1]:
                    raise Exception("Indentation error")
        return t


class Parser(object):
    tokens = Lexer.tokens

    precedence = (
        ('left', 'OR'),
        ('left', 'AND'),
        ('left', 'NOT'),
        ('right', 'EQUALS'),
        ('left', 'PLUS', 'MINUS'),
        ('right', 'UMINUS'),
    )

    def __init__(self):
        self.parser = yacc.yacc(module=self)

    def parse(self, data, lexer):
        return self.parser.parse(data, lexer=lexer)

    def p_module(self, p):
        """
        module : statements
               | NEWLINE
        """
        p[0] = Module(body=p[1]) if p[1] else Module(body=[])
        verboseprint(get_fileinfo(), ast.dump(p[0]))

    def p_statements(self, p):
        """
        statements : statement statements
                   | statement
        """
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = [p[1]] + p[2]
        verboseprint(get_fileinfo(), p[0])

    def p_statement(self, p):
        """
        statement : stmt_list NEWLINE
                  | compound_stmt
        """
        p[0] = p[1]
        verboseprint(get_fileinfo(), ast.dump(p[0]))

    # we don't support multiple statements in a single line
    # so we don't care about semicolons
    def p_stmt_list(self, p):
        """
        stmt_list : simple_stmt
        """
        p[0] = p[1]
        verboseprint(get_fileinfo(), ast.dump(p[0]))

    def p_simple_stmt(self, p):
        """
        simple_stmt : expression_stmt
                    | assignment_stmt
                    | return_stmt
        """
        p[0] = p[1]
        verboseprint(get_fileinfo(), ast.dump(p[0]))

    def p_compound_stmt(self, p):
        """
        compound_stmt : if_stmt
                      | while_stmt
                      | funcdef
        """
        p[0] = p[1]
        verboseprint(get_fileinfo(), ast.dump(p[0]))

    def p_expression_stmt(self, p):
        """
        expression_stmt : expression
        """
        p[0] = Expr(value=p[1])
        verboseprint(get_fileinfo(), ast.dump(p[0]))

    # we don't support multiple targets in a single assignment
    def p_assignment_stmt(self, p):
        """
        assignment_stmt : target_list ASSIGN expression
        """
        p[0] = Assign(targets=p[1], value=p[3])
        verboseprint(get_fileinfo(), ast.dump(p[0]))

    def p_target_list(self, p):
        """
        target_list : target
        """
        p[0] = [p[1]]
        verboseprint(get_fileinfo(), p[0])

    def p_target(self, p):
        """
        target : identifier
               | LPAREN target_list RPAREN
               | LBRACKET target_list RBRACKET
               | subscription
        """
        if len(p) == 2:
            p[0] = Name(id=p[1], ctx=Store())
        else:
            p[0] = p[2]
        verboseprint(get_fileinfo(), ast.dump(p[0]))

    def p_atom(self, p):
        """
        atom : identifier
             | literal
             | enclosure
        """
        if p.slice[1].type == "identifier":
            p[0] = Name(id=p[1], ctx=Load())
        else:
            p[0] = p[1]
        verboseprint(get_fileinfo(), ast.dump(p[0]))

    def p_literal(self, p):
        """
        literal : integer
                | TRUE
                | FALSE
        """
        p[0] = Constant(value=p[1])
        verboseprint(get_fileinfo(), ast.dump(p[0]))

    def p_enclosure(self, p):
        """
        enclosure : parenth_form
                   | list_display
                   | dict_display
        """
        p[0] = p[1]
        verboseprint(get_fileinfo(), ast.dump(p[0]))

    def p_parenth_form(self, p):
        """
        parenth_form : LPAREN expression RPAREN
        """
        p[0] = p[2]
        verboseprint(get_fileinfo(), ast.dump(p[0]))

    def p_list_display(self, p):
        """
        list_display : LBRACKET expression_list RBRACKET
        """
        p[0] = List(elts=p[2])
        verboseprint(get_fileinfo(), ast.dump(p[0]))

    def p_dict_display(self, p):
        """
        dict_display : LBRACE key_datum_list RBRACE
        """
        p[0] = p[2]
        verboseprint(get_fileinfo(), ast.dump(p[0]))

    def p_key_datum_list(self, p):
        """
        key_datum_list : key_datum_list COMMA key_datum
                       | key_datum
                       | empty
        """
        if len(p) == 4:
            p[1].keys.append(p[3][0])
            p[1].values.append(p[3][1])
            p[0] = p[1]
        elif len(p) == 2:
            if p[1] is None:
                p[0] = Dict(keys=[], values=[])
            else:
                p[0] = Dict(keys=[p[1][0]], values=[p[1][1]])
        verboseprint(get_fileinfo(), ast.dump(p[0]))

    def p_key_datum(self, p):
        """
        key_datum : expression COLON expression
        """
        p[0] = (p[1], p[3])
        verboseprint(get_fileinfo(), p[0])

    def p_subscription(self, p):
        """
        subscription : primary LBRACKET expression_list RBRACKET
        """
        p[0] = Subscript(value=p[1], slice=p[3])
        verboseprint(get_fileinfo(), ast.dump(p[0]))

    def p_primary(self, p):
        """
        primary : atom
                | call
                | subscription
        """
        p[0] = p[1]
        verboseprint(get_fileinfo(), ast.dump(p[0]))

    def p_call(self, p):
        """
        call : primary LPAREN argument_list RPAREN
        """
        p[0] = Call(func=p[1], args=p[3])
        verboseprint(get_fileinfo(), ast.dump(p[0]))

    def p_argument_list(self, p):
        """
        argument_list : positional_arguments
        """
        p[0] = p[1]
        verboseprint(get_fileinfo(), p[0])

    def p_positional_arguments(self, p):
        """
        positional_arguments : positional_arguments COMMA positional_item
                             | positional_item
                             | empty
        """
        if len(p) == 2:
            p[0] = [p[1]] if p[1] else []
        elif len(p) == 4:
            p[0] = p[1] + [p[3]]
        verboseprint(get_fileinfo(), p[0])

    def p_positional_item(self, p):
        """
        positional_item : expression
        """
        p[0] = p[1]
        verboseprint(get_fileinfo(), ast.dump(p[0]))

    def p_expression_list(self, p):
        """
        expression_list : expression_list COMMA expression
                         | expression
                         | empty
        """
        if len(p) == 2:
            p[0] = [p[1]] if p[1] else []
        elif len(p) == 4:
            p[0] = p[1] + [p[3]]
        verboseprint(get_fileinfo(), p[0])

    def p_expression(self, p):
        """
        expression : conditional_expression
                    | lambda_expr
        """
        p[0] = p[1]
        verboseprint(get_fileinfo(), ast.dump(p[0]))

    def p_conditional_expression(self, p):
        """
        conditional_expression : or_test
                                | or_test IF or_test ELSE conditional_expression
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = IfExp(test=p[1], body=p[3], orelse=p[5])
        verboseprint(get_fileinfo(), ast.dump(p[0]))

    def p_lambda_expr(self, p):
        """
        lambda_expr : LAMBDA parameter_list COLON expression
        """
        p[0] = Lambda(args=arguments(args=p[2]), body=p[4])
        verboseprint(get_fileinfo(), ast.dump(p[0]))

    def p_parameter_list(self, p):
        """
        parameter_list : parameter_list COMMA parameter
                       | parameter
                       | empty
        """
        if len(p) == 4:
            p[0] = p[1] + [p[3]]
        elif len(p) == 2:
            p[0] = [p[1]] if p[1] else []

    def p_parameter(self, p):
        """
        parameter : identifier
        """
        p[0] = arg(arg=p[1])
        verboseprint(get_fileinfo(), ast.dump(p[0]))

    def p_or_test(self, p):
        """
        or_test : and_test
                | or_test OR and_test
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = BoolOp(op=Or(), values=[p[1], p[3]])
        verboseprint(get_fileinfo(), ast.dump(p[0]))

    def p_and_test(self, p):
        """
        and_test : not_test
                 | and_test AND not_test
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = BoolOp(op=And(), values=[p[1], p[3]])
        verboseprint(get_fileinfo(), ast.dump(p[0]))

    def p_not_test(self, p):
        """
        not_test : NOT not_test
                 | comparison
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = UnaryOp(op=Not(), operand=p[2])
        verboseprint(get_fileinfo(), ast.dump(p[0]))

    def p_comparison(self, p):
        """
        comparison : comparison comp_operator a_expr
                   | a_expr
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = Compare(left=p[1], ops=[p[2]], comparators=[p[3]])
        verboseprint(get_fileinfo(), ast.dump(p[0]))

    def p_comp_operator(self, p):
        """
        comp_operator : EQ
                      | NE
                      | IS
        """
        p[0] = Eq() if p[1] == "==" else NotEq() if p[1] == "!=" else Is()
        verboseprint(get_fileinfo(), ast.dump(p[0]))

    def p_a_expr(self, p):
        """
        a_expr : a_expr PLUS u_expr
               | u_expr
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = BinOp(left=p[1], op=Add(), right=p[3])
        verboseprint(get_fileinfo(), ast.dump(p[0]))

    def p_if_stmt(self, p):
        """
        if_stmt : IF expression COLON suite
            | IF expression COLON suite ELSE COLON suite
        """
        if len(p) == 5:
            p[0] = If(test=p[2], body=p[4])
        else:
            p[0] = If(test=p[2], body=p[4], orelse=p[7])
        verboseprint(get_fileinfo(), ast.dump(p[0]))

    def p_while_stmt(self, p):
        """
        while_stmt : WHILE expression COLON suite
        """
        p[0] = While(test=p[2], body=p[4])
        verboseprint(get_fileinfo(), ast.dump(p[0]))

    def p_funcdef(self, p):
        """
        funcdef : DEF funcname LPAREN parameter_list RPAREN COLON suite
        """
        p[0] = FunctionDef(name=p[2], args=arguments(args=p[4]), body=p[7])
        verboseprint(get_fileinfo(), ast.dump(p[0]))

    def p_funcname(self, p):
        """
        funcname : identifier
        """
        p[0] = p[1]
        verboseprint(get_fileinfo(), p[0])

    def p_return_stmt(self, p):
        """
        return_stmt : RETURN expression_list
        """
        p[0] = Return(value=p[2])
        verboseprint(get_fileinfo(), ast.dump(p[0]))

    def p_suite(self, p):
        """
        suite : stmt_list NEWLINE
              | NEWLINE INDENT statements DEDENT
        """
        if len(p) == 3:
            p[0] = p[1]
        else:
            p[0] = p[3]
        verboseprint(get_fileinfo(), p[0])

    def p_u_expr(self, p):
        """
        u_expr : primary
               | MINUS u_expr %prec UMINUS
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = UnaryOp(op=USub(), operand=p[2])
        verboseprint(get_fileinfo(), ast.dump(p[0]))

    def p_empty(self, p):
        """
        empty :
        """
        pass

    def p_error(self, p):
        stack_state_str = ' '.join(
            [symbol.type for symbol in self.parser.symstack][1:])
        err_tok = 'EOF'
        if p:
            err_tok = p
        verboseprint(get_fileinfo(), '\033[1;31m Syntax error at "{}".\033[0m \n \033[1;31mParser State:{} {} . {}\033[0m'
                     .format(err_tok,
                             self.parser.state,
                             stack_state_str,
                             p))
        exit(1)


def pparse(subset, codef):
    """call ply parser"""
    with open(codef.name, 'r') as f:
        code = f.read()
    # Hack to get the Indentation working
    # Everyline must end with a newline
    code = code + '\n'
    lexer = Lexer()
    lexer = IndentWrapper(lexer)
    parser = Parser()
    return parser.parse(code, lexer=lexer)


def exec_prog(file):
    infilename = os.path.splitext(file)[0] + '.in'
    cmd = [python_exe, file]
    if os.path.isfile(infilename):
        with open(infilename, 'r') as infile:
            popen = subprocess.Popen(cmd,
                                     stdin=infile,
                                     stdout=subprocess.PIPE)
    else:
        popen = subprocess.Popen(cmd,
                                 stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE)
    result = popen_result(popen)
    return result


def parse_args():
    parser = argparse.ArgumentParser(description="Validate python subset")
    parser.add_argument(
        "--subset", help="python subset to validate", required=True)
    parser.add_argument(
        "--input", help="input file(s) to validate", required=True)
    parser.add_argument(
        "--verbose", help="print verbose output", action="store_true")
    return parser.parse_args()


def main():
    args = parse_args()
    global verboseprint
    verboseprint = print if args.verbose else lambda *a, **k: None
    prog_files = []
    if is_valid_subset(args.subset):
        if os.path.isdir(args.input):
            # run validation on all files in the directory
            for file in os.listdir(args.input):
                prog_files.append(os.path.join(args.input, file))
        else:
            prog_files.append(args.input)

        for file in prog_files:
            with open(file, 'r') as f:
                assert traverse(args.subset, f) \
                    and pparse(args.subset, f) \
                    and exec_prog(file) == True, \
                    "invalid program: {}".format(file)


if __name__ == "__main__":
    main()
