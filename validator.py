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

def subset(subset):
    """
    Validate the python subset
    """
    logging.info("Validating python subset")

    # create an attribute for the subset called valid
    
    # Check if the python subset is valid
    if subset.lower() not in ["p0", "p1", "p2", "p3"]:
        logging.error("Invalid python subset")
        return False
    logging.info("Python subset: %s", subset)

def validate(subset, input_file):
    """
    Validate the python program
    """
    logging.info("Validating python program")

    
    # Check if the python subset is valid
    if subset.lower() not in ["p0", "p1", "p2", "p3"]:
        logging.error("Invalid python subset")
        return False
    logging.info("Python subset: %s", subset)

    # Check if the input file exists
    try:
    input_file = open(input_file, 'r')


    logging.info("Input file: %s", input_file)


def main():
    """
    Main function
    """
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

    validate(args.subset, args.input_file)
    

# call main function
if __name__ == "__main__":
    main()
