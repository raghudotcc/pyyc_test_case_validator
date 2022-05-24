# python3 grammar for P0:

import ply.lex as lex
import ply.yacc as yacc
from ast import *
import ast
import logging

class P0Lexer:
    tokens = ('INT',
              'ID',
              'ASSIGN', 
              'LPAREN', 
              'RPAREN',  
              'MINUS', 
              'PLUS')
    

    t_PLUS = r'\+'
    t_MINUS = r'-'
    t_ASSIGN = r'='
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_ignore = ' \t'
    t_ignore_comment = r'\#.*'

    def __init__(self):
        self.lexer = lex.lex(module=self)
        self.lexer.begin('INITIAL')

    def t_ID(self, t):
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


# Parser
# mod = Module(stmt* body)
#        | Expression(expr body)
# stmt = Assign(expr* targets, expr value)
#        | Expr(expr value)
# expr = BinOp(expr left, operator op, expr right)
#        | UnaryOp(operator op, expr operand)
#        | Call(expr func, expr* args, keywords* keywords)
#        | Constant(constant value)
#        | Name(identifier id, expr_context ctx)
# expr_context = Load | Store | Del
# operator = Add
# unaryop = USub
class P0Parser:
    tokens = P0Lexer.tokens

    precedence = (
        ('left', 'PLUS', 'MINUS'),
        ('right', 'UMINUS'),
    )

    def __init__(self):
        self.lexer = P0Lexer()
        self.parser = yacc.yacc(module=self)

    def p_Module(self, p):
        '''
        Module : stmt_list
        '''
        p[0] = Module(body=p[1])
        logging.info(ast.dump(p[0]))

    def p_stmt_list(self, p):
        '''
        stmt_list : stmt
                  | stmt stmt_list
        '''
        # set p[0] to Module.body
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = [p[1]] + p[2]
        logging.info(ast.dump(p[0]) if not isinstance(p[0], list) else ast.dump(p[0][0]))

    def p_stmt(self, p):
        '''
        stmt : Expr
             | Assign
        '''
        p[0] = p[1]
        logging.info(ast.dump(p[0]))

    def p_Assign(self, p):
        '''
        Assign : Name ASSIGN expr
        '''
        if isinstance(p[1], Name):
            p[1].ctx = ast.Store()
        p[0] = Assign(targets=[p[1]], value=p[3])
        logging.info(ast.dump(p[0]))

    def p_Expr(self, p):
        '''
        Expr : expr
        '''
        p[0] = Expr(value=p[1])
        logging.info(ast.dump(p[0]))

    def p_expr(self, p):
        '''
        expr : BinOp
             | UnaryOp
             | Call
             | Constant
             | Name
             | Empty
        '''
        if isinstance(p[1], Name):
            p[1].ctx = ast.Load()
        p[0] = p[1]
        logging.info(ast.dump(p[0]) if p[0] is not None else None)

    def p_BinOp(self, p):
        '''
        BinOp : Add
        '''
        p[0] = p[1]
        logging.info(ast.dump(p[0]))

    def p_Add(self, p):
        '''
        Add : expr PLUS expr
        '''
        p[0] = BinOp(left=p[1], op=Add(), right=p[3])
        logging.info(ast.dump(p[0]))


    def p_UnaryOp(self, p):
        '''
        UnaryOp : USub
        '''
        p[0] = p[1]
        logging.info(ast.dump(p[0]))

    def p_USub(self, p):
        '''
        USub : MINUS expr %prec UMINUS
        '''
        p[0] = UnaryOp(op=USub(), operand=p[2])
        logging.info(ast.dump(p[0]))

    def p_Call(self, p):
        '''
        Call : Name LPAREN expr RPAREN
        '''
        if isinstance(p[1], Name):
            p[1].ctx = ast.Load()
        p[0] = Call(func=p[1], args=[p[3]] if p[3] is not None else [])
        logging.info(ast.dump(p[0]))

    def p_Constant(self, p):
        '''
        Constant : INT
        '''
        p[0] = Constant(value=p[1])
        logging.info(ast.dump(p[0]))

    def p_Name(self, p):
        '''
        Name : ID
        '''
        p[0] = Name(id=p[1])
        logging.info(ast.dump(p[0]))

    def p_Empty(self, p):
        'Empty :'
        pass

    def p_error(self, p):
        logging.error("Syntax error at '%s'" % p.value)
        exit(1)


# Setup logging format
FORMAT = '[%(levelname)s] File: %(filename)s, Line: %(lineno)d, %(message)s'
logging.basicConfig(
    format=FORMAT, level=logging.INFO)
parser = P0Parser().parser
x = '''
-x - 2
'''
parser.parse(x)
logging.info(ast.dump(ast.parse(x)))
