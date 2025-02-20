class Assembler:
   def __init__(self):
       self.opcodes={
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
       self.func3={
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
       self.registers={
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
       self.abi_registers={
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


   def get_line_number(self):
       return self.current_line


   def text_parser(self,file_name):
       self.labels={}
       self.current_address=0
       self.instructions=[]
       has_halt=False
       try:
           with open(file_name,'r') as file:
               text=file.read()
               lines=text.split('\n')
               line_num=1
               for line in lines:
                   # Remove comments and whitespace
                   self.current_line=line_num
                   line=line.split('#')[0].strip()
                   if not line:
                       line_num+=1
                       continue
                   # Handle labels
                   if ':' in line:
                       label_parts=line.split(':')
                       label=label_parts[0].strip()
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
                       self.labels[label]=self.current_address
                       line=label_parts[1].strip()
                       if not line:
                           line_num+=1
                           continue
                   # Process instruction
                   parts=line.split(" ")
                   if not parts:
                       line_num+=1
                       continue
                   opcode_name=parts[0]
                   arguments_str=" ".join(parts[1:])
                   arguments=[arg.strip() for arg in arguments_str.split(",") if arg.strip()]
                   instruction_parts=[opcode_name]+arguments
                   opcode=self.opcodes.get(instruction_parts[0])
                   if opcode is None:
                       raise SyntaxError(f"Line {line_num}: Opcode {instruction_parts[0]} is invalid")
                   if instruction_parts[0]=='beq' and len(instruction_parts)==4:
                       if (instruction_parts[1]=='zero' and instruction_parts[2]=='zero' and instruction_parts[3]=='0x00000000' or instruction_parts[3]=='0'):
                           has_halt=True
                           if self.current_address!=len(self.instructions) * 4:
                               raise SyntaxError("Virtual Halt must be the last instruction")
                   # Validate registers and immediates
                   for reg in instruction_parts[1:]:
                       if reg in self.abi_registers:
                           continue
                       if '0x' in reg:
                           try:
                               imm=int(reg,16)
                               if imm>0x7FF or imm<-0x800:
                                   raise SyntaxError(f"Line {line_num}: Immediate value out of range: {reg}")
                           except ValueError:
                               raise SyntaxError(f"Line {line_num}: Invalid immediate value: {reg}")


                   self.instructions.append((instruction_parts,self.current_address,line_num))
                   self.current_address+=4
                   line_num+=1
               if not has_halt:
                   raise SyntaxError("Missing Virtual Halt instruction (beq zero,zero,0x00000000)")
               return self.instructions
       except FileNotFoundError:
           raise FileNotFoundError(f"Assembly file not found: {file_name}")
       except IOError:
           raise IOError(f"Error reading file: {file_name}")


   def reg_to_binary(self,reg):
       if reg in self.abi_registers:
           reg=self.abi_registers[reg]
       if reg in self.registers:
           return self.registers[reg]
       else:
           raise ValueError(f"Line {self.get_line_number()}: Invalid register: {reg}")


   def get_immediate_binary(self,imm_str,bits,signed=True):
       try:
           if imm_str.lower().startswith("0x"):
               imm=int(imm_str,16)
           else:
               imm=int(str(int(imm_str)),0)
           # If signed and the immediate is given in hex (or in any form)
           # but represents a negative two's complement number,adjust it.
           if signed and imm >= 2**(bits-1):
               imm=imm-2**bits
           max_val=(2**(bits-1))-1 if signed else (2**bits)-1
           min_val=-(2**(bits-1)) if signed else 0
           if imm>max_val or imm<min_val:
               raise ValueError(
                   f"Line {self.get_line_number()}: Immediate value {imm} out of range for {bits} bits"
               )
           # Use bit-masking to always get the two's complement representation.
           return format(imm & ((1<<bits)-1),f'0{bits}b')
       except ValueError as e:
           raise ValueError(
               f"Line {self.get_line_number()}: Invalid immediate value: {imm_str}"
           ) from e


   def get_branch_offset(self,label,current_address):
       if label not in self.labels:
           raise ValueError(f"Line {self.get_line_number()}: Undefined label: {label}")
       offset=self.labels[label]-current_address
       if offset%2!=0:
           raise ValueError(f"Line {self.get_line_number()}: Branch offset must be 2-byte aligned.")
       offset=offset>>1
       imm=self.get_immediate_binary(str(offset),12,signed=True)
       return f"{imm[0]}{imm[2:8]}{imm[8:12]}{imm[1]}"


   def get_jump_offset(self,target,current_address):
       if target.strip().lstrip("-").isdigit():
           offset=int(target)
       else:
           if target not in self.labels:
               raise ValueError(f"Line {self.get_line_number()}: Undefined label: {target}")
           # For labels,compute the byte offset and convert to halfword offset.
           offset=(self.labels[target]-current_address)>>1
       return self.get_immediate_binary(str(offset),20,signed=True)


   def I_type(self,instruction):
       if len(instruction)!=3 and len(instruction)!=4:
           raise SyntaxError(
               f"Line {self.get_line_number()}: Invalid number of arguments for I-type instruction: {instruction}")
       opcode=self.opcodes[instruction[0]]
       rd=self.reg_to_binary(instruction[1])
       if len(instruction)==3:
           mem_addr=instruction[2]
           if '(' not in mem_addr or ')' not in mem_addr:
               raise SyntaxError(f"Line {self.get_line_number()}: Invalid memory address format: {mem_addr}")
           offset=mem_addr[:mem_addr.find('(')]
           rs1=mem_addr[mem_addr.find('(')+1:mem_addr.find(')')]
           rs1=self.reg_to_binary(rs1)
           imm=self.get_immediate_binary(offset if offset else '0',12)
       else:
           rs1=self.reg_to_binary(instruction[2])
           imm=self.get_immediate_binary(instruction[3],12)
       func3=self.func3[instruction[0]]
       binary=f"{imm}{rs1}{func3}{rd}{opcode}"
       return binary


   def R_type(self,instruction):
       if len(instruction)!=4:
           raise SyntaxError(
               f"Line {self.get_line_number()}: Invalid number of arguments for R-type instruction: {instruction}")
       opcode=self.opcodes[instruction[0]]
       rd=self.reg_to_binary(instruction[1])
       rs1=self.reg_to_binary(instruction[2])
       rs2=self.reg_to_binary(instruction[3])
       func3=self.func3[instruction[0]]
       if instruction[0]=='sub':
           func7='0100000'
       else:
           func7='0000000'
       binary=f"{func7}{rs2}{rs1}{func3}{rd}{opcode}"
       return binary


   def B_type(self,instruction,current_address):
       if len(instruction)!=4:
           raise SyntaxError(
               f"Line {self.get_line_number()}: Invalid number of arguments for B-type instruction: {instruction}")
       opcode=self.opcodes[instruction[0]]
       rs1=self.reg_to_binary(instruction[1])
       rs2=self.reg_to_binary(instruction[2])
       func3=self.func3[instruction[0]]

       # Determine the immediate (branch offset) value.
       if (instruction[3].startswith('0x') or instruction[3].isdigit()
               or instruction[3].startswith('-')):
           imm=self.get_immediate_binary(instruction[3],12)
       else:
           imm=self.get_branch_offset(instruction[3],current_address)
       binary=f"{imm[0]}{imm[1:7]}{rs2}{rs1}{func3}{imm[7:11]}{imm[11]}{opcode}"
       return binary

   def J_type(self,instruction,current_address):
       if len(instruction)!=3:
           raise SyntaxError(
               f"Line {self.get_line_number()}: Invalid number of arguments for J-type instruction: {instruction}")
       opcode=self.opcodes[instruction[0]]
       rd=self.reg_to_binary(instruction[1])
       if instruction[2].startswith('0x') or instruction[2].isdigit() or instruction[2].startswith('-'):
           imm=self.get_immediate_binary(instruction[2],20)
       else:
           imm=self.get_jump_offset(instruction[2],current_address)
           binary=f"{imm[0]}{imm[10:20]}{imm[9]}{imm[1:9]}{rd}{opcode}"
           return binary
       if imm[0]=="1":
           binary=f"{'1'}{imm[0]}{imm[10:19]}{imm[9]}{imm[1:9]}{rd}{opcode}"
           return binary
       else:
           binary=f"{"0"}{imm[0]}{imm[10:19]}{imm[9]}{imm[1:9]}{rd}{opcode}"
           return binary

   def U_type(self,instruction):
       if len(instruction)!=3:
           raise SyntaxError(
               f"Line {self.get_line_number()}: Invalid number of arguments for U-type instruction: {instruction}")
       opcode=self.opcodes[instruction[0]]
       rd=self.reg_to_binary(instruction[1])
       imm=self.get_immediate_binary(instruction[2],20)
       binary=f"{imm}{rd}{opcode}"
       return binary

   def S_type(self,instruction):
       if len(instruction)!=3:
           raise SyntaxError(
               f"Line {self.get_line_number()}: Invalid number of arguments for S-type instruction: {instruction}")
       opcode=self.opcodes[instruction[0]]
       rs2=self.reg_to_binary(instruction[1])
       mem_addr=instruction[2]
       if '(' not in mem_addr or ')' not in mem_addr:
           raise SyntaxError(f"Line {self.get_line_number()}: Invalid memory address format: {mem_addr}")
       offset=mem_addr[:mem_addr.find('(')]
       rs1=mem_addr[mem_addr.find('(')+1:mem_addr.find(')')]
       rs1=self.reg_to_binary(rs1)
       imm=self.get_immediate_binary(offset if offset else '0',12)
       imm1=imm[:7]
       imm2=imm[7:]
       func3=self.func3[instruction[0]]
       binary=f"{imm1}{rs2}{rs1}{func3}{imm2}{opcode}"
       return binary
   
def _test(filename):
   assembler=Assembler()
   try:
       instructions_with_address=assembler.text_parser(filename)
       with open('output.txt','w') as f:  # Open in write mode to clear previous output
           for instruction_data in instructions_with_address:
               instruction,address,line_num=instruction_data
               assembler.current_line=line_num
               binary=None
               if instruction[0] in ['add','sub','and','or','slt','srl']:
                   binary=assembler.R_type(instruction)
               elif instruction[0] in ['addi','lw','jalr']:
                   binary=assembler.I_type(instruction)
               elif instruction[0]=='sw':
                   binary=assembler.S_type(instruction)
               elif instruction[0] in ['beq','bne','blt']:
                   binary=assembler.B_type(instruction,address)
               elif instruction[0]=='jal':
                   binary=assembler.J_type(instruction,address)
               if binary:
                   f.write(f"{binary}\n")
                   print(f"{binary}")
   except Exception as e:
       print(f"Error: {e}")

if __name__=="__main__":
    for i in range(0,11,1):
        if i==3:
            continue
        else:
            _test(f"Ex_test_{i}.txt")
            p=[]
            k=[]
            with open('output.txt','r') as f:
                for line in f:
                    p.append(line)
            with open(f'Ex_test_{i}1.txt','r') as f:
                for line in f:
                    k.append(line)
            for i in range(0,len(p)-1,1):
                if p[i]==k[i]:
                    print("Test Passed")
                else:
                    print("Test Failed")

            
