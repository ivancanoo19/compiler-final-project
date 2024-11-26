#Esta clase SIMULA la ejecución de el codigo en python

class Linker:
    def __init__(self, symbol_table, assembly_code):
        self.symbol_table = symbol_table

        if isinstance(assembly_code, str):  # Si se pasa como texto único
            self.assembly_code = assembly_code.splitlines()  # Divide por líneas
        else:
            self.assembly_code = assembly_code  # Si ya es una lista, úsala directamente
        
        self.labels = {}
        self.memory = [0] * 1000 # Simula 256 posiciones de memoria
        self.registers = {f"R{i}": 0 for i in range(16)}  # 16 registros generales
        self.program_counter = 0
        self.memory_segment = {}
        self.code_object = []
        self.opcodes = {
            'MOV': '01',
            'SLT': '02',
            'JZ': '03',
            'JMP': '04'
        }

        #nombre del dirección de memoria / nombre_registro : valor 
        self.registers = {
            '00': {'name':'R0', 'value': 0},
            '01': {'name':'R1', 'value': 0},
            '0A': {'name':'R10', 'value': 0}
        }
        
        
    #Genera diccionarios que nos permiten saber en que parte de la memoria de codigo esta cada instrucción 
    def generate_code_object(self):

        self.store()

        for index, instruction in self.memory_segment.items():
            opcode = self.opcodes.get(instruction['opcode'], '??')  # Obtengo el codigo de operación 
            operands = instruction['operands']                      # Recupero los operandos de la operación 

        # Para cada tipo de opecación genero su codigo objeto 
            if instruction['opcode'] == 'MOV':  #MOV REG VALOR 
                reg = self.get_key_by_name(operands[0][:-1])        # Recupera la dirección de memoria del registro 
                val_hex = f"{int(operands[1]):04X}"               # Convertir valor a hexadecimal de 4 dígitos
                self.code_object.append(f"{opcode} {reg} {val_hex}")

            elif instruction['opcode'] == 'SLT':  # SLT R, [R], VALOR
                reg_dest = self.get_key_by_name(operands[0][:-1])
                reg_src = self.get_key_by_name(operands[1][1:-2])
                val_hex = f"{int(operands[2]):04X}"
                self.code_object.append(f"{opcode} {reg_dest} {reg_src} {val_hex}")
            
            elif instruction['opcode'] == 'JZ':  # JZ R, LABEL
                reg = self.get_key_by_name(operands[0][:-1])
                label = self.get_key_by_label(operands[1]); 
                self.code_object.append(f"{opcode} {reg} {label}")  

            elif instruction['opcode'] == 'JMP':  # JMP LABEL
                label = self.get_key_by_label(operands[0]); 
                self.code_object.append(f"{opcode} {label}")
            else:
                self.code_object.append("INVALID")  # Caso para instrucciones no reconocidas
        return self.code_object
    
    def get_key_by_name(self, register_name):
        for key, value in self.registers.items():
            if value['name'] == register_name:
                return key
        return None
    
    def get_key_by_label(self, label):
        for k, v in self.labels.items(): # Obtener dirección de la etiqueta
            if v == label:
                return k 
        return None
    
    def store(self): 
        # Primera pasada: resolver etiquetas
        for idx, line in enumerate(self.assembly_code):
            if ":" in line:  # Detectar etiquetas
                label, _ = line.split(":")
                self.labels[idx] = label.strip()       #Guardo en el diccionario la etiqueta y no linea
        # Segunda pasada: Guardar cada linea de codigo en una sección de la memoria
        for idx, line in enumerate(self.assembly_code):
            if ":" in line:  # Omitir etiquetas en la segunda pasada
                continue
            instruction = self.parse_instruction(line)
            self.memory_segment[idx] = instruction
    
    def parse_instruction(self, line):
        # Traducir instrucciones ensamblador a un formato binario/objeto
        triple = line.split()
        opcode = triple[0]
        operands = triple[1:]
        return {"opcode": opcode, "operands": operands}
    
    def simulate_execution(self):
        """Simula la ejecución del código objeto"""
        self.program_counter = 0  # Inicializa el contador de programa
        while self.program_counter < len(self.code_object):
            instruction = self.code_object[self.program_counter]  #Recupera cada instrucción del codigo objeto 
            parts = instruction.split()                           #Genera una lista con cada parte 
            opcode = parts[0]                                     #recuperamos el codigo de operación 
            if opcode == '01':                  # Si el codigo de operación es un 01 es una operación MOV asignación 3 partes
                reg = parts[1]                  # registro 
                val = int(parts[2], 16)       # Valor
                print(f" {reg} <-- {val}")
                self.registers[reg]['value'] = val
            elif opcode == '02':  # SLT reg_dest, [reg_src], value
                reg_dest = parts[1]                         # donde vamos a guardar el resultado de la op 
                reg_src = self.registers[parts[2]]['value'] # recuperamos el valor de ese registro 
                value = int(parts[3], 16)                   # recuperamos el valor 
                print(f"Comparando {reg_src} < {value}")
                self.registers[reg_dest]['value'] = int(reg_src < value)
                print(f"{reg_dest} <-- {int(reg_src < value)}")

            elif opcode == '03':  # JZ reg, label
                reg_value = self.registers[parts[1]]['value']     #Recupera el valor del registro 
                linea_de_codigo = parts[2]                                  #Recupera la linea de codigo de esa etiqueta
                if reg_value == 0:                                #Si es igual a cero tiene que saltar
                    self.program_counter = int(linea_de_codigo) - 1  # Salto a la etiqueta
                    print(f"Salto a linea de codigo {linea_de_codigo}")
                else:
                    print(f" No salta")

            elif opcode == '04':  # JMP label
                label = parts[1]
                if label in self.labels:
                    self.program_counter = self.labels[label] - 1  # Salto a la etiqueta
                    print(f"JMP: Salto a {label}")
                else:
                    print(f"JMP: Etiqueta no encontrada {label}")

            self.program_counter += 1  # Incrementar el contador de programa

        print("Ejecución completada.")
        print("Estado final de los registros:", self.registers)
