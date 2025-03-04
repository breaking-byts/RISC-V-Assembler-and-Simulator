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
    def execute(self,opcode,instruction):
        if opcode==0x33:
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
            rd=(instruction>>7)&0x1F;
            func3=(instruction>>12)&0x7;
            rs1=(instruction>>15)&0x1F;
            imm=(instruction>>20);
            if opcode==0b0000011:
                if func3==0b010:
                    self.registers[rd]=self.memory.read(self.registers[rs1]+imm);
            elif opcode==0b0010011:
                if func3==0b000:
                    self.registers[rd]=self.registers[rs1]+imm;
            elif opcode==0b1100111:
                if func3==0b000:
                    self.registers[rd]=self.pc+imm;
        elif opcode==0b1000011:
            #S type
            func3=(instruction>>12)&0x7;
            rs1=(instruction>>15)&0x1F;
            rs2=(instruction>>20)&0x1F;
            imm=(instruction>>25);
            if func3==0b010:
                self.memory.write(self.registers[rs1]+imm,self.registers[rs2]);
        elif opcode==0b1100011:
            #B type


        elif opcode==0b1101111:
            imm=(instruction>>20);
            self.memory.write(self.registers[rs1]+imm,self.registers[rs2]);












