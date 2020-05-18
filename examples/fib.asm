3 256 14 5

mov r0 30
call fib
jmp exit


label fib
#r0 recives paramer and returns output
jnz r0 after_zero_case
ret #return 0
label after_zero_case
sub r0 r0 1
jnz r0 after_one_case
mov r0 1
ret
label after_one_case
push r0 # backup x-1
call fib
pop r1 # r1 = x-1
push r0
mov r0 r1
sub r0 r0 1 # r0 = x-2
call fib  # r0 = fib(x-2)
pop r1
add r0 r0 r1
ret