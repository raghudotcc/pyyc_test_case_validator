##############################################################################
# File: validator.py
# Description: This file validates the input python programs
#              as defined in the book "Python-to-x86" by
#              Jeremy Siek. User can also specify the subset of
#              python(P0, P1, P2, P3) to be validated. Both subset
#              and input program are required parameters to run the
#              validator.
# Date: 23/05/2022
# Version: 0.1
# Usage: python3 validator.py --subset=<python-subset> <input_file>
#        Example: python3 validator.py --subset=P0 test.py
##############################################################################

import argparse
import logging
import ast
from ast import *
import os

def is_valid_subset(subset):
    logging.info("Validating python subset: %s", subset)
    if subset.lower() not in ["p0", "p1", "p2", "p3"]:
        logging.error("Invalid python subset")
        return False
    return True

def is_valid_input_file(input_file):
    # Check if it is a python file
    logging.info("Validating input file: %s", input_file)
    if not input_file.endswith(".py"):
        logging.warning("Invalid input file")

    # check if input file exists
    if not os.path.exists(input_file):
        logging.error("Input file does not exist")
        return False
    return True

def is_valid_p0(tree):
    logging.info("Validating P0")
    P0_nodes = [Module, Assign, Name,
                Constant, Expr, Call,
                UnaryOp, BinOp, USub,
                Add, Store, Load]
    nodes = NodeVisitor().visit(tree).nodes
    for node in nodes:
        if node not in P0_nodes:
            logging.error("Invalid node: %s", node.__name__)
            raise Exception("P0 verification failed. Invalid node: %s" % node.__name__)
    
    return True
            

def validate(subset, input_file):
    logging.info("Validating input python program")
    tree = ast.parse(open(input_file).read())
    if subset.lower() == "p0":
        is_valid_p0(tree)
    logging.info("Validation complete")

class NodeVisitor(ast.NodeVisitor):
    def __init__(self):
        self.nodes = []

    def generic_visit(self, node):
        self.nodes.append(type(node))
        ast.NodeVisitor.generic_visit(self, node)
        return self
    

def main():
    parser = argparse.ArgumentParser(description="Validate python subset")
    parser.add_argument(
        "--subset", help="python subset to validate", required=True)
    parser.add_argument(
        "input_file", help="input file to validate")
    args = parser.parse_args()

    # Setup logging format
    FORMAT = '[%(levelname)s] File: %(filename)s, Line: %(lineno)d, %(message)s'
    logging.basicConfig(
        format=FORMAT, level=logging.INFO)

    if is_valid_subset(args.subset) and is_valid_input_file(args.input_file):
        validate(args.subset, args.input_file)
    

# call main function
if __name__ == "__main__":
    main()
