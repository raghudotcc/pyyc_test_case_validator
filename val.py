##############################################################################
# File: validator.py
# Description: This file validates the input python programs
#              as defined in the book "Python-to-x86" by
#              Jeremy Siek. User can also specify the subset of
#              python(P0, P1, P2, P3) to be validated. Both subset
#              and input program are required parameters to run the
#              validator.
# Date: 23/05/2022
# Version: 0.11
# Usage: python3 val.py --subset=<python-subset> --input_file=<input_file>
#        Example: python3 validator.py --subset=P0 --input=test.py
##############################################################################

import ast
from ast import *
import subprocess
import logging
import argparse
import os
import sys

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
    # type: (Popen) -> Result
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
    logging.info("Validating %s", subset_func.__name__)
    def wrapper(prog):
        tree = ast.parse(prog)
        valid_nodes = subset_func(prog)
        for node in ast.walk(tree):
            if type(node) not in valid_nodes:
                logging.error("Invalid node type: %s", type(node))
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

dispatch_tbl = { subset : eval(subset) for subset in subset_tbl }

def is_valid_subset(subset):
    if subset.lower() not in subset_tbl:
        logging.error("Invalid python subset")
        return False
    return True

def parse_nodes(subset, f):
    prog = f.read()
    return dispatch_tbl[subset.lower()](prog)

def exec_prog(file):
    tmp_file = 'tmp.py'
    def create_tmp(file):
        with open(file, 'r') as f:
            prog = f.read()
            prog = prog.replace('input()', 'int(input())')
            with open(tmp_file, 'w') as f:
                f.write(prog)
        return tmp_file
    
    def clean_tmp():
        if os.path.exists(tmp_file):
            os.remove(tmp_file)

    cmd = [python_exe, create_tmp(file)]
    infilename = os.path.splitext(file)[0] + '.in'
    if os.path.isfile(infilename):
        with open(infilename, 'r') as infile:
            popen = subprocess.Popen(cmd, 
                        stdin=infile, 
                        stdout=subprocess.PIPE)
    else:
        popen = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
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

    # Setup logging format
    FORMAT = '[%(levelname)s] File: %(filename)s, Line: %(lineno)d, %(message)s'
    logging.basicConfig(
        format=FORMAT, level=logging.INFO)

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
                        "Invalid program: %s" % file
                


if __name__ == "__main__":
    main()
