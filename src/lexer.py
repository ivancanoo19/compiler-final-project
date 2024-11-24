import ply.lex as lex

# Lista de tokens
tokens = [
    'IDENTIFIER', 'LITERAL_NUM', 'MAS', 'MENOS', 'POR', 'DIVIDIDO', 
    'PARIZQ', 'PARDER', 'PTCOMA', 'IGUAL', 'MENORQUE', 'MAYORQUE', 
    'MENORIGUAL', 'MAYORIGUAL', 'IGUALDAD', 'LLAVEIZQ', 'LLAVEDER'
]

# Palabras reservadas
reserved = {
    'if': 'IF',
    'else': 'ELSE',
    'int': 'INT',
    'return': 'RETURN',
    'for': 'FOR'
}

tokens += list(reserved.values())

# Definiciones de tokens
t_PARIZQ = r'\('
t_PARDER = r'\)'
t_LLAVEIZQ = r'\{'
t_LLAVEDER = r'\}'
t_MAS = r'\+'
t_MENOS = r'-'
t_POR = r'\*'
t_DIVIDIDO = r'/'
t_PTCOMA = r';'
t_IGUAL = r'='
t_MENORQUE = r'<'
t_MAYORQUE = r'>'
t_MENORIGUAL = r'<='
t_MAYORIGUAL = r'>='
t_IGUALDAD = r'=='
t_ignore = ' \t'

# Token de número literal
def t_LITERAL_NUM(t):
    r'\d+'
    t.value = int(t.value)
    return t

# Token de identificador y palabras reservadas
def t_IDENTIFIER(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'IDENTIFIER')  # Verifica si es una palabra reservada
    return t

# Seguimiento de líneas
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Manejo de errores
def t_error(t):
    print(f"Carácter ilegal '{t.value[0]}' en la línea {t.lineno}")
    t.lexer.skip(1)

# Construye el lexer
def build_lexer():
    return lex.lex()
