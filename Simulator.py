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





