1 256 14 2

store 0 72
store 1 101
store 2 108
store 3 108
store 4 111
store 5 32
store 6 87
store 7 111
store 8 114
store 9 108
store 9 100
store 10 33
store 11 0
mov r0 0
call print
jmp exit


label print
load r1 r0
write r1
add r0 r0 1
jnz r1 print
ret