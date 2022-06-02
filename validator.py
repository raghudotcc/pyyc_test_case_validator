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
import p0

def is_valid_subset(subset):
    logging.info("Validating python subset: %s", subset)
    if subset.lower() not in ["p0", "p1", "p2", "p3"]:
        logging.error("Invalid python subset")
        return False
    return True

def validate(subset, input_file):
    # make the file name blue
    logging.info("Validating \033[1;34m %s \033[0m", input_file)
    with open(input_file, "r") as f:
        program = f.read()
        if subset.lower() == "p0":
            p0.validate(program)
    logging.info("Validation complete")
    

def main():
    parser = argparse.ArgumentParser(description="Validate python subset")
    parser.add_argument(
        "--subset", help="python subset to validate", required=True)
    parser.add_argument(
        "--input", help="input file(s) to validate")
    args = parser.parse_args()

    # Setup logging format
    FORMAT = '[%(levelname)s] File: %(filename)s, Line: %(lineno)d, %(message)s'
    logging.basicConfig(
        format=FORMAT, level=logging.INFO)

    if is_valid_subset(args.subset):
        if os.path.isdir(args.input):
            # run validation on all files in the directory
            for file in os.listdir(args.input):
                validate(args.subset, os.path.join(args.input, file))
        else:
            validate(args.subset, args.input)
    

# call main function
if __name__ == "__main__":
    main()
