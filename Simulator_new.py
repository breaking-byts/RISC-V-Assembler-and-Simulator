import sys
class CPU:
    def __init__(self): 
        self.regs = [0] * 32  # Register file (32 registers)
        self.regs[2] = 380
        self.pc = 0  # Program counter
        self.memory = None 
        self.running = True  # Execution status

    def fetch(self):  # Fetch instruction from memory
        instruction = self.memory.read(self.pc)
        self.pc += 4  # Move to next instruction
        return instruction

    def decode(self, instruction):  # Decode instruction to get the opcode
        if instruction is None:
            return None
        opcode = f"{instruction:032b}"
        return opcode[-7:]  # Extract the last 7 bits (opcode)

    def sign_extend(self, value, bits):  # Sign-extend immediate values
        num = int(value, 2)
        sign_bit = 1 << (bits - 1)
        if (num & sign_bit) != 0:
            num -= (1 << bits)
        return num

    def execute(self, opcode, instruction):  # Execute instruction based on opcode
        if opcode is None or instruction is None:
            self.running = False
            return

        # Halt execution on special halt instruction
        if instruction == 0b00000000000000000000000001100011:
            self.running = False
            self.pc -= 4
            return

        i_str = f"{instruction:032b}"

        # R-type instructions (register operations)
        if opcode == "0110011":
            rd = int(i_str[20:25], 2)
            func3 = i_str[17:20]
            rs1 = int(i_str[12:17], 2)
            rs2 = int(i_str[7:12], 2)
            func7 = i_str[0:7]
            val1 = self.regs[rs1]
            val2 = self.regs[rs2]
            result = 0

            if func3 == "000":
                if func7 == "0000000":  # ADD
                    result = val1 + val2
                elif func7 == "0100000":  # SUB
                    result = val1 - val2
            elif func3 == "001":  # SLL (Shift Left Logical)
                shift_amount = val2 & 0b11111
                result = val1 << shift_amount
            elif func3 == "010":  # SLT (Set Less Than)
                result = 1 if val1 < val2 else 0
            elif func3 == "110":  # OR
                result = val1 | val2
            elif func3 == "111":  # AND
                result = val1 & val2

            if rd != 0:  # Do not modify register 0
                self.regs[rd] = result & 0xFFFFFFFF

        # I-type instructions (immediate and load)
        elif opcode in ["0000011", "0010011", "1100111"]:
            rd = int(i_str[20:25], 2)
            func3 = i_str[17:20]
            rs1 = int(i_str[12:17], 2)
            imm = self.sign_extend(i_str[0:12], 12)

            if opcode == "0000011":  # LW (Load Word)
                addr = self.regs[rs1] + imm
                if func3 == "010":
                    data = self.memory.read(addr)
                    if rd != 0:
                        self.regs[rd] = data

            elif opcode == "0010011":  # ADDI (Add Immediate)
                val1 = self.regs[rs1]
                result = val1 + imm
                if rd != 0:
                    self.regs[rd] = result & 0xFFFFFFFF

            elif opcode == "1100111":  # JALR (Jump and Link Register)
                current_pc = self.pc - 4
                next_pc = self.pc
                target = ((self.regs[rs1] + imm) // 2) * 2
                self.pc = target
                if rd != 0:
                    self.regs[rd] = next_pc & 0xFFFFFFFF

        # S-type instruction (store)
        elif opcode == "0100011":
            func3 = i_str[17:20]
            rs1 = int(i_str[12:17], 2)
            rs2 = int(i_str[7:12], 2)
            imm_s = i_str[0:7] + i_str[20:25]
            imm = self.sign_extend(imm_s, 12)
            addr = self.regs[rs1] + imm
            data = self.regs[rs2]
            if func3 == "010":
                self.memory.write(addr, data)

        # B-type instructions (branch)
        elif opcode == "1100011":
            func3 = i_str[17:20]
            rs1 = int(i_str[12:17], 2)
            rs2 = int(i_str[7:12], 2)
            imm_b = i_str[0] + i_str[24] + i_str[1:7] + i_str[20:24] + "0"
            imm = self.sign_extend(imm_b, 13)
            current_pc = self.pc - 4
            val1 = self.regs[rs1]
            val2 = self.regs[rs2]
            taken = False

            if func3 == "000":  # BEQ (Branch if Equal)
                taken = (val1 == val2)
            elif func3 == "001":  # BNE (Branch if Not Equal)
                taken = (val1 != val2)

            if taken:
                self.pc = current_pc + I'm
# J-type (jump)
        elif opcode == "1101111":  # JAL (Jump and Link)
            rd = int(i_str[20:25], 2)
            imm_j = i_str[0] + i_str[12:20] + i_str[11] + i_str[1:11] + "0"
            imm = self.sign_extend(imm_j, 21)
            current_pc = self.pc - 4
            next_pc_val = self.pc
            self.pc = current_pc + imm
            if rd != 0:
                self.regs[rd] = next_pc_val & 0xFFFFFFFF

class Memory:
    def __init__(self, size):  # Initialize memory with a given size
        self.size = size
        self.memory = bytearray(size)

    def load_binaryprogram(self, program, start=0):  # Load a binary program
        self.memory[start:start + len(program)] = program

    def read(self, address):  # Read a 4-byte word from memory
        return int.from_bytes(self.memory[address:address + 4], "little", signed=False)

    def write(self, address, data):  # Write a 4-byte word to memory
        self.memory[address:address + 4] = data.to_bytes(4, "little", signed=False)

def dec_to_bin(num):  # Convert decimal to binary (32-bit)
    mask = 1 << 31
    result = ""
    for _ in range(32):
        result += "1" if num & mask else "0"
        mask //= 2
    return int(result, 2)
def simulate(instructions):  # Main simulation function
    cpu = CPU()
    cpu.memory = Memory(1024 * 128)  # Initialize memory (128KB)
    program_bytes = bytearray()

    for instr in instructions:  # Convert instructions to bytes
        program_bytes.extend(instr.to_bytes(4, 'little', signed=False))
    
    cpu.memory.load_binaryprogram(program_bytes)

    max_cycles = 1000
    cycles = 0

    with open(sys.argv[2], "w") as f:  # Write execution trace
        while cpu.running and cycles < max_cycles:
            instruction = cpu.fetch()
            opcode = cpu.decode(instruction)
            cpu.execute(opcode, instruction)

            # Write state to file
            f.write(f"0b{cpu.pc:032b} ")
            for i in cpu.regs:
                f.write(f"0b{i:032b} ")
            f.write("\n")

            cycles += 1

# Read binary instructions from file and run simulation
with open(sys.argv[1], "r") as f:
    instructions = [int(line, 2) for line in f]
simulate(instructions)
