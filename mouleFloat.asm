extern printf, atoi, atof
section .data
fmtInt : db "%d", 10, 0
fmtFloat : db "%g", 10, 0
argc : dq 0
argv : dq 0


DECL_VARS
STORE_FLOATS

section .text
global main
main : 
    push rbp
    mov [argc], rdi
    mov [argv], rsi
    
    INIT_VARS
    BODY
    RETURN 


    cmp cl, 'd'
    je _IntPrint
    cmp cl, 'f'
    je _FloatPrint
    jmp _end

    _IntPrint :
    mov rdi, fmtInt
    mov rsi, rax
    jmp _end

    _FloatPrint :
    mov rdi, fmtFloat
    mov rax, 1
    jmp _end


    _end :
    call printf
    pop rbp
    ret
