# src/gui.py

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from parser import build_parser  # Usando importación del módulo renombrado
from symbol_table import MemoryManager, SymbolTable
from my_ast import AssignNode, DeclaracionNode, IfNode  # Asegúrate de que estos nodos existan en my_ast.py
from ir_generator import IRGenerator
from optimizer import optimize_ir
from code_generator import CodeGenerator
import os
import linker

class CompilerApp:
    """Interfaz gráfica para el compilador."""
    def __init__(self, root):
        self.root = root
        self.root.title("Compiler")
        self.root.geometry("1000x800")
        self.root.config(bg="#2C3E50")
        
        # Variable para almacenar la ruta del archivo de entrada
        self.input_file_path = None
        
        # Crear elementos de la interfaz
        self.create_widgets()

    def create_widgets(self):
        # Título
        title_label = tk.Label(self.root, text="Compiler", bg="#2C3E50", fg="white", font=("Helvetica", 24, "bold"))
        title_label.pack(pady=20)

        # Input Code
        input_frame = tk.Frame(self.root, bg="#34495E", bd=2)
        input_frame.pack(pady=10, padx=20)
        tk.Label(input_frame, text="Enter the code to compile:", bg="#34495E", fg="white", font=("Arial", 14)).pack(anchor="w", padx=10, pady=5)
        self.input_text = scrolledtext.ScrolledText(input_frame, height=10, width=80, font=("Consolas", 12), bd=0, relief="flat")
        self.input_text.pack(padx=10, pady=5)

        # Buttons
        button_frame = tk.Frame(self.root, bg="#2C3E50")
        button_frame.pack(pady=20)
        compile_button = tk.Button(button_frame, text="Compile Code", command=self.compile_code, bg="#1ABC9C", fg="white", font=("Arial", 12, "bold"), width=18, bd=0, relief="flat")
        compile_button.grid(row=0, column=0, padx=10)
        file_button = tk.Button(button_frame, text="Load from File", command=self.load_file, bg="#3498DB", fg="white", font=("Arial", 12, "bold"), width=18, bd=0, relief="flat")
        file_button.grid(row=0, column=1, padx=10)
        # Eliminar el botón "Save Assembly" ya que se guarda automáticamente
        # save_button = tk.Button(button_frame, text="Save Assembly", command=self.save_assembly, bg="#E67E22", fg="white", font=("Arial", 12, "bold"), width=18, bd=0, relief="flat")
        # save_button.grid(row=0, column=2, padx=10)  # Comentar o eliminar estas líneas

        # IR Result
        ir_frame = tk.Frame(self.root, bg="#34495E", bd=2)
        ir_frame.pack(pady=10, padx=20)
        tk.Label(ir_frame, text="Intermediate Representation (IR):", bg="#34495E", fg="white", font=("Arial", 14)).pack(anchor="w", padx=10, pady=5)
        self.ir_text = scrolledtext.ScrolledText(ir_frame, height=10, width=80, font=("Consolas", 12), bd=0, relief="flat", state="disabled")
        self.ir_text.pack(padx=10, pady=5)

        # Assembly Result
        asm_frame = tk.Frame(self.root, bg="#34495E", bd=2)
        asm_frame.pack(pady=10, padx=20)
        tk.Label(asm_frame, text="Assembly Code:", bg="#34495E", fg="white", font=("Arial", 14)).pack(anchor="w", padx=10, pady=5)
        self.asm_text = scrolledtext.ScrolledText(asm_frame, height=10, width=80, font=("Consolas", 12), bd=0, relief="flat", state="disabled")
        self.asm_text.pack(padx=10, pady=5)

    
    def compile_code(self):
        """Compila el código ingresado y muestra el IR y el código ensamblador."""
        input_code = self.input_text.get("1.0", tk.END).strip() # Obtiene el codigo ingresado
        if not input_code: #En caso de que no se obtenga el codigo
            messagebox.showwarning("Warning", "The text field is empty.")
            return
        
        try:
            print("Starting compilation...")
            # Parsing y Generación del AST
            parser = build_parser()         # Crea el parser 
            ast = parser.parse(input_code)  # Crea el arbol de parseo con el  Parser 
            
            if ast is None: 
                raise Exception("Parsing failed. Please check your code for syntax errors.")
            
            print("AST generated successfully.")
            
            memory_manager = MemoryManager()
            symbol_table = SymbolTable(memory_manager)
            
            # Procesar todas las declaraciones y asignaciones en el AST
            self.process_statements(ast.statements, symbol_table)
            
            # Generación de IR
            ir_generator = IRGenerator()
            ir_generator.generate(ast)
            ir = ir_generator.instructions

            print("Original IR:")
            for instr in ir:
                print(instr)

            # Optimización
            optimized_ir = optimize_ir(ir.copy())
            print("IR optimized successfully.")
            print("Optimized IR:")
            for instr in optimized_ir:
                print(instr)

            # Mostrar IR optimizado
            ir_optimized_str = '\n'.join(str(instr) for instr in optimized_ir)
            self.display_ir(ir_optimized_str)

            # Generación de Código Ensamblador
            code_gen = CodeGenerator(optimized_ir, symbol_table, memory_manager)
            code_gen.translate()
            assembly_code = code_gen.get_assembly()
            self.display_assembly(assembly_code)
            print("Assembly code generated successfully.")

            # Guardar automáticamente el código ensamblador
            self.auto_save_assembly(assembly_code)

            #Genera el codigo objeto 
            lnkr=linker.Linker(symbol_table.scopes, assembly_code)
            code_obj = lnkr.generate_code_object()
            print(code_obj)
            
            #Ejecuta el codigo
            lnkr.simulate_execution()

        except Exception as e:
            print(f"Compilation Error: {str(e)}")
            messagebox.showerror("Compilation Error", str(e))

    def process_statements(self, statements, symbol_table):
        """Procesa una lista de declaraciones y asignaciones."""
        for stmt in statements:
            self.process_statement(stmt, symbol_table)

    def process_statement(self, stmt, symbol_table):
        """Procesa una sola declaración o asignación."""
        if isinstance(stmt, DeclaracionNode):
            symbol_table.declare(stmt.identifier, type='int', value=stmt.expression)
            print(f"Declared variable '{stmt.identifier}' with initial value {stmt.expression}.")
        elif isinstance(stmt, AssignNode):
            symbol_table.assign(stmt.identifier, stmt.expression)
            print(f"Assigned value {stmt.expression} to variable '{stmt.identifier}'.")
        elif isinstance(stmt, IfNode):
            print("Processing IfNode...")
            symbol_table.enter_scope()
            # Procesar la condición
            # Asumiendo que la condición ya está manejada en el IR
            # Procesar el bloque 'if'
            self.process_statements(stmt.if_block.statements, symbol_table)
            # Procesar el bloque 'else' si existe
            if stmt.else_block:
                self.process_statements(stmt.else_block.statements, symbol_table)
            symbol_table.exit_scope()
        else:
            raise Exception(f"Unknown statement type: {type(stmt).__name__}")

    def load_file(self):
        """Carga código desde un archivo."""
        self.input_file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if self.input_file_path:
            with open(self.input_file_path, 'r') as file:
                content = file.read()
                self.input_text.delete("1.0", tk.END)
                self.input_text.insert(tk.END, content)

    def display_ir(self, ir):
        """Muestra el código intermedio en la interfaz."""
        self.ir_text.config(state="normal")
        self.ir_text.delete("1.0", tk.END)
        self.ir_text.insert(tk.END, ir)
        self.ir_text.config(state="disabled")

    def display_assembly(self, asm):
        """Muestra el código ensamblador en la interfaz."""
        self.asm_text.config(state="normal")
        self.asm_text.delete("1.0", tk.END)
        self.asm_text.insert(tk.END, asm)
        self.asm_text.config(state="disabled")

    def auto_save_assembly(self, assembly_code):
        """Guarda automáticamente el código ensamblador en un archivo."""
        if self.input_file_path:
            base_name = os.path.splitext(os.path.basename(self.input_file_path))[0]
            default_filename = f"{base_name}.asm"
            default_dir = os.path.dirname(self.input_file_path)
        else:
            default_filename = "output.asm"
            default_dir = os.getcwd()  # Directorio actual

        # Construir la ruta completa
        file_path = filedialog.asksaveasfilename(defaultextension=".asm",
                                                 initialfile=default_filename,
                                                 initialdir=default_dir,
                                                 filetypes=[("Assembly files", "*.asm"), ("All files", "*.*")],
                                                 title="Save Assembly Code")
        if file_path:
            try:
                with open(file_path, 'w') as asm_file:
                    asm_file.write(assembly_code)
                messagebox.showinfo("Success", f"Assembly code saved successfully at:\n{file_path}")
                print(f"Assembly code saved at: {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save assembly code:\n{str(e)}")
                print(f"Failed to save assembly code: {str(e)}")
        else:
            messagebox.showwarning("Warning", "Assembly code was not saved.")
