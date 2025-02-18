def generate_test_assembly():
    with open('test.txt', 'w') as f:
        # Write some labels and instructions
        f.write("start:\n")

        # Generate 998 instructions (leaving space for the first label and final halt)
        for i in range(998):
            if i % 100 == 0:
                f.write(f"label_{i}:\n")

            # Mix of different instruction types
            if i % 7 == 0:
                f.write(f"add x1,x2,x3\n")
            elif i % 7 == 1:
                f.write(f"addi x1,x2,5\n")
            elif i % 7 == 2:
                f.write(f"sw x1,4(x2)\n")
            elif i % 7 == 3:
                f.write(f"lw x1,8(x2)\n")
            elif i % 7 == 4:
                f.write(f"beq x1,x2,label_{(i // 100) * 100}\n")
            elif i % 7 == 5:
                f.write(f"jal x1,label_{(i // 100) * 100}\n")
            else:
                f.write(f"slt x1,x2,x3\n")

        # Add the required halt instruction at the end
        f.write("beq zero,zero,0x00000000\n")


if __name__ == "__main__":
    generate_test_assembly()