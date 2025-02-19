class Assembler:
    def __init__(self):
        self.R_TYPE = 0
        self.I_TYPE = 1
        self.S_TYPE = 2
        self.B_TYPE = 3
        self.U_TYPE = 4
        self.J_TYPE = 5
        self.opcodes = {
            'sw': '0100011',
            'beq': '1100011',
            'bne': '1100011',
            'blt': '1100011',
            'jal': '1101111',
            'addi': '0010011',
            'rst': '0000000',
            'halt': '0000000',
            'rvrs': '0000000',
            'add': '0110011',
            'sub': '0110011',
            'slt': '0110011',
            'srl': '0110011',
            'or': '0110011',
            'and': '0110011',
            'lw': '0000011',
            'jalr': '1100111'
        }
        self.func3 = {
            'add': '000',
            'sub': '000',
            'slt': '010',
            'srl': '101',
            'or': '110',
            'and': '111',
            'sw': '010',
            'beq': '000',
            'bne': '001',
            'blt': '100',
            'rst': '000',
            'halt': '000',
            'rvrs': '000',
            'lw': '010',
            'addi': '000',
            'jalr': '000'
        }
        self.registers = {
            'x0': '00000',
            'x1': '00001',
            'x2': '00010',
            'x3': '00011',
            'x4': '00100',
            'x5': '00101',
            'x6': '00110',
            'x7': '00111',
            'x8': '01000',
            'x9': '01001',
            'x10': '01010',
            'x11': '01011',
            'x12': '01100',
            'x13': '01101',
            'x14': '01110',
            'x15': '01111',
            'x16': '10000',
            'x17': '10001',
            'x18': '10010',
            'x19': '10011',
            'x20': '10100',
            'x21': '10101',
            'x22': '10110',
            'x23': '10111',
            'x24': '11000',
            'x25': '11001',
            'x26': '11010',
            'x27': '11011',
            'x28': '11100',
            'x29': '11101',
            'x30': '11110',
            'x31': '11111'
        }
        self.abi_registers = {
            'zero': 'x0',
            'ra': 'x1',
            'sp': 'x2',
            'gp': 'x3',
            'tp': 'x4',
            't0': 'x5',
            't1': 'x6',
            't2': 'x7',
            's0': 'x8',
            'fp': 'x8',
            's1': 'x9',
            'a0': 'x10',
            'a1': 'x11',
            'a2': 'x12',
            'a3': 'x13',
            'a4': 'x14',
            'a5': 'x15',
            'a6': 'x16',
            'a7': 'x17',
            's2': 'x18',
            's3': 'x19',
            's4': 'x20',
            's5': 'x21',
            's6': 'x22',
            's7': 'x23',
            's8': 'x24',
            's9': 'x25',
            's10': 'x26',
            's11': 'x27',
            't3': 'x28',
            't4': 'x29',
            't5': 'x30',
            't6': 'x31'
        }
        self.PROGRAM_MEMORY_START = 0x00000000
        self.PROGRAM_MEMORY_END = 0x000000FF
        self.STACK_MEMORY_START = 0x00000100
        self.STACK_MEMORY_END = 0x0000017F
        self.DATA_MEMORY_START = 0x00010000
        self.DATA_MEMORY_END = 0x0001007F

        self.program_memory = [0] * 64
        self.stack_memory = [0] * 32
        self.data_memory = [0] * 32

    def get_line_number(self):
        return self.current_line

    def text_parser(self, file_name):
        self.labels = {}
        self.current_address = 0
        self.instructions = []
        has_halt = False
        try:
            with open(file_name, 'r') as file:
                text = file.read()
                lines = text.split('\n')
                line_num = 1
                for line in lines:
                    # Remove comments and whitespace
                    self.current_line = line_num
                    line = line.split('#')[0].strip()
                    if not line:
                        line_num += 1
                        continue
                    # Handle labels
                    if ':' in line:
                        label_parts = line.split(':')
                        label = label_parts[0].strip()
                        # Add these new validations
                        if label in self.opcodes:
                            raise SyntaxError(f"Line {line_num}: Label '{label}' cannot be an instruction name")
                        if label in self.registers or label in self.abi_registers:
                            raise SyntaxError(f"Line {line_num}: Label '{label}' cannot be a register name")
                        if not label[0].isalpha():
                            raise SyntaxError(f"Line {line_num}: Label must start with an alphabet")
                        if " " in label:
                            raise SyntaxError(f"Line {line_num}: Label must not contain any spaces")
                        if label in self.labels:
                            raise SyntaxError(f"Line {line_num}: Label {label} is duplicate")
                        self.labels[label] = self.current_address
                        line = label_parts[1].strip()
                        if not line:
                            line_num += 1
                            continue
                    # Process instruction
                    a, b = line.split(" ")
                    parts = [a] + b.split(",")
                    if not parts:
                        line_num += 1
                        continue
                    opcode = self.opcodes.get(parts[0])
                    if opcode is None:
                        raise SyntaxError(f"Line {line_num}: Opcode {parts[0]} is invalid")
                    if parts[0] == 'beq' and len(parts) == 4:
                        if parts[1] == 'zero' and parts[2] == 'zero' and parts[3] == '0x00000000':
                            has_halt = True
                            if self.current_address != len(self.instructions) * 4:
                                raise SyntaxError("Virtual Halt must be the last instruction")
                    # Validate registers and immediates
                    for reg in parts[1:]:
                        if reg in self.abi_registers:
                            continue
                        if '0x' in reg:
                            try:
                                imm = int(reg, 16)
                                if imm > 0x7FF or imm < -0x800:
                                    raise SyntaxError(f"Line {line_num}: Immediate value out of range: {reg}")
                            except ValueError:
                                raise SyntaxError(f"Line {line_num}: Invalid immediate value: {reg}")

                    self.instructions.append((parts, self.current_address, line_num))
                    self.current_address += 4
                    line_num += 1
                # if not has_halt:
                # raise SyntaxError("Missing Virtual Halt instruction (beq zero,zero,0x00000000)")
                return self.instructions
        except FileNotFoundError:
            raise FileNotFoundError(f"Assembly file not found: {file_name}")
        except IOError:
            raise IOError(f"Error reading file: {file_name}")

    def reg_to_binary(self, reg):
        if reg in self.abi_registers:
            reg = self.abi_registers[reg]
        if reg in self.registers:
            return self.registers[reg]
        else:
            raise ValueError(f"Line {self.get_line_number()}: Invalid register: {reg}")

    def get_immediate_binary(self, imm_str, bits, signed=True):
        try:
            if '0x' in imm_str:
                imm = int(imm_str, 16)
            else:
                imm = int(imm_str)
            max_val = (2 ** (bits - 1)) - 1 if signed else (2 ** bits) - 1
            min_val = -(2 ** (bits - 1)) if signed else 0
            if imm > max_val or imm < min_val:
                raise ValueError(f"Line {self.get_line_number()}: Immediate value {imm} out of range for {bits} bits")
            if imm < 0:
                imm = (2 ** bits) + imm
            return format(imm % (2 ** bits), f'0{bits}b')
        except ValueError:
            raise ValueError(f"Line {self.get_line_number()}: Invalid immediate value: {imm_str}")

    def get_branch_offset(self, label, current_address):
        if label not in self.labels:
            raise ValueError(f"Line {self.get_line_number()}: Undefined label: {label}")
        # Calculate offset in instructions (divide by 4 since each instruction is 4 bytes)
        offset = (self.labels[label] - current_address) >> 2
        return self.get_immediate_binary(str(offset), 12, signed=True)

    def get_jump_offset(self, label, current_address):
        if label not in self.labels:
            raise ValueError(f"Line {self.get_line_number()}: Undefined label: {label}")
        # Calculate offset in instructions (divide by 4 since each instruction is 4 bytes)
        offset = (self.labels[label] - current_address) >> 2
        return self.get_immediate_binary(str(offset), 20, signed=True)

    def I_type(self, instruction):
        if len(instruction) != 3 and len(instruction) != 4:
            raise SyntaxError(
                f"Line {self.get_line_number()}: Invalid number of arguments for I-type instruction: {instruction}")
        opcode = self.opcodes[instruction[0]]
        rd = self.reg_to_binary(instruction[1])
        if len(instruction) == 3:
            mem_addr = instruction[2]
            if '(' not in mem_addr or ')' not in mem_addr:
                raise SyntaxError(f"Line {self.get_line_number()}: Invalid memory address format: {mem_addr}")
            offset = mem_addr[:mem_addr.find('(')]
            rs1 = mem_addr[mem_addr.find('(') + 1:mem_addr.find(')')]
            rs1 = self.reg_to_binary(rs1)
            imm = self.get_immediate_binary(offset if offset else '0', 12)
        else:
            rs1 = self.reg_to_binary(instruction[2])
            imm = self.get_immediate_binary(instruction[3], 12)
        func3 = self.func3[instruction[0]]
        binary = f"{imm}{rs1}{func3}{rd}{opcode}"
        return binary

    def R_type(self, instruction):
        if len(instruction) != 4:
            raise SyntaxError(
                f"Line {self.get_line_number()}: Invalid number of arguments for R-type instruction: {instruction}")
        opcode = self.opcodes[instruction[0]]
        rd = self.reg_to_binary(instruction[1])
        rs1 = self.reg_to_binary(instruction[2])
        rs2 = self.reg_to_binary(instruction[3])
        func3 = self.func3[instruction[0]]
        if instruction[0] == 'sub':
            func7 = '0100000'
        else:
            func7 = '0000000'
        binary = f"{func7}{rs2}{rs1}{func3}{rd}{opcode}"
        return binary

    def B_type(self, instruction):
        if len(instruction) != 4:
            raise SyntaxError(
                f"Line {self.get_line_number()}: Invalid number of arguments for B-type instruction: {instruction}")
        opcode = self.opcodes[instruction[0]]
        rs1 = self.reg_to_binary(instruction[1])
        rs2 = self.reg_to_binary(instruction[2])
        func3 = self.func3[instruction[0]]

        # Get the current instruction's address from self.instructions
        current_instr_addr = None
        for instr, addr, _ in self.instructions:
            if instr == instruction:
                current_instr_addr = addr
                break

        if instruction[3].startswith('0x') or instruction[3].isdigit() or instruction[3].startswith('-'):
            imm = self.get_immediate_binary(instruction[3], 12)
        else:
            imm = self.get_branch_offset(instruction[3], current_instr_addr)

        binary = f"{imm[0]}{imm[2:8]}{rs2}{rs1}{func3}{imm[8:12]}{imm[1]}{opcode}"
        return binary

    def J_type(self, instruction):
        if len(instruction) != 3:
            raise SyntaxError(
                f"Line {self.get_line_number()}: Invalid number of arguments for J-type instruction: {instruction}")
        opcode = self.opcodes[instruction[0]]
        rd = self.reg_to_binary(instruction[1])

        # Get the current instruction's address from self.instructions
        current_instr_addr = None
        for instr, addr, _ in self.instructions:
            if instr == instruction:
                current_instr_addr = addr
                break

        if instruction[2].startswith('0x') or instruction[2].isdigit() or instruction[2].startswith('-'):
            imm = self.get_immediate_binary(instruction[2], 20)
        else:
            imm = self.get_jump_offset(instruction[2], current_instr_addr)

        binary = f"{imm[0]}{imm[10:20]}{imm[9]}{imm[1:9]}{rd}{opcode}"
        return binary

    def U_type(self, instruction):
        if len(instruction) != 3:
            raise SyntaxError(
                f"Line {self.get_line_number()}: Invalid number of arguments for U-type instruction: {instruction}")
        opcode = self.opcodes[instruction[0]]
        rd = self.reg_to_binary(instruction[1])
        imm = self.get_immediate_binary(instruction[2], 20)
        binary = f"{imm}{rd}{opcode}"
        return binary

    def S_type(self, instruction):
        if len(instruction) != 3:
            raise SyntaxError(
                f"Line {self.get_line_number()}: Invalid number of arguments for S-type instruction: {instruction}")
        opcode = self.opcodes[instruction[0]]
        rs2 = self.reg_to_binary(instruction[1])
        mem_addr = instruction[2]
        if '(' not in mem_addr or ')' not in mem_addr:
            raise SyntaxError(f"Line {self.get_line_number()}: Invalid memory address format: {mem_addr}")
        offset = mem_addr[:mem_addr.find('(')]
        rs1 = mem_addr[mem_addr.find('(') + 1:mem_addr.find(')')]
        rs1 = self.reg_to_binary(rs1)
        imm = self.get_immediate_binary(offset if offset else '0', 12)
        imm1 = imm[:7]
        imm2 = imm[7:]
        func3 = self.func3[instruction[0]]
        binary = f"{imm1}{rs2}{rs1}{func3}{imm2}{opcode}"
        return binary


def _test():
    assembler = Assembler()
    try:
        instructions = assembler.text_parser('test.txt')
        for instruction, _, line_num in instructions:
            assembler.current_line = line_num
            binary = None
            if instruction[0] in ['add', 'sub', 'and', 'or', 'slt', 'srl']:
                binary = assembler.R_type(instruction)
            elif instruction[0] in ['addi', 'lw', 'jalr']:
                binary = assembler.I_type(instruction)
            elif instruction[0] == 'sw':
                binary = assembler.S_type(instruction)
            elif instruction[0] in ['beq', 'bne', 'blt']:
                binary = assembler.B_type(instruction)
            elif instruction[0] == 'jal':
                binary = assembler.J_type(instruction)
            if binary:
                with open('output.txt', 'a') as f:
                    f.write(f"{binary}\n")
                print(f"{binary}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    _test()

