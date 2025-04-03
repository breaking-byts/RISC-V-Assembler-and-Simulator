


















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
                self.pc = current_pc + imm
