import ply.lex as lex
import ply.yacc as yacc
from ply.lex import TOKEN
from ast import *
import ast
import logging
import copy

# Lexer

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
    'EQ', 
    'NOT_EQ', 
    'NEWLINE', 
    'INDENT', 
    'DEDENT', 
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
    ] + list(reserved.values())
t_ignore = ' \t'
t_ignore_comment = r'\#.*'
t_WHITESPACE = r'\n[ ]*'
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




def t_identifier(t):
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

def t_NEWLINE(t):
    r'( \r?\n[ \t]* )+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    logging.error("Illegal character '%s'" % t.value[0])
    exit(1)

lexer = lex.lex()

################################### Indent Lexer

class IndentLexer(object):
    """
    A second lexing stage that interprets WHITESPACE
    Manages Off-Side Rule for indentation
    """
    def __init__(self, lexer):
        self.indents = [0]  # indentation stack
        self.tokens = []    # token queue
        self.lexer = lexer

    def input(self, *args, **kwds):
        self.lexer.input(*args, **kwds)

    # Iterator interface
    def __iter__(self):
        return self

    def next(self):
        t = self.token()
        if t is None:
            raise StopIteration
        return t

    __next__ = next

    def token(self):
        # empty our buffer first
        if self.tokens:
            return self.tokens.pop(0)

        # loop until we find a valid token
        while 1:
            # grab the next from first stage
            token = self.lexer.token()

            # we only care about whitespace
            if not token or token.type != 'WHITESPACE':
                return token

            # check for new indent/dedent
            whitespace = token.value[1:]  # strip \n
            change = self._calc_indent(whitespace)
            if change:
                break

        # indentation change
        if change == 1:
            token.type = 'INDENT'
            return token

        # dedenting one or more times
        assert change < 0
        change += 1
        token.type = 'DEDENT'

        # buffer any additional DEDENTs
        while change:
            self.tokens.append(copy.copy(token))
            change += 1

        return token

    def _calc_indent(self, whitespace):
        "returns a number representing indents added or removed"
        n = len(whitespace) # number of spaces
        indents = self.indents # stack of space numbers
        if n > indents[-1]:
            indents.append(n)
            return 1

        # we are at the same level
        if n == indents[-1]:
            return 0

        # dedent one or more times
        i = 0
        while n < indents[-1]:
            indents.pop()
            if n > indents[-1]:
                raise SyntaxError("wrong indentation level")
            i -= 1
        return i

lexer = IndentLexer(lexer)

################################### Parser

# atom ::= identifier | literal | enclosure
# enclosure ::= parenth_form | list_display | dict_display
# parenth_form ::= '(' starred_expression ')'
# starred_expression ::= expression | starred_expression ',' expression
# list_display ::= '[' expression_list ']'
# dict_display ::= '{' key_datum_list '}'
# key_datum_list ::= key_datum | key_datum_list ',' key_datum | empty
# key_datum ::= expression ':' expression
# literal ::= integer
# primary := atom | subscription | call
# subscription ::= primary "[" expression_list "]"
# call ::= primary "(" argument_list ")"
# argument_list ::= positional_arguments
# positional_arguments ::= positional_arguments "," positional_item | positional_item
# positional_item ::= expression
# expression_list ::= expression_list "," expression | expression | empty
# expression ::= conditional_expression | lambda_expr
# conditional_expression ::= or_test | or_test 'if' or_test 'else' expression
# lambda_expr ::= "lambda" parameter_list ":" expression
# or_test ::= and_test | or_test "or" and_test
# and_test ::= not_test | and_test "and" not_test
# not_test ::= "not" not_test | comparison
# comparison ::= a_expr | comparison comp_operator a_expr
# comp_operator ::= "==" | "!=" | "is" | "is" "not"
# a_expr ::= u_expr | a_expr "+" u_expr
# u_expr ::= primary | "-" u_expr


# simple_stmt ::= expression_stmt
#             | assignment_stmt
#             | return_stmt

# expression_stmt ::= expression

# assignment_stmt ::= target_list '=' expression
# target_list ::= target_list ',' target | target
# target ::= identifier | "(" target_list ")" | "[" target_list "]" | subscription

# return_stmt ::= "return" expression_list

# compound_stmt ::= if_stmt
#                 | while_stmt
#                 | funcdef
#                 | classdef

# suite is stmt_list followed by a NEWLINE
# or NEWLINE followed by an INDENT statement+ DEDENT
# suite ::= stmt_list NEWLINE | NEWLINE INDENT statements DEDENT
# statements ::= statements statement | statement
# statement ::= stmt_list NEWLINE | compound_stmt
# stmt_list ::= stmt_list ';' simple_stmt | simple_stmt

# if_stmt ::= "if" expression ":" suite | "if" expression ":" suite "else" ":" suite
# while_stmt ::= "while" expression ":" suite

# funcdef ::= "def" funcname "(" parameter_list ")" ":" suite
# parameter_list ::= parameter_list "," parameter | parameter | empty
# parameter ::= identifier
# funcname ::= identifier

# classdef ::= "class" classname ":" suite
# classname ::= identifier

# parenthesis has the highest precedence
# function call has the highest precedence
precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('right', 'UMINUS'),
)


def p_module(p):
    '''
    module : statements
    '''
    p[0] = Module(body=p[1])
    logging.info(ast.dump(p[0]))


def p_statements(p):
    '''
    statements : statements statement
               | statement
    '''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = [p[1]]
    logging.info(ast.dump(p[0]))


def p_statement(p):
    '''
    statement : stmt_list NEWLINE
              | compound_stmt
    '''
    p[0] = p[1]
    logging.info(ast.dump(p[0]))


def p_stmt_list(p):
    '''
    stmt_list : stmt_list SEMICOLON simple_stmt
             | simple_stmt
    '''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]
    logging.info(ast.dump(p[0]))


def p_simple_stmt(p):
    '''
    simple_stmt : expression_stmt
                | assignment_stmt
                | return_stmt
    '''
    p[0] = p[1]
    logging.info(ast.dump(p[0]))


def p_compound_stmt(p):
    '''
    compound_stmt : if_stmt
                  | while_stmt
                  | funcdef
                  | classdef
    '''
    p[0] = p[1]
    logging.info(ast.dump(p[0]))


def p_expression_stmt(p):
    '''
    expression_stmt : expression
    '''
    p[0] = Expr(value=p[1])
    logging.info(ast.dump(p[0]))


def p_assignment_stmt(p):
    '''
    assignment_stmt : target_list EQUALS expression
    '''
    p[0] = Assign(targets=p[1], value=p[3])
    logging.info(ast.dump(p[0]))


def p_target_list(p):
    '''
    target_list : target
    '''
    p[0] = [p[1]]
    logging.info(ast.dump(p[0]))


def p_target(p):
    '''
    target : identifier
          | LPAREN target_list RPAREN
          | LBRACKET target_list RBRACKET
          | subscription
    '''
    p[0] = p[1]
    logging.info(ast.dump(p[0]))


def p_return_stmt(p):
    '''
    return_stmt : RETURN expression_list
    '''
    p[0] = Return(value=p[2])
    logging.info(ast.dump(p[0]))


def p_if_stmt(p):
    '''
    if_stmt : IF expression COLON suite
           | IF expression COLON suite ELSE COLON suite
    '''
    if len(p) == 6:
        p[0] = If(test=p[2], body=p[4], orelse=p[6])
    else:
        p[0] = If(test=p[2], body=p[4])
    logging.info(ast.dump(p[0]))


def p_while_stmt(p):
    '''
    while_stmt : WHILE expression COLON suite
    '''
    p[0] = While(test=p[2], body=p[4])
    logging.info(ast.dump(p[0]))


def p_funcdef(p):
    '''
    funcdef : DEF funcname LPAREN parameter_list RPAREN COLON suite
    '''
    p[0] = FunctionDef(name=p[2], args=p[4], body=p[6])
    logging.info(ast.dump(p[0]))


def p_parameter_list(p):
    '''
    parameter_list : parameter_list COLON parameter 
                    | parameter 
                    | empty
    '''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]
    logging.info(ast.dump(p[0]))


def p_parameter(p):
    '''
    parameter : identifier
    '''
    p[0] = p[1]
    logging.info(ast.dump(p[0]))

def p_funcname(p):
    '''
    funcname : identifier
    '''
    p[0] = p[1]
    logging.info(ast.dump(p[0]))

def p_suite(p):
    '''
    suite : stmt_list NEWLINE
         | NEWLINE INDENT statements DEDENT
    '''
    if len(p) == 3:
        p[0] = p[1]
    else:
        p[0] = p[3]
    logging.info(ast.dump(p[0]))


def p_classdef(p):
    '''
    classdef : CLASS classname COLON suite
    '''
    p[0] = ClassDef(name=p[2], body=p[4])
    logging.info(ast.dump(p[0]))


def p_classname(p):
    '''
    classname : identifier
    '''
    p[0] = Name(id=p[1])
    logging.info(ast.dump(p[0]))


def p_atom(p):
    '''
    atom : identifier
         | literal
         | enclosure
    '''
    p[0] = p[1]
    logging.info(ast.dump(p[0]))


def p_enclosure(p):
    '''
    enclosure : parenth_form
              | list_display
              | dict_display
    '''
    p[0] = p[1]
    logging.info(ast.dump(p[0]))


def p_parenth_form(p):
    '''
    parenth_form : LPAREN starred_expression RPAREN
    '''
    p[0] = p[2]
    logging.info(ast.dump(p[0]))


def p_starred_expression(p):
    '''
    starred_expression : expression
                       | starred_expression COLON expression
    '''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]
    logging.info(ast.dump(p[0]))


def p_list_display(p):
    '''
    list_display : LBRACKET expression_list RBRACKET
    '''
    p[0] = List(elts=p[2])
    logging.info(ast.dump(p[0]))


def p_dict_display(p):
    '''
    dict_display : LBRACE key_datum_list RBRACE
    '''
    p[0] = Dict(keys=[], values=[])
    if len(p[2]) > 0:
        for k, v in p[2]:
            p[0].keys.append(k)
            p[0].values.append(v)
    logging.info(ast.dump(p[0]))


def p_key_datum_list(p):
    '''
    key_datum_list : key_datum_list COMMA key_datum
                   | key_datum
                   | empty
    '''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]
    logging.info(ast.dump(p[0]))


def p_key_datum(p):
    '''
    key_datum : expression COLON expression
    '''
    p[0] = (p[1], p[3])
    logging.info(ast.dump(p[0]))


def p_literal(p):
    '''
    literal : integer 
            | TRUE 
            | FALSE
    '''
    p[0] = Constant(value=p[1])
    logging.info(ast.dump(p[0]))


def p_primary(p):
    '''
    primary : atom
            | subscription
            | call
    '''
    p[0] = p[1]
    logging.info(ast.dump(p[0]))


def p_subscription(p):
    '''
    subscription : primary LBRACKET expression_list RBRACKET
    '''
    p[0] = Subscript(value=p[1], slice=p[3])
    logging.info(ast.dump(p[0]))


def p_call(p):
    '''
    call : primary LPAREN argument_list RPAREN
    '''
    p[0] = Call(func=p[1], args=p[3])
    logging.info(ast.dump(p[0]))


def p_argument_list(p):
    '''
    argument_list : positional_arguments
    '''
    p[0] = p[1]
    logging.info(ast.dump(p[0]))


def p_positional_arguments(p):
    '''
    positional_arguments : positional_arguments COMMA positional_item
                         | positional_item
                         | empty
    '''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]
    logging.info(ast.dump(p[0]))


def p_positional_item(p):
    '''
    positional_item : expression
    '''
    p[0] = p[1]
    logging.info(ast.dump(p[0]))


def p_expression_list(p):
    '''
    expression_list : expression_list COMMA expression
                    | expression
                    | empty
    '''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]
    logging.info(ast.dump(p[0]))


def p_expression(p):
    '''
    expression : conditional_expression
                | lambda_expr
    '''
    p[0] = p[1]
    logging.info(ast.dump(p[0]))


def p_conditional_expression(p):
    '''
    conditional_expression : or_test
                            | or_test IF or_test ELSE expression
    '''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = IfExp(test=p[1], body=p[3], orelse=p[5])
    logging.info(ast.dump(p[0]))


def p_lambda_expr(p):
    '''
    lambda_expr : LAMBDA parameter_list COLON expression
    '''
    p[0] = Lambda(args=p[2], body=p[4])
    logging.info(ast.dump(p[0]))


def p_or_test(p):
    '''
    or_test : and_test
            | or_test OR and_test
    '''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = BoolOp(op=Or(), values=[p[1], p[3]])
    logging.info(ast.dump(p[0]))


def p_and_test(p):
    '''
    and_test : not_test 
             | and_test AND not_test
    '''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = BoolOp(op=And(), values=[p[1], p[3]])
    logging.info(ast.dump(p[0]))


def p_not_test(p):
    '''
    not_test : NOT not_test
             | comparison
    '''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = UnaryOp(op=Not(), operand=p[2])
    logging.info(ast.dump(p[0]))


def p_comparison(p):
    '''
    comparison : a_expr 
               | comparison comp_operator a_expr
    '''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = Compare(left=p[1], ops=[p[2]], comparators=[p[3]])
    logging.info(ast.dump(p[0]))


def p_comp_operator(p):
    '''
    comp_operator : EQ
                  | NOT_EQ
                  | IS
    '''
    p[0] = Eq() if p[1] == '==' else NotEq() if p[1] == '!=' else Is()
    logging.info(ast.dump(p[0]))


def p_a_expr(p):
    '''
    a_expr : a_expr PLUS u_expr
            | u_expr
    '''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = BinOp(left=p[1], op=Add(), right=p[3])
    logging.info(ast.dump(p[0]))


def p_u_expr(p):
    '''
    u_expr : primary
           | MINUS primary %prec UMINUS
    '''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = UnaryOp(op=USub(), operand=p[2])
    logging.info(ast.dump(p[0]))

def p_empty(p):
    '''
    empty :
    '''
    pass

def p_error(p):
    stack_state_str = ' '.join(
        [symbol.type for symbol in parser.symstack][1:])
    err_tok = 'EOF'
    if p:
        err_tok = p
    logging.error('\033[1;31m Syntax error at "{}".\033[0m \n \033[1;31mParser State:{} {} . {}\033[0m'
                  .format(err_tok,
                          parser.state,
                          stack_state_str,
                          p))
    exit(1)

FORMAT = '[%(levelname)s] File: %(filename)s, Line: %(lineno)d, %(message)s'
logging.basicConfig(
    format=FORMAT, level=logging.INFO)
parser = yacc.yacc(debug=True)
res = parser.parse('1 + 2', lexer) 
print(res)