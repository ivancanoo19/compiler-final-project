# src/symbol_table.py

class MemoryManager:
    """Gestiona la asignación de memoria para variables y heap."""
    def __init__(self):
        self.stack_pointer = 0

    def allocate_stack(self, var_name):
        """Asigna una dirección en el stack para una variable."""
        address = self.stack_pointer
        self.stack_pointer += 1
        return address


class SymbolTable:
    """Tabla de símbolos para gestionar información sobre identificadores."""
    def __init__(self, memory_manager):
        self.scopes = [{}]  # Lista de diccionarios, uno por cada scope
        self.memory_manager = memory_manager

    def enter_scope(self):
        """Ingresa a un nuevo scope."""
        self.scopes.append({})

    def exit_scope(self):
        """Sale del scope actual."""
        self.scopes.pop()

    def declare(self, name, type=None, value=None):
        """Declara una nueva variable en el scope actual."""
        if name in self.scopes[-1]:
            raise Exception(f"Variable '{name}' ya declarada en el scope actual.")
        address = self.memory_manager.allocate_stack(name)
        self.scopes[-1][name] = {'type': type, 'address': address, 'value': value}

    def assign(self, name, value):
        """Asigna un valor a una variable existente."""
        for scope in reversed(self.scopes):
            if name in scope:
                scope[name]['value'] = value
                return
        raise Exception(f"Variable '{name}' no declarada.")

    def lookup(self, name):
        """Busca una variable en los scopes actuales."""
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        raise Exception(f"Variable '{name}' no declarada.")
