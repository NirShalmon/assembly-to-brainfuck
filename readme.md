#  Assembly to Brainfuck Cross-Compiler

###  How to use:
##### Copmilation
To compile assembly code run:

    python compiler.py source_file.asm output_file.bf

#####  Framework definition - first line in assembly code
On the first non-comment line of the assembly file, there should be a line containing 4 space seperated integers.

The first integer is the size of the registers and memory cells in bytes(brainfuck cells). This should not be larger than required, as it strongly effects the runtime of the compiled code.

The second integer is the range of each byte(brainfuck memory cell). This should match the cell size that your interpreter supports. Use 256 unless you have a reason not to.

The third integer is the amount of temp registers. They are used internally by the compiled code. You should use a value that minimizes the compiled code size. 15 should be a good value to use. 

The last integer is the amount of user registers. If you use 5, your registers will be r0 to r4.

You can use 4 256 15 5 s a default.

##### Assembly language
The commands only change the value of the first register operand.
Some examples:
```
        add r0 r1 r2  # r0 = r1 + r2
        eq r0 r0 5     # r0 = r0 == 5
        mov r0 r2     # r0 = r2
```

The stack and main memory are seperate. You can use the stack with push, pop, call and ret commands.
###### Notice 
At each memory address or stack value, you have the same amount of bytes as you selected for your registers. This differs from most assembly languages where each memory adress points to a single byte.

You can find examples of code in the examples folder.

The file supported_commands.txt contains a full list of supported commands.