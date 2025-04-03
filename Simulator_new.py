import sys
class CPU:
 def __init__(self):
     self.regs=[0]*32 #Register file
     self.regs[2]=380
     self.pc=0 #Program counter
     self.memory=None # Memory reference
     self.running=True # Execution status

 def fetch(self):
      instruction=self.memory.read(self.pc)
      self.pc+=4
      return instruction

 def decode(self,instruction):
     if instruction is None:
        return None
     opcode=f"{instruction:032b}"
     return opcode[-7:] #Extract last 7 digits for opcode

 def sign_extend(self,value,bits): #Sign extension of imm
     num=int(value,2)
     sign_bit=1<<(bits-1)
     if (num&sign_bit)!=0:
          num-=(1<<bits)
     return num

 def execute(self,opcode,instruction):
     if opcode is None or instruction is None: 
       self.running=False
       return
     if instruction==0b00000000000000000000000001100011:
       self.running=False
       self.pc-=4
       return
     i_str=f"{instruction:032b}"
     if opcode=="0110011": #R-type
           rd=int(i_str[20:25],2)
           func3=i_str[17:20]
           rs1=int(i_str[12:17],2)
           rs2=int(i_str[7:12],2)
           func7=i_str[0:7]
           val1=self.regs[rs1]
           val2=self.regs[rs2]
           result=0
           if func3=="000":
               if func7=="0000000": #Add
                     result=val1+val2
               elif func7=="0100000": #Sub
                     result=val1-val2
           elif func3=="001": #SRL
               shift_amount=val2&0b11111
               result=val1<<shift_amount
           elif func3=="010": #SLT
                 result=1 if val1<val2 else 0
           elif func3=="110": #OR
                 result=val1|val2
           elif func3=="111": #AND
                 result=val1&val2
           if rd!=0:
               self.regs[rd]=result&0xFFFFFFFF

     elif (opcode=="0000011" or opcode=="0010011" or opcode=="1100111"): #I-type
         rd=int(i_str[20:25],2)
         func3=i_str[17:20]
         rs1=int(i_str[12:17],2)
         imm=self.sign_extend(i_str[0:12],12)
         if opcode=="0000011": #lw
             addr=self.regs[rs1]+imm
             if func3=="010":
                  data=self.memory.read(addr) #extracting at data at memory address
                  if rd!=0:
                     self.regs[rd]=data
         elif opcode=="0010011": #addi
             val1=self.regs[rs1]
             result=0
             if func3=="000":
                 result=val1+imm
             if rd!=0:
                 self.regs[rd]=result&0xFFFFFFFF
         elif opcode=="1100111": #jalr
             current_pc=self.pc-4
             next_pc=self.pc
             target=((self.regs[rs1]+imm)//2)*2
             self.pc=target
             if rd!=0:
                self.regs[rd]=next_pc&0xFFFFFFFF

     elif opcode=="0100011": #Sw
          func3=i_str[17:20]
          rs1=int(i_str[12:17],2)
          rs2=int(i_str[7:12],2)
          imm_s=i_str[0:7]+i_str[20:25]
          imm=self.sign_extend(imm_s,12)
          addr=self.regs[rs1]+imm
          data=self.regs[rs2]
          if func3=="010":
              self.memory.write(addr,data) #writing at address the data


     elif opcode=="1100011": #B-Type
         func3=i_str[17:20]
         rs1=int(i_str[12:17],2)
         rs2=int(i_str[7:12],2)
         imm_b=i_str[0]+i_str[24]+i_str[1:7]+i_str[20:24]+"0"
         imm=self.sign_extend(imm_b,13)
         current_pc=self.pc-4
         val1=self.regs[rs1]
         val2=self.regs[rs2]
         taken=False
         if func3=="000": #BEQ
             taken=(val1==val2)
         elif func3=="001": #BNE
             taken=(val1!=val2)
         if taken:
              self.pc=current_pc+imm

     elif opcode=="1101111": #jal
          rd=int(i_str[20:25],2)
          imm_j=i_str[0]+i_str[12:20]+i_str[11]+i_str[1:11]+"0"
          imm=self.sign_extend(imm_j,21)
          current_pc=self.pc-4
          next_pc_val=self.pc
          self.pc=current_pc+imm
          if rd!=0:
              self.regs[rd]=next_pc_val&0xFFFFFFFF

class Memory:
    def __init__(self,size):
        self.size=size #initialize memory with the given size
        self.memory=bytearray(size)
    def load_binaryprogram(self,program,start=0): # Load a binary program
        self.memory[start:start+len(program)]=program
    def read(self,address):  # Read a 4-byte word from memory
        return int.from_bytes(self.memory[address:address+4],"little",signed=False)
    def write(self,address,data): # Write a 4-byte word to memory
        self.memory[address:address+4]=data.to_bytes(4,"little",signed=False)

def dec_to_bin(num): #2's complement for negative integers
   mask=1<<31
   result=""
   for _ in range(32):
       result+="1" if num&mask else "0"
       mask//=2
   return int(result,2)

def simulate(instructions): #Main function 
  cpu=CPU()
  cpu.memory=Memory(1024*128) #128kB
  program_bytes=bytearray()
  for instr in instructions: # Convert instructions to bytes
      program_bytes.extend(instr.to_bytes(4,'little',signed=False))
  cpu.memory.load_binaryprogram(program_bytes)
  max_cycles=1000
  cycles=0
  with open(sys.argv[2],"w") as f:
      while cpu.running and cycles<max_cycles:
          instruction=cpu.fetch()
          if not cpu.running:
              break
          opcode=cpu.decode(instruction)
          cpu.execute(opcode,instruction)
          f.write(f"0b{cpu.pc:032b} ") #Writing in file
          for i in cpu.regs:
              if i>0:
                  f.write(f"0b{i:032b} ")
              else:
                  f.write(f"0b{dec_to_bin(i):032b} ")
          f.write("\n")
          if cpu.pc>=len(instructions)*4 and cpu.pc%4==0 :
              is_beyond=True
              try:
                  next_addr=cpu.pc
                  if next_addr>cpu.memory.size:
                      is_beyond=True
              except IndexError:
                  is_beyond=True
              if is_beyond:
                  cpu.running=False
          cycles +=1
      for i in range(65536,65536+128,4):
          f.write(f"0x{i:08X}:0b{cpu.memory.read(i):032b}\n")
#Read binary file and simulate
with open(sys.argv[1],"r") as f:
  instructions=[int(line,2) for line in f]     
simulate(instructions)
