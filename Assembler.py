from fileinput import lineno


class Assembler:
    def __init__(self):
        self.R_TYPE = 0
        self.I_TYPE = 1
        self.S_TYPE = 2
        self.B_TYPE = 3
        self.U_TYPE=  4
        self.J_TYPE = 5
        self.opcodes = {
            'sw':     '0100011',
            'beq':    '1100011',
            'bne':    '1100011',
            'blt':    '1100011',
            'jal':    '1101111',
            'addi':   '0010011',
            'rst':    '0000000',
            'halt':   '0000000',
            'rvrs':   '0000000',
            'add':    '0110011',
            'sub':    '0110011',
            'slt':    '0110011',
            'srl':    '0110011',
            'or':     '0110011',
            'and':    '0110011',
            'lw':     '0000011',
            'jalr':   '1100111'
            }
        self.func3={
            'add': '000',
            'sub': '000',
            'slt': '010',
            'srl': '101',
            'or':  '110',
            'and': '111',
            'sw':  '010',
            'beq': '000',
            'bne': '001',
            'blt': '100',
            'rst': '000',
            'halt': '000',
            'rvrs': '000',
            'lw':   '010',
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

    def text_parser(self, file_name):

        #Parses an assembly language text file and converts it into machine instructions.
        #Returns:List of tuples containing parsed instructions and their addresses
        # It raises errors such as
        #    1)Filenotfounderror - if input file does not exist
        #    2)IOError - if there is an error reading the file
        #    3)SyntaxError - if there are syntax errors in assembly code


        self.labels = {}   # Dictionary to store label names and their addresses
        self.current_address = 0  # Tracks the current instruction address (increments by 4 each instruction)
        self.instructions = []    # List to store parsed instructions
        has_halt = False   # Flag to check if the program has a halt instruction

        try:
            with open(file_name, 'r') as file:  #opens and reads the assembly file
                text = file.read()
                lines = text.split('\n')
                line_num = 1

                for line in lines: # processes each line in file
                    # Remove comments and whitespace
                    line = line.split('#')[0].strip()
                    if not line:
                        line_num += 1
                        continue

                    # Handle labels containing ":"
                    if ':' in line:
                        label_parts = line.split(':')
                        label = label_parts[0].strip()

                        if not label[0].isalpha():
                            raise SyntaxError(f"Line {line_num}: Label must start with an alphabet")
                        if " " in label:
                            raise SyntaxError(f"Line {line_num}: Label must not contain any spaces")
                        if label in self.labels:
                            raise SyntaxError(f"Line {line_num}: Label {label} is duplicate")

                        self.labels[label] = self.current_address  #store label and its address

                        # Get remainder of line after label (if any)
                        line = label_parts[1].strip()
                        if not line:  # Skip if no instruction after label
                            line_num += 1
                            continue

                    # Process instruction which splits instruction into opcode and operands
                    a,b= line.split(" ")
                    parts = [a]+b.split(",")

                    if not parts:      # Skip if no valid instruction parts
                        line_num += 1
                        continue

                    # validate opcode
                    opcode = self.opcodes.get(parts[0])
                    if opcode is None:
                        raise SyntaxError(f"Line {line_num}: Opcode {parts[0]} is invalid")

                    if parts[0] == 'beq' and len(parts) == 4:
                        if parts[1] == 'zero' and parts[2] == 'zero' and parts[3] == '0x00000000':
                            has_halt = True
                            # ensure that halt is the last instruction
                            if self.current_address != len(self.instructions) * 4:
                                raise SyntaxError("Virtual Halt must be the last instruction")

                    # Validate registers and immediates
                    for reg in parts[1:]:
                        if reg in self.abi_registers:
                            continue
                        if '0x' in reg:  # check if its a hexadecimal immediate value
                            try:
                                imm = int(reg, 16)
                                # Validate immediate value is within valid range (-0x800 to 0x7FF)
                                if imm > 0x7FF or imm < -0x800:
                                    raise SyntaxError(f"Line {line_num}: Immediate value out of range: {reg}")
                            except ValueError:
                                raise SyntaxError(f"Line {line_num}: Invalid immediate value: {reg}")

                    # store instruction with its address
                    self.instructions.append((parts, self.current_address))
                    self.current_address += 4
                    line_num += 1

               #if not has_halt:
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
                raise ValueError( f "Invalid register: {reg}")

    def get_immediate_binary(self, imm_str, bits, signed=True):
            try:
                if '0x' in imm_str:
                    imm = int(imm_str, 16)
                else:
                    imm = int(imm_str)
                max_val = (2 ** (bits - 1)) - 1 if signed else (2 ** bits) - 1
                min_val = -(2 ** (bits - 1)) if signed else 0
                if imm > max_val or imm < min_val:
                    raise ValueError(f"Immediate value {imm} out of range for {bits} bits")

                if imm < 0:
                    imm = (2 ** bits) + imm

                return format(imm % (2 ** bits), f'0{bits}b')
            except ValueError:
                raise ValueError(f"Invalid immediate value: {imm_str}")

    def get_branch_offset(self, label, current_address):
            if label not in self.labels:
                raise ValueError(f"Undefined label: {label}")
            offset = self.labels[label] - current_address
            return self.get_immediate_binary(str(offset), 12, signed=True)

    def get_jump_offset(self, label, current_address):
            if label not in self.labels:
                raise ValueError(f"Undefined label: {label}")
            offset = self.labels[label] - current_address
            return self.get_immediate_binary(str(offset), 20, signed=True)

    def S_type(self, instruction):
        if len(instruction) != 3:
            raise SyntaxError(f"Invalid number of arguments for S-type instruction: {instruction}")
        opcode = self.opcodes[instruction[0]]
        rs2 = self.reg_to_binary(instruction[1])
        mem_addr = instruction[2]
        if '(' not in mem_addr or ')' not in mem_addr:
            raise SyntaxError(f"Invalid memory address format: {mem_addr}")

        offset = mem_addr[:mem_addr.find('(')]
        rs1 = mem_addr[mem_addr.find('(') + 1:mem_addr.find(')')]
        rs1 = self.reg_to_binary(rs1)
        imm = self.get_immediate_binary(offset if offset else '0', 12)

        imm1 = imm[:7]
        imm2 = imm[7:]

        func3 = self.func3[instruction[0]]
        binary = f"{imm1}{rs2}{rs1}{func3}{imm2}{opcode}"
        return binary

    def J_type(self, instruction):
        if len(instruction) != 3:
            raise SyntaxError(f"Invalid number of arguments for J-type instruction: {instruction}")
        opcode = self.opcodes[instruction[0]]
        rd = self.reg_to_binary(instruction[1])
        imm = self.get_jump_offset(instruction[2], 0)
        binary = f"{imm[0]}{imm[10:20]}{imm[9]}{imm[1:9]}{rd}{opcode}"
        return binary

