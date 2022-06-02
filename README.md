## Pyyc Test Case Validator

Python to x86 Test Case Validator

Given an input file and a subset of python(as mentioned in 
the book 'python-to-x86'), verify that the program is valid.

Validation is two part:

1) Parse the program and check if the program has 
the correct AST nodes.
2) Execute the program and check if the program runs
without error.

```python
Usage: python3 val.py --subset=<python-subset> \
                      --input_file=<file|dir>

Example: python3 val.py --subset=P0 --input=test.py
```

| Subset | Features |
| :-- | :--: |
| `P0`   | `Int`, `Assign`, `Add`, `Print`, `UnarySub`, `UserInput` |
| `P1`   | `P0`, `Dict`, `List`, `Bool`, `Subscription`, `List Concatenation`, `ComparisonOperators`(==, !=, is), `LogicalOperators`(and, or, not), `TernaryOperator`(IfExp) |
| `P2`   | `P1`, `Functions`, `Lambdas` |
| `P3`   | `P2`, `While`, `If` |





