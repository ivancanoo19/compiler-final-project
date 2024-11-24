# src/code_generator.py

from symbol_table import SymbolTable, MemoryManager
from ir_generator import IRInstruction

class CodeGenerator:
    """Genera código ensamblador a partir del código intermedio optimizado."""
    def __init__(self, ir_instructions, symbol_table, memory_manager):
        self.ir = ir_instructions
        self.symbol_table = symbol_table
        self.memory_manager = memory_manager
        self.asm = []
        self.temp_registers = {}  # Mapa de temporales a registros
        self.available_registers = [f"R{i}" for i in range(10, 16)]  # R10 a R15 para temporales

    def allocate_register(self, temp):
        """Asigna un registro disponible a un temporal."""
        if temp in self.temp_registers:
            return self.temp_registers[temp]
        if not self.available_registers:
            raise Exception("No hay registros disponibles para asignar a temporales.")
        reg = self.available_registers.pop(0)
        self.temp_registers[temp] = reg
        return reg

    def free_register(self, temp):
        """Libera un registro asignado a un temporal."""
        if temp in self.temp_registers:
            reg = self.temp_registers.pop(temp)
            self.available_registers.insert(0, reg)

    def translate(self):
        """Traduce cada instrucción de IR a ensamblador."""
        for instr in self.ir:
            print(f"Translating IR instruction: {instr.op} {instr.arg1} {instr.arg2} {instr.result}")
            if instr.op == 'assign':
                self.translate_assign(instr)
            elif instr.op in ['+', '-', '*', '/']:
                self.translate_arithmetic(instr)
            elif instr.op in ['<', '>', '==', '!=']:
                self.translate_comparison(instr)
            elif instr.op == 'if_false':
                self.translate_if_false(instr)
            elif instr.op == 'goto':
                self.translate_goto(instr)
            elif instr.op == 'label':
                self.translate_label(instr)
            else:
                raise Exception(f"Instrucción IR desconocida: {instr.op}")

    def translate_assign(self, instr):
        """Traduce una instrucción de asignación."""
        dest_reg = self.get_destination_register(instr.result)
        # Determinar si arg1 es una variable, temporal o literal
        if isinstance(instr.arg1, str):
            if instr.arg1.startswith('t'):
                # Es un temporal
                src_reg = self.get_register(instr.arg1)
                if src_reg is None:
                    raise Exception(f"Temporal {instr.arg1} no está asignado a ningún registro.")
                self.asm.append(f"MOV {dest_reg}, {src_reg}")
            else:
                # Es una variable
                var_info = self.symbol_table.lookup(instr.arg1)
                src_address = var_info['address']
                self.asm.append(f"MOV {dest_reg}, [R{src_address}]")
        else:
            # Es un literal
            self.asm.append(f"MOV {dest_reg}, {instr.arg1}")

    def translate_arithmetic(self, instr):
        """Traduce una instrucción aritmética."""
        # Asignar registros a los operandos
        if isinstance(instr.arg1, str):
            if instr.arg1.startswith('t'):
                src1 = self.get_register(instr.arg1)
                if src1 is None:
                    raise Exception(f"Temporal {instr.arg1} no está asignado a ningún registro.")
            else:
                var_info = self.symbol_table.lookup(instr.arg1)
                src1 = f"[R{var_info['address']}]"
        else:
            src1 = instr.arg1  # Literal

        if isinstance(instr.arg2, str):
            if instr.arg2.startswith('t'):
                src2 = self.get_register(instr.arg2)
                if src2 is None:
                    raise Exception(f"Temporal {instr.arg2} no está asignado a ningún registro.")
            else:
                var_info = self.symbol_table.lookup(instr.arg2)
                src2 = f"[R{var_info['address']}]"
        else:
            src2 = instr.arg2  # Literal

        # Asignar un registro para el resultado
        dest_reg = self.allocate_register(instr.result)

        # Emitir la instrucción aritmética
        op_map = {
            '+': 'ADD',
            '-': 'SUB',
            '*': 'MUL',
            '/': 'DIV'
        }

        if instr.op not in op_map:
            raise Exception(f"Operación aritmética desconocida: {instr.op}")

        asm_op = op_map[instr.op]
        self.asm.append(f"{asm_op} {src1}, {src2}, {dest_reg}")

    def translate_comparison(self, instr):
        """Traduce una instrucción de comparación."""
        # Asignar registros a los operandos
        if isinstance(instr.arg1, str):
            if instr.arg1.startswith('t'):
                src1 = self.get_register(instr.arg1)
                if src1 is None:
                    raise Exception(f"Temporal {instr.arg1} no está asignado a ningún registro.")
            else:
                var_info = self.symbol_table.lookup(instr.arg1)
                src1 = f"[R{var_info['address']}]"
        else:
            src1 = instr.arg1  # Literal

        if isinstance(instr.arg2, str):
            if instr.arg2.startswith('t'):
                src2 = self.get_register(instr.arg2)
                if src2 is None:
                    raise Exception(f"Temporal {instr.arg2} no está asignado a ningún registro.")
            else:
                var_info = self.symbol_table.lookup(instr.arg2)
                src2 = f"[R{var_info['address']}]"
        else:
            src2 = instr.arg2  # Literal

        # Asignar un registro para el resultado
        dest_reg = self.allocate_register(instr.result)

        # Emitir la instrucción de comparación
        # Suponiendo que existe una instrucción 'SLT' (Set on Less Than), 'SGT', etc.
        op_map = {
            '<': 'SLT',  # Set on Less Than
            '>': 'SGT',  # Set on Greater Than
            '==': 'SEQ', # Set on Equal
            '!=': 'SNE'  # Set on Not Equal
        }

        if instr.op not in op_map:
            raise Exception(f"Operación de comparación desconocida: {instr.op}")

        asm_op = op_map[instr.op]
        self.asm.append(f"{asm_op} {dest_reg}, {src1}, {src2}")

    def translate_if_false(self, instr):
        """Traduce una instrucción condicional 'if_false'."""
        # Asumimos que 'arg1' es un temporal que contiene el resultado de la condición
        condition_temp = instr.arg1
        condition_reg = self.get_register(condition_temp)
        if condition_reg is None:
            raise Exception(f"Temporal {condition_temp} no está asignado a ningún registro.")

        # Emitir la instrucción de salto condicional
        self.asm.append(f"JZ {condition_reg}, {instr.result}")

    def translate_goto(self, instr):
        """Traduce una instrucción de salto incondicional."""
        self.asm.append(f"JMP {instr.result}")

    def translate_label(self, instr):
        """Traduce una instrucción de etiqueta."""
        self.asm.append(f"{instr.arg1}:")

    def get_register(self, temp):
        """Obtiene el registro asignado a un temporal."""
        return self.temp_registers.get(temp, None)

    def get_destination_register(self, dest):
        """Obtiene el registro de destino para una variable o temporal."""
        if dest.startswith('t'):
            # Es un temporal
            reg = self.allocate_register(dest)
            return reg
        else:
            # Es una variable, asignar un registro dedicado basado en su dirección
            var_info = self.symbol_table.lookup(dest)
            reg = f"R{var_info['address']}"  # Asumimos que cada variable tiene un registro correspondiente
            return reg

    def get_assembly(self):
        """Retorna el código ensamblador generado como una cadena."""
        return '\n'.join(self.asm)
