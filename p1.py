# python3 grammar for P0:

import ply.lex as lex
import ply.yacc as yacc
from ast import *
import ast
import logging


class P0Lexer:
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
    tokens = ['integer',
              'identifier',
              'EQUALS', 
              'LPAREN', 
              'RPAREN',  
              'MINUS', 
              'PLUS',
              'COMMA',
              'NEWLINE'] + list(reserved.values())

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

    def t_identifier(self, t):
        r'[a-zA-Z_][a-zA-Z_0-9]*'
        t.type = reserved.get(t.value, 'identifier')
        return t

    def t_integer(t):
        r'\d+'
        try:
            t.value = int(t.value)
        except ValueError:
            logging.error("Integer value too large %d", t.value)
            t.value = 0
        return t

    def t_NEWLINE(self, t):
        r'( \r?\n[ \t]* )+'
        t.lexer.lineno += len(t.value)
        # return t

    def t_error(self, t):
        logging.error("Illegal character '%s'" % t.value[0])
        exit(1)



# Grammar for P0:
# module := statement*
# statements := statement+
# statement := simple_statements
# simple_statements := simple_statement 
#       | simple_statements NEWLINE simple_statement
# simple_statement := assignment | d_expression
# assignment := NAME '=' expression
# d_expression := expression
# expression := binary_expression
#             | unary_expression
#             | call_expression
#             | LPAREN expression RPAREN
#             | atom
# binary_expression := expression PLUS expression
# unary_expression := MINUS expression
# call_expression := NAME LPAREN expression_list RPAREN
# atom := INT | NAME
# arguments := args | empty
# args := arg | args ',' arg
# arg := expression
class P0Parser:
    tokens = P0Lexer.tokens

    # parenthesis has the highest precedence
    precedence = (
        ('left', 'PLUS', 'MINUS'),
        ('right', 'UMINUS'),
    )

    def __init__(self):
        self.lexer = P0Lexer()
        self.parser = yacc.yacc(module=self, start='module', debug=1)
        logging.info('\033[1;33m Validating P0 using PLY \033[0m')

    def p_module(self, p):
        '''
        module : statements
        '''
        p[0] = Module(body=p[1])
        logging.info(ast.dump(p[0]))

    def p_statements(self, p):
        '''
        statements : statement statements
                    | statement
                    | empty
        '''
        if len(p) == 2:
            p[0] = [p[1]] if p[1] is not None else []
        else:
            p[0] = [p[1]] + p[2]

    def p_statement(self, p):
        '''
        statement : simple_statements
        '''
        p[0] = p[1]

    def p_simple_statements(self, p):
        '''
        simple_statements : simple_statement
                            | simple_statements NEWLINE simple_statement
        '''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[3]]

    def p_simple_statement(self, p):
        '''
        simple_statement : assignment
                        | expression_stmt
        '''
        p[0] = p[1]
    
    def p_assignment(self, p):
        '''
        assignment : NAME EQUALS expression
        '''
        p[0] = Assign(targets=[Name(id=p[1], ctx=Store())], value=p[3])

    def p_expression_stmt(self, p):
        '''
        expression_stmt : expression 
        '''
        p[0] = Expr(value=p[1])

    def p_expression(self, p):
        '''
        expression : binary_expression
                    | unary_expression
                    | call_expression
                    | paren_expression
                    | atom
        '''
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = p[2]

    def p_binary_expression(self, p):
        '''
        binary_expression : expression PLUS expression
        '''
        p[0] = BinOp(left=p[1], op=Add(), right=p[3])

    def p_unary_expression(self, p):
        '''
        unary_expression : MINUS expression %prec UMINUS
        '''
        p[0] = UnaryOp(op=USub(), operand=p[2])

    def p_call_expression(self, p):
        '''
        call_expression : primary LPAREN arguments RPAREN
        '''
        p[0] = Call(func=p[1], args=p[3])

    def p_parent_expr(self, p):
        '''
        paren_expression : LPAREN expression RPAREN
        '''
        p[0] = p[2]


    def p_arguments(self, p):
        '''
        arguments : args
                    | empty
        '''
        if len(p) == 2:
            p[0] = p[1] if p[1] is not None else []
        else:
            p[0] = []
    
    def p_args(self, p):
        '''
        args : arg
             | args COMMA arg
        '''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[3]]

    def p_arg(self, p):
        '''
        arg : expression
        '''
        p[0] = p[1]

    def p_atom(self, p):
        '''
        atom : INT
             | NAME
        '''
        if isinstance(p[1], int):
            p[0] = Constant(value=p[1])
        else:
            p[0] = Name(id=p[1], ctx=Load())

    def p_empty(self, p):
        '''
        empty :
        '''
        pass


    def p_error(self, p):
        stack_state_str = ' '.join([symbol.type for symbol in self.parser.symstack][1:])
        err_tok = 'EOF'
        if p:
            err_tok = p
        logging.error('\033[1;31m Syntax error at "{}".\033[0m \n \033[1;31mParser State:{} {} . {}\033[0m'
                  .format(err_tok,
                          self.parser.state,
                          stack_state_str,
                          p))
        exit(1)


# def ply_validate(data):
#     return P0Parser().parser.parse(data)
#
# def past_validate(tree):
#     logging.info("\033[1;33m Validating P0 using AST Module \033[0m")
#     P0_nodes = [Module, Assign, Name,
#                 Constant, Expr, Call,
#                 UnaryOp, BinOp, USub,
#                 Add, Store, Load,
#                 List, Dict, Subscript,
#                 BoolOp, And, Or, Not,
#                 Eq, NotEq, Is,
#                 IfExp]
#     nodes = NodeVisitor().visit(tree).nodes
#     for node in nodes:
#         if node not in P0_nodes:
#             # make the text red
#             logging.error("\033[1;31m Invalid node: %s \033[0m", node)
#             raise Exception("\033[1;31mP0 verification failed. Invalid node: %s \033[0m" % node.__name__)

#     for node in ast.walk(tree):
#         if isinstance(node, ast.UnaryOp):
#             if not isinstance(node.op, ast.USub) or \
#                 not isinstance(node.operand, ast.Not):
#                 raise Exception("\033[1;31mP0 verification failed. Invalid UnaryOp: %s \033[0m" % node.op)
#         if isinstance(node, ast.BinOp):
#             if not isinstance(node.op, ast.Add):
#                 raise Exception("\033[1;31mP0 verification failed. Invalid BinOp: %s \033[0m" % node.op)
#         if isinstance(node, ast.Call):
#             if not node.func.id in ['print', 'input']:
#                 raise Exception("\033[1;31mP0 verification failed. Invalid Call: %s \033[0m" % node.func.id)
                
#     return True 

# class NodeVisitor(ast.NodeVisitor):
#     def __init__(self):
#         self.nodes = []

#     def generic_visit(self, node):
#         self.nodes.append(type(node))
#         ast.NodeVisitor.generic_visit(self, node)
#         return self       

FORMAT = '[%(levelname)s] File: %(filename)s, Line: %(lineno)d, %(message)s'
logging.basicConfig(
    format=FORMAT, level=logging.INFO)

x = '''
x = get_func_ptr(function)()
'''
P0Parser().parser.parse(x)
logging.info(ast.dump(ast.parse(x)))