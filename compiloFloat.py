import lark

grammaire = lark.Lark(r"""
exp : SIGNED_NUMBER                     -> exp_nombre
| IDENTIFIER                            -> exp_var
| exp OPBIN exp                         -> exp_opbin
| "(" exp ")"                           -> exp_par
| SIGNED_NUMBER "," NUMBER              -> exp_reel
| SIGNED_NUMBER "!"                     -> exp_fact
| "float" "("exp")"                     -> exp_nb_to_reel
| "sqrt" "("exp")"                      -> exp_sqrt
com : IDENTIFIER "=" exp ";"            -> assignation
| "if" "(" exp ")" "{" bcom "}"         -> if
| "while" "(" exp ")" "{" bcom "}"      -> while
| "print" "(" exp ")"                   -> print
bcom : (com)*
prg : "main" "(" var_list ")" "{" bcom "return" "(" exp ")" ";"  "}"
var_list :                       -> vide
| IDENTIFIER (","  IDENTIFIER)*  -> aumoinsune
IDENTIFIER : /[a-zA-Z][a-zA-Z0-9]*/
OPBIN : /[+\-*>]/
%import common.WS
%import common.NUMBER
%import common.SIGNED_NUMBER
%ignore WS
""",start="prg")

op = {'+' : 'add', '-' : 'sub'}

def asm_exp(e):
    if e.data == "exp_nombre":
        return f"mov rax, {e.children[0].value}\n"
    elif e.data == "exp_var":
        n = next()
        return f"""
        mov cl, [{e.children[0].value}Type]
        cmp cl, 'd'
        je _IntVar{n}
        cmp cl, 'f'
        je _FloatVar{n}
        jmp _endVar{n}

        _IntVar{n} :
        mov rax, [{e.children[0].value}]
        jmp _endVar{n}

        _FloatVar{n} :
        movq xmm0, [{e.children[0].value}]
        jmp _endVar{n}

        _endVar{n} :
        """
    elif e.data == "exp_par":
        return asm_exp(e.children[0])
    elif e.data == "exp_reel":
        return f"movq xmm0, [cst{e.children[0].value}_{e.children[1].value}]"
    else:
        n = next()
        return f"""
        {reelOrInt(e, "Add", n)}
        _FloatAdd{n}:
        {asm_exp(e.children[2])}
        movq xmm1, xmm0
        {asm_exp(e.children[0])}
        {op[e.children[1].value]}sd xmm0, xmm1
        jmp _endAdd{n}

        _IntAdd{n}:
        {asm_exp(e.children[2])}
        push rax
        {asm_exp(e.children[0])}
        pop rbx
        {op[e.children[1].value]} rax, rbx
        jmp _endAdd{n}

        _endAdd{n}:
        """
def reelOrInt(e, jumpLabel,n):
    
    if e.data == "exp_nombre":
        return f"jmp _Int{jumpLabel}{n}"
    elif e.data == "exp_reel":
        return f"jmp _Float{jumpLabel}{n}"
    elif e.data == "exp_var":
        return f"""
            mov cl, [{e.children[0].value}Type]
            cmp cl, 'd'
            je _Int{jumpLabel}{n}
            cmp cl, 'f'
            je _Float{jumpLabel}{n}
            jmp _end{jumpLabel}{n}
            """
    elif e.data == "exp_par":
        return reelOrInt(e.children[0], jumpLabel, n)
    elif e.data == "exp_opbin":
        return reelOrInt(e.children[0], jumpLabel, n)


def pp_exp(e):
    if e.data in {"exp_nombre", "exp_var"}:
        return e.children[0].value
    elif e.data == "exp_par":
        return f"({pp_exp(e.children[0])})"
    elif e.data == "exp_reel":
        return f"{e.children[0].value}.{e.children[1].value}"
    elif e.data == "exp_fact":
        return f"{e.children[0].value}!"
    elif e.data == "exp_nb_to_reel":
        return f"float({pp_exp(e.children[0])})"
    elif e.data == "exp_sqrt":
        return f"sqrt({pp_exp(e.children[0])})"
    else:
        return f"{pp_exp(e.children[0])} {e.children[1].value} {pp_exp(e.children[2])}"

def vars_exp(e):
    if e.data  == "exp_nombre" or e.data == "exp_reel":
        return set()
    elif e.data ==  "exp_var":
        return { e.children[0].value }
    elif e.data == "exp_par":
        return vars_exp(e.children[0])
    elif e.data == "exp_opbin":
        L = vars_exp(e.children[0])
        R = vars_exp(e.children[2])
        return L | R

def floats_exp(e):
    S = set()
    if e.data == "exp_reel" :
        S = S | { f"cst{e.children[0].value}_{e.children[1].value} : dq {e.children[0].value}.{e.children[1].value}" }
    elif e.data == "exp_par":
        return floats_exp(e.children[0])
    elif e.data == "exp_opbin":
        S = S | floats_exp(e.children[2]) | floats_exp(e.children[0])
    return S



cpt = 0
def next():
    global cpt
    cpt += 1
    return cpt

def asm_com(c):
    if c.data == "assignation":
        n = next()
        E = asm_exp(c.children[1])
        S = f"{E}"
        if c.children[1].data == "exp_nombre":               
            S = S + f"""
            jmp _IntOutput{n}       
            """
        elif c.children[1].data == "exp_reel":               
            S = S + f"""
            jmp _FloatOutput{n}
            """
        elif c.children[1].data == "exp_var" :
            S = S + f"""
            mov cl, [{c.children[1].children[0].value}Type]
            cmp cl, 'd'
            je _IntOutput{n}
            cmp cl, 'f'
            je _FloatOutput{n}
            jmp _endOutput{n}
            """
        elif c.children[1].data == "exp_opbin":
            S = S + f""" {reelOrInt(c.children[1], "Output", n)}"""

        S = S + f"""
        _IntOutput{n} :
        mov [{c.children[0].value}], rax
        mov cl, 'd'
        mov [{c.children[0].value}Type], cl
        jmp _endOutput{n} 

        _FloatOutput{n} :
        movq [{c.children[0].value}], xmm0
        mov cl, 'f'
        mov [{c.children[0].value}Type], cl
        jmp _endOutput{n}

        _endOutput{n} :
        """

        return S
        
        

    elif c.data == "if":
        E = asm_exp(c.children[0])
        C = asm_bcom(c.children[1])
        n = next()
        return f"""
        {E}
        cmp rax, 0
        jz fin{n}
        {C}
fin{n} : nop
"""
    elif c.data == "while":
        E = asm_exp(c.children[0])
        C = asm_bcom(c.children[1])
        n = next()
        return f"""
        debut{n} : {E}
        cmp rax, 0
        jz fin{n}
        {C}
        jmp debut{n}
fin{n} : nop
"""
    elif c.data == "print":
        E = asm_exp(c.children[0])
        return f"""
        {E}
        mov rdi, fmt
        mov rsi, rax
        call printf
        """

def pp_com(c):
    if c.data == "assignation":
        return f"{c.children[0].value} = {pp_exp(c.children[1])};"
    elif c.data == "if":
        x = f"\n{pp_bcom(c.children[1])}"
        return f"if ({pp_exp(c.children[0])}) {{{x}}}"
    elif c.data == "while":
        x = f"\n{pp_bcom(c.children[1])}"
        return f"while ({pp_exp(c.children[0])}) {{{x}}}"
    elif c.data == "print":
        return f"print({pp_exp(c.children[0])})"

def vars_com(c):
    if c.data == "assignation":
        R = vars_exp(c.children[1])
        return {c.children[0].value} | R
    elif c.data in {"if", "while"}:
        B = vars_bcom(c.children[1])
        E = vars_exp(c.children[0]) 
        return E | B
    elif c.data == "print":
        return vars_exp(c.children[0])

def floats_com(c):
    if c.data == "assignation":
        return floats_exp(c.children[1])
    elif c.data in {"if", "while"}:
        B = floats_bcom(c.children[1])
        E = floats_exp(c.children[0]) 
        return E | B
    elif c.data == "print":
        return floats_exp(c.children[0])

def asm_bcom(bc):
    return "".join([asm_com(c) for c in bc.children])

def pp_bcom(bc):
    return "\n".join([pp_com(c) for c in bc.children])

def vars_bcom(bc):
    S = set()
    for c in bc.children:
        S = S | vars_com(c)
    return S

def floats_bcom(bc):
    S = set()
    for c in bc.children:
        S = S | floats_com(c)
    return S

def pp_var_list(vl):
    return ", ".join([t.value for t in vl.children])

def asm_prg(p):
    f = open("mouleFloat.asm")
    moule = f.read()
    C = asm_bcom(p.children[1])
    moule = moule.replace("BODY", C)
    E = asm_exp(p.children[2]) + f"\nmov cl, [{p.children[2].children[0].value}Type]"
    moule = moule.replace("RETURN", E)
    D = "\n".join([f"""{v} : dq 0\n{v}Type : db "" """ for v in vars_prg(p)])
    moule = moule.replace("DECL_VARS", D)
    F = "\n".join([f"{f}" for f in floats_prg(p)])
    moule = moule.replace("STORE_FLOATS", F)
    s = ""
    for i in range(len(p.children[0].children)):
        n = next()
        v = p.children[0].children[i].value
        e = f"""
        mov rbx, [argv]
        mov rdi, [rbx + { 8*(i+1)}]
        mov rcx, rdi
        _FloatOrInt{n} :
        mov al, [rcx]
        inc rcx
        cmp al, 0
        je _IntInput{n}
        cmp al, '.'
        je _FoaltInput{n}
        jmp _FloatOrInt{n}

        _FoaltInput{n} :
        xor rax, rax
        call atof
        movq [{v}], xmm0
        mov cl, 'f'
        mov [{v}Type], cl
        jmp _inputDone{n}

        _IntInput{n} :
        xor rax, rax

        call atoi
        mov [{v}], rax
        mov cl, 'd'
        mov [{v}Type], cl
        jmp _inputDone{n}

        _inputDone{n} :
        """
        s = s + e
    moule = moule.replace("INIT_VARS", s)    
    return moule

def vars_prg(p):
    L = set([t.value for t in p.children[0].children])
    C = vars_bcom(p.children[1])
    R = vars_exp(p.children[2])
    return L | C | R

def floats_prg(p):
    C = floats_bcom(p.children[1])
    R = floats_exp(p.children[2])
    return C | R

def pp_prg(p):
    L = pp_var_list(p.children[0])
    C = pp_bcom(p.children[1])
    R = pp_exp(p.children[2])
    return "main( %s ) { %s return(%s);\n}" % (L, C, R)

#ast = grammaire.parse("""main(a){
#    return (a);
#}
#""")

#ast = grammaire.parse("""main(){
#    b = 1 + 2;
#    return(b);
#    }
#    """)

#ast = grammaire.parse("""main(){
#    b = 1,3 + 2,1;
#    return(b);
#    }
#    """)

ast = grammaire.parse("""main(a){
    a = a + 1,2;
    b = 3,2;
    d = a + b;
    return(d);
    }
    """)




asm = asm_prg(ast)
f = open("ouf.asm", "w")
f.write(asm)
f.close()