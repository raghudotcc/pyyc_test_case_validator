from collections import deque
import ply.lex as lex
import ply.yacc as yacc
from ply.lex import TOKEN
from ast import *
import ast

from inspect import currentframe, getframeinfo
from pathlib import Path

def get_fileinfo():
    """Get the file name, function name and line number of the current frame."""
    cf = currentframe()
    filename = getframeinfo(cf).filename
    lineno = cf.f_back.f_lineno
    funcname = cf.f_back.f_code.co_name
    return Path(filename).stem, funcname, lineno

verbose = True
verboseprint = print if verbose else lambda *a, **k: None
    
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
            verboseprint(get_fileinfo(), "Integer value too large {}".format(t.value))
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
        """
        p[0] = Module(body=p[1])
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
        """
        p[0] = p[1]
        verboseprint(get_fileinfo(), ast.dump(p[0]))

    def p_parenth_form(self, p):
        """
        parenth_form : LPAREN expression RPAREN
        """
        p[0] = p[2]
        verboseprint(get_fileinfo(), ast.dump(p[0]))

    def p_primary(self, p):
        """
        primary : atom
                | call
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

    def p_expression(self, p):
        """
        expression : conditional_expression
        """
        p[0] = p[1]
        verboseprint(get_fileinfo(), ast.dump(p[0]))

    def p_conditional_expression(self, p):
        """
        conditional_expression : or_test
        """
        p[0] = p[1]
        verboseprint(get_fileinfo(), ast.dump(p[0]))

    def p_or_test(self, p):
        """
        or_test : a_expr
        """
        p[0] = p[1]
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
    
    def p_u_expr(self, p):
        """
        u_expr : primary
               | MINUS primary %prec UMINUS
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






    

# parser = yacc.yacc(debug=True)
# res = parser.parse('1 + 2', lexer)
# verboseprint(get_fileinfo(), res)

program = '''x = 1
y = 2
z = 3
w = 23
v = -2
k = 12
print(x + y + z + w + v + k)
'''

lexer = Lexer()
lexer = IndentWrapper(lexer)
# lexer.input(program)
# while True:
#     tok = lexer.token()
#     if not tok:
#         break      # No more input
#     verboseprint(get_fileinfo(), tok)

Parser().parse(program, lexer)