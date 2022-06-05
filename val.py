"""Given an input file and a subset of python(as mentioned in 
the book 'python-to-x86'), verify that the program is valid.

Validation is two part:
1) Parse the program and check if the program has 
the correct AST nodes.
2) Execute the program and check if the program runs
without error.

Usage: python3 val.py --subset=<python-subset> \
                      --input_file=<file|dir>

Example: python3 val.py --subset=P0 --input=test.py
"""

import ast
from ast import *
import subprocess
import argparse
import os
import re

subset_tbl = ['p0', 'p1', 'p2', 'p3']
python_exe = 'python3'
nodes = [
    [Module, Assign, Name,
    Constant, Expr, Call,
    UnaryOp, BinOp, USub,
    Add, Store, Load], # < P0
    [List, Dict, Subscript,
    BoolOp, And, Or, Not,
    Eq, NotEq, Is,
    IfExp, Compare], # < P1
    [Return, FunctionDef, 
    Lambda, arguments, arg], # < P2
    [If, While, ClassDef] # < P3
]

def popen_result(popen):
    (out, err) = popen.communicate()
    retcode = popen.wait()
    if retcode != 0:
        if not (out is None):
            print(out)
        return False
    elif err: # stderr is not empty or None
        return False
    else:
        return True

def validate(subset_func):
    """Decorator to get valid nodes from subset func, 
    walk the AST and verify if input prog has valid AST nodes."""
    def wrapper(prog):
        tree = ast.parse(prog)
        valid_nodes = subset_func(prog)
        for node in ast.walk(tree):
            if type(node) not in valid_nodes:
                print("Invalid node type: {}".format(type(node)))
                return False
        return True
    return wrapper

@validate
def p0(prog):
    return nodes[0]

@validate
def p1(prog):
    return nodes[0] \
            + nodes[1]

@validate
def p2(prog):
    return nodes[0] \
            + nodes[1] \
            + nodes[2]

@validate
def p3(prog):
    return nodes[0] \
            + nodes[1] \
            + nodes[2] \
            + nodes[3]

# create a dict containing the subset as key
# and the function with the same name as the value
dispatch_tbl = { subset : eval(subset) for subset in subset_tbl }

def is_valid_subset(subset):
    if subset.lower() not in subset_tbl:
        print("Invalid python subset." \
            " Supported subsets: {}".format(subset_tbl))
        return False
    return True

def parse_nodes(subset, f):
    """validate the AST nodes using the validate decorator"""
    prog = f.read()
    return dispatch_tbl[subset.lower()](prog)

def exec_prog(file):
    """copy the prog to a tmp file and modify 
    the prog to replace stdin in the orig prog. 
    check if the modified program runs without 
    any error.
    """
    tmp_file = 'tmp.py'
    infilename = os.path.splitext(file)[0] + '.in'
    def create_tmp(file):
        with open(file, 'r') as f:
            prog = f.read()

        def stdin_to_ib(prog, infilename):
            re_input = re.compile(r'input\s*\(\s*\)')
            num_input = len(re_input.findall(prog))

            inputs = []
            if os.path.isfile(infilename):
                with open(infilename, 'r') as infile:
                        inputs = [line.rstrip() for line in infile.read().splitlines()]

            if len(inputs) < num_input:
                raise Exception("Not enough user inputs in the input" \
                    " file: {}".format(infilename))
            else:
                prog = re_input.sub(lambda x: 'bool(int(input()))' \
                        if inputs.pop(0) in ['True', 'False'] else 'int(int(input()))', prog)
                # debug modified prog
                # print("file: {}".format(file))
                # print(prog)
            
            return prog

        prog = stdin_to_ib(prog, infilename)    
        with open(tmp_file, 'w') as f:
            f.write(prog)
        return tmp_file
    
    def clean_tmp():
        if os.path.exists(tmp_file):
            os.remove(tmp_file)

    cmd = [python_exe, create_tmp(file)]
    if os.path.isfile(infilename):
        with open(infilename, 'r') as infile:
            popen = subprocess.Popen(cmd, 
                        stdin=infile, 
                        stdout=subprocess.PIPE)
    else:
        popen = subprocess.Popen(cmd, 
            stdin=subprocess.PIPE, 
            stdout=subprocess.PIPE)
    result = popen_result(popen)
    clean_tmp()
    return result

def parse_args():
    parser = argparse.ArgumentParser(description="Validate python subset")
    parser.add_argument(
        "--subset", help="python subset to validate", required=True)
    parser.add_argument(
        "--input", help="input file(s) to validate")
    return parser.parse_args()

def main():
    args = parse_args()

    prog_files = []
    if is_valid_subset(args.subset):
        if os.path.isdir(args.input):
            # run validation on all files in the directory
            for file in os.listdir(args.input):
                prog_files.append(os.path.join(args.input, file))
        else:
            prog_files.append(args.input)

        for file in prog_files:
            with open(file, 'r') as f:
                assert parse_nodes(args.subset, f) \
                        and exec_prog(file) == True, \
                        "invalid program: {}".format(file)

if __name__ == "__main__":
    main()
