class Memory:
    def __init__(self,size):
        self.size=size;
        self.memory=bytearray(size);

    def load_binaryprogram(self,program,start=0):
        if len(program)>self.size:
            raise Exception("Program too large for memory");
        else:
            self.memory[start:start+len(program)]=program;

    def read(self,address):
        if address<0 or address +4 > self.size:
            raise Exception("Invalid memory access");
        else:
            return int.from_bytes(self.memory[address:address+4],"little");
    def write(self,address,data):
        if address<0 or address +4 > self.size:
            raise Exception("Invalid memory access");
        else:
            self.memory[address:address+4]=data.to_bytes(4,"little");
class CPU:
    def __init__(self):
        self.registers=[0]*32;
        self.pc=0;
        self.memory=None;
        self.running=True;
    def fetch(self):
        instruction=self.memory.read(self.pc);
        self.pc+=4;
        return instruction;
    def decode(self,instruction):
        opcode=instruction & 0x7F;
        return opcode;
    def sign_extend(value, bits):
        if value & (1 << (bits - 1)):
            value -= 1 << bits
        return value

    def execute(self,opcode,instruction):
        if opcode==0x33:
            #R TYPE
              rd=(instruction>>7)&0x1F;
              func3=(instruction>>12)&0x7;
              rs1=(instruction>>15)&0x1F;
              rs2=(instruction>>20)&0x1F;
              func7=(instruction>>25)&0x7F
              if rd==0:
                  return ;
              if func3==0b000:
                  if func7==0b0000000:
                        self.registers[rd]=self.registers[rs1]+self.registers[rs2];
                  elif func7==0b0100000:
                        self.registers[rd]=self.registers[rs1]-self.registers[rs2];
              elif func3==0b010:
                    self.registers[rd]=int(self.registers[rs1]<self.registers[rs2]);
              elif func3==0b101:
                  shift_amount=self.registers[rs2]&0x1F;
                  self.registers[rd]=self.registers[rs1]>>shift_amount;
              elif func3==0b110:
                    self.registers[rd]=self.registers[rs1]|self.registers[rs2];
              elif func3==0b111:
                    self.registers[rd]=self.registers[rs1]&self.registers[rs2];
        elif (opcode==0b0000011 or opcode==0b0010011 or opcode==0b1100111):
            #I type
            rd=(instruction>>7)&0x1F;
            func3=(instruction>>12)&0x7;
            rs1=(instruction>>15)&0x1F;
            imm= self.sign_extend(instruction >> 20, 12)
            if opcode==0b0000011:#
                if func3==0b010:
                    addr = self.registers[rs1] + imm
                    self.registers[rd] = self.memory.read(addr)
            elif opcode==0b0010011:
                if func3==0b000:
                    self.registers[rd]=self.registers[rs1]+imm;
            elif opcode==0b1100111:
                if func3==0b000:
                    next_pc = self.pc
                    self.pc = (self.registers[rs1] + imm) & ~1
                    self.registers[rd] = next_pc
        elif opcode==0b0100011:
            #S type
            func3 = (instruction >> 12) & 0x7
            rs1 = (instruction >> 15) & 0x1F
            rs2 = (instruction >> 20) & 0x1F
            imm = ((instruction >> 25) << 5) | ((instruction >> 7) & 0x1F)
            imm = self.sign_extend(imm, 12)
            if func3 == 0b010:  # SW
                addr = self.registers[rs1] + imm
                self.memory.write(addr, self.registers[rs2])
        elif opcode==0b1100011:
            #B type
            func3 = (instruction >> 12) & 0x7
            rs1 = (instruction >> 15) & 0x1F
            rs2 = (instruction >> 20) & 0x1F
            # Immediate for branch instructions:
            imm = (((instruction >> 31) & 0x1) << 12) | \
                  (((instruction >> 25) & 0x3F) << 5) | \
                  (((instruction >> 8) & 0xF) << 1) | \
                  (((instruction >> 7) & 0x1) << 11)
            imm = self.sign_extend(imm, 13)

            if func3 == 0b000:  # BEQ
                if self.registers[rs1] == self.registers[rs2]:
                                 self.pc = self.pc - 4 + imm
            elif func3 == 0b001:  # BNE
                if self.registers[rs1] != self.registers[rs2]:
                                  self.pc = self.pc - 4 + imm
            elif func3 == 0b100:  # BLT
                if self.registers[rs1] < self.registers[rs2]:
                                 self.pc = self.pc - 4 + imm;

        elif opcode==0b1101111:
            #J TYPE
            rd = (instruction >> 7) & 0x1F
            # Immediate for JAL:
            imm = (((instruction >> 31) & 0x1) << 20) | \
                  (((instruction >> 21) & 0x3FF) << 1) | \
                  (((instruction >> 20) & 0x1) << 11) | \
                  (((instruction >> 12) & 0xFF) << 12)
            imm = self.sign_extend(imm, 21)
            next_pc = self.pc
            self.registers[rd] = next_pc
            self.pc = self.pc - 4 + imm
    def print_trace(self, file_handle):
        line = f"{self.pc}"
        for reg in self.registers:
            line += " " + f"{reg}"
        file_handle.write(line + "\n")

    def run(self, trace_filename="trace.txt"):
        with open(trace_filename, "w") as f:
            header = "PC"
            for i in range(32):
                header += " x" + str(i)
            f.write(header + "\n")
            while self.running:
                try:
                    instruction = self.fetch()
                except Exception as e:
                    self.running = False
                    break
                opcode = self.decode(instruction)
                self.execute(opcode, instruction)
                self.print_trace(f)
            f.write("Data Memory\n")
            for addr in range(0x00010000, 0x00010080, 4):
                try:
                    word = self.memory.read(addr)
                except Exception:
                    word = 0
                f.write(f"0x{addr:08X}:{word}\n")












