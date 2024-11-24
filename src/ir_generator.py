# src/ir_generator.py

class IRInstruction:
    """Representa una instrucción de Código Intermedio (IR)."""
    def __init__(self, op, arg1, arg2=None, result=None):
        self.op = op
        self.arg1 = arg1
        self.arg2 = arg2
        self.result = result

    def __str__(self):
        if self.op in ['assign']:
            return f"{self.op} {self.arg1}, {self.result}"
        elif self.op in ['+', '-', '*', '/', '<', '>', '==', '!=']:
            return f"{self.op} {self.arg1} {self.arg2} {self.result}"
        elif self.op in ['if_false', 'goto']:
            return f"{self.op} {self.arg1}, {self.result}"
        elif self.op == 'label':
            return f"label {self.arg1}:"
        else:
            return f"{self.op} {self.arg1} {self.arg2} {self.result}"

class IRGenerator:
    """Genera código intermedio (IR) a partir del AST."""
    def __init__(self):
        self.instructions = []
        self.temp_count = 0
        self.label_count = 0

    def new_temp(self):
        """Genera un nuevo temporal."""
        temp = f"t{self.temp_count}"
        self.temp_count += 1
        return temp

    def new_label(self):
        """Genera una nueva etiqueta."""
        label = f"L{self.label_count}"
        self.label_count += 1
        return label

    def generate(self, node):
        """Genera IR a partir de un nodo del AST."""
        method_name = f'gen_{type(node).__name__}'
        method = getattr(self, method_name, self.gen_generic)
        return method(node)

    def gen_generic(self, node):
        """Maneja nodos genéricos."""
        raise Exception(f"No se implementó la generación de IR para el nodo: {type(node).__name__}")

    def gen_BlockNode(self, node):
        """Genera IR para un bloque de código."""
        for stmt in node.statements:
            self.generate(stmt)

    def gen_AssignNode(self, node):
        """Genera IR para una asignación."""
        if isinstance(node.expression, tuple):
            # Es una operación binaria
            op, arg1, arg2 = node.expression
            temp = self.new_temp()
            self.instructions.append(IRInstruction(op, arg1, arg2, temp))
            self.instructions.append(IRInstruction('assign', temp, None, node.identifier))
        else:
            # Es una asignación simple
            self.instructions.append(IRInstruction('assign', node.expression, None, node.identifier))

    def gen_DeclaracionNode(self, node):
        """Genera IR para una declaración de variable."""
        if node.expression is not None:
            # Declaración con inicialización
            self.instructions.append(IRInstruction('assign', node.expression, None, node.identifier))
        else:
            # Declaración sin inicialización
            pass  # Podría inicializarse a 0 o similar si se desea

    def gen_IfNode(self, node):
        """Genera IR para una estructura if-else."""
        # Generar IR para la condición
        op, arg1, arg2 = node.condition
        temp = self.new_temp()
        self.instructions.append(IRInstruction(op, arg1, arg2, temp))
        # Instrucción condicional
        label_false = self.new_label()
        label_end = self.new_label()
        self.instructions.append(IRInstruction('if_false', temp, None, label_false))
        # Bloque if
        self.generate(node.if_block)
        self.instructions.append(IRInstruction('goto', None, None, label_end))
        # Bloque else
        self.instructions.append(IRInstruction('label', label_false, None, None))
        if node.else_block:
            self.generate(node.else_block)
        # Etiqueta de fin
        self.instructions.append(IRInstruction('label', label_end, None, None))
