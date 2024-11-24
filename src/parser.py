# src/my_parser.py

import ply.lex as lex
import ply.yacc as yacc
from my_ast import AssignNode, DeclaracionNode, IfNode, BlockNode

# Definición de tokens
tokens = (
    'INT',
    'IF',
    'ELSE',
    'IDENTIFIER',
    'NUMBER',
    'SEMICOLON',
    'EQUALS',
    'LT',
    'PLUS',
    'MINUS',
    'TIMES',
    'DIVIDE',
    'LPAREN',
    'RPAREN',
    'LBRACE',
    'RBRACE',
)

# Expresiones regulares para tokens simples
t_SEMICOLON = r';'
t_EQUALS    = r'='
t_LT        = r'<'
t_PLUS      = r'\+'
t_MINUS     = r'-'
t_TIMES     = r'\*'
t_DIVIDE    = r'/'
t_LPAREN    = r'\('
t_RPAREN    = r'\)'
t_LBRACE    = r'\{'
t_RBRACE    = r'\}'

# Ignorar espacios y tabs
t_ignore = ' \t'

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_IF(t):
    r'if'
    return t

def t_ELSE(t):
    r'else'
    return t

def t_INT(t):
    r'int'
    return t

def t_IDENTIFIER(t):
    r'[a-zA-Z_áéíóúÁÉÍÓÚñÑ][a-zA-Z0-9_áéíóúÁÉÍÓÚñÑ]*'
    return t

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

# Manejo de errores
def t_error(t):
    print(f"Illegal character '{t.value[0]}' at line {t.lineno}")
    t.lexer.skip(1)

# Construir el lexer
lexer = lex.lex()

# Precedencia de operadores
precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
    ('nonassoc', 'LT'),
)

# Definición de la gramática
def p_program(p):
    '''program : statements'''
    p[0] = BlockNode(p[1])

def p_statements_multiple(p):
    '''statements : statements statement'''
    p[0] = p[1] + [p[2]]

def p_statements_single(p):
    '''statements : statement'''
    p[0] = [p[1]]

def p_statement_declaration(p):
    '''statement : INT IDENTIFIER SEMICOLON
                 | INT IDENTIFIER EQUALS expression SEMICOLON'''
    if len(p) == 4:
        p[0] = DeclaracionNode(p[2])
    else:
        p[0] = DeclaracionNode(p[2], p[4])

def p_statement_assignment(p):
    '''statement : IDENTIFIER EQUALS expression SEMICOLON'''
    p[0] = AssignNode(p[1], p[3])

def p_statement_if(p):
    '''statement : IF LPAREN condition RPAREN block
                 | IF LPAREN condition RPAREN block ELSE block'''
    if len(p) == 6:
        p[0] = IfNode(p[3], p[5])
    else:
        p[0] = IfNode(p[3], p[5], p[7])

def p_condition(p):
    '''condition : expression LT expression'''
    p[0] = ('<', p[1], p[3])

def p_block(p):
    '''block : LBRACE statements RBRACE'''
    p[0] = BlockNode(p[2])

def p_expression_binop(p):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression'''
    p[0] = (p[2], p[1], p[3])

def p_expression_number(p):
    '''expression : NUMBER'''
    p[0] = p[1]

def p_expression_identifier(p):
    '''expression : IDENTIFIER'''
    p[0] = p[1]

def p_error(p):
    if p:
        print(f"Syntax error at '{p.value}' on line {p.lineno}")
    else:
        print("Syntax error at EOF")

# Construir el parser
def build_parser():
    return yacc.yacc()
