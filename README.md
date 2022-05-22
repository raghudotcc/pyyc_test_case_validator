# Pyyc Test Case Validator
Python to x86 Test Case Validator

## Description

Validates the input python programs as defined in the book "Python-to-x86" by
Jeremy Siek. User can also specify the subset of python(P0, P1, P2, P3) to be validated. Both subset and input program file are required parameters to run the validator.

### Subset

| Subset | Features |
| :-- | :--: |
| `P0`   | `Int`, `Assign`, `Add`, `Print`, `UnarySub`, `UserInput` |
| `P1`   | `P0`, `Dict`, `List`, `Bool`, `Subscription`, `List Concatenation`, `ComparisonOperators`(==, !=, is), `LogicalOperators`(and, or, not), `TernaryOperator`(IfExp) |
| `P2`   | `P1`, `Functions`, `Lambdas` |
| `P3`   | `P2`, `While`, `If` |



## Usage

```python
python3 validator.py --subset=[P0 | P1 | P2 | P3] <input_file>  
```

## Example

```python
python3 validator.py --subset=P0 test_case_0.py  
```


