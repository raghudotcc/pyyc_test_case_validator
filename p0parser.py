# python3 grammar for P0:

import ply.lex as lex
import ply.yacc as yacc
from ast import *
import ast
import logging


class P0Lexer:
    tokens = ('INT',
              'NAME',
              'EQUALS', 
              'LPAREN', 
              'RPAREN',  
              'MINUS', 
              'PLUS',
              'COMMA',
              )

    t_PLUS = r'\+'
    t_MINUS = r'-'
    t_EQUALS = r'='
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_COMMA = r','
    t_ignore = ' \t'
    t_ignore_comment = r'\#.*'

    def __init__(self):
        self.lexer = lex.lex(module=self)
        self.lexer.begin('INITIAL')

    def t_NAME(self, t):
        r'[a-zA-Z_][a-zA-Z_0-9]*'
        return t

    def t_INT(self, t):
        r'\d+'
        t.value = int(t.value)
        return t

    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    def t_error(self, t):
        logging.error("Illegal character '%s'" % t.value[0])
        exit(1)


# Grammar for P0:
# statements := statement+
# statement := compound_statement | simple_statement
# simple_statement := assignment
# assignment := NAME ['=' expression]
# expression := sum
# sum := sum '+' term | term
# term := factor
# factor := '+' factor | '-' factor | primary
# primary: primary '(' [arguments] ') | atom
# atom := INT | NAME
# arguments := argument | argument ',' arguments
# argument := expression
class P0Parser:
    tokens = P0Lexer.tokens

    precedence = (
        ('left', 'PLUS', 'MINUS'),
        ('right', 'UMINUS'),
    )

    def __init__(self):
        self.lexer = P0Lexer()
        self.parser = yacc.yacc(module=self)

    def p_statements(self, p):
        '''
        statements : statement
                   | statement statements
        '''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = [p[1]] + p[2]
        p[0] = Module(body=p[0])
        logging.info(ast.dump(p[0]))

    def p_statement(self, p):
        '''
        statement : simple_statement
        '''
        p[0] = p[1]
        logging.info(ast.dump(p[0]))

    def p_simple_statement(self, p):
        '''
        simple_statement : assignment
        '''
        p[0] = p[1]
        logging.info(ast.dump(p[0]))
    
    def p_assignment(self, p):
        '''
        assignment : NAME EQUALS expression
        '''
        p[0] = Assign(targets=[Name(id=p[1], ctx=Store())], value=p[3])
        logging.info(ast.dump(p[0]))

    def p_expression(self, p):
        '''
        expression : sum
        '''
        p[0] = p[1]
        logging.info(ast.dump(p[0]))

    def p_sum(self, p):
        '''
        sum : sum PLUS term
            | term
        '''
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = BinOp(left=p[1], op=Add(), right=p[3])
        logging.info(ast.dump(p[0]))

    def p_term(self, p):
        '''
        term : factor
        '''
        p[0] = p[1]
        logging.info(ast.dump(p[0]))

    def p_factor(self, p):
        '''
        factor : MINUS factor %prec UMINUS
               | primary
        '''
        if len(p) == 2:
            p[0] = p[1]
        else:
            if p[1] == '+':
                p[0] = UnaryOp(op=UAdd(), operand=p[2])
            else:
                p[0] = UnaryOp(op=USub(), operand=p[2])
        logging.info(ast.dump(p[0]))

    def p_primary(self, p):
        '''
        primary : primary LPAREN arguments RPAREN
                | atom
        '''
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = Call(func=p[1], args=p[3])
        logging.info(ast.dump(p[0]))

    def p_arguments(self, p):
        '''
        arguments : argument
                  | argument COMMA arguments
        '''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = [p[1]] + p[3]
        logging.info(ast.dump(p[0]))

    def p_argument(self, p):
        '''
        argument : expression
        '''
        p[0] = p[1]
        logging.info(ast.dump(p[0]))

    def p_atom(self, p):
        '''
        atom : INT
             | NAME
        '''
        if isinstance(p[1], int):
            p[0] = Constant(value=p[1])
        else:
            p[0] = Name(id=p[1], ctx=Load())
        logging.info(ast.dump(p[0]))


    def p_error(self, p):
        if p:
            logging.error("Syntax error at '%s'" % p.value)
        else:
            logging.error("Syntax error at EOF")
        exit(1)


# Setup logging format
FORMAT = '[%(levelname)s] File: %(filename)s, Line: %(lineno)d, %(message)s'
logging.basicConfig(
    format=FORMAT, level=logging.INFO)
parser = P0Parser().parser
x = '''
x
'''
parser.parse(x)
logging.info(ast.dump(ast.parse(x)))
