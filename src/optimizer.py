# src/optimizer.py

def optimize_ir(ir):
    """Realiza optimizaciones simples en el IR."""
    optimized = []
    assigned = set()
    for instr in ir:
        if instr.op == 'assign':
            if instr.result in assigned:
                # Redundante, ya que se está reasignando
                continue
            assigned.add(instr.result)
        optimized.append(instr)
    return optimized
