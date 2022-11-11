extern printf, atoi
section .data
fmt : db "%d", 10, 0
argc : dq 0
argv : dq 0

DECL_VARS

section .text
global main
loop: 
    mov rax, rcx
    dec rcx 
    mul rbx 
    mov rbx,rax
    cmp rcx, 0 
    jnz loop 

    mov rax,rbx
    ret
main : 
    push rbp
    mov [argc], rdi
    mov [argv], rsi
    INIT_VARS
    BODY
    RETURN 
    
    mov rdi, fmt
    mov rsi, rax
    call printf
    pop rbp
    ret

