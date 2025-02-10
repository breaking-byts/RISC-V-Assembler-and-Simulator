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
            'rvrs':   '0000000'
        }
        self.func3={
            'sw': '010',
            'beq': '000',
            'bne': '001',
            'blt': '100',
            'addi': '000',
            'rst': '000',
            'halt': '000',
            'rvrs': '000'
        }
        self.a=2


