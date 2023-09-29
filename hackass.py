"""
structure

- parser
    IN raw code
    OUT rm comments
    return all the const @

- assembler
    takes the code with no comments + symbol set
    returns binary string
"""
import re
import argparse

AT = '@'

comp_table = {
    '0': '0101010',
    '1': '0111111',
    '-1': '0111010',
    'D': '0001100',
    'A': '0110000', #
    'M': '1110000', #
    '!D': '0001101',
    '!A': '0110001', #
    '!M': '1110001', #
    '-D': '0001111',
    '-A': '0110011', #
    '-M': '1110011', #
    'D+1': '0011111',
    'A+1': '0110111', #
    'M+1': '1110111', #
    'D-1': '0001110',
    'A-1': '0110010', #
    'M-1': '1110010', #
    'D+A': '0000010', #
    'D+M': '1000010', #
    'D-A': '0010011', #
    'D-M': '1010011', #
    'A-D': '0000111', #
    'M-D': '1000111', #
    'D&A': '0000000', #
    'D&M': '1000000', #
    'D|A': '0010101', #
    'D|M': '1010101', #
}

jump_table = {
    'JGT': '001',
    'JEQ': '010',
    'JLT': '100',
    'JGE': '011',
    'JNE': '101',
    'JLE': '110',
    'JMP': '111',
}

def dest_bit(dest: str) -> str:
    M = 1
    D = 10
    A = 100
    res = 0
    if 'M' in dest: res += M
    if 'D' in dest: res += D
    if 'A' in dest: res += A

    return str(res).zfill(3)

def remove_comments(input_string):
    pattern = r'\/\/[^\n]*'
    nocom =  re.sub(pattern, '', input_string)
    return "\n".join([ll.strip() for ll in nocom.splitlines() if ll.strip()])


def next_address(syms: list[int], sym_cursor: int) -> tuple[int, int]:
    for i in range(sym_cursor, len(syms) - 1):
        if syms[i + 1] - syms[i] != 1:
            nsym = syms[i] + 1
            syms.insert(i + 1, nsym)
            return nsym, i + 1
    nsym = syms[-1] + 1
    syms.append(nsym)
    return nsym, len(syms)


def parse(code: str) -> tuple[str, list[int]]:
    code = remove_comments(code)
    sym = {i for i in range(16)}

    for line in code.splitlines():
        try:
            if line[0] == AT:
                sym.add(int(line[1:]))
        except ValueError:
            pass
    l = sorted(sym)
    return code, l


def instruct(line: str) -> str:
    # print('converting:', line, end=' ')
    if line[0] == AT:
        res = bin(int(line[1:]))[2:].zfill(16)
        # print('->', res)
        return res
    
    ac = ''
    dest = '000'
    jump = '000'

    rhs = line
    if '=' in line:
        dest_reg, rhs = line.split('=')
        dest = dest_bit(dest_reg)
    if ';' in rhs:
        comp, jmp = rhs.split(';')
        jump = jump_table[jmp]
    else:
        comp = rhs
    ac = comp_table[comp]


    res = f'111{ac}{dest}{jump}'
    # print('->', res)
    return res


def assemble(code: str, syms: list[int]) -> list[str]:
    sym_cursor = 0
    sym_table = {f'R{i}': i for i in range(16)}
    sym_table['KBD'] = 24576
    sym_table['SCREEN'] = 16384
    sym_table['SP'] = 0
    sym_table['LCL'] = 1
    sym_table['ARG'] = 2
    sym_table['THIS'] = 3
    sym_table['THAT'] = 4
    assembled = []
    only_codes = []
    line_number = 0
    for line in code.splitlines():
        if line[0] == '(':
            symbol = line[1:-1]
            sym_table[symbol] = line_number
        else:
            line_number += 1
            only_codes.append(line)


    for line in only_codes:
        nline = line
        if line[0] == AT:
            symbol: str = line[1:]
            if symbol.isnumeric():
                pass
            elif symbol in sym_table:
                nline = f'@{sym_table[symbol]}'
            else:
                nsym, sym_cursor = next_address(syms, sym_cursor)
                sym_table[symbol] = nsym
                print(f'{symbol} -> {nsym}')
                nline = f'@{nsym}'
        
        assembled.append(instruct(nline))
    
    return assembled


def read_file(fp: str) -> str:
    with open(fp) as f:
        return f.read()
    

parser = argparse.ArgumentParser()
parser.add_argument("file", type=str, help="file path of the .asm file")
args = parser.parse_args()
code = read_file(args.file)
code, sym = parse(code)
binary = assemble(code, sym)
with open(f'{args.file}.hack', 'w') as f:
    for line in binary:
        f.write(line + '\n')