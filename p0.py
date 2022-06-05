from collections import deque
import ply.lex as lex
import ply.yacc as yacc
from ply.lex import TOKEN
from ast import *
import ast
import logging


class Lexer:
    reserved = {
        'if': 'IF',
        'else': 'ELSE',
        'while': 'WHILE',
        'return': 'RETURN',
        'true': 'TRUE',
        'false': 'FALSE',
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
        'NOT_EQ',
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
    t_NOT_EQ = r'!='
    t_COMMA = r','
    t_PLUS = r'\+'
    t_MINUS = r'-'
    t_EQUALS = r'='
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
            logging.error("Integer value too large %d", t.value)
            t.value = 0
        return t

    def t_NEWLINE(self, t):
        r'\n(?:\s*(?:[#].*)?\n)*\s*'
        t.value = len(t.value) - 1 - t.value.rfind('\n')
        return t

    def t_error(self, t):
        logging.error("Unknown Symbol: %s" % t.value[0])
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

FORMAT = '[%(levelname)s] File: %(filename)s, Line: %(lineno)d, %(message)s'
logging.basicConfig(
    format=FORMAT, level=logging.INFO)
# parser = yacc.yacc(debug=True)
# res = parser.parse('1 + 2', lexer)
# print(res)

program = '''
x + y
'''

lexer = Lexer()
lexer = IndentWrapper(lexer)
# lexer.input(program)
# while True:
#     tok = lexer.token()
#     if not tok:
#         break      # No more input
#     print(tok)

Parser().parse(program, lexer)