# src/my_ast.py

class ASTNode:
    """Nodo base para el AST."""
    pass

class AssignNode(ASTNode):
    """Nodo para una asignación."""
    def __init__(self, identifier, expression):
        self.identifier = identifier
        self.expression = expression

    def __str__(self):
        return f"AssignNode(identifier={self.identifier}, expression={self.expression})"

class DeclaracionNode(ASTNode):
    """Nodo para una declaración de variable."""
    def __init__(self, identifier, expression=None):
        self.identifier = identifier
        self.expression = expression

    def __str__(self):
        return f"DeclaracionNode(identifier={self.identifier}, expression={self.expression})"

class IfNode(ASTNode):
    """Nodo para una estructura if-else."""
    def __init__(self, condition, if_block, else_block=None):
        self.condition = condition
        self.if_block = if_block  # Debería ser otro nodo que contenga declaraciones y asignaciones
        self.else_block = else_block  # Opcional

    def __str__(self):
        return f"IfNode(condition={self.condition}, if_block={self.if_block}, else_block={self.else_block})"

class BlockNode(ASTNode):
    """Nodo para un bloque de código."""
    def __init__(self, statements):
        self.statements = statements  # Lista de nodos

    def __str__(self):
        return f"BlockNode(statements={self.statements})"
