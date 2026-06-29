# RISC-V Assembler and Simulator

A Python-based RISC-V RV32I assembler and simulator for learning computer organization and instruction set architecture concepts.

## 📋 Overview

This project implements a complete assembler and simulator for a subset of the RISC-V RV32I instruction set. It translates RISC-V assembly code into binary machine instructions and then executes those instructions on a simulated processor with a 32-register model and memory system.

**Perfect for:**
- Understanding instruction set architecture (ISA) fundamentals
- Learning how assemblers work
- Exploring CPU execution models
- Computer organization coursework

## ✨ Features

### Assembler (`assembler.py`)
- **Instruction Support:** R-type, I-type, S-type, B-type, and J-type instructions
- **Label Resolution:** Support for program labels and branch/jump targets
- **Register Support:** All 32 RISC-V registers plus ABI register names (x0-x31, zero, ra, sp, etc.)
- **Error Handling:** Comprehensive syntax validation and error reporting with line numbers
- **Immediate Value Handling:** 12-bit and 20-bit immediate value support with range checking
- **Output:** Binary machine code (32-bit instructions per line)

### Simulator (`Simulator.py`)
- **Register Model:** 32-register CPU with proper x0 (zero) register handling
- **Memory System:** Byte-addressed memory with 32-bit word operations
- **Instruction Execution:** Full decode-execute cycle for all supported instruction types
- **Trace Output:** Detailed execution trace showing PC and register state after each instruction
- **Data Memory Inspection:** Memory dump at program completion

## 🚀 Quick Start

### Prerequisites
- Python 3.x

### Installation

```bash
# Clone the repository
git clone https://github.com/breaking-byts/RISC-V-Assembler-and-Simulator.git
cd RISC-V-Assembler-and-Simulator
```

### Usage

#### Step 1: Assemble RISC-V Code
Create an assembly file (e.g., `program.asm`):

```assembly
addi t0, zero, 4
loop: addi s0, s0, 1
beq s0, t0, end
jal ra, loop
end: beq zero, zero, 0x00000000
```

Assemble it to binary:
```bash
python assembler.py program.asm output.txt
```

#### Step 2: Simulate Execution
Create a Python script to simulate:

```python
from Simulator import CPU, Memory

# Create memory (64KB)
memory = Memory(65536)

# Read binary program from assembler output
with open('output.txt', 'r') as f:
    program = []
    for line in f:
        line = line.strip()
        if line and not line.startswith('#'):
            program.append(int(line, 2).to_bytes(4, 'little'))

# Flatten program
program_bytes = b''.join(program)

# Initialize and run CPU
cpu = CPU()
cpu.memory = memory
memory.load_binaryprogram(program_bytes)

cpu.run('trace.txt')
```

## 📚 Supported Instructions

### R-Type (Register-Register Operations)
- `add rd, rs1, rs2` - Addition
- `sub rd, rs1, rs2` - Subtraction
- `and rd, rs1, rs2` - Bitwise AND
- `or rd, rs1, rs2` - Bitwise OR
- `slt rd, rs1, rs2` - Set Less Than
- `srl rd, rs1, rs2` - Shift Right Logical

### I-Type (Register-Immediate Operations)
- `addi rd, rs1, imm` - Add Immediate
- `lw rd, offset(rs1)` - Load Word
- `jalr rd, rs1, imm` - Jump and Link Register

### S-Type (Store Operations)
- `sw rs2, offset(rs1)` - Store Word

### B-Type (Conditional Branches)
- `beq rs1, rs2, label/offset` - Branch if Equal
- `bne rs1, rs2, label/offset` - Branch if Not Equal
- `blt rs1, rs2, label/offset` - Branch if Less Than

### J-Type (Unconditional Jumps)
- `jal rd, label/offset` - Jump and Link

### Special Instructions
- `beq zero, zero, 0x00000000` - Virtual Halt (required to end program)

## 📖 Assembly Examples

### Basic Loop
```assembly
# Initialize counter
addi s0, zero, 0      # s0 = 0
addi t0, zero, 10     # t0 = 10

loop:
addi s0, s0, 1        # s0 += 1
bne s0, t0, loop      # if s0 != t0, jump to loop

beq zero, zero, 0     # Halt
```

### Function Call (with JAL)
```assembly
jal ra, function      # Jump to function, save return address in ra

# Main program continues here
jal ra, end           # Jump to end

function:             # Function code here
jalr zero, ra, 0      # Return

end:
beq zero, zero, 0     # Halt
```

## 📝 Assembly Rules

1. **Labels:** Must start with an alphabetic character, no spaces, no duplicates
2. **Registers:** Use `x0-x31` or ABI names (e.g., `zero`, `ra`, `sp`, `t0`, `a0`)
3. **Immediates:** Decimal or hexadecimal (0x prefix) format
4. **Comments:** Use `#` to start line comments
5. **Virtual Halt:** Every program must end with `beq zero, zero, 0x00000000`
6. **Memory Addresses:** Use offset(register) format for loads/stores

## 🔧 Project Structure

```
RISC-V-Assembler-and-Simulator/
├── assembler.py       # Assembly parser and binary generator
├── Simulator.py       # CPU and memory simulation
├── Simulator_new.py   # Alternative simulator implementation
├── test.txt           # Example assembly code
├── output.txt         # Example assembler output
└── README.md          # This file
```

## 🎯 How It Works

### Assembler Pipeline
1. **Parsing:** Read assembly file, remove comments, identify labels
2. **Validation:** Check instruction syntax, register names, immediates
3. **Encoding:** Convert each instruction to 32-bit binary encoding based on RISC-V ISA
4. **Output:** Write binary instructions to output file

### Simulator Pipeline
1. **Fetch:** Load 32-bit instruction from memory at PC
2. **Decode:** Extract opcode and instruction type
3. **Execute:** Perform operation, update registers/memory
4. **Trace:** Record execution state for analysis

## 🧪 Testing

Run the provided test file:

```bash
python assembler.py test.txt output.txt
```

Check the output binary and trace files for correctness.

## 📋 Requirements

- Python 3.x
- File I/O capabilities
- No external dependencies

## 🤝 Contributing

Contributions are welcome! Areas for enhancement:
- Additional instruction types (M-extension, F-extension)
- Improved error messages
- Interactive debugger
- GUI simulator
- Performance optimizations

## 📄 License

This project is part of a computer organization learning initiative by the Breaking Bytes team.

## 🎓 Learning Resources

- [RISC-V Specification](https://riscv.org/)
- [RISC-V ISA Manual](https://github.com/riscv/riscv-isa-manual)
- Computer Organization textbooks covering assembly and ISA

## ⚠️ Known Limitations

- Supports only RV32I base integer instruction set
- Limited to 64KB memory
- No privilege level support
- No floating-point instructions
- No compressed instruction (C-extension) support

## 📧 Support

For issues or questions, please open an issue in the repository.

---

**Happy Learning! 🚀**
