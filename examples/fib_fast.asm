4 256 14 4

mov r0 30
mov r1 0
mov r2 1

label loop
mov r3 r2
sub r0 r0 1
add r2 r2 r1
mov r1 r3
jnz r0 loop